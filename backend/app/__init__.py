"""
Doomly Event Management Platform
Main Application Entry Point
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from config import config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()
mail = Mail()


def create_app(config_name='default'):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    from .api.routes.auth import auth_bp
    from .api.routes.events import events_bp
    from .api.routes.tickets import tickets_bp
    from .api.routes.attendees import attendees_bp
    from .api.routes.orders import orders_bp
    from .api.routes.users import users_bp
    from .api.routes.organizations import orgs_bp
    from .api.routes.emails import emails_bp
    from .api.routes.checkin import checkin_bp
    from .api.routes.dashboard import dashboard_bp
    from .api.routes.settings import settings_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(events_bp, url_prefix='/api/events')
    app.register_blueprint(tickets_bp, url_prefix='/api/tickets')
    app.register_blueprint(attendees_bp, url_prefix='/api/attendees')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(orgs_bp, url_prefix='/api/organizations')
    app.register_blueprint(emails_bp, url_prefix='/api/emails')
    app.register_blueprint(checkin_bp, url_prefix='/api/checkin')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(settings_bp, url_prefix='/api/settings')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'app': 'Doomly Event Management'}
    
    return app
