"""
Database Models for Doomly Event Management
"""

from datetime import datetime
from app import db
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class User(db.Model):
    """User/Organizer model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(50))
    avatar = db.Column(db.String(500))
    timezone = db.Column(db.String(50), default='Europe/Brussels')
    language = db.Column(db.String(10), default='en')
    
    # Role-based access
    is_super_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    organization = db.relationship('Organization', backref='members', foreign_keys=[organization_id])
    events = db.relationship('Event', backref='organizer', lazy='dynamic')
    orders = db.relationship('Order', backref='user', lazy='dynamic')
    attendee_records = db.relationship('Attendee', backref='user', lazy='dynamic')
    
    def to_dict(self, include_email=False):
        data = {
            'uuid': self.uuid,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'avatar': self.avatar,
            'timezone': self.timezone,
            'language': self.language,
            'organization': self.organization.to_dict() if self.organization else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_email:
            data['email'] = self.email
        return data


class Organization(db.Model):
    """Organization/Company model"""
    __tablename__ = 'organizations'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)
    logo = db.Column(db.String(500))
    banner = db.Column(db.String(500))
    description = db.Column(db.Text)
    website = db.Column(db.String(500))
    facebook = db.Column(db.String(255))
    twitter = db.Column(db.String(255))
    linkedin = db.Column(db.String(255))
    instagram = db.Column(db.String(255))
    
    # Contact info
    address = db.Column(db.String(500))
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    vat_number = db.Column(db.String(50))
    
    # Settings
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    events = db.relationship('Event', backref='organization', lazy='dynamic')
    team_members = db.relationship('User', backref='org_membership', lazy='dynamic')
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'slug': self.slug,
            'logo': self.logo,
            'banner': self.banner,
            'description': self.description,
            'website': self.website,
            'social': {
                'facebook': self.facebook,
                'twitter': self.twitter,
                'linkedin': self.linkedin,
                'instagram': self.instagram
            },
            'address': self.address,
            'city': self.city,
            'country': self.country,
            'vat_number': self.vat_number,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Event(db.Model):
    """Event model"""
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    # Basic info
    title = db.Column(db.String(500), nullable=False)
    slug = db.Column(db.String(500), nullable=False, index=True)
    description = db.Column(db.Text)
    summary = db.Column(db.String(1000))
    
    # Event type
    event_type = db.Column(db.String(50))  # conference, workshop, webinar, concert, etc.
    
    # Media
    logo = db.Column(db.String(500))
    banner = db.Column(db.String(500))
    gallery = db.Column(db.JSON)  # Array of image URLs
    
    # Date/time
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    timezone = db.Column(db.String(50), default='Europe/Brussels')
    is_all_day = db.Column(db.Boolean, default=False)
    
    # Location
    is_online = db.Column(db.Boolean, default=False)
    venue_name = db.Column(db.String(255))
    address = db.Column(db.String(500))
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    online_link = db.Column(db.String(500))
    
    # Capacity & visibility
    capacity = db.Column(db.Integer)
    is_private = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=False)
    is_cancelled = db.Column(db.Boolean, default=False)
    is_sold_out = db.Column(db.Boolean, default=False)
    
    # organizer
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    
    # SEO
    meta_title = db.Column(db.String(255))
    meta_description = db.Column(db.String(500))
    meta_keywords = db.Column(db.String(255))
    
    # Settings
    settings = db.Column(db.JSON)  # Custom event settings
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    
    # Relationships
    tickets = db.relationship('TicketType', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    attendees = db.relationship('Attendee', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    sections = db.relationship('Section', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    promo_codes = db.relationship('PromoCode', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    emails = db.relationship('EmailTemplate', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    checkin_codes = db.relationship('CheckInCode', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_tickets=True, include_stats=False):
        data = {
            'uuid': self.uuid,
            'title': self.title,
            'slug': self.slug,
            'description': self.description,
            'summary': self.summary,
            'event_type': self.event_type,
            'logo': self.logo,
            'banner': self.banner,
            'gallery': self.gallery,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'timezone': self.timezone,
            'is_all_day': self.is_all_day,
            'location': {
                'is_online': self.is_online,
                'venue_name': self.venue_name,
                'address': self.address,
                'city': self.city,
                'country': self.country,
                'latitude': self.latitude,
                'longitude': self.longitude,
                'online_link': self.online_link
            },
            'capacity': self.capacity,
            'is_private': self.is_private,
            'is_published': self.is_published,
            'is_cancelled': self.is_cancelled,
            'is_sold_out': self.is_sold_out,
            'organizer': self.organizer.to_dict() if self.organizer else None,
            'organization': self.organization.to_dict() if self.organization else None,
            'seo': {
                'title': self.meta_title,
                'description': self.meta_description,
                'keywords': self.meta_keywords
            },
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None
        }
        
        if include_tickets:
            data['tickets'] = [t.to_dict() for t in self.tickets]
        
        if include_stats:
            data['stats'] = self.get_stats()
        
        return data
    
    def get_stats(self):
        total_orders = self.orders.count()
        completed_orders = self.orders.filter_by(status='completed').count()
        total_attendees = sum(o.quantity for o in self.orders.filter_by(status='completed'))
        revenue = sum(o.total_amount for o in self.orders.filter_by(status='completed'))
        
        return {
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'total_attendees': total_attendees,
            'revenue': float(revenue),
            'capacity': self.capacity,
            'remaining_capacity': (self.capacity or 0) - total_attendees
        }


class TicketType(db.Model):
    """Ticket type/variant model"""
    __tablename__ = 'ticket_types'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Pricing
    price = db.Column(db.Numeric(10, 2), default=0)
    currency = db.Column(db.String(3), default='EUR')
    is_free = db.Column(db.Boolean, default=False)
    
    # Quantity
    quantity_total = db.Column(db.Integer, nullable=False)
    quantity_sold = db.Column(db.Integer, default=0)
    
    # Sales window
    sales_start = db.Column(db.DateTime)
    sales_end = db.Column(db.DateTime)
    
    # Settings
    is_hidden = db.Column(db.Boolean, default=False)
    is_default = db.Column(db.Boolean, default=False)
    allow_quantity_limit = db.Column(db.Boolean, default=True)
    max_per_order = db.Column(db.Integer, default=10)
    min_per_order = db.Column(db.Integer, default=1)
    
    # Attributes
    attributes = db.Column(db.JSON)  # Custom attributes like color, icon
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='ticket_type', lazy='dynamic')
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'description': self.description,
            'price': float(self.price) if self.price else 0,
            'currency': self.currency,
            'is_free': self.is_free,
            'quantity_total': self.quantity_total,
            'quantity_sold': self.quantity_sold,
            'quantity_remaining': self.quantity_total - self.quantity_sold,
            'sales_start': self.sales_start.isoformat() if self.sales_start else None,
            'sales_end': self.sales_end.isoformat() if self.sales_end else None,
            'is_hidden': self.is_hidden,
            'is_default': self.is_default,
            'max_per_order': self.max_per_order,
            'min_per_order': self.min_per_order,
            'attributes': self.attributes,
            'is_available': self.is_available()
        }
    
    def is_available(self):
        now = datetime.utcnow()
        if self.is_hidden:
            return False
        if self.quantity_sold >= self.quantity_total:
            return False
        if self.sales_start and now < self.sales_start:
            return False
        if self.sales_end and now > self.sales_end:
            return False
        return True


class PromoCode(db.Model):
    """Promo/discount codes"""
    __tablename__ = 'promo_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    
    code = db.Column(db.String(50), nullable=False, unique=True, index=True)
    description = db.Column(db.String(255))
    
    # Discount type
    discount_type = db.Column(db.String(20))  # percentage, fixed
    discount_value = db.Column(db.Numeric(10, 2))
    
    # Usage limits
    max_uses = db.Column(db.Integer)
    uses_count = db.Column(db.Integer, default=0)
    
    # Ticket type restriction
    ticket_type_id = db.Column(db.Integer, db.ForeignKey('ticket_types.id'))
    
    # Validity
    valid_from = db.Column(db.DateTime)
    valid_until = db.Column(db.DateTime)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'code': self.code,
            'description': self.description,
            'discount_type': self.discount_type,
            'discount_value': float(self.discount_value) if self.discount_value else 0,
            'max_uses': self.max_uses,
            'uses_count': self.uses_count,
            'valid_from': self.valid_from.isoformat() if self.valid_from else None,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'is_active': self.is_active
        }


class Order(db.Model):
    """Order model"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, completed, cancelled, refunded
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, failed, refunded
    
    # Quantities
    quantity = db.Column(db.Integer, nullable=False)
    
    # Pricing
    subtotal = db.Column(db.Numeric(10, 2), default=0)
    discount = db.Column(db.Numeric(10, 2), default=0)
    fees = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(10, 2), default=0)
    currency = db.Column(db.String(3), default='EUR')
    
    # Promo code
    promo_code_id = db.Column(db.Integer, db.ForeignKey('promo_codes.id'))
    promo_code = db.relationship('PromoCode', backref='orders')
    
    # Attendee info
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(255), nullable=False)
    
    # Billing info
    company = db.Column(db.String(255))
    vat_number = db.Column(db.String(50))
    address = db.Column(db.String(500))
    
    # Payment info
    payment_method = db.Column(db.String(50))
    payment_reference = db.Column(db.String(255))
    
    # Notes
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_items=True):
        data = {
            'uuid': self.uuid,
            'order_number': self.order_number,
            'status': self.status,
            'payment_status': self.payment_status,
            'quantity': self.quantity,
            'subtotal': float(self.subtotal) if self.subtotal else 0,
            'discount': float(self.discount) if self.discount else 0,
            'fees': float(self.fees) if self.fees else 0,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'currency': self.currency,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'company': self.company,
            'payment_method': self.payment_method,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
        
        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
        
        return data


class OrderItem(db.Model):
    """Order item/ticket instance"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    ticket_type_id = db.Column(db.Integer, db.ForeignKey('ticket_types.id'), nullable=False)
    
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'ticket_type': self.ticket_type.to_dict() if self.ticket_type else None,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'total_price': float(self.total_price) if self.total_price else 0
        }


class Attendee(db.Model):
    """Attendee model (individual ticket holder)"""
    __tablename__ = 'attendees'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    ticket_number = db.Column(db.String(50), unique=True, nullable=False)
    
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    ticket_type_id = db.Column(db.Integer, db.ForeignKey('ticket_types.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Personal info
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50))
    
    # Custom fields
    custom_fields = db.Column(db.JSON)
    
    # Check-in status
    is_checked_in = db.Column(db.Boolean, default=False)
    check_in_time = db.Column(db.DateTime)
    check_in_method = db.Column(db.String(50))  # qr_code, manual, api
    
    # Status
    is_cancelled = db.Column(db.Boolean, default=False)
    is_refunded = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    order = db.relationship('Order', backref='attendees')
    ticket_type = db.relationship('TicketType', backref='attendees')
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'ticket_number': self.ticket_number,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'ticket_type': self.ticket_type.to_dict() if self.ticket_type else None,
            'is_checked_in': self.is_checked_in,
            'check_in_time': self.check_in_time.isoformat() if self.check_in_time else None,
            'check_in_method': self.check_in_method,
            'is_cancelled': self.is_cancelled,
            'is_refunded': self.is_refunded,
            'custom_fields': self.custom_fields,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Section(db.Model):
    """Event section/agenda item"""
    __tablename__ = 'sections'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    location = db.Column(db.String(255))
    
    speaker_name = db.Column(db.String(255))
    speaker_title = db.Column(db.String(255))
    speaker_bio = db.Column(db.Text)
    speaker_avatar = db.Column(db.String(500))
    
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'location': self.location,
            'speaker': {
                'name': self.speaker_name,
                'title': self.speaker_title,
                'bio': self.speaker_bio,
                'avatar': self.speaker_avatar
            } if self.speaker_name else None,
            'sort_order': self.sort_order
        }


class CheckInCode(db.Model):
    """QR code for event check-in"""
    __tablename__ = 'checkin_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    is_active = db.Column(db.Boolean, default=True)
    valid_from = db.Column(db.DateTime)
    valid_until = db.Column(db.DateTime)
    
    scans_count = db.Column(db.Integer, default=0)
    last_scan = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'code': self.code,
            'is_active': self.is_active,
            'valid_from': self.valid_from.isoformat() if self.valid_from else None,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'scans_count': self.scans_count,
            'last_scan': self.last_scan.isoformat() if self.last_scan else None
        }


class EmailTemplate(db.Model):
    """Email templates for events"""
    __tablename__ = 'email_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    
    name = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(500), nullable=False)
    body = db.Column(db.Text, nullable=False)
    
    template_type = db.Column(db.String(50))  # confirmation, reminder, cancellation, custom
    
    is_active = db.Column(db.Boolean, default=True)
    send_delay_hours = db.Column(db.Integer, default=0)  # Hours after order to send
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'subject': self.subject,
            'body': self.body,
            'template_type': self.template_type,
            'is_active': self.is_active,
            'send_delay_hours': self.send_delay_hours
        }


class EmailLog(db.Model):
    """Log of sent emails"""
    __tablename__ = 'email_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    attendee_id = db.Column(db.Integer, db.ForeignKey('attendees.id'))
    
    recipient_email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(500), nullable=False)
    
    status = db.Column(db.String(20), default='pending')  # pending, sent, failed
    error_message = db.Column(db.Text)
    
    sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'recipient_email': self.recipient_email,
            'subject': self.subject,
            'status': self.status,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None
        }
