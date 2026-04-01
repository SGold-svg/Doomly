"""
Check-in Routes
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import uuid
from app import db
from app.models import Event, Attendee, CheckInCode

checkin_bp = Blueprint('checkin', __name__)


@checkin_bp.route('/event/<int:event_id>/codes', methods=['GET'])
@jwt_required()
def get_checkin_codes(event_id):
    """Get check-in codes for event"""
    user_id = int(get_jwt_identity())
    event = Event.query.get(event_id)
    
    if not event or event.organizer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    codes = CheckInCode.query.filter_by(event_id=event_id).all()
    
    return jsonify({'codes': [c.to_dict() for c in codes]}), 200


@checkin_bp.route('/event/<int:event_id>/codes', methods=['POST'])
@jwt_required()
def create_checkin_code(event_id):
    """Create a new check-in code"""
    user_id = int(get_jwt_identity())
    event = Event.query.get(event_id)
    
    if not event or event.organizer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    
    # Generate unique code
    code = uuid.uuid4().hex[:8].upper()
    
    checkin_code = CheckInCode(
        event_id=event_id,
        name=data['name'],
        code=code,
        valid_from=datetime.fromisoformat(data['valid_from'].replace('Z', '+00:00')) if data.get('valid_from') else None,
        valid_until=datetime.fromisoformat(data['valid_until'].replace('Z', '+00:00')) if data.get('valid_until') else None
    )
    
    db.session.add(checkin_code)
    db.session.commit()
    
    return jsonify({'code': checkin_code.to_dict()}), 201


@checkin_bp.route('/event/<int:event_id>/stats', methods=['GET'])
@jwt_required()
def get_checkin_stats(event_id):
    """Get check-in statistics for event"""
    user_id = int(get_jwt_identity())
    event = Event.query.get(event_id)
    
    if not event or event.organizer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    total_attendees = Attendee.query.filter_by(event_id=event_id, is_cancelled=False).count()
    checked_in = Attendee.query.filter_by(event_id=event_id, is_checked_in=True).count()
    
    # By ticket type
    ticket_stats = []
    for ticket in event.tickets:
        ticket_total = Attendee.query.filter_by(
            event_id=event_id, 
            ticket_type_id=ticket.id, 
            is_cancelled=False
        ).count()
        ticket_checked = Attendee.query.filter_by(
            event_id=event_id, 
            ticket_type_id=ticket.id, 
            is_checked_in=True
        ).count()
        
        ticket_stats.append({
            'name': ticket.name,
            'total': ticket_total,
            'checked_in': ticket_checked,
            'rate': round(ticket_checked / ticket_total * 100, 1) if ticket_total > 0 else 0
        })
    
    return jsonify({
        'total_attendees': total_attendees,
        'checked_in': checked_in,
        'rate': round(checked_in / total_attendees * 100, 1) if total_attendees > 0 else 0,
        'by_ticket_type': ticket_stats
    }), 200


@checkin_bp.route('/scan/<code>', methods=['GET'])
@jwt_required()
def scan_code(code):
    """Check if a check-in code is valid"""
    user_id = int(get_jwt_identity())
    
    checkin_code = CheckInCode.query.filter_by(code=code.upper()).first()
    
    if not checkin_code:
        return jsonify({'valid': False, 'error': 'Invalid code'}), 404
    
    event = checkin_code.event
    if event.organizer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if not checkin_code.is_active:
        return jsonify({'valid': False, 'error': 'Code is deactivated'}), 400
    
    now = datetime.utcnow()
    if checkin_code.valid_from and now < checkin_code.valid_from:
        return jsonify({'valid': False, 'error': 'Code not yet valid'}), 400
    if checkin_code.valid_until and now > checkin_code.valid_until:
        return jsonify({'valid': False, 'error': 'Code expired'}), 400
    
    # Increment scan count
    checkin_code.scans_count += 1
    checkin_code.last_scan = now
    db.session.commit()
    
    return jsonify({
        'valid': True,
        'name': checkin_code.name,
        'event': event.title
    }), 200


@checkin_bp.route('/event/<int:event_id>/qr', methods=['GET'])
@jwt_required()
def get_event_qr_codes(event_id):
    """Get QR codes for event attendees"""
    user_id = int(get_jwt_identity())
    event = Event.query.get(event_id)
    
    if not event or event.organizer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    attendees = Attendee.query.filter_by(
        event_id=event_id, 
        is_cancelled=False
    ).all()
    
    qr_data = []
    for attendee in attendees:
        qr_data.append({
            'ticket_number': attendee.ticket_number,
            'name': f"{attendee.first_name} {attendee.last_name}",
            'email': attendee.email,
            'ticket_type': attendee.ticket_type.name if attendee.ticket_type else 'General',
            'is_checked_in': attendee.is_checked_in
        })
    
    return jsonify({'attendees': qr_data}), 200
