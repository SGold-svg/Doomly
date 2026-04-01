"""
Orders Routes
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import uuid
from app import db
from app.models import Event, Order, OrderItem, TicketType, Attendee, PromoCode, User

orders_bp = Blueprint('orders', __name__)


def generate_order_number():
    """Generate unique order number"""
    return f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"


def generate_ticket_number():
    """Generate unique ticket number"""
    return f"TKT-{uuid.uuid4().hex[:12].upper()}"


@orders_bp.route('', methods=['POST'])
def create_order():
    """Create a new order (public endpoint for ticket purchasing)"""
    data = request.get_json()
    
    required = ['event_id', 'items', 'email']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    event = Event.query.get(data['event_id'])
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    if not event.is_published:
        return jsonify({'error': 'Event is not published'}), 400
    
    if event.is_cancelled:
        return jsonify({'error': 'Event is cancelled'}), 400
    
    # Validate items
    if not data.get('items') or len(data['items']) == 0:
        return jsonify({'error': 'At least one item is required'}), 400
    
    total_quantity = 0
    subtotal = 0
    order_items = []
    
    for item in data['items']:
        ticket = TicketType.query.get(item.get('ticket_type_id'))
        if not ticket:
            return jsonify({'error': f"Ticket type {item.get('ticket_type_id')} not found"}), 404
        
        quantity = item.get('quantity', 1)
        
        # Check availability
        if not ticket.is_available():
            return jsonify({'error': f"Ticket '{ticket.name}' is not available"}), 400
        
        if quantity > ticket.quantity_remaining:
            return jsonify({'error': f"Not enough tickets for '{ticket.name}'"}), 400
        
        if quantity > ticket.max_per_order:
            return jsonify({'error': f"Maximum {ticket.max_per_order} tickets per order for '{ticket.name}'"}), 400
        
        total_quantity += quantity
        unit_price = float(ticket.price) if ticket.price else 0
        item_total = unit_price * quantity
        subtotal += item_total
        
        order_items.append({
            'ticket': ticket,
            'quantity': quantity,
            'unit_price': unit_price,
            'total_price': item_total
        })
    
    # Check event capacity
    if event.capacity:
        current_attendees = sum(o.quantity for o in event.orders.filter_by(status='completed'))
        if current_attendees + total_quantity > event.capacity:
            return jsonify({'error': 'Not enough capacity for this event'}), 400
    
    # Calculate discount
    discount = 0
    promo = None
    if data.get('promo_code'):
        promo = PromoCode.query.filter_by(code=data['promo_code'].upper(), event_id=event.id).first()
        if promo and promo.is_active:
            now = datetime.utcnow()
            if (not promo.valid_from or now >= promo.valid_from) and (not promo.valid_until or now <= promo.valid_until):
                if not promo.max_uses or promo.uses_count < promo.max_uses:
                    if promo.discount_type == 'percentage':
                        discount = subtotal * (float(promo.discount_value) / 100)
                    elif promo.discount_type == 'fixed':
                        discount = float(promo.discount_value)
                    promo.uses_count += 1
    
    # Calculate fees (optional platform fee)
    fees = 0  # Could add platform fee calculation here
    
    total = subtotal - discount + fees
    
    # Create order
    order = Order(
        event_id=event.id,
        order_number=generate_order_number(),
        status='pending' if total > 0 else 'completed',
        payment_status='pending' if total > 0 else 'paid',
        quantity=total_quantity,
        subtotal=subtotal,
        discount=discount,
        fees=fees,
        total_amount=total,
        currency='EUR',
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        email=data['email'],
        company=data.get('company'),
        vat_number=data.get('vat_number'),
        notes=data.get('notes'),
        promo_code_id=promo.id if promo else None
    )
    
    if data.get('user_id'):
        order.user_id = data['user_id']
    
    db.session.add(order)
    db.session.flush()
    
    # Create order items and attendees
    for item in order_items:
        order_item = OrderItem(
            order_id=order.id,
            ticket_type_id=item['ticket'].id,
            quantity=item['quantity'],
            unit_price=item['unit_price'],
            total_price=item['total_price']
        )
        db.session.add(order_item)
        
        # Update ticket sales count
        item['ticket'].quantity_sold += item['quantity']
        
        # Create attendee records
        for i in range(item['quantity']):
            attendee_data = data.get('attendees', [{}])[i] if i < len(data.get('attendees', [])) else {}
            
            attendee = Attendee(
                event_id=event.id,
                order_id=order.id,
                ticket_type_id=item['ticket'].id,
                ticket_number=generate_ticket_number(),
                first_name=attendee_data.get('first_name', data.get('first_name', 'Guest')),
                last_name=attendee_data.get('last_name', data.get('last_name', '')),
                email=attendee_data.get('email', data['email']),
                phone=attendee_data.get('phone'),
                custom_fields=attendee_data.get('custom_fields')
            )
            db.session.add(attendee)
    
    # Update order status for free events
    if total == 0:
        order.status = 'completed'
        order.payment_status = 'paid'
        order.completed_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Order created',
        'order': order.to_dict()
    }), 201


@orders_bp.route('/<order_number>', methods=['GET'])
def get_order(order_number):
    """Get order by order number (public)"""
    order = Order.query.filter_by(order_number=order_number).first()
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    return jsonify({'order': order.to_dict()}), 200


@orders_bp.route('/my-orders', methods=['GET'])
@jwt_required()
def my_orders():
    """Get orders for current user"""
    user_id = int(get_jwt_identity())
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', '')
    
    query = Order.query.filter_by(user_id=user_id)
    
    if status:
        query = query.filter_by(status=status)
    
    query = query.order_by(Order.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'orders': [o.to_dict(include_items=True) for o in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@orders_bp.route('/event/<int:event_id>', methods=['GET'])
@jwt_required()
def get_event_orders(event_id):
    """Get all orders for an event (organizer only)"""
    user_id = int(get_jwt_identity())
    event = Event.query.get(event_id)
    
    if not event or event.organizer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    status = request.args.get('status', '')
    
    query = Order.query.filter_by(event_id=event_id)
    
    if status:
        query = query.filter_by(status=status)
    
    query = query.order_by(Order.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'orders': [o.to_dict() for o in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@orders_bp.route('/<int:order_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_order(order_id):
    """Cancel an order"""
    user_id = int(get_jwt_identity())
    order = Order.query.get(order_id)
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    # Check if user owns the order
    if order.user_id != user_id and order.event.organizer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if order.status == 'cancelled':
        return jsonify({'error': 'Order already cancelled'}), 400
    
    # Refund tickets
    for item in order.items:
        item.ticket_type.quantity_sold -= item.quantity
    
    # Mark attendees as cancelled
    for attendee in order.attendees:
        attendee.is_cancelled = True
    
    order.status = 'cancelled'
    order.cancelled_at = datetime.utcnow()
    
    # Release promo code usage
    if order.promo_code:
        order.promo_code.uses_count = max(0, order.promo_code.uses_count - 1)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Order cancelled',
        'order': order.to_dict()
    }), 200


@orders_bp.route('/<int:order_id>/complete', methods=['POST'])
@jwt_required()
def complete_order(order_id):
    """Mark order as completed (payment successful)"""
    user_id = int(get_jwt_identity())
    order = Order.query.get(order_id)
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    event = order.event
    if event.organizer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    order.status = 'completed'
    order.payment_status = 'paid'
    order.completed_at = datetime.utcnow()
    
    db.session.commit()
    
    # TODO: Send confirmation email
    
    return jsonify({
        'message': 'Order completed',
        'order': order.to_dict()
    }), 200
