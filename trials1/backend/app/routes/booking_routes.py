from flask import Blueprint, request, jsonify  # Import Blueprint here
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.models import Booking, db
from app.mpesa.mpesa import stk_push
from app.email import send_booking_confirmation  # Import the send_booking_confirmation function

# Create a Blueprint for booking routes
booking_routes = Blueprint('booking_routes', __name__)

@booking_routes.route('/', methods=['POST'])
@jwt_required()
def create_booking():
    """
    Create a new booking and initiate M-Pesa payment.
    """
    data = request.get_json()
    room_id = data.get('room_id')
    check_in_date = data.get('check_in_date')
    check_out_date = data.get('check_out_date')
    number_of_guests = data.get('number_of_guests')
    total_price = data.get('total_price')
    phone_number = data.get('phone_number')  # User's phone number for M-Pesa

    # Validate required fields
    if not all([room_id, check_in_date, check_out_date, number_of_guests, total_price, phone_number]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    # Validate date formats
    try:
        check_in = datetime.strptime(check_in_date, '%Y-%m-%d')
        check_out = datetime.strptime(check_out_date, '%Y-%m-%d')
        if check_out <= check_in:
            return jsonify({'success': False, 'message': 'Check-out date must be after check-in date.'}), 400
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    # Get the user ID from the JWT token
    user_id = get_jwt_identity()

    # Create new booking
    try:
        new_booking = Booking(
            user_id=user_id,
            room_id=room_id,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            number_of_guests=number_of_guests,
            total_price=total_price,
            payment_status='pending'
        )
        db.session.add(new_booking)
        db.session.commit()

        # Initiate M-Pesa payment
        mpesa_response = stk_push(phone_number, total_price, new_booking.id)
        if not mpesa_response.get("success"):
            return jsonify({"success": False, "message": "Failed to initiate M-Pesa payment."}), 500

        # Send booking confirmation email
        send_booking_confirmation(
            user_email=new_booking.user.email,
            username=new_booking.user.name,
            room_type=new_booking.room.type,
            check_in_date=check_in_date,
            check_out_date=check_out_date
        )

        return jsonify({
            'success': True,
            'message': 'Booking created successfully. Payment initiated.',
            'booking_id': new_booking.id,
            'mpesa_response': mpesa_response
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'}), 500