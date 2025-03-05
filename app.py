from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_mail import Mail, Message
import sqlite3
import bcrypt
import uuid
import os
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configure JWT
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "your-secret-key")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
jwt = JWTManager(app)

# Configure Mail
app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
app.config['MAIL_PORT'] = int(os.getenv("MAIL_PORT", 587))
app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS", "True") == "True"
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME", "your-email@gmail.com")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD", "your-password")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_DEFAULT_SENDER", "your-email@gmail.com")
mail = Mail(app)

# Database connection function
def get_db_connection():
    conn = sqlite3.connect(os.getenv("DB_PATH", "wellhall_hotel.db"))
    conn.row_factory = sqlite3.Row
    return conn

# Helper function to convert SQLite result to JSON serializable format
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        value = row[idx]
        if isinstance(value, datetime):
            d[col[0]] = value.isoformat()
        else:
            d[col[0]] = value
    return d

# Authentication routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not name or not email or not password:
        return jsonify({"message": "All fields are required"}), 400
    
    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        conn.close()
        return jsonify({"message": "User already exists"}), 400
    
    # Create new user
    user_id = str(uuid.uuid4())
    try:
        cursor.execute(
            "INSERT INTO users (id, name, email, password, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, name, email, hashed_password, datetime.now().isoformat())
        )
        conn.commit()
        
        # Create access token
        access_token = create_access_token(identity=user_id)
        
        conn.close()
        
        return jsonify({
            "message": "User registered successfully",
            "user": {"id": user_id, "name": name, "email": email},
            "token": access_token
        }), 201
    except sqlite3.Error as e:
        conn.close()
        return jsonify({"message": f"Registration failed: {str(e)}"}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400
    
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    # Find user by email
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        conn.close()
        return jsonify({"message": "Invalid email or password"}), 401
    
    # Create access token
    access_token = create_access_token(identity=user['id'])
    
    conn.close()
    
    return jsonify({
        "message": "Login successful",
        "user": {"id": user['id'], "name": user['name'], "email": user['email']},
        "token": access_token
    }), 200

# Room routes
@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM rooms")
        rooms = cursor.fetchall()
        
        # Get amenities for each room
        for room in rooms:
            cursor.execute(
                "SELECT amenity FROM room_amenities WHERE room_id = ?",
                (room['id'],)
            )
            amenities = cursor.fetchall()
            room['amenities'] = [item['amenity'] for item in amenities]
        
        conn.close()
        
        return jsonify(rooms), 200
    except sqlite3.Error as e:
        conn.close()
        return jsonify({"message": f"Failed to fetch rooms: {str(e)}"}), 500

@app.route('/api/rooms/<int:room_id>', methods=['GET'])
def get_room(room_id):
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM rooms WHERE id = ?", (room_id,))
        room = cursor.fetchone()
        
        if not room:
            conn.close()
            return jsonify({"message": "Room not found"}), 404
        
        # Get amenities
        cursor.execute(
            "SELECT amenity FROM room_amenities WHERE room_id = ?",
            (room_id,)
        )
        amenities = cursor.fetchall()
        room['amenities'] = [item['amenity'] for item in amenities]
        
        conn.close()
        
        return jsonify(room), 200
    except sqlite3.Error as e:
        conn.close()
        return jsonify({"message": f"Failed to fetch room: {str(e)}"}), 500

# Special offers routes
@app.route('/api/special-offers', methods=['GET'])
def get_special_offers():
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM special_offers")
        offers = cursor.fetchall()
        
        # Get details for each offer
        for offer in offers:
            cursor.execute(
                "SELECT * FROM offer_details WHERE offer_id = ?",
                (offer['id'],)
            )
            details = cursor.fetchall()
            offer['details'] = details
        
        conn.close()
        
        return jsonify(offers), 200
    except sqlite3.Error as e:
        conn.close()
        return jsonify({"message": f"Failed to fetch special offers: {str(e)}"}), 500

# About us route
@app.route('/api/about', methods=['GET'])
def get_about():
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM about_us LIMIT 1")
        about = cursor.fetchone()
        
        conn.close()
        
        return jsonify(about), 200
    except sqlite3.Error as e:
        conn.close()
        return jsonify({"message": f"Failed to fetch about us content: {str(e)}"}), 500

# Booking routes
@app.route('/api/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    room_id = data.get('roomId')
    check_in = data.get('checkIn')
    check_out = data.get('checkOut')
    guests = data.get('guests', 1)
    payment_details = data.get('paymentDetails')
    
    if not room_id or not check_in or not check_out or not payment_details:
        return jsonify({"message": "Missing required booking information"}), 400
    
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    try:
        # Get room details
        cursor.execute("SELECT * FROM rooms WHERE id = ?", (room_id,))
        room = cursor.fetchone()
        
        if not room:
            conn.close()
            return jsonify({"message": "Room not found"}), 404
        
        # Get user details
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return jsonify({"message": "User not found"}), 404
        
        # Create booking
        booking_id = str(uuid.uuid4())
        payment_details_json = json.dumps(payment_details)
        
        cursor.execute(
            """
            INSERT INTO bookings 
            (id, room_id, user_id, check_in, check_out, guests, status, payment_details, created_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                booking_id, 
                room_id, 
                user_id, 
                check_in, 
                check_out, 
                guests, 
                'confirmed', 
                payment_details_json, 
                datetime.now().isoformat()
            )
        )
        conn.commit()
        
        # Get the created booking
        cursor.execute(
            """
            SELECT b.*, r.type as room_type, r.price as room_price, r.image as room_image, 
                   r.description as room_description, r.max_guests, r.bed_config,
                   u.name as user_name, u.email as user_email
            FROM bookings b
            JOIN rooms r ON b.room_id = r.id
            JOIN users u ON b.user_id = u.id
            WHERE b.id = ?
            """,
            (booking_id,)
        )
        booking = cursor.fetchone()
        
        # Format the booking response
        booking_response = {
            "id": booking['id'],
            "room": {
                "id": booking['room_id'],
                "type": booking['room_type'],
                "price": booking['room_price'],
                "image": booking['room_image'],
                "description": booking['room_description'],
                "maxGuests": booking['max_guests'],
                "bedConfig": booking['bed_config']
            },
            "user": {
                "id": booking['user_id'],
                "name": booking['user_name'],
                "email": booking['user_email']
            },
            "checkIn": booking['check_in'],
            "checkOut": booking['check_out'],
            "guests": booking['guests'],
            "status": booking['status'],
            "paymentDetails": json.loads(booking['payment_details']),
            "createdAt": booking['created_at']
        }
        
        # Send confirmation email
        try:
            msg = Message(
                subject="Booking Confirmation - The Wellhall Hotel",
                recipients=[user['email']],
                html=f"""
                <h1>Booking Confirmation</h1>
                <p>Dear {user['name']},</p>
                <p>Thank you for choosing The Wellhall Hotel. Your booking has been confirmed.</p>
                <h2>Booking Details</h2>
                <p><strong>Room:</strong> {room['type']}</p>
                <p><strong>Check-in:</strong> {booking['check_in']}</p>
                <p><strong>Check-out:</strong> {booking['check_out']}</p>
                <p><strong>Guests:</strong> {guests}</p>
                <p><strong>Total Amount:</strong> ${payment_details.get('amount')}</p>
                <p>We look forward to welcoming you to The Wellhall Hotel.</p>
                <p>Best regards,<br>The Wellhall Hotel Team</p>
                """
            )
            mail.send(msg)
        except Exception as e:
            print(f"Error sending email: {e}")
        
        conn.close()
        
        return jsonify({
            "message": "Booking created successfully",
            "booking": booking_response
        }), 201
    except sqlite3.Error as e:
        conn.close()
        return jsonify({"message": f"Booking failed: {str(e)}"}), 500

@app.route('/api/bookings/user/<user_id>', methods=['GET'])
@jwt_required()
def get_user_bookings(user_id):
    # Ensure the user is requesting their own bookings
    current_user_id = get_jwt_identity()
    if current_user_id != user_id:
        return jsonify({"message": "Unauthorized"}), 403
    
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            SELECT b.*, r.type as room_type, r.price as room_price, r.image as room_image, 
                   r.description as room_description, r.max_guests, r.bed_config,
                   u.name as user_name, u.email as user_email
            FROM bookings b
            JOIN rooms r ON b.room_id = r.id
            JOIN users u ON b.user_id = u.id
            WHERE b.user_id = ?
            ORDER BY b.created_at DESC
            """,
            (user_id,)
        )
        bookings = cursor.fetchall()
        
        # Format the bookings response
        bookings_response = []
        for booking in bookings:
            bookings_response.append({
                "id": booking['id'],
                "room": {
                    "id": booking['room_id'],
                    "type": booking['room_type'],
                    "price": booking['room_price'],
                    "image": booking['room_image'],
                    "description": booking['room_description'],
                    "maxGuests": booking['max_guests'],
                    "bedConfig": booking['bed_config']
                },
                "user": {
                    "id": booking['user_id'],
                    "name": booking['user_name'],
                    "email": booking['user_email']
                },
                "checkIn": booking['check_in'],
                "checkOut": booking['check_out'],
                "guests": booking['guests'],
                "status": booking['status'],
                "paymentDetails": json.loads(booking['payment_details']),
                "createdAt": booking['created_at']
            })
        
        conn.close()
        
        return jsonify(bookings_response), 200
    except sqlite3.Error as e:
        conn.close()
        return jsonify({"message": f"Failed to fetch bookings: {str(e)}"}), 500

@app.route('/api/bookings/<booking_id>/cancel', methods=['PATCH'])
@jwt_required()
def cancel_booking(booking_id):
    user_id = get_jwt_identity()
    
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    try:
        # Check if booking exists and belongs to the user
        cursor.execute(
            "SELECT * FROM bookings WHERE id = ?", 
            (booking_id,)
        )
        booking = cursor.fetchone()
        
        if not booking:
            conn.close()
            return jsonify({"message": "Booking not found"}), 404
        
        if booking['user_id'] != user_id:
            conn.close()
            return jsonify({"message": "Unauthorized"}), 403
        
        # Update booking status
        cursor.execute(
            "UPDATE bookings SET status = 'cancelled' WHERE id = ?",
            (booking_id,)
        )
        conn.commit()
        
        # Get user details for email
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        # Get room details for email
        cursor.execute("SELECT * FROM rooms WHERE id = ?", (booking['room_id'],))
        room = cursor.fetchone()
        
        # Send cancellation email
        try:
            msg = Message(
                subject="Booking Cancellation - The Wellhall Hotel",
                recipients=[user['email']],
                html=f"""
                <h1>Booking Cancellation</h1>
                <p>Dear {user['name']},</p>
                <p>Your booking at The Wellhall Hotel has been cancelled as requested.</p>
                <h2>Booking Details</h2>
                <p><strong>Room:</strong> {room['type']}</p>
                <p><strong>Check-in:</strong> {booking['check_in']}</p>
                <p><strong>Check-out:</strong> {booking['check_out']}</p>
                <p>If you have any questions, please contact our customer service.</p>
                <p>Best regards,<br>The Wellhall Hotel Team</p>
                """
            )
            mail.send(msg)
        except Exception as e:
            print(f"Error sending email: {e}")
        
        conn.close()
        
        return jsonify({"message": "Booking cancelled successfully"}), 200
    except sqlite3.Error as e:
        conn.close()
        return jsonify({"message": f"Cancellation failed: {str(e)}"}), 500

# Payment routes
@app.route('/api/payments/mpesa', methods=['POST'])
@jwt_required()
def process_mpesa_payment():
    data = request.get_json()
    phone_number = data.get('phoneNumber')
    amount = data.get('amount')
    
    if not phone_number or not amount:
        return jsonify({"message": "Phone number and amount are required"}), 400
    
    # In a real app, you would integrate with the M-Pesa API here
    # For this example, we'll simulate a successful payment
    
    transaction_id = f"MPESA{uuid.uuid4().hex[:8].upper()}"
    
    return jsonify({
        "success": True,
        "message": "Payment processed successfully",
        "transactionId": transaction_id,
        "amount": amount,
        "phoneNumber": phone_number,
        "timestamp": datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)