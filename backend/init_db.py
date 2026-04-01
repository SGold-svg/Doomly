#!/usr/bin/env python3
"""
Database Initialization Script for Doomly
Run this to create all tables and seed data
"""

import os
import sys
from app import create_app, db
from app.models import User, Organization, Role, Permission
from app.advanced_models import (
    Session, CustomField, RegistrationGroup, WaitingList,
    RegistrationCode, Invoice, EmailCampaign, Hotel,
    EventFile, BadgeTemplate, Venue, BadgeTemplate
)

def init_database():
    """Initialize the database with tables and seed data"""
    
    app = create_app('development')
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Tables created successfully")
        
        # Create default roles
        create_default_roles()
        
        # Create default permissions
        create_default_permissions()
        
        print("\n✓ Database initialization complete!")

def create_default_roles():
    """Create default system roles"""
    
    roles = [
        {
            'name': 'Super Admin',
            'description': 'Full system access',
            'is_system': True
        },
        {
            'name': 'Organization Admin',
            'description': 'Full access to organization',
            'is_system': True
        },
        {
            'name': 'Event Manager',
            'description': 'Manage events and attendees',
            'is_system': True
        },
        {
            'name': 'Ticket Seller',
            'description': 'Sell tickets and manage check-in',
            'is_system': True
        },
        {
            'name': 'Viewer',
            'description': 'Read-only access',
            'is_system': True
        }
    ]
    
    for role_data in roles:
        existing = Role.query.filter_by(name=role_data['name']).first()
        if not existing:
            role = Role(**role_data)
            db.session.add(role)
    
    db.session.commit()
    print("✓ Default roles created")

def create_default_permissions():
    """Create default permissions"""
    
    permissions = [
        # Events
        {'name': 'Create Events', 'code': 'events.create', 'category': 'events'},
        {'name': 'View Events', 'code': 'events.view', 'category': 'events'},
        {'name': 'Edit Events', 'code': 'events.edit', 'category': 'events'},
        {'name': 'Delete Events', 'code': 'events.delete', 'category': 'events'},
        {'name': 'Publish Events', 'code': 'events.publish', 'category': 'events'},
        
        # Attendees
        {'name': 'View Attendees', 'code': 'attendees.view', 'category': 'attendees'},
        {'name': 'Edit Attendees', 'code': 'attendees.edit', 'category': 'attendees'},
        {'name': 'Check-in Attendees', 'code': 'attendees.checkin', 'category': 'attendees'},
        {'name': 'Export Attendees', 'code': 'attendees.export', 'category': 'attendees'},
        
        # Orders
        {'name': 'View Orders', 'code': 'orders.view', 'category': 'orders'},
        {'name': 'Refund Orders', 'code': 'orders.refund', 'category': 'orders'},
        
        # Finance
        {'name': 'View Revenue', 'code': 'finance.view', 'category': 'finance'},
        {'name': 'Manage Invoices', 'code': 'finance.invoices', 'category': 'finance'},
        
        # Settings
        {'name': 'Manage Settings', 'code': 'settings.manage', 'category': 'settings'},
        {'name': 'Manage Users', 'code': 'users.manage', 'category': 'users'},
    ]
    
    for perm_data in permissions:
        existing = Permission.query.filter_by(code=perm_data['code']).first()
        if not existing:
            permission = Permission(**perm_data)
            db.session.add(permission)
    
    db.session.commit()
    print("✓ Default permissions created")

if __name__ == '__main__':
    init_database()
