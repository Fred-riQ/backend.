import requests
from base64 import b64encode
from datetime import datetime
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# M-Pesa API credentials
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
BUSINESS_SHORTCODE = os.getenv("BUSINESS_SHORTCODE")
PASSKEY = os.getenv("PASSKEY")
CALLBACK_URL = os.getenv("CALLBACK_URL")

# Validate environment variables
if not all([CONSUMER_KEY, CONSUMER_SECRET, BUSINESS_SHORTCODE, PASSKEY, CALLBACK_URL]):
    raise ValueError("Missing required M-Pesa API credentials in environment variables")

# Generate access token
def get_access_token():
    """
    Retrieve the access token from the M-Pesa API.
    """
    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    auth = b64encode(f"{CONSUMER_KEY}:{CONSUMER_SECRET}".encode()).decode("utf-8")
    headers = {"Authorization": f"Basic {auth}"}
    
    try:
        response = requests.get(auth_url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json().get("access_token")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to retrieve access token: {e}")
        raise Exception("Failed to retrieve access token")

# Initiate STK push
def initiate_stk_push(phone_number, amount):
    """
    Initiate an STK push payment request.
    
    :param phone_number: The customer's phone number in the format 2547XXXXXXXX.
    :param amount: The amount to be paid.
    :return: JSON response from the M-Pesa API.
    """
    access_token = get_access_token()
    stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = b64encode(f"{BUSINESS_SHORTCODE}{PASSKEY}{timestamp}".encode()).decode("utf-8")
    
    payload = {
        "BusinessShortCode": BUSINESS_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": BUSINESS_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": "Wellhall Hotel",
        "TransactionDesc": "Payment for booking"
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(stk_url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to initiate STK push: {e}")
        raise Exception("Failed to initiate STK push")

# Example usage
if __name__ == "__main__":
    try:
        phone_number ='254703647000'
        '' ## Replace with the user's phone number
        amount = 1  # Replace with the payment amount
        response = initiate_stk_push(phone_number, amount)
        print("STK Push Response:", response)
    except Exception as e:
        logger.error(f"Error in STK push example: {e}")