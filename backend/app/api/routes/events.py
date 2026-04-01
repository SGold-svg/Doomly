"""
Events Routes
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models import Event, User, TicketType, Section, PromoCode
from sqlalchemy import or_, and_

events_bp = Blueprint('events', __name__)


def generate_slug(title):
    """Generate URL-friendly slug from title"""
    slug = title.lower().replace(' ', '-')
    slug = ''.join(c for c in slug if c.isalnum() or c == '-')
    return slug


@events_bp.route('', methods=['GET'])
def list_events():
    """List public events"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    event_type = request.args.get('type', '')
    city = request.args.get('city', '')
    country = request.args.get('country', '')
    upcoming_only = request.args.get('upcoming', 'true').lower() == 'true'
    
    query = Event.query.filter_by(is_published=True, is_cancelled=False)
    
    if upcoming_only:
        query = query.filter(Event.end_date >= datetime.utcnow())
    
    if search:
        query = query.filter(
            or_(
                Event.title.ilike(f'%{search}%'),
                Event.description.ilike(f'%{search}%')
            )
        )
    
    if event_type:
        query = query.filter_by(event_type=event_type)
    
    if city:
        query = query.filter(Event.city.ilike(f'%{city}%'))
    
    if country:
        query = query.filter(Event.country.ilike(f'%{country}%'))
    
    query = query.order_by(Event.start_date.asc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'events': [e.to_dict(include_tickets=False) for e in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@events_bp.route('/<event_slug>', methods=['GET'])
def get_event(event_slug):
    """Get event details by slug"""
    event = Event.query.filter_by(slug=event_slug).first()
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # If private and not authenticated, return error
    if event.is_private:
        # TODO: Check if user has access
        pass
    
    return jsonify({'event': event.to_dict()}), 200


@events_bp.route('/my-events', methods=['GET'])
@jwt_required()
def my_events():
    """Get events for current user (organizer)"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', '')
    
    query = Event.query.filter_by(organizer_id=user_id)
    
    if status == 'draft':
        query = query.filter_by(is_published=False)
    elif status == 'published':
        query = query.filter_by(is_published=True)
    elif status == 'upcoming':
        query = query.filter(Event.start_date >= datetime.utcnow())
    elif status == 'past':
        query = query.filter(Event.end_date < datetime.utcnow())
    
    query = query.order_by(Event.start_date.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'events': [e.to_dict(include_tickets=True, include_stats=True) for e in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@events_bp.route('', methods=['POST'])
@jwt_required()
def create_event():
    """Create a new event"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Validate required fields
    required = ['title', 'start_date', 'end_date']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Generate unique slug
    base_slug = generate_slug(data['title'])
    slug = base_slug
    counter = 1
    while Event.query.filter_by(slug=slug).first():
        slug = f'{base_slug}-{counter}'
        counter += 1
    
    # Parse dates
    try:
        start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    event = Event(
        title=data['title'],
        slug=slug,
        description=data.get('description'),
        summary=data.get('summary'),
        event_type=data.get('event_type'),
        start_date=start_date,
        end_date=end_date,
        timezone=data.get('timezone', 'Europe/Brussels'),
        is_all_day=data.get('is_all_day', False),
        is_online=data.get('is_online', False),
        venue_name=data.get('venue_name'),
        address=data.get('address'),
        city=data.get('city'),
        country=data.get('country'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        online_link=data.get('online_link'),
        capacity=data.get('capacity'),
        is_private=data.get('is_private', False),
        organizer_id=user_id,
        organization_id=user.organization_id
    )
    
    db.session.add(event)
    db.session.commit()
    
    return jsonify({
        'message': 'Event created',
        'event': event.to_dict()
    }), 201


@events_bp.route('/<int:event_id>', methods=['GET'])
@jwt_required()
def get_event_by_id(event_id):
    """Get event by ID (for organizers)"""
    user_id = int(get_jwt_identity())
    event = Event.query.get(event_id)
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Check ownership
    if event.organizer_id != user_id and not User.query.get(user_id).is_super_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({'event': event.to_dict(include_stats=True)}), 200


@events_bp.route('/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_event(event_id):
    """Update an event"""
    user_id = int(get_jwt_identity())
    event = Event.query.get(event_id)
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Check ownership
    if event.organizer_id != user_id and not User.query.get(user_id).is_super_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Update allowed fields
    allowed_fields = [
        'title', 'description', 'summary', 'event_type', 'logo', 'banner', 'gallery',
        'start_date', 'end_date', 'timezone', 'is_all_day', 'is_online',
        'venue_name', 'address', 'city', 'country', 'latitude', 'longitude', 'online_link',
        'capacity', 'is_private', 'is_published', 'is_cancelled', 'meta_title', 'meta_description', 'meta_keywords'
    ]
    
    for field in allowed_fields:
        if field in data:
            if 'date' in field and data[field]:
                setattr(event, field, datetime.fromisoformat(data[field].replace('Z', '+00:00')))
            else:
                setattr(event, field, data[field])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Event updated',
        'event': event.to_dict()
    }), 200


@events_bp.route('/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_event(event_id):
    """Delete an event"""
    user_id = int(get_jwt_identity())
    event = Event.query.get(event_id)
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Check ownership
    if event.organizer_id != user_id and not User.query.get(user_id).is_super_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(event)
    db.session.commit()
    
    return jsonify({'message': 'Event deleted'}), 200


@events_bp.route('/<int:event_id>/publish', methods=['POST'])
@jwt_required()
def publish_event(event_id):
    """Publish an event"""
    user_id = int(get_jwt_identity())
    event = Event.query.get(event_id)
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    if event.organizer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    event.is_published = True
    event.published_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Event published',
        'event': event.to_dict()
    }), 200


@events_bp.route('/<int:event_id>/duplicate', methods=['POST'])
@jwt_required()
def duplicate_event(event_id):
    """Duplicate an event"""
    user_id = int(get_jwt_identity())
    event = Event.query.get(event_id)
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    if event.organizer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Create new event with duplicated data
    base_slug = generate_slug(f'{event.title} (Copy)')
    slug = base_slug
    counter = 1
    while Event.query.filter_by(slug=slug).first():
        slug = f'{base_slug}-{counter}'
        counter += 1
    
    new_event = Event(
        title=f'{event.title} (Copy)',
        slug=slug,
        description=event.description,
        summary=event.summary,
        event_type=event.event_type,
        logo=event.logo,
        banner=event.banner,
        capacity=event.capacity,
        organizer_id=user_id,
        organization_id=event.organization_id
    )
    
    db.session.add(new_event)
    db.session.commit()
    
    return jsonify({
        'message': 'Event duplicated',
        'event': new_event.to_dict()
    }), 201


# Sections/Agenda
@events_bp.route('/<int:event_id>/sections', methods=['GET'])
def get_sections(event_id):
    """Get event sections/agenda"""
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    sections = Section.query.filter_by(event_id=event_id, is_active=True).order_by(Section.sort_order).all()
    
    return jsonify({'sections': [s.to_dict() for s in sections]}), 200


@events_bp.route('/<int:event_id>/sections', methods=['POST'])
@jwt_required()
def create_section(event_id):
    """Create a section/agenda item"""
    user_id = int(get_jwt_identity())
    event = Event.query.get(event_id)
    
    if not event or event.organizer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    section = Section(
        event_id=event_id,
        title=data['title'],
        description=data.get('description'),
        start_time=datetime.fromisoformat(data['start_time'].replace('Z', '+00:00')) if data.get('start_time') else None,
        end_time=datetime.fromisoformat(data['end_time'].replace('Z', '+00:00')) if data.get('end_time') else None,
        location=data.get('location'),
        speaker_name=data.get('speaker_name'),
        speaker_title=data.get('speaker_title'),
        speaker_bio=data.get('speaker_bio'),
        speaker_avatar=data.get('speaker_avatar'),
        sort_order=data.get('sort_order', 0)
    )
    
    db.session.add(section)
    db.session.commit()
    
    return jsonify({'section': section.to_dict()}), 201


# Promo Codes
@events_bp.route('/<int:event_id>/promo-codes', methods=['GET'])
@jwt_required()
def get_promo_codes(event_id):
    """Get promo codes for event"""
    user_id = int(get_jwt_identity())
    event = Event.query.get(event_id)
    
    if not event or event.organizer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    codes = PromoCode.query.filter_by(event_id=event_id).all()
    
    return jsonify({'promo_codes': [c.to_dict() for c in codes]}), 200


@events_bp.route('/<int:event_id>/promo-codes', methods=['POST'])
@jwt_required()
def create_promo_code(event_id):
    """Create a promo code"""
    user_id = int(get_jwt_identity())
    event = Event.query.get(event_id)
    
    if not event or event.organizer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if not data.get('code'):
        return jsonify({'error': 'Code is required'}), 400
    
    # Check if code exists
    if PromoCode.query.filter_by(code=data['code'].upper()).first():
        return jsonify({'error': 'Code already exists'}), 409
    
    promo = PromoCode(
        event_id=event_id,
        code=data['code'].upper(),
        description=data.get('description'),
        discount_type=data.get('discount_type', 'percentage'),
        discount_value=data.get('discount_value', 0),
        max_uses=data.get('max_uses'),
        valid_from=datetime.fromisoformat(data['valid_from'].replace('Z', '+00:00')) if data.get('valid_from') else None,
        valid_until=datetime.fromisoformat(data['valid_until'].replace('Z', '+00:00')) if data.get('valid_until') else None
    )
    
    db.session.add(promo)
    db.session.commit()
    
    return jsonify({'promo_code': promo.to_dict()}), 201


@events_bp.route('/validate-promo', methods=['POST'])
def validate_promo_code():
    """Validate a promo code for an event"""
    data = request.get_json()
    
    code = data.get('code', '').upper()
    event_id = data.get('event_id')
    ticket_type_id = data.get('ticket_type_id')
    
    promo = PromoCode.query.filter_by(code=code, event_id=event_id).first()
    
    if not promo or not promo.is_active:
        return jsonify({'valid': False, 'error': 'Invalid code'}), 400
    
    now = datetime.utcnow()
    if promo.valid_from and now < promo.valid_from:
        return jsonify({'valid': False, 'error': 'Code not yet valid'}), 400
    if promo.valid_until and now > promo.valid_until:
        return jsonify({'valid': False, 'error': 'Code expired'}), 400
    if promo.max_uses and promo.uses_count >= promo.max_uses:
        return jsonify({'valid': False, 'error': 'Code usage limit reached'}), 400
    
    return jsonify({
        'valid': True,
        'discount_type': promo.discount_type,
        'discount_value': float(promo.discount_value)
    }), 200
