"""
Test Gmail credentials
"""
import imaplib
import os
from dotenv import load_dotenv

load_dotenv()

email = os.getenv('EMAIL_ADDRESS')
password = os.getenv('EMAIL_PASSWORD')

print(f"Testing Gmail credentials...")
print(f"Email: {email}")
print(f"Password: {'*' * len(password)}")
print()

try:
    print("Connecting to Gmail IMAP server...")
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    
    print("Attempting login...")
    mail.login(email, password)
    
    print("✅ SUCCESS! Gmail credentials are correct!")
    print()
    print("Your Gmail is properly configured.")
    
    # Get mailbox info
    status, messages = mail.select("INBOX")
    if status == "OK":
        print(f"📬 You have {messages[0].decode()} emails in your inbox")
    
    mail.logout()
    
except imaplib.IMAP4.error as e:
    error_msg = str(e)
    print(f"❌ FAILED! Gmail login error: {error_msg}")
    print()
    
    if "AUTHENTICATIONFAILED" in error_msg or "Invalid credentials" in error_msg:
        print("🔐 This means your password is INCORRECT or you need an App Password")
        print()
        print("Gmail requires an 'App Password' for third-party apps:")
        print()
        print("How to get an App Password:")
        print("1. Go to: https://myaccount.google.com/apppasswords")
        print("2. Sign in to your Google account")
        print("3. Select 'Mail' and 'Windows Computer'")
        print("4. Click 'Generate'")
        print("5. Copy the 16-character password (looks like: xxxx xxxx xxxx xxxx)")
        print("6. Update .env file with:")
        print(f"   EMAIL_PASSWORD=your_app_password_here")
        print()
        print("Note: 'KingLuffy#@1' is NOT a valid Gmail App Password format")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
