from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from app.email import init_email  # Import the email initialization function

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')  # Load configuration from config.py

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    init_email(app)  # Initialize the email module

    # Register blueprints
    from app.routes.auth_routes import auth_routes
    from app.routes.booking_routes import booking_routes
    from app.routes.room_routes import room_routes

    app.register_blueprint(auth_routes, url_prefix='/api/auth')
    app.register_blueprint(booking_routes, url_prefix='/api/bookings')
    app.register_blueprint(room_routes, url_prefix='/api/rooms')

    # Create database tables
    with app.app_context():
        db.create_all()

    return app