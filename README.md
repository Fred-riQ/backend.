# Wellhall Hotel Backend API (SQLite Version)

This is the backend API for the Wellhall Hotel website. It provides endpoints for user authentication, room management, booking, and payment processing using SQLite as the database.

## Setup Instructions

### Prerequisites
- Python 3.8 or higher

### Installation

1. Clone the repository
2. Navigate to the backend directory
3. Create a virtual environment:
   ```
   python -m venv venv
   ```
4. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
5. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
6. Create a `.env` file based on `.env.example` and update with your configuration
7. Set up the database:
   ```
   python db_setup.py
   ```
8. Start the server:
   ```
   python app.py
   ```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login a user

### Rooms
- `GET /api/rooms` - Get all rooms
- `GET /api/rooms/:id` - Get a specific room

### Special Offers
- `GET /api/special-offers` - Get all special offers

### About Us
- `GET /api/about` - Get about us content

### Bookings
- `POST /api/bookings` - Create a new booking (requires authentication)
- `GET /api/bookings/user/:userId` - Get bookings for a specific user (requires authentication)
- `PATCH /api/bookings/:id/cancel` - Cancel a booking (requires authentication)

### Payments
- `POST /api/payments/mpesa` - Process M-Pesa payment (requires authentication)

## Database Schema

The SQLite database consists of the following tables:
- `users` - Stores user information
- `rooms` - Stores room information
- `room_amenities` - Stores amenities for each room
- `special_offers` - Stores special offers
- `offer_details` - Stores details for each special offer
- `about_us` - Stores about us content
- `bookings` - Stores booking information

## Test User

A test user is created during database setup:
- Email: test@example.com
- Password: password123

## Advantages of SQLite

- No separate database server required
- Zero configuration
- Cross-platform
- Self-contained database file
- Excellent for development and smaller applications