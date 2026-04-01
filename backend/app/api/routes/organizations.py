"""
Organizations Routes
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Organization, User

orgs_bp = Blueprint('organizations', __name__)


@orgs_bp.route('', methods=['GET'])
@jwt_required()
def get_my_organization():
    """Get current user's organization"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user or not user.organization:
        return jsonify({'error': 'No organization found'}), 404
    
    return jsonify({'organization': user.organization.to_dict()}), 200


@orgs_bp.route('', methods=['POST'])
@jwt_required()
def create_organization():
    """Create a new organization"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    
    if not data.get('slug'):
        return jsonify({'error': 'Slug is required'}), 400
    
    # Check if slug exists
    if Organization.query.filter_by(slug=data['slug']).first():
        return jsonify({'error': 'Slug already taken'}), 409
    
    org = Organization(
        name=data['name'],
        slug=data['slug'],
        description=data.get('description'),
        website=data.get('website'),
        address=data.get('address'),
        city=data.get('city'),
        country=data.get('country')
    )
    
    db.session.add(org)
    db.session.flush()
    
    # Assign user to organization
    user.organization_id = org.id
    db.session.commit()
    
    return jsonify({
        'message': 'Organization created',
        'organization': org.to_dict()
    }), 201


@orgs_bp.route('', methods=['PUT'])
@jwt_required()
def update_organization():
    """Update organization"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user or not user.organization:
        return jsonify({'error': 'No organization found'}), 404
    
    org = user.organization
    data = request.get_json()
    
    allowed_fields = ['name', 'description', 'website', 'facebook', 'twitter', 'linkedin', 'instagram', 'address', 'city', 'country', 'vat_number', 'logo', 'banner']
    for field in allowed_fields:
        if field in data:
            setattr(org, field, data[field])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Organization updated',
        'organization': org.to_dict()
    }), 200


@orgs_bp.route('/<int:org_id>', methods=['GET'])
@jwt_required()
def get_organization(org_id):
    """Get organization by ID"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    org = Organization.query.get(org_id)
    if not org:
        return jsonify({'error': 'Organization not found'}), 404
    
    # Check if user is member
    if user.organization_id != org_id and not user.is_super_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({'organization': org.to_dict()}), 200


@orgs_bp.route('/team', methods=['GET'])
@jwt_required()
def get_team():
    """Get organization team members"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user or not user.organization:
        return jsonify({'error': 'No organization found'}), 404
    
    members = User.query.filter_by(organization_id=user.organization_id).all()
    
    return jsonify({
        'team': [m.to_dict(include_email=True) for m in members]
    }), 200
