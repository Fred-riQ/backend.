from flask import Blueprint, request, jsonify
from app.models import Room, db

# Create a Blueprint for room routes
room_routes = Blueprint('room_routes', __name__)

@room_routes.route('/', methods=['GET'])
def get_all_rooms():
    rooms = Room.query.all()
    return jsonify([{
        'id': room.id,
        'type': room.type,
        'price': room.price,
        'description': room.description,
        'image': room.image
    } for room in rooms])

@room_routes.route('/', methods=['POST'])
def add_room():
    data = request.get_json()
    type = data.get('type')
    price = data.get('price')
    description = data.get('description')
    image = data.get('image')

    # Validate required fields
    if not type or not price or not description or not image:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    # Validate price is a positive number
    if not isinstance(price, (int, float)) or price <= 0:
        return jsonify({'success': False, 'message': 'Price must be a positive number.'}), 400

    # Create new room
    try:
        new_room = Room(
            type=type,
            price=price,
            description=description,
            image=image
        )
        db.session.add(new_room)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Room created successfully.',
            'room_id': new_room.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred while creating the room.'}), 500