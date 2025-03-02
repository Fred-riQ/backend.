import requests
import base64
from datetime import datetime
from flask import current_app

def generate_access_token():
    """
    Generate an access token for M-Pesa API authentication.
    """
    consumer_key = current_app.config['MPESA_CONSUMER_KEY']
    consumer_secret = current_app.config['MPESA_CONSUMER_SECRET']
    auth_url = current_app.config['MPESA_AUTH_URL']

    # Encode consumer key and secret
    credentials = f"{consumer_key}:{consumer_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    # Request access token
    headers = {
        'Authorization': f'Basic {encoded_credentials}'
    }
    response = requests.get(auth_url, headers=headers)
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        raise Exception("Failed to generate access token")

def stk_push(phone_number, amount, booking_id):
    """
    Initiate an STK Push payment request.
    """
    access_token = generate_access_token()
    stk_url = current_app.config['MPESA_STK_URL']
    business_short_code = current_app.config['MPESA_BUSINESS_SHORT_CODE']
    passkey = current_app.config['MPESA_PASSKEY']
    callback_url = current_app.config['MPESA_CALLBACK_URL']

    # Generate timestamp
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    # Generate password
    password = base64.b64encode(f"{business_short_code}{passkey}{timestamp}".encode()).decode()

    # Prepare payload
    payload = {
        "BusinessShortCode": business_short_code,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": business_short_code,
        "PhoneNumber": phone_number,
        "CallBackURL": callback_url,
        "AccountReference": f"Booking_{booking_id}",
        "TransactionDesc": "Hotel Booking Payment"
    }

    # Send STK Push request
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(stk_url, json=payload, headers=headers)

    if response.status_code == 200:
        return {
            "success": True,
            "response": response.json(),
            "message": "STK Push initiated successfully."
        }
    else:
        return {
            "success": False,
            "message": "Failed to initiate STK Push.",
            "error": response.json()
        }