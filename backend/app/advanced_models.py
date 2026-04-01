"""
Advanced Models for Doomly Event Management
Contains: User Roles, Permissions, Sessions, Custom Fields, Groups, Waiting Lists, Venues, etc.
"""

from datetime import datetime
from app import db
import uuid


def generate_uuid():
    return str(uuid.uuid4())


# ============== USER ROLES & PERMISSIONS ==============

class Role(db.Model):
    """User roles"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(500))
    
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    is_system = db.Column(db.Boolean, default=False)  # System roles can't be deleted
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    permissions = db.relationship('Permission', secondary='role_permissions', backref='roles')
    users = db.relationship('User', secondary='user_roles', backref='user_roles')
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'description': self.description,
            'permissions': [p.to_dict() for p in self.permissions],
            'is_system': self.is_system
        }


class Permission(db.Model):
    """Permissions"""
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(100), nullable=False, unique=True)  # e.g., 'events.create'
    description = db.Column(db.String(500))
    category = db.Column(db.String(50))  # e.g., 'events', 'attendees', 'finance'
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'category': self.category
        }


class UserRole(db.Model):
    """User to Role mapping"""
    __tablename__ = 'user_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))  # Event-specific role
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='role_assignments')
    role = db.relationship('Role', backref='user_assignments')


class RolePermission(db.Model):
    """Role to Permission mapping"""
    __tablename__ = 'role_permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=False)


# ============== VENUES & LOCATIONS ==============

class Venue(db.Model):
    """Venue/Location model"""
    __tablename__ = 'venues'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Address
    address = db.Column(db.String(500))
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Capacity
    capacity = db.Column(db.Integer)
    standing_capacity = db.Column(db.Integer)
    seating_capacity = db.Column(db.Integer)
    
    # Facilities
    facilities = db.Column(db.JSON)  # List of facilities: wifi, parking, catering, etc.
    
    # Contact
    contact_name = db.Column(db.String(255))
    contact_email = db.Column(db.String(255))
    contact_phone = db.Column(db.String(50))
    
    # Media
    images = db.Column(db.JSON)  # List of image URLs
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    rooms = db.relationship('VenueRoom', backref='venue', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'description': self.description,
            'address': self.address,
            'city': self.city,
            'country': self.country,
            'capacity': self.capacity,
            'facilities': self.facilities,
            'images': self.images,
            'rooms': [r.to_dict() for r in self.rooms]
        }


class VenueRoom(db.Model):
    """Rooms within a venue"""
    __tablename__ = 'venue_rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    capacity = db.Column(db.Integer)
    area_sqm = db.Column(db.Float)  # Square meters
    
    # Resources
    resources = db.Column(db.JSON)  # projector, whiteboard, etc.
    
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'description': self.description,
            'capacity': self.capacity,
            'area_sqm': self.area_sqm,
            'resources': self.resources
        }


# ============== SESSIONS & SCHEDULE ==============

class Session(db.Model):
    """Session/Track within an event"""
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
    venue_room_id = db.Column(db.Integer, db.ForeignKey('venue_rooms.id'))
    
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    
    # Timing
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    timezone = db.Column(db.String(50), default='Europe/Brussels')
    
    # Capacity
    capacity = db.Column(db.Integer)
    
    # Session type
    session_type = db.Column(db.String(50))  # keynote, workshop, break, networking
    
    # Visibility
    is_public = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    
    # Track/Category
    track = db.Column(db.String(100))
    
    # Speakers
    speakers = db.Column(db.JSON)  # List of speaker info
    
    # Materials
    materials = db.Column(db.JSON)  # Links to presentation files, etc.
    
    # Settings
    settings = db.Column(db.JSON)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(50), default='scheduled')  # scheduled, cancelled, completed
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    registrations = db.relationship('SessionRegistration', backref='session', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'venue_id': self.venue_id,
            'venue_room_id': self.venue_room_id,
            'capacity': self.capacity,
            'session_type': self.session_type,
            'track': self.track,
            'speakers': self.speakers,
            'is_public': self.is_public,
            'status': self.status,
            'registrations_count': self.registrations.count()
        }


class SessionRegistration(db.Model):
    """Session registration/capacity management"""
    __tablename__ = 'session_registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    attendee_id = db.Column(db.Integer, db.ForeignKey('attendees.id'), nullable=False)
    
    status = db.Column(db.String(50), default='registered')  # registered, waitlisted, attended, cancelled
    
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('session_id', 'attendee_id', name='unique_session_attendee'),)
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'session': self.session.to_dict() if self.session else None,
            'status': self.status,
            'registered_at': self.registered_at.isoformat() if self.registered_at else None
        }


# ============== CUSTOM FIELDS ==============

class CustomField(db.Model):
    """Custom registration fields"""
    __tablename__ = 'custom_fields'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    
    name = db.Column(db.String(255), nullable=False)
    field_type = db.Column(db.String(50), nullable=False)  # text, number, email, phone, dropdown, checkbox, radio, file, date
    
    # Options (for dropdown, radio, checkbox)
    options = db.Column(db.JSON)  # List of options
    
    # Validation
    is_required = db.Column(db.Boolean, default=False)
    min_length = db.Column(db.Integer)
    max_length = db.Column(db.Integer)
    pattern = db.Column(db.String(255))  # Regex pattern
    
    # Conditional logic
    conditional_logic = db.Column(db.JSON)  # Show this field when other field meets condition
    
    # Display
    placeholder = db.Column(db.String(255))
    help_text = db.Column(db.String(500))
    default_value = db.Column(db.String(255))
    
    # Order
    sort_order = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'field_type': self.field_type,
            'options': self.options,
            'is_required': self.is_required,
            'placeholder': self.placeholder,
            'help_text': self.help_text,
            'conditional_logic': self.conditional_logic,
            'sort_order': self.sort_order
        }


# ============== GROUP REGISTRATION ==============

class RegistrationGroup(db.Model):
    """Group registration (group leader)"""
    __tablename__ = 'registration_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    leader_attendee_id = db.Column(db.Integer, db.ForeignKey('attendees.id'))
    
    group_name = db.Column(db.String(255))
    
    # Status
    status = db.Column(db.String(50), default='pending')  # pending, complete, cancelled
    total_members = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    members = db.relationship('Attendee', backref='group', foreign_keys='Attendee.group_id')
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'group_name': self.group_name,
            'status': self.status,
            'total_members': self.total_members,
            'members': [m.to_dict() for m in self.members]
        }


# ============== WAITING LIST ==============

class WaitingList(db.Model):
    """Waiting list for sold out events"""
    __tablename__ = 'waiting_list'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    ticket_type_id = db.Column(db.Integer, db.ForeignKey('ticket_types.id'))
    
    # Person info
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50))
    
    # Request
    quantity_requested = db.Column(db.Integer, default=1)
    notes = db.Column(db.Text)
    
    # Status
    status = db.Column(db.String(50), default='waiting')  # waiting, notified, registered, expired
    position = db.Column(db.Integer)  # Queue position
    
    # Notification
    notified_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)  # When their spot offer expires
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    event = db.relationship('Event', backref='waiting_list')
    ticket_type = db.relationship('TicketType', backref='waiting_list')
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'quantity_requested': self.quantity_requested,
            'status': self.status,
            'position': self.position,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ============== REGISTRATION CODES ==============

class RegistrationCode(db.Model):
    """Code-restricted registrations"""
    __tablename__ = 'registration_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    
    code = db.Column(db.String(50), nullable=False, unique=True, index=True)
    description = db.Column(db.String(255))
    
    # Usage limits
    max_uses = db.Column(db.Integer)
    uses_count = db.Column(db.Integer, default=0)
    
    # Restrictions
    ticket_type_id = db.Column(db.Integer, db.ForeignKey('ticket_types.id'))  # Which ticket this code grants
    discount_percentage = db.Column(db.Float)  # Optional discount
    
    # Validity
    valid_from = db.Column(db.DateTime)
    valid_until = db.Column(db.DateTime)
    
    # Settings
    is_active = db.Column(db.Boolean, default=True)
    allow_multiple = db.Column(db.Boolean, default=False)  # Same email can use multiple times
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    event = db.relationship('Event', backref='registration_codes')
    ticket_type = db.relationship('TicketType', backref='registration_codes')
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'code': self.code,
            'description': self.description,
            'max_uses': self.max_uses,
            'uses_count': self.uses_count,
            'remaining': (self.max_uses - self.uses_count) if self.max_uses else None,
            'valid_from': self.valid_from.isoformat() if self.valid_from else None,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'is_active': self.is_active
        }


# ============== INVOICING ==============

class Invoice(db.Model):
    """Invoices"""
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    
    # Customer info
    customer_name = db.Column(db.String(255), nullable=False)
    customer_email = db.Column(db.String(255), nullable=False)
    customer_company = db.Column(db.String(255))
    customer_vat = db.Column(db.String(50))
    customer_address = db.Column(db.Text)
    
    # Invoice items
    items = db.Column(db.JSON)  # List of line items
    
    # Totals
    subtotal = db.Column(db.Numeric(10, 2), default=0)
    vat_rate = db.Column(db.Float, default=0)  # VAT percentage
    vat_amount = db.Column(db.Numeric(10, 2), default=0)
    total = db.Column(db.Numeric(10, 2), default=0)
    currency = db.Column(db.String(3), default='EUR')
    
    # Status
    status = db.Column(db.String(50), default='draft')  # draft, sent, paid, overdue, cancelled, refunded
    due_date = db.Column(db.DateTime)
    paid_at = db.Column(db.DateTime)
    
    # Notes
    notes = db.Column(db.Text)
    terms = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sent_at = db.Column(db.DateTime)
    
    order = db.relationship('Order', backref='invoice')
    event = db.relationship('Event', backref='invoices')
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'invoice_number': self.invoice_number,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'items': self.items,
            'subtotal': float(self.subtotal) if self.subtotal else 0,
            'vat_rate': self.vat_rate,
            'vat_amount': float(self.vat_amount) if self.vat_amount else 0,
            'total': float(self.total) if self.total else 0,
            'currency': self.currency,
            'status': self.status,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class CreditNote(db.Model):
    """Credit notes for refunds"""
    __tablename__ = 'credit_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    credit_note_number = db.Column(db.String(50), unique=True, nullable=False)
    
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    
    reason = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='EUR')
    
    status = db.Column(db.String(50), default='draft')  # draft, issued, void
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    invoice = db.relationship('Invoice', backref='credit_notes')
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'credit_note_number': self.credit_note_number,
            'amount': float(self.amount),
            'reason': self.reason,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ============== EMAIL CAMPAIGNS ==============

class EmailCampaign(db.Model):
    """Email campaigns"""
    __tablename__ = 'email_campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    
    name = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(500), nullable=False)
    
    # Content
    template_id = db.Column(db.Integer, db.ForeignKey('email_templates.id'))
    html_content = db.Column(db.Text)
    
    # Audience
    audience_type = db.Column(db.String(50))  # all_attendees, specific_tickets, waiting_list, etc.
    audience_filters = db.Column(db.JSON)  # Filter criteria
    
    # Scheduling
    send_at = db.Column(db.DateTime)  # Scheduled time
    sent_at = db.Column(db.DateTime)  # Actual send time
    
    # Status
    status = db.Column(db.String(50), default='draft')  # draft, scheduled, sending, sent, cancelled
    
    # Stats
    sent_count = db.Column(db.Integer, default=0)
    opened_count = db.Column(db.Integer, default=0)
    clicked_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    event = db.relationship('Event', backref='email_campaigns')
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'subject': self.subject,
            'audience_type': self.audience_type,
            'send_at': self.send_at.isoformat() if self.send_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'status': self.status,
            'sent_count': self.sent_count,
            'opened_count': self.opened_count,
            'clicked_count': self.clicked_count
        }


# ============== HOTEL & ACCOMMODATION ==============

class Hotel(db.Model):
    """Hotel/Acommodation partner"""
    __tablename__ = 'hotels'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    address = db.Column(db.String(500))
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    
    contact_email = db.Column(db.String(255))
    contact_phone = db.Column(db.String(50))
    website = db.Column(db.String(500))
    
    rating = db.Column(db.Float)  # Star rating
    
    images = db.Column(db.JSON)
    amenities = db.Column(db.JSON)  # wifi, parking, etc.
    
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    room_types = db.relationship('HotelRoomType', backref='hotel', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'description': self.description,
            'address': self.address,
            'city': self.city,
            'rating': self.rating,
            'amenities': self.amenities,
            'images': self.images,
            'room_types': [r.to_dict() for r in self.room_types]
        }


class HotelRoomType(db.Model):
    """Room types at a hotel"""
    __tablename__ = 'hotel_room_types'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id'), nullable=False)
    
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price_per_night = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='EUR')
    
    capacity = db.Column(db.Integer, default=2)
    
    amenities = db.Column(db.JSON)
    images = db.Column(db.JSON)
    
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'description': self.description,
            'price_per_night': float(self.price_per_night) if self.price_per_night else 0,
            'currency': self.currency,
            'capacity': self.capacity,
            'amenities': self.amenities
        }


class HotelBooking(db.Model):
    """Hotel bookings made through the platform"""
    __tablename__ = 'hotel_bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    booking_reference = db.Column(db.String(50), unique=True, nullable=False)
    
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    attendee_id = db.Column(db.Integer, db.ForeignKey('attendees.id'))
    
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id'), nullable=False)
    room_type_id = db.Column(db.Integer, db.ForeignKey('hotel_room_types.id'), nullable=False)
    
    # Dates
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    nights = db.Column(db.Integer)
    
    # Guest info
    guest_name = db.Column(db.String(255), nullable=False)
    guest_email = db.Column(db.String(255), nullable=False)
    guest_phone = db.Column(db.String(50))
    
    # Pricing
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='EUR')
    
    # Status
    status = db.Column(db.String(50), default='pending')  # pending, confirmed, cancelled
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    hotel = db.relationship('Hotel', backref='bookings')
    room_type = db.relationship('HotelRoomType', backref='bookings')
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'booking_reference': self.booking_reference,
            'guest_name': self.guest_name,
            'check_in': self.check_in.isoformat() if self.check_in else None,
            'check_out': self.check_out.isoformat() if self.check_out else None,
            'nights': self.nights,
            'total_price': float(self.total_price) if self.total_price else 0,
            'status': self.status
        }


# ============== FILE UPLOADS ==============

class EventFile(db.Model):
    """Files uploaded for events"""
    __tablename__ = 'event_files'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    
    name = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(500), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(100))  # mime type
    file_size = db.Column(db.Integer)  # bytes
    
    # Access
    access_type = db.Column(db.String(50), default='attendees')  # attendees, public, restricted
    
    # Visibility
    is_active = db.Column(db.Boolean, default=True)
    
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    event = db.relationship('Event', backref='files')
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'filename': self.filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'access_type': self.access_type,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }


class AttendeeFile(db.Model):
    """Files uploaded by attendees during registration"""
    __tablename__ = 'attendee_files'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    attendee_id = db.Column(db.Integer, db.ForeignKey('attendees.id'), nullable=False)
    custom_field_id = db.Column(db.Integer, db.ForeignKey('custom_fields.id'))
    
    name = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(500), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(100))
    file_size = db.Column(db.Integer)
    
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    attendee = db.relationship('Attendee', backref='files')
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'filename': self.filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }


# ============== WEBHOOKS & INTEGRATIONS ==============

class Webhook(db.Model):
    """Webhooks for integrations"""
    __tablename__ = 'webhooks'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    
    # Events to trigger on
    events = db.Column(db.JSON)  # e.g., ['order.created', 'attendee.checkin']
    
    # Security
    secret = db.Column(db.String(255))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Stats
    success_count = db.Column(db.Integer, default=0)
    failure_count = db.Column(db.Integer, default=0)
    last_triggered = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    organization = db.relationship('Organization', backref='webhooks')
    logs = db.relationship('WebhookLog', backref='webhook', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'url': self.url,
            'events': self.events,
            'is_active': self.is_active,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None
        }


class WebhookLog(db.Model):
    """Webhook delivery logs"""
    __tablename__ = 'webhook_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    webhook_id = db.Column(db.Integer, db.ForeignKey('webhooks.id'), nullable=False)
    
    event = db.Column(db.String(100), nullable=False)  # Event type
    payload = db.Column(db.JSON)
    
    response_status = db.Column(db.Integer)
    response_body = db.Column(db.Text)
    
    status = db.Column(db.String(50), default='pending')  # pending, success, failed
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    delivered_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'event': self.event,
            'status': self.status,
            'response_status': self.response_status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ============== API KEYS ==============

class APIKey(db.Model):
    """API keys for external integrations"""
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    
    name = db.Column(db.String(255), nullable=False)
    key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    
    # Permissions
    permissions = db.Column(db.JSON)  # List of allowed operations
    
    # Restrictions
    ip_whitelist = db.Column(db.JSON)  # List of allowed IPs
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Usage stats
    request_count = db.Column(db.Integer, default=0)
    last_used = db.Column(db.DateTime)
    
    expires_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    organization = db.relationship('Organization', backref='api_keys')
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'key_preview': self.key[:8] + '...' if self.key else None,
            'permissions': self.permissions,
            'is_active': self.is_active,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'last_used': self.last_used.isoformat() if self.last_used else None
        }


# ============== REGISTRATION THRESHOLDS & FEES ==============

class RegistrationThreshold(db.Model):
    """Early bird and deadline pricing"""
    __tablename__ = 'registration_thresholds'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    ticket_type_id = db.Column(db.Integer, db.ForeignKey('ticket_types.id'), nullable=False)
    
    name = db.Column(db.String(255), nullable=False)  # e.g., "Early Bird", "Regular", "Late"
    
    # Price
    price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Timing
    valid_from = db.Column(db.DateTime, nullable=False)
    valid_until = db.Column(db.DateTime, nullable=False)
    
    # Usage
    max_sales = db.Column(db.Integer)  # Max tickets at this price
    sales_count = db.Column(db.Integer, default=0)
    
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    ticket_type = db.relationship('TicketType', backref='thresholds')
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'price': float(self.price) if self.price else 0,
            'valid_from': self.valid_from.isoformat() if self.valid_from else None,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'remaining': (self.max_sales - self.sales_count) if self.max_sales else None
        }


class AdministrativeFee(db.Model):
    """Administrative fees for orders"""
    __tablename__ = 'administrative_fees'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500))
    
    # Fee type
    fee_type = db.Column(db.String(50))  # fixed, percentage
    
    value = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Conditions
    min_order_amount = db.Column(db.Numeric(10, 2))  # Apply only if order >= this
    max_fee = db.Column(db.Numeric(10, 2))  # Cap for percentage fees
    
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'description': self.description,
            'fee_type': self.fee_type,
            'value': float(self.value) if self.value else 0,
            'min_order_amount': float(self.min_order_amount) if self.min_order_amount else None,
            'max_fee': float(self.max_fee) if self.max_fee else None
        }


# ============== MULTILINGUAL ==============

class EventTranslation(db.Model):
    """Event translations for multilingual"""
    __tablename__ = 'event_translations'
    
    id = db.Column(db.Integer, primary_key=True)
    
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    language = db.Column(db.String(10), nullable=False)  # en, fr, nl, de, etc.
    
    title = db.Column(db.String(500))
    description = db.Column(db.Text)
    summary = db.Column(db.String(1000))
    
    # SEO
    meta_title = db.Column(db.String(255))
    meta_description = db.Column(db.String(500))
    
    # Location
    venue_name = db.Column(db.String(255))
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    event = db.relationship('Event', backref='translations')
    
    __table_args__ = (db.UniqueConstraint('event_id', 'language', name='unique_event_language'),)


# ============== STOCK MANAGEMENT ==============

class StockItem(db.Model):
    """Stock items for events (merchandise, etc.)"""
    __tablename__ = 'stock_items'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Pricing
    price = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='EUR')
    
    # Stock
    stock_total = db.Column(db.Integer, default=0)
    stock_available = db.Column(db.Integer, default=0)
    
    # Options (sizes, colors, etc.)
    options = db.Column(db.JSON)  # {'sizes': ['S', 'M', 'L'], 'colors': ['red', 'blue']}
    
    image = db.Column(db.String(500))
    
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    event = db.relationship('Event', backref='stock_items')
    sales = db.relationship('StockSale', backref='item', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'description': self.description,
            'price': float(self.price) if self.price else 0,
            'stock_total': self.stock_total,
            'stock_available': self.stock_available,
            'options': self.options,
            'image': self.image
        }


class StockSale(db.Model):
    """Stock item sales"""
    __tablename__ = 'stock_sales'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    item_id = db.Column(db.Integer, db.ForeignKey('stock_items.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    options_selected = db.Column(db.JSON)  # {'size': 'M', 'color': 'blue'}
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    order = db.relationship('Order', backref='stock_sales')


# ============== BADGE DESIGNER ==============

class BadgeTemplate(db.Model):
    """Badge design templates"""
    __tablename__ = 'badge_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    
    name = db.Column(db.String(255), nullable=False)
    
    # Dimensions (in mm or inches)
    width = db.Column(db.Float, default=90)  # mm
    height = db.Column(db.Float, default=55)  # mm
    
    # Design (JSON or HTML)
    design = db.Column(db.JSON)  # {elements: [{type: 'text', content: '{first_name}', x: 10, y: 10}, ...]}
    
    # Colors
    background_color = db.Column(db.String(20), default='#FFFFFF')
    border_color = db.Column(db.String(20))
    border_width = db.Column(db.Integer, default=0)
    
    # Elements to show
    show_name = db.Column(db.Boolean, default=True)
    show_company = db.Column(db.Boolean, default=False)
    show_title = db.Column(db.Boolean, default=False)
    show_qr = db.Column(db.Boolean, default=True)
    
    is_default = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    event = db.relationship('Event', backref='badge_templates')
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'width': self.width,
            'height': self.height,
            'design': self.design,
            'background_color': self.background_color,
            'show_name': self.show_name,
            'show_qr': self.show_qr,
            'is_default': self.is_default
        }
