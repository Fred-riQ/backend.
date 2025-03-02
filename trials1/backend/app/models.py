from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """
    User model representing a hotel guest.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    bookings = db.relationship('Booking', backref='user', lazy=True)  # One-to-many relationship with Booking

    def set_password(self, password):
        """
        Hash the password before storing it in the database.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Verify the password against the hashed password.
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.name}>'

class Room(db.Model):
    """
    Room model representing a hotel room.
    """
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)  # Room type (e.g., Deluxe, Superior)
    price = db.Column(db.Float, nullable=False)  # Price per night
    description = db.Column(db.String(500), nullable=False)  # Room description
    image = db.Column(db.String(200), nullable=False)  # URL to room image
    bookings = db.relationship('Booking', backref='room', lazy=True)  # One-to-many relationship with Booking

    def __repr__(self):
        return f'<Room {self.type}>'

class Booking(db.Model):
    """
    Booking model representing a reservation made by a user.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to User
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)  # Foreign key to Room
    check_in_date = db.Column(db.String(20), nullable=False)  # Check-in date (stored as string)
    check_out_date = db.Column(db.String(20), nullable=False)  # Check-out date (stored as string)
    number_of_guests = db.Column(db.Integer, nullable=False)  # Number of guests
    total_price = db.Column(db.Float, nullable=False)  # Total price for the booking
    payment_status = db.Column(db.String(20), default='pending')  # Payment status (e.g., pending, completed)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp of booking creation

    def __repr__(self):
        return f'<Booking {self.id} - User {self.user_id} - Room {self.room_id}>'