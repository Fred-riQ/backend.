from flask_mail import Message
from flask import current_app
from .extensions import mail  # Import the mail object from the extensions module

def send_booking_confirmation(user_email, username, room_type, check_in_date, check_out_date):
    """
    Send a booking confirmation email to the user.
    """
    try:
        # Create email message
        subject = "Your Booking Confirmation"
        body = f"""
        Dear {username},

        Thank you for booking with us!

        Here are your booking details:
        - Room Type: {room_type}
        - Check-in Date: {check_in_date}
        - Check-out Date: {check_out_date}

        We look forward to hosting you!

        Best regards,
        The Wellhall Hotel Team
        """

        msg = Message(
            subject=subject,
            recipients=[user_email],
            body=body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )

        # Send email
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False