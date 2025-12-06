"""
Application settings loaded from environment variables
Following 12-factor app principles
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# Application Settings
# ============================================================================

APP_NAME = "FinSTK"
APP_VERSION = "2.0.0"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# ============================================================================
# Base URL
# ============================================================================

BASE_URL = os.getenv("BASE_URL", "http://localhost:8501")

# ============================================================================
# Security
# ============================================================================

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")

# ============================================================================
# Feature Flags
# ============================================================================

# Simulation limits
FREE_SIMULATION_LIMIT = int(os.getenv("FREE_SIMULATION_LIMIT", "10"))

# Feature toggles
ENABLE_PDF_EXPORT = os.getenv("ENABLE_PDF_EXPORT", "True").lower() == "true"
ENABLE_EMAIL_VERIFICATION = os.getenv("ENABLE_EMAIL_VERIFICATION", "True").lower() == "true"
ENABLE_ANALYTICS = os.getenv("ENABLE_ANALYTICS", "True").lower() == "true"

# ============================================================================
# Currency Settings
# ============================================================================

DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "GBP")
BASE_CURRENCY = "GBP"  # Internal base currency for storage

# Supported currencies
SUPPORTED_CURRENCIES = [
    'EUR', 'GBP', 'CAD', 'USD', 'AUD', 'NZD', 
    'CHF', 'SEK', 'NOK', 'DKK', 'JPY', 'CNY'
]

# ============================================================================
# Validation
# ============================================================================

def validate_settings():
    """Validate required settings are present"""
    errors = []
    
    if SECRET_KEY == "change-me-in-production" and not DEBUG:
        errors.append("SECRET_KEY must be set in production")
    
    if DEFAULT_CURRENCY not in SUPPORTED_CURRENCIES:
        errors.append(f"DEFAULT_CURRENCY {DEFAULT_CURRENCY} not in SUPPORTED_CURRENCIES")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    return True

# ============================================================================
# Auto-validate on import (optional, comment out if problematic)
# ============================================================================

# Uncomment to enable auto-validation:
# validate_settings()
