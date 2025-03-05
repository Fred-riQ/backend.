import sqlite3
import bcrypt
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database():
    # Get database path from environment variable or use default
    db_path = os.getenv("DB_PATH", "wellhall_hotel.db")
    
    # Connect to SQLite database (will create it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        price REAL NOT NULL,
        description TEXT NOT NULL,
        image TEXT NOT NULL,
        max_guests INTEGER NOT NULL,
        bed_config TEXT NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS room_amenities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_id INTEGER NOT NULL,
        amenity TEXT NOT NULL,
        FOREIGN KEY (room_id) REFERENCES rooms (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS special_offers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        image TEXT NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS offer_details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        offer_id INTEGER NOT NULL,
        title TEXT,
        description TEXT NOT NULL,
        FOREIGN KEY (offer_id) REFERENCES special_offers (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS about_us (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        text TEXT NOT NULL,
        image TEXT NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id TEXT PRIMARY KEY,
        room_id INTEGER NOT NULL,
        user_id TEXT NOT NULL,
        check_in TEXT NOT NULL,
        check_out TEXT NOT NULL,
        guests INTEGER NOT NULL,
        status TEXT NOT NULL,
        payment_details TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (room_id) REFERENCES rooms (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Insert sample data
    try:
        # Sample rooms
        rooms = [
            {
                "type": "Deluxe Room",
                "price": 9500,
                "description": "Spacious room with a king-size bed and city view",
                "image": "https://images.unsplash.com/photo-1611892440504-42a792e24d32?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1470&q=80",
                "max_guests": 2,
                "bed_config": "1 King Bed",
                "amenities": ["Free Wi-Fi", "Air Conditioning", "Flat-screen TV", "Mini Bar", "Coffee Maker", "Safe"]
            },
            {
                "type": "Executive Suite",
                "price": 7500,
                "description": "Luxurious suite with separate living area and panoramic views",
                "image": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1470&q=80",
                "max_guests": 3,
                "bed_config": "1 King Bed + Sofa Bed",
                "amenities": ["Free Wi-Fi", "Air Conditioning", "Flat-screen TV", "Mini Bar", "Coffee Maker", "Safe", "Bathtub", "Separate Living Area", "Work Desk"]
            },
            {
                "type": "Family Room",
                "price": 8000,
                "description": "Comfortable room for families with two queen beds",
                "image": "https://images.unsplash.com/photo-1566665797739-1674de7a421a?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1074&q=80",
                "max_guests": 4,
                "bed_config": "2 Queen Beds",
                "amenities": ["Free Wi-Fi", "Air Conditioning", "Flat-screen TV", "Mini Bar", "Coffee Maker", "Safe", "Extra Space"]
            },
            {
                "type": "Presidential Suite",
                "price": 15000,
                "description": "Our most luxurious accommodation with premium amenities and services",
                "image": "https://images.unsplash.com/photo-1591088398332-8a7791972843?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1074&q=80",
                "max_guests": 4,
                "bed_config": "1 King Bed + 2 Queen Beds",
                "amenities": ["Free Wi-Fi", "Air Conditioning", "Flat-screen TV", "Mini Bar", "Coffee Maker", "Safe", "Bathtub", "Separate Living Area", "Work Desk", "Private Balcony", "Butler Service", "Complimentary Breakfast"]
            },
            {
                "type": "Standard Room",
                "price": 4000,
                "description": "Cozy room with all essential amenities for a comfortable stay",
                "image": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1470&q=80",
                "max_guests": 2,
                "bed_config": "1 Queen Bed",
                "amenities": ["Free Wi-Fi", "Air Conditioning", "Flat-screen TV", "Coffee Maker"]
            }
        ]
        
        for room in rooms:
            cursor.execute(
                "SELECT * FROM rooms WHERE type = ?",
                (room["type"],)
            )
            existing_room = cursor.fetchone()
            
            if not existing_room:
                cursor.execute(
                    "INSERT INTO rooms (type, price, description, image, max_guests, bed_config) VALUES (?, ?, ?, ?, ?, ?)",
                    (room["type"], room["price"], room["description"], room["image"], room["max_guests"], room["bed_config"])
                )
                room_id = cursor.lastrowid
                
                # Insert amenities for the room
                for amenity in room["amenities"]:
                    cursor.execute(
                        "INSERT INTO room_amenities (room_id, amenity) VALUES (?, ?)",
                        (room_id, amenity)
                    )
                print(f"Room '{room['type']}' inserted")
        
        # Sample special offers
        offers = [
            {
                "title": "Weekend Getaway Package",
                "image": "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1470&q=80",
                "details": [
                    {
                        "title": "Two Nights Stay",
                        "description": "Enjoy a relaxing weekend in one of our Deluxe Rooms"
                    },
                    {
                        "title": "Complimentary Breakfast",
                        "description": "Start your day with our gourmet breakfast buffet"
                    },
                    {
                        "title": "Spa Credit",
                        "description": "Receive $50 credit to use at our luxury spa"
                    }
                ]
            },
            {
                "title": "Honeymoon Special",
                "image": "https://images.unsplash.com/photo-1520854221256-17451cc331bf?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1470&q=80",
                "details": [
                    {
                        "title": "Executive Suite",
                        "description": "Three nights in our romantic Executive Suite"
                    },
                    {
                        "title": "Champagne & Chocolates",
                        "description": "Welcome package with premium champagne and artisan chocolates"
                    },
                    {
                        "title": "Couples Massage",
                        "description": "Complimentary 60-minute couples massage"
                    },
                    {
                        "title": "Private Dinner",
                        "description": "Candlelit dinner for two on your private balcony"
                    }
                ]
            },
            {
                "title": "Business Travel Package",
                "image": "https://images.unsplash.com/photo-1497366754035-f200968a6e72?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1469&q=80",
                "details": [
                    {
                        "title": "Deluxe Room",
                        "description": "Comfortable accommodation with work desk"
                    },
                    {
                        "title": "Airport Transfer",
                        "description": "Complimentary airport pickup and drop-off"
                    },
                    {
                        "title": "Business Center Access",
                        "description": "24/7 access to our fully equipped business center"
                    },
                    {
                        "title": "Laundry Service",
                        "description": "Express laundry service for your business attire"
                    }
                ]
            }
        ]
        
        for offer in offers:
            cursor.execute(
                "SELECT * FROM special_offers WHERE title = ?",
                (offer["title"],)
            )
            existing_offer = cursor.fetchone()
            
            if not existing_offer:
                cursor.execute(
                    "INSERT INTO special_offers (title, image) VALUES (?, ?)",
                    (offer["title"], offer["image"])
                )
                offer_id = cursor.lastrowid
                
                # Insert details for the offer
                for detail in offer["details"]:
                    cursor.execute(
                        "INSERT INTO offer_details (offer_id, title, description) VALUES (?, ?, ?)",
                        (offer_id, detail["title"], detail["description"])
                    )
                print(f"Offer '{offer['title']}' inserted")
        
        # About us content
        about_us = {
            "title": "About The Wellhall Hotel",
            "text": "The Wellhall Hotel is a luxury establishment located in the heart of Eldoret, Kenya. Founded in 2010, our hotel has been providing exceptional service and comfort to our guests for over a decade. Our mission is to create memorable experiences through personalized service and attention to detail. We pride ourselves on our commitment to sustainability and community engagement. Our team of dedicated professionals is always ready to go above and beyond to ensure your stay is nothing short of perfect. Whether you're traveling for business or pleasure, The Wellhall Hotel offers the perfect blend of luxury, comfort, and convenience.",
            "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1470&q=80"
        }
        
        cursor.execute("SELECT * FROM about_us LIMIT 1")
        existing_about = cursor.fetchone()
        
        if not existing_about:
            cursor.execute(
                "INSERT INTO about_us (title, text, image) VALUES (?, ?, ?)",
                (about_us["title"], about_us["text"], about_us["image"])
            )
            print("About us content inserted")
        
        # Create a test user
        cursor.execute("SELECT * FROM users WHERE email = 'test@example.com'")
        existing_user = cursor.fetchone()
        
        if not existing_user:
            hashed_password = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt())
            cursor.execute(
                "INSERT INTO users (id, name, email, password, created_at) VALUES (?, ?, ?, ?, ?)",
                ('1', 'Test User', 'test@example.com', hashed_password, datetime.now().isoformat())
            )
            print("Test user created")
        
        conn.commit()
        print("Sample data inserted successfully")
        
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()
        print("SQLite connection closed")

if __name__ == "__main__":
    create_database()