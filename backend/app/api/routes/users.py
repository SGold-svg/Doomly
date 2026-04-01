"""
Users Routes
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User

users_bp = Blueprint('users', __name__)


@users_bp.route('', methods=['GET'])
@jwt_required()
def list_users():
    """List users in organization"""
    user_id = int(get_jwt_identity())
    current_user = User.query.get(user_id)
    
    if not current_user or not current_user.organization_id:
        return jsonify({'error': 'Not part of an organization'}), 400
    
    users = User.query.filter_by(organization_id=current_user.organization_id).all()
    
    return jsonify({'users': [u.to_dict(include_email=True) for u in users]}), 200


@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get user details"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict(include_email=True)}), 200


@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update user (admin only)"""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    # Only admins can update other users
    if user_id != current_user_id and not current_user.is_super_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Admin can update more fields
    if current_user.is_super_admin or current_user_id == user_id:
        allowed_fields = ['first_name', 'last_name', 'phone', 'timezone', 'language', 'avatar']
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        # Admin-only fields
        if current_user.is_super_admin:
            if 'is_active' in data:
                user.is_active = data['is_active']
            if 'is_super_admin' in data:
                user.is_super_admin = data['is_super_admin']
            if 'organization_id' in data:
                user.organization_id = data['organization_id']
    
    db.session.commit()
    
    return jsonify({'user': user.to_dict(include_email=True)}), 200


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Delete user (super admin only)"""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    if not current_user.is_super_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Prevent deleting yourself
    if user.id == current_user_id:
        return jsonify({'error': 'Cannot delete yourself'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted'}), 200


@users_bp.route('/invite', methods=['POST'])
@jwt_required()
def invite_user():
    """Invite a new user to organization"""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    if not current_user.organization_id:
        return jsonify({'error': 'Not part of an organization'}), 400
    
    data = request.get_json()
    
    if not data.get('email'):
        return jsonify({'error': 'Email is required'}), 400
    
    # Check if user exists
    if User.query.filter_by(email=data['email'].lower()).first():
        return jsonify({'error': 'User already exists'}), 409
    
    # TODO: Send invitation email with setup link
    
    return jsonify({'message': 'Invitation sent'}), 200
