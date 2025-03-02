# app/routes/__init__.py

# Import route blueprints
from .auth_routes import auth_routes
from .room_routes import room_routes
from .booking_routes import booking_routes

# Define __all__ to specify what gets imported when using `from app.routes import *`
__all__ = ['auth_routes', 'room_routes', 'booking_routes']

# Optional: Add a function to register all blueprints with the Flask app
def register_routes(app):
    """
    Register all route blueprints with the Flask app.
    """
    app.register_blueprint(auth_routes, url_prefix='/api/auth')
    app.register_blueprint(room_routes, url_prefix='/api/rooms')
    app.register_blueprint(booking_routes, url_prefix='/api/bookings')