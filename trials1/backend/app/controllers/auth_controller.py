from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, JWTManager
from datetime import timedelta
from app.models import User, db

app = Flask(__name__)
CORS(app)  # Enable CORS
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Replace with a secure key
jwt = JWTManager(app)

@app.route('/api/register', methods=['POST', 'OPTIONS'])
def register_user():
    if request.method == 'OPTIONS':
        # Handle preflight request
        return jsonify({'success': True}), 200

    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    # Validate inputs
    if not name or not email or not password:
        return jsonify({'success': False, 'message': 'Name, email, and password are required.'}), 400

    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'success': False, 'message': 'User with this email already exists.'}), 400

    try:
        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        # Create new user
        new_user = User(name=name, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        # Generate JWT token with an expiration time
        access_token = create_access_token(identity=new_user.id, expires_delta=timedelta(days=7))

        return jsonify({
            'success': True,
            'message': 'User registered successfully.',
            'access_token': access_token,
            'user': {
                'id': new_user.id,
                'name': new_user.name,
                'email': new_user.email
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred during registration.'}), 500

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login_user():
    if request.method == 'OPTIONS':
        # Handle preflight request
        return jsonify({'success': True}), 200

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Validate inputs
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required.'}), 400

    # Check if user exists
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'success': False, 'message': 'User not found.'}), 404

    # Verify password
    if not check_password_hash(user.password_hash, password):
        return jsonify({'success': False, 'message': 'Invalid password.'}), 401

    try:
        # Generate JWT token with an expiration time
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(days=7))

        return jsonify({
            'success': True,
            'message': 'Login successful.',
            'access_token': access_token,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred during login.'}), 500

if __name__ == '__main__':
    app.run(debug=True)