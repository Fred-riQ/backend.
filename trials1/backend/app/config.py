import os

# Database Configuration
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///app.db')  # Default to SQLite
SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable modification tracking

# M-Pesa Configuration
MPESA_CONSUMER_KEY = os.getenv('MPESA_CONSUMER_KEY', 'WMCSmuK7QTDVJmcE5afjdcpuGrnOqgC0MgjA9QGwUBcjciKF')  # Your M-Pesa consumer key
MPESA_CONSUMER_SECRET = os.getenv('MPESA_CONSUMER_SECRET', 'OQdsS2rbTIK1ExAEoLXVc4MosHaeRft6O6IfLp0DWqfGqpOhp6D9JY891hW78EWq')  # Your M-Pesa consumer secret
MPESA_AUTH_URL = os.getenv('MPESA_AUTH_URL', 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials')  # M-Pesa OAuth URL
MPESA_STK_URL = os.getenv('MPESA_STK_URL', 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest')  # M-Pesa STK Push URL
MPESA_BUSINESS_SHORT_CODE = os.getenv('MPESA_BUSINESS_SHORT_CODE', '174379')  # Your M-Pesa business short code
MPESA_PASSKEY = os.getenv('MPESA_PASSKEY', 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919')  # Your M-Pesa passkey
MPESA_CALLBACK_URL = os.getenv('MPESA_CALLBACK_URL', 'https://cc05-102-0-15-200.ngrok-free.app/daraja/callback')  # Your callback URL for M-Pesa notifications

# Email Configuration
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')  # SMTP server for Gmail
MAIL_PORT = int(os.getenv('MAIL_PORT', 587))  # Port for TLS
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'  # Use TLS for secure communication
MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'belascohotel@gmail.com')  # Your Gmail address
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'pciu hmmg jtkm rasu')  # Your Gmail app password
MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'belascohotel@gmail.com')  # Default sender email address