#!/usr/bin/env python3
"""
Doomly Event Management Platform
Production Entry Point (for Gunicorn)
"""

import os
import sys

# Ensure proper path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

# Create app instance
app = create_app(os.environ.get('FLASK_ENV', 'production'))
