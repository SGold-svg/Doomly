"""
Tickets Routes
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models import Event, TicketType, User

tickets_bp = Blueprint('tickets', __name__)


@tickets_bp.route('/event/<int:event_id>', methods=['GET'])
def get_event_tickets(event_id):
    """Get all ticket types for an event"""
    event = Event.query.get(event_id)
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    tickets = TicketType.query.filter_by(event_id=event_id, is_hidden=False).order_by(TicketType.price).all()
    
    return jsonify({'tickets': [t.to_dict() for t in tickets]}), 200


@tickets_bp.route('/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    """Get ticket type details"""
    ticket = TicketType.query.get(ticket_id)
    
    if not ticket:
        return jsonify({'error': 'Ticket type not found'}), 404
    
    return jsonify({'ticket': ticket.to_dict()}), 200


@tickets_bp.route('/event/<int:event_id>', methods=['POST'])
@jwt_required()
def create_ticket(event_id):
    """Create a ticket type for an event"""
    user_id = int(get_jwt_identity())
    event = Event.query.get(event_id)
    
    if not event or event.organizer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    
    if not data.get('quantity_total'):
        return jsonify({'error': 'Quantity is required'}), 400
    
    ticket = TicketType(
        event_id=event_id,
        name=data['name'],
        description=data.get('description'),
        price=data.get('price', 0),
        currency=data.get('currency', 'EUR'),
        is_free=data.get('is_free', data.get('price', 0) == 0),
        quantity_total=data['quantity_total'],
        sales_start=datetime.fromisoformat(data['sales_start'].replace('Z', '+00:00')) if data.get('sales_start') else None,
        sales_end=datetime.fromisoformat(data['sales_end'].replace('Z', '+00:00')) if data.get('sales_end') else None,
        is_hidden=data.get('is_hidden', False),
        is_default=data.get('is_default', False),
        max_per_order=data.get('max_per_order', 10),
        min_per_order=data.get('min_per_order', 1),
        attributes=data.get('attributes')
    )
    
    db.session.add(ticket)
    db.session.commit()
    
    return jsonify({'ticket': ticket.to_dict()}), 201


@tickets_bp.route('/<int:ticket_id>', methods=['PUT'])
@jwt_required()
def update_ticket(ticket_id):
    """Update a ticket type"""
    user_id = int(get_jwt_identity())
    ticket = TicketType.query.get(ticket_id)
    
    if not ticket:
        return jsonify({'error': 'Ticket type not found'}), 404
    
    event = ticket.event
    if event.organizer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Update allowed fields
    allowed_fields = [
        'name', 'description', 'price', 'currency', 'is_free', 'quantity_total',
        'sales_start', 'sales_end', 'is_hidden', 'is_default', 'max_per_order', 'min_per_order', 'attributes'
    ]
    
    for field in allowed_fields:
        if field in data:
            if 'date' in field and data[field]:
                setattr(ticket, field, datetime.fromisoformat(data[field].replace('Z', '+00:00')))
            else:
                setattr(ticket, field, data[field])
    
    db.session.commit()
    
    return jsonify({'ticket': ticket.to_dict()}), 200


@tickets_bp.route('/<int:ticket_id>', methods=['DELETE'])
@jwt_required()
def delete_ticket(ticket_id):
    """Delete a ticket type"""
    user_id = int(get_jwt_identity())
    ticket = TicketType.query.get(ticket_id)
    
    if not ticket:
        return jsonify({'error': 'Ticket type not found'}), 404
    
    event = ticket.event
    if event.organizer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if tickets have been sold
    if ticket.quantity_sold > 0:
        # Just hide it instead of deleting
        ticket.is_hidden = True
        db.session.commit()
        return jsonify({'message': 'Ticket hidden (has existing sales)'}), 200
    
    db.session.delete(ticket)
    db.session.commit()
    
    return jsonify({'message': 'Ticket deleted'}), 200
