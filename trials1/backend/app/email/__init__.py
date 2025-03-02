from .extensions import mail
from .email import send_booking_confirmation  # Import the send_booking_confirmation function

def init_email(app):
    """
    Initialize the email module with the Flask app.
    """
    mail.init_app(app)