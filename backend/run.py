#!/usr/bin/env python3
"""
Doomly Event Management Platform
Run Script
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

# Create app instance
app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║     ██████╗ ███████╗██████╗ ██╗     ██╗ ██████╗████████╗║
    ║     ██╔══██╗██╔════╝██╔══██╗██║     ██║██╔════╝╚══██╔══╝║
    ║     ██║  ██║█████╗  ██████╔╝██║     ██║██║        ██║   ║
    ║     ██║  ██║██╔══╝══██╗██  ██╔║     ██║██║        ██║   ║
    ║     ██████╔╝███████╗██████╔╝███████╗██║╚██████╗   ██║   ║
    ║     ╚═════╝ ╚══════╝╚═════╝ ╚══════╝╚═╝ ╚═════╝   ╚═╝   ║
    ║                                                           ║
    ║     Event Management Platform                            ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    print(f"🚀 Starting Doomly API Server")
    print(f"📍 Running on http://localhost:{port}")
    print(f"📚 API Documentation: http://localhost:{port}/api/health")
    print("")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
