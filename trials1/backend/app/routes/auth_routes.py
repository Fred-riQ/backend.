from flask import Blueprint
from ..controllers.auth_controller import register_user, login_user

# Create a Blueprint for auth routes
auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route('/register', methods=['POST'])
def register():
    return register_user()

@auth_routes.route('/login', methods=['POST'])
def login():
    return login_user()