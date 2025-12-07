"""
Test email configuration
Run this to verify your SMTP settings work before using in production
"""

import os
from dotenv import load_dotenv
from services.email_service import send_email, create_verification_email

load_dotenv()

def test_email_config():
    """Test email sending with current configuration"""
    
    print("="*60)
    print("Email Configuration Test")
    print("="*60)
    
    # Show configuration (hide password)
    smtp_server = os.getenv('SMTP_SERVER', 'Not set')
    smtp_port = os.getenv('SMTP_PORT', 'Not set')
    smtp_username = os.getenv('SMTP_USERNAME', 'Not set')
    smtp_password = os.getenv('SMTP_PASSWORD', 'Not set')
    sender_email = os.getenv('SENDER_EMAIL', 'Not set')
    sender_name = os.getenv('SENDER_NAME', 'Not set')
    base_url = os.getenv('BASE_URL', 'Not set')
    
    print(f"\nCurrent Configuration:")
    print(f"  SMTP Server: {smtp_server}")
    print(f"  SMTP Port: {smtp_port}")
    print(f"  Username: {smtp_username}")
    print(f"  Password: {'*' * len(smtp_password) if smtp_password != 'Not set' else 'Not set'}")
    print(f"  Sender Email: {sender_email}")
    print(f"  Sender Name: {sender_name}")
    print(f"  Base URL: {base_url}")
    
    # Check if configured
    if smtp_username == 'Not set' or smtp_password == 'Not set':
        print("\n❌ Error: Email not configured!")
        print("Please set SMTP_USERNAME and SMTP_PASSWORD in .env file")
        return False
    
    # Ask for test email
    print("\n" + "="*60)
    test_email = input("Enter email address to send test to: ").strip()
    
    if not test_email or '@' not in test_email:
        print("❌ Invalid email address")
        return False
    
    print(f"\n📧 Sending test verification email to {test_email}...")
    
    # Create test verification email
    test_token = "test_token_12345"
    message = create_verification_email(test_email, "Test User", test_token)
    
    # Send email
    success, result_message = send_email(test_email, message)
    
    print("\n" + "="*60)
    if success:
        print("✅ SUCCESS! Email sent successfully!")
        print(f"\nCheck {test_email} for the test email.")
        print("Look in inbox and spam folder.")
        print("\nIf received, your email configuration is working! 🎉")
    else:
        print("❌ FAILED to send email")
        print(f"\nError: {result_message}")
        print("\nTroubleshooting:")
        print("1. Verify SMTP_USERNAME and SMTP_PASSWORD are correct")
        print("2. For Microsoft 365: Check smtp.office365.com port 587")
        print("3. Ensure SMTP authentication is enabled in your email settings")
        print("4. Check if 2FA is enabled - you may need an app password")
    print("="*60)
    
    return success

if __name__ == "__main__":
    test_email_config()
