"""
Dashboard Routes
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func
from app import db
from app.models import Event, Order, Attendee, User

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/overview', methods=['GET'])
@jwt_required()
def get_overview():
    """Get dashboard overview stats"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    # Get stats for user's events
    my_events = Event.query.filter_by(organizer_id=user_id)
    event_ids = [e.id for e in my_events.all()]
    
    if not event_ids:
        return jsonify({
            'total_events': 0,
            'total_orders': 0,
            'total_revenue': 0,
            'total_attendees': 0,
            'upcoming_events': 0,
            'recent_orders': []
        }), 200
    
    # Total orders
    total_orders = Order.query.filter(Order.event_id.in_(event_ids)).count()
    
    # Total revenue (completed orders)
    total_revenue = db.session.query(func.sum(Order.total_amount)).filter(
        Order.event_id.in_(event_ids),
        Order.status == 'completed'
    ).scalar() or 0
    
    # Total attendees
    total_attendees = Attendee.query.filter(
        Attendee.event_id.in_(event_ids),
        Attendee.is_cancelled == False
    ).count()
    
    # Upcoming events
    upcoming_events = my_events.filter(Event.start_date >= datetime.utcnow()).count()
    
    # Recent orders
    recent_orders = Order.query.filter(
        Order.event_id.in_(event_ids)
    ).order_by(Order.created_at.desc()).limit(10).all()
    
    return jsonify({
        'total_events': my_events.count(),
        'total_orders': total_orders,
        'total_revenue': float(total_revenue),
        'total_attendees': total_attendees,
        'upcoming_events': upcoming_events,
        'recent_orders': [o.to_dict() for o in recent_orders]
    }), 200


@dashboard_bp.route('/event/<int:event_id>', methods=['GET'])
@jwt_required()
def get_event_dashboard(event_id):
    """Get dashboard stats for specific event"""
    user_id = int(get_jwt_identity())
    event = Event.query.get(event_id)
    
    if not event or event.organizer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get stats
    total_orders = event.orders.count()
    completed_orders = event.orders.filter_by(status='completed').count()
    pending_orders = event.orders.filter_by(status='pending').count()
    
    total_revenue = db.session.query(func.sum(Order.total_amount)).filter(
        Order.event_id == event_id,
        Order.status == 'completed'
    ).scalar() or 0
    
    total_attendees = event.attendees.filter_by(is_cancelled=False).count()
    checked_in = event.attendees.filter_by(is_checked_in=True).count()
    
    # Revenue by day (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    daily_revenue = db.session.query(
        func.date(Order.created_at).label('date'),
        func.sum(Order.total_amount).label('revenue')
    ).filter(
        Order.event_id == event_id,
        Order.status == 'completed',
        Order.created_at >= thirty_days_ago
    ).group_by(func.date(Order.created_at)).all()
    
    # Ticket sales by type
    ticket_sales = []
    for ticket in event.tickets:
        ticket_sales.append({
            'name': ticket.name,
            'sold': ticket.quantity_sold,
            'remaining': ticket.quantity_total - ticket.quantity_sold,
            'revenue': ticket.quantity_sold * float(ticket.price or 0)
        })
    
    return jsonify({
        'event': event.to_dict(include_stats=True),
        'stats': {
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'pending_orders': pending_orders,
            'total_revenue': float(total_revenue),
            'total_attendees': total_attendees,
            'checked_in': checked_in,
            'check_in_rate': round(checked_in / total_attendees * 100, 1) if total_attendees > 0 else 0
        },
        'daily_revenue': [{'date': str(r.date), 'revenue': float(r.revenue)} for r in daily_revenue],
        'ticket_sales': ticket_sales
    }), 200


@dashboard_bp.route('/revenue', methods=['GET'])
@jwt_required()
def get_revenue_stats():
    """Get revenue statistics"""
    user_id = int(get_jwt_identity())
    
    # Get all events for user
    event_ids = [e.id for e in Event.query.filter_by(organizer_id=user_id).all()]
    
    if not event_ids:
        return jsonify({'revenue': [], 'total': 0}), 200
    
    # Revenue by month (last 12 months)
    twelve_months_ago = datetime.utcnow() - timedelta(days=365)
    
    monthly_revenue = db.session.query(
        func.strftime('%Y-%m', Order.completed_at).label('month'),
        func.sum(Order.total_amount).label('revenue'),
        func.count(Order.id).label('orders')
    ).filter(
        Order.event_id.in_(event_ids),
        Order.status == 'completed',
        Order.completed_at >= twelve_months_ago
    ).group_by(func.strftime('%Y-%m', Order.completed_at)).all()
    
    total = db.session.query(func.sum(Order.total_amount)).filter(
        Order.event_id.in_(event_ids),
        Order.status == 'completed'
    ).scalar() or 0
    
    return jsonify({
        'monthly': [{'month': r.month, 'revenue': float(r.revenue), 'orders': r.orders} for r in monthly_revenue],
        'total': float(total)
    }), 200


@dashboard_bp.route('/activity', methods=['GET'])
@jwt_required()
def get_activity():
    """Get recent activity"""
    user_id = int(get_jwt_identity())
    
    event_ids = [e.id for e in Event.query.filter_by(organizer_id=user_id).all()]
    
    if not event_ids:
        return jsonify({'activity': []}), 200
    
    # Recent orders
    recent_orders = Order.query.filter(
        Order.event_id.in_(event_ids)
    ).order_by(Order.created_at.desc()).limit(20).all()
    
    activity = []
    for order in recent_orders:
        event = Event.query.get(order.event_id)
        activity.append({
            'type': 'order',
            'message': f"New order #{order.order_number} for {event.title}",
            'amount': float(order.total_amount),
            'timestamp': order.created_at.isoformat()
        })
    
    # Recent check-ins
    recent_checkins = Attendee.query.filter(
        Attendee.event_id.in_(event_ids),
        Attendee.is_checked_in == True
    ).order_by(Attendee.check_in_time.desc()).limit(10).all()
    
    for attendee in recent_checkins:
        if attendee.check_in_time:
            activity.append({
                'type': 'checkin',
                'message': f"{attendee.first_name} {attendee.last_name} checked in",
                'timestamp': attendee.check_in_time.isoformat()
            })
    
    # Sort by timestamp
    activity.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return jsonify({'activity': activity[:20]}), 200
