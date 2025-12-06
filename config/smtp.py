"""
SMTP/Email configuration
Used by email verification and notification services
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# SMTP Server Configuration
# ============================================================================

SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')

# ============================================================================
# Email Sender Configuration
# ============================================================================

SENDER_EMAIL = os.getenv('SENDER_EMAIL', SMTP_USERNAME)
SENDER_NAME = os.getenv('SENDER_NAME', 'FinSTK')

# ============================================================================
# Email Templates Configuration
# ============================================================================

# Base URL for email links (verification, password reset, etc.)
from config.settings import BASE_URL
EMAIL_BASE_URL = BASE_URL

# Email verification settings
VERIFICATION_TOKEN_EXPIRY_HOURS = 24
WELCOME_EMAIL_ENABLED = True

# ============================================================================
# Validation
# ============================================================================

def is_email_configured():
    """Check if email service is properly configured"""
    return bool(SMTP_USERNAME and SMTP_PASSWORD)

def validate_email_config():
    """Validate email configuration"""
    errors = []
    
    if not SMTP_USERNAME:
        errors.append("SMTP_USERNAME not set")
    
    if not SMTP_PASSWORD:
        errors.append("SMTP_PASSWORD not set")
    
    if not SMTP_SERVER:
        errors.append("SMTP_SERVER not set")
    
    if SMTP_PORT not in [25, 465, 587, 2525]:
        errors.append(f"Unusual SMTP_PORT: {SMTP_PORT}")
    
    return errors

# ============================================================================
# Export
# ============================================================================

__all__ = [
    'SMTP_SERVER',
    'SMTP_PORT',
    'SMTP_USERNAME',
    'SMTP_PASSWORD',
    'SENDER_EMAIL',
    'SENDER_NAME',
    'EMAIL_BASE_URL',
    'VERIFICATION_TOKEN_EXPIRY_HOURS',
    'WELCOME_EMAIL_ENABLED',
    'is_email_configured',
    'validate_email_config'
]
