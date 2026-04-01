"""
Authentication Routes
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import datetime
from app import db, bcrypt
from app.models import User, Organization
import re

auth_bp = Blueprint('auth', __name__)


def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    return len(password) >= 8


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Validate required fields
    required = ['email', 'password', 'first_name', 'last_name']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Validate email
    if not validate_email(data['email']):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Validate password
    if not validate_password(data['password']):
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    
    # Check if user exists
    if User.query.filter_by(email=data['email'].lower()).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create user
    password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    user = User(
        email=data['email'].lower(),
        password_hash=password_hash,
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone=data.get('phone'),
        timezone=data.get('timezone', 'Europe/Brussels'),
        language=data.get('language', 'en')
    )
    
    # Create default organization if requested
    if data.get('create_organization'):
        org_name = data.get('organization_name', f"{user.first_name}'s Organization")
        org_slug = data.get('organization_slug', f"{user.first_name}-{user.last_name}".lower().replace(' ', '-'))
        
        if not Organization.query.filter_by(slug=org_slug).first():
            org = Organization(
                name=org_name,
                slug=org_slug
            )
            db.session.add(org)
            db.session.flush()
            user.organization_id = org.id
    
    db.session.add(user)
    db.session.commit()
    
    # Generate tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        'message': 'Registration successful',
        'user': user.to_dict(include_email=True),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    user = User.query.filter_by(email=data['email'].lower()).first()
    
    if not user or not bcrypt.check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 403
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Generate tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(include_email=True),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({'access_token': access_token}), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user profile"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict(include_email=True)}), 200


@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    """Update current user profile"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update allowed fields
    allowed_fields = ['first_name', 'last_name', 'phone', 'timezone', 'language']
    for field in allowed_fields:
        if field in data:
            setattr(user, field, data[field])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated',
        'user': user.to_dict(include_email=True)
    }), 200


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    if not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Current and new password required'}), 400
    
    if not bcrypt.check_password_hash(user.password_hash, data['current_password']):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    if not validate_password(data['new_password']):
        return jsonify({'error': 'New password must be at least 8 characters'}), 400
    
    user.password_hash = bcrypt.generate_password_hash(data['new_password']).decode('utf-8')
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'}), 200


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Send password reset email"""
    data = request.get_json()
    
    if not data.get('email'):
        return jsonify({'error': 'Email required'}), 400
    
    user = User.query.filter_by(email=data['email'].lower()).first()
    
    # Always return success to prevent email enumeration
    if not user:
        return jsonify({'message': 'If email exists, reset instructions were sent'}), 200
    
    # TODO: Generate reset token and send email
    # For now, just return success
    return jsonify({'message': 'If email exists, reset instructions were sent'}), 200


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token"""
    data = request.get_json()
    
    if not data.get('token') or not data.get('new_password'):
        return jsonify({'error': 'Token and new password required'}), 400
    
    # TODO: Validate reset token and update password
    return jsonify({'message': 'Password reset functionality coming soon'}), 501
