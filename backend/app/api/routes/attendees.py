"""
Attendees Routes
"""

from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models import Event, Attendee, Order

attendees_bp = Blueprint('attendees', __name__)


@attendees_bp.route('/event/<int:event_id>', methods=['GET'])
@jwt_required()
def get_event_attendees(event_id):
    """Get all attendees for an event"""
    user_id = int(get_jwt_identity())
    event = Event.query.get(event_id)
    
    if not event or event.organizer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    checked_in = request.args.get('checked_in')
    ticket_type = request.args.get('ticket_type')
    search = request.args.get('search', '')
    
    query = Attendee.query.filter_by(event_id=event_id, is_cancelled=False)
    
    if checked_in is not None:
        query = query.filter_by(is_checked_in=checked_in.lower() == 'true')
    
    if ticket_type:
        query = query.filter_by(ticket_type_id=int(ticket_type))
    
    if search:
        query = query.filter(
            db.or_(
                Attendee.first_name.ilike(f'%{search}%'),
                Attendee.last_name.ilike(f'%{search}%'),
                Attendee.email.ilike(f'%{search}%'),
                Attendee.ticket_number.ilike(f'%{search}%')
            )
        )
    
    query = query.order_by(Attendee.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'attendees': [a.to_dict() for a in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@attendees_bp.route('/event/<int:event_id>/export', methods=['GET'])
@jwt_required()
def export_attendees(event_id):
    """Export attendees to CSV"""
    user_id = int(get_jwt_identity())
    event = Event.query.get(event_id)
    
    if not event or event.organizer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    attendees = Attendee.query.filter_by(event_id=event_id, is_cancelled=False).order_by(Attendee.created_at).all()
    
    # Generate CSV
    csv_data = "Ticket Number,First Name,Last Name,Email,Phone,Ticket Type,Checked In,Check-in Time\n"
    
    for a in attendees:
        ticket_type_name = a.ticket_type.name if a.ticket_type else 'N/A'
        check_in_time = a.check_in_time.strftime('%Y-%m-%d %H:%M:%S') if a.check_in_time else ''
        
        csv_data += f"{a.ticket_number},{a.first_name},{a.last_name},{a.email},{a.phone or ''},{ticket_type_name},{a.is_checked_in},{check_in_time}\n"
    
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=attendees_{event.slug}.csv'}
    )


@attendees_bp.route('/<int:attendee_id>', methods=['GET'])
@jwt_required()
def get_attendee(attendee_id):
    """Get attendee details"""
    attendee = Attendee.query.get(attendee_id)
    
    if not attendee:
        return jsonify({'error': 'Attendee not found'}), 404
    
    return jsonify({'attendee': attendee.to_dict()}), 200


@attendees_bp.route('/<int:attendee_id>', methods=['PUT'])
@jwt_required()
def update_attendee(attendee_id):
    """Update attendee information"""
    user_id = int(get_jwt_identity())
    attendee = Attendee.query.get(attendee_id)
    
    if not attendee:
        return jsonify({'error': 'Attendee not found'}), 404
    
    event = attendee.event
    if event.organizer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    allowed_fields = ['first_name', 'last_name', 'email', 'phone', 'custom_fields']
    for field in allowed_fields:
        if field in data:
            setattr(attendee, field, data[field])
    
    db.session.commit()
    
    return jsonify({'attendee': attendee.to_dict()}), 200


@attendees_bp.route('/<int:attendee_id>/check-in', methods=['POST'])
@jwt_required()
def checkin_attendee(attendee_id):
    """Check in an attendee"""
    user_id = int(get_jwt_identity())
    attendee = Attendee.query.get(attendee_id)
    
    if not attendee:
        return jsonify({'error': 'Attendee not found'}), 404
    
    event = attendee.event
    if event.organizer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if attendee.is_checked_in:
        return jsonify({
            'message': 'Already checked in',
            'attendee': attendee.to_dict()
        }), 200
    
    attendee.is_checked_in = True
    attendee.check_in_time = datetime.utcnow()
    attendee.check_in_method = 'manual'
    
    db.session.commit()
    
    return jsonify({
        'message': 'Check-in successful',
        'attendee': attendee.to_dict()
    }), 200


@attendees_bp.route('/ticket/<ticket_number>/check-in', methods=['POST'])
@jwt_required()
def checkin_by_ticket(ticket_number):
    """Check in by ticket number (for QR scanning)"""
    user_id = int(get_jwt_identity())
    attendee = Attendee.query.filter_by(ticket_number=ticket_number.upper()).first()
    
    if not attendee:
        return jsonify({'error': 'Ticket not found', 'checked_in': False}), 404
    
    event = attendee.event
    if event.organizer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if attendee.is_checked_in:
        return jsonify({
            'message': 'Already checked in',
            'checked_in': True,
            'attendee': attendee.to_dict()
        }), 200
    
    attendee.is_checked_in = True
    attendee.check_in_time = datetime.utcnow()
    attendee.check_in_method = 'qr_code'
    
    db.session.commit()
    
    return jsonify({
        'message': 'Check-in successful',
        'checked_in': True,
        'attendee': attendee.to_dict()
    }), 200


@attendees_bp.route('/<int:attendee_id>/undo-check-in', methods=['POST'])
@jwt_required()
def undo_checkin(attendee_id):
    """Undo check-in for an attendee"""
    user_id = int(get_jwt_identity())
    attendee = Attendee.query.get(attendee_id)
    
    if not attendee:
        return jsonify({'error': 'Attendee not found'}), 404
    
    event = attendee.event
    if event.organizer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    attendee.is_checked_in = False
    attendee.check_in_time = None
    
    db.session.commit()
    
    return jsonify({
        'message': 'Check-in undone',
        'attendee': attendee.to_dict()
    }), 200
