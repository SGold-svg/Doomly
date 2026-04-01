"""
Email Templates Routes
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db, mail
from app.models import Event, EmailTemplate, EmailLog
from flask import current_app
from flask_mail import Message
import re

emails_bp = Blueprint('emails', __name__)


def render_template(template_str, data):
    """Simple template rendering"""
    for key, value in data.items():
        template_str = template_str.replace(f'{{{key}}}', str(value))
    return template_str


@emails_bp.route('/templates/event/<int:event_id>', methods=['GET'])
@jwt_required()
def get_templates(event_id):
    """Get email templates for event"""
    user_id = int(get_jwt_identity())
    event = Event.query.get(event_id)
    
    if not event or event.organizer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    templates = EmailTemplate.query.filter_by(event_id=event_id).all()
    
    return jsonify({'templates': [t.to_dict() for t in templates]}), 200


@emails_bp.route('/templates/event/<int:event_id>', methods=['POST'])
@jwt_required()
def create_template(event_id):
    """Create email template"""
    user_id = int(get_jwt_identity())
    event = Event.query.get(event_id)
    
    if not event or event.organizer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if not data.get('name') or not data.get('subject') or not data.get('body'):
        return jsonify({'error': 'Name, subject, and body are required'}), 400
    
    template = EmailTemplate(
        event_id=event_id,
        name=data['name'],
        subject=data['subject'],
        body=data['body'],
        template_type=data.get('template_type'),
        is_active=data.get('is_active', True),
        send_delay_hours=data.get('send_delay_hours', 0)
    )
    
    db.session.add(template)
    db.session.commit()
    
    return jsonify({'template': template.to_dict()}), 201


@emails_bp.route('/templates/<int:template_id>', methods=['PUT'])
@jwt_required()
def update_template(template_id):
    """Update email template"""
    user_id = int(get_jwt_identity())
    template = EmailTemplate.query.get(template_id)
    
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    event = template.event
    if event.organizer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    allowed_fields = ['name', 'subject', 'body', 'template_type', 'is_active', 'send_delay_hours']
    for field in allowed_fields:
        if field in data:
            setattr(template, field, data[field])
    
    db.session.commit()
    
    return jsonify({'template': template.to_dict()}), 200


@emails_bp.route('/templates/<int:template_id>', methods=['DELETE'])
@jwt_required()
def delete_template(template_id):
    """Delete email template"""
    user_id = int(get_jwt_identity())
    template = EmailTemplate.query.get(template_id)
    
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    event = template.event
    if event.organizer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(template)
    db.session.commit()
    
    return jsonify({'message': 'Template deleted'}), 200


@emails_bp.route('/send', methods=['POST'])
@jwt_required()
def send_email():
    """Send a custom email"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data.get('to') or not data.get('subject') or not data.get('body'):
        return jsonify({'error': 'Recipient, subject, and body are required'}), 400
    
    try:
        msg = Message(
            subject=data['subject'],
            recipients=[data['to']],
            body=data['body'],
            sender=current_app.config.get('MAIL_USERNAME')
        )
        mail.send(msg)
        
        # Log the email
        email_log = EmailLog(
            recipient_email=data['to'],
            subject=data['subject'],
            status='sent',
            sent_at=datetime.utcnow()
        )
        db.session.add(email_log)
        db.session.commit()
        
        return jsonify({'message': 'Email sent'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@emails_bp.route('/logs/event/<int:event_id>', methods=['GET'])
@jwt_required()
def get_email_logs(event_id):
    """Get email logs for event"""
    user_id = int(get_jwt_identity())
    event = Event.query.get(event_id)
    
    if not event or event.organizer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    logs = EmailLog.query.filter_by(event_id=event_id).order_by(EmailLog.created_at.desc()).limit(100).all()
    
    return jsonify({'logs': [l.to_dict() for l in logs]}), 200


@emails_bp.route('/preview', methods=['POST'])
def preview_email():
    """Preview email template with sample data"""
    data = request.get_json()
    
    if not data.get('subject') or not data.get('body'):
        return jsonify({'error': 'Subject and body are required'}), 400
    
    # Sample data for preview
    sample_data = {
        'event_name': 'Sample Event 2024',
        'event_date': 'January 15, 2024',
        'event_location': 'Brussels, Belgium',
        'attendee_name': 'John Doe',
        'order_number': 'ORD-20240115-ABC12345',
        'ticket_type': 'VIP Pass',
        'ticket_count': '2 tickets',
        'total_amount': '€149.00',
        'organization_name': 'Doomly Events'
    }
    
    preview_subject = render_template(data['subject'], sample_data)
    preview_body = render_template(data['body'], sample_data)
    
    return jsonify({
        'subject': preview_subject,
        'body': preview_body
    }), 200
