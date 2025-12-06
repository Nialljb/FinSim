"""
Email service for FinSTK
Handles email verification and notifications
"""

import smtplib
import secrets
import hashlib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional, Tuple
import os
from dotenv import load_dotenv

load_dotenv()

# Email configuration from environment variables
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
SENDER_EMAIL = os.getenv('SENDER_EMAIL', SMTP_USERNAME)
SENDER_NAME = os.getenv('SENDER_NAME', 'FinSTK')

# Base URL for verification links
BASE_URL = os.getenv('BASE_URL', 'http://localhost:8501')


def generate_verification_token(email: str) -> str:
    """Generate a secure verification token for email"""
    # Create token with email, random bytes, and timestamp
    random_part = secrets.token_urlsafe(32)
    timestamp = datetime.now().isoformat()
    token_data = f"{email}:{random_part}:{timestamp}"
    
    # Hash for security
    token = hashlib.sha256(token_data.encode()).hexdigest()
    return token


def create_verification_email(email: str, username: str, verification_token: str) -> MIMEMultipart:
    """Create verification email message"""
    verification_link = f"{BASE_URL}/?verify={verification_token}"
    
    message = MIMEMultipart("alternative")
    message["Subject"] = "Verify Your FinSTK Account"
    message["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    message["To"] = email
    
    # Plain text version
    text_content = f"""
    Hi {username},
    
    Thank you for registering with FinSTK!
    
    Please verify your email address by clicking the link below:
    {verification_link}
    
    This link will expire in 24 hours.
    
    If you didn't create this account, please ignore this email.
    
    Best regards,
    The FinSTK Team
    """
    
    # HTML version
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            .content {{
                background: #f9f9f9;
                padding: 30px;
                border-radius: 0 0 10px 10px;
            }}
            .button {{
                display: inline-block;
                padding: 15px 30px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
                font-weight: bold;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎯 Welcome to FinSTK!</h1>
        </div>
        <div class="content">
            <p>Hi <strong>{username}</strong>,</p>
            
            <p>Thank you for registering with FinSTK - your Financial Simulation Toolkit!</p>
            
            <p>Please verify your email address to activate your account and start planning your financial future:</p>
            
            <center>
                <a href="{verification_link}" class="button">Verify Email Address</a>
            </center>
            
            <p style="font-size: 12px; color: #666;">
                Or copy and paste this link into your browser:<br>
                <a href="{verification_link}">{verification_link}</a>
            </p>
            
            <p><strong>This link will expire in 24 hours.</strong></p>
            
            <p>If you didn't create this account, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>© {datetime.now().year} FinSTK - Financial Simulation Toolkit</p>
            <p>This is an automated email. Please do not reply.</p>
        </div>
    </body>
    </html>
    """
    
    # Attach both versions
    text_part = MIMEText(text_content, "plain")
    html_part = MIMEText(html_content, "html")
    
    message.attach(text_part)
    message.attach(html_part)
    
    return message


def send_email(to_email: str, message: MIMEMultipart) -> Tuple[bool, str]:
    """Send email via SMTP
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        return False, "Email service not configured. Please contact administrator."
    
    try:
        # Create SMTP session
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Enable TLS
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            
            # Send email
            server.send_message(message)
            
        return True, "Email sent successfully"
        
    except smtplib.SMTPAuthenticationError:
        return False, "Email authentication failed"
    except smtplib.SMTPException as e:
        return False, f"Email sending failed: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def send_verification_email(email: str, username: str, verification_token: str) -> Tuple[bool, str]:
    """Send verification email to user
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    message = create_verification_email(email, username, verification_token)
    return send_email(email, message)


def create_welcome_email(email: str, username: str) -> MIMEMultipart:
    """Create welcome email after verification"""
    message = MIMEMultipart("alternative")
    message["Subject"] = "Welcome to FinSTK - Let's Get Started!"
    message["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    message["To"] = email
    
    # Plain text version
    text_content = f"""
    Hi {username},
    
    Your email has been verified! Welcome to FinSTK.
    
    You can now access all features:
    - Monte Carlo wealth simulations
    - Budget builder with monthly tracking
    - UK pension calculators (State Pension, USS, SIPP)
    - Multiple currency support
    - Export results to PDF
    
    Get started at: {BASE_URL}
    
    Need help? Check out our documentation or contact support.
    
    Happy planning!
    The FinSTK Team
    """
    
    # HTML version
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            .content {{
                background: #f9f9f9;
                padding: 30px;
                border-radius: 0 0 10px 10px;
            }}
            .feature {{
                background: white;
                padding: 15px;
                margin: 10px 0;
                border-left: 4px solid #667eea;
                border-radius: 5px;
            }}
            .button {{
                display: inline-block;
                padding: 15px 30px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎉 You're All Set!</h1>
        </div>
        <div class="content">
            <p>Hi <strong>{username}</strong>,</p>
            
            <p>Your email has been verified! Welcome to FinSTK.</p>
            
            <h3>What You Can Do Now:</h3>
            
            <div class="feature">
                <strong>📊 Monte Carlo Simulations</strong><br>
                Model your financial future with probability-based projections
            </div>
            
            <div class="feature">
                <strong>💰 Budget Builder</strong><br>
                Track monthly expenses and plan ahead
            </div>
            
            <div class="feature">
                <strong>🏦 UK Pension Calculators</strong><br>
                State Pension, USS, and SIPP planning tools
            </div>
            
            <div class="feature">
                <strong>💱 Multi-Currency Support</strong><br>
                Plan in GBP, EUR, USD, and more
            </div>
            
            <center>
                <a href="{BASE_URL}" class="button">Start Planning Now</a>
            </center>
            
            <p>Questions? Check our documentation or use the feedback button in the app.</p>
        </div>
    </body>
    </html>
    """
    
    text_part = MIMEText(text_content, "plain")
    html_part = MIMEText(html_content, "html")
    
    message.attach(text_part)
    message.attach(html_part)
    
    return message


def send_welcome_email(email: str, username: str) -> Tuple[bool, str]:
    """Send welcome email after verification"""
    message = create_welcome_email(email, username)
    return send_email(email, message)
