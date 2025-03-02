from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

# Hash a password
def hash_password(password):
    return generate_password_hash(password)

# Verify a password
def verify_password(hashed_password, password):
    return check_password_hash(hashed_password, password)

# Generate a JWT token
def generate_token(user_id):
    return create_access_token(identity=user_id)