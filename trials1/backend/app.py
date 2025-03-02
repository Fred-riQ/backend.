from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

# Register route
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

        return jsonify({
            'success': True,
            'message': 'User registered successfully.',
            'user': {
                'id': new_user.id,
                'name': new_user.name,
                'email': new_user.email
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred during registration.'}), 500

if __name__ == '__main__':
    app.run(debug=True)