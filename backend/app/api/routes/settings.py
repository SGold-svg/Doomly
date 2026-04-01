"""
Settings Routes
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('', methods=['GET'])
@jwt_required()
def get_settings():
    """Get user settings"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    return jsonify({
        'settings': {
            'timezone': user.timezone,
            'language': user.language,
            'email_notifications': True,  # TODO: Add to model
            'marketing_emails': False
        }
    }), 200


@settings_bp.route('', methods=['PUT'])
@jwt_required()
def update_settings():
    """Update user settings"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    if 'timezone' in data:
        user.timezone = data['timezone']
    if 'language' in data:
        user.language = data['language']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Settings updated',
        'settings': {
            'timezone': user.timezone,
            'language': user.language
        }
    }), 200


@settings_bp.route('/notifications', methods=['PUT'])
@jwt_required()
def update_notification_settings():
    """Update notification preferences"""
    user_id = int(get_jwt_identity())
    
    # TODO: Create notification settings model
    
    return jsonify({'message': 'Notification settings updated'}), 200


@settings_bp.route('/api-keys', methods=['GET'])
@jwt_required()
def get_api_keys():
    """Get API keys for integrations"""
    user_id = int(get_jwt_identity())
    
    # TODO: Create API keys model
    
    return jsonify({
        'api_keys': []
    }), 200


@settings_bp.route('/api-keys', methods=['POST'])
@jwt_required()
def create_api_key():
    """Create new API key"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    
    # TODO: Create API keys
    
    return jsonify({'message': 'API key created'}), 201
