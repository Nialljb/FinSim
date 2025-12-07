"""
Input validation utilities
"""

from typing import Optional, Tuple
from lib.constants import (
    MIN_AGE, MAX_AGE, MIN_SIMULATIONS, MAX_SIMULATIONS,
    SIPP_ANNUAL_ALLOWANCE
)


def validate_age(age: int, field_name: str = "Age") -> Tuple[bool, Optional[str]]:
    """
    Validate age is within acceptable range
    
    Returns:
        (is_valid, error_message)
    """
    if not isinstance(age, (int, float)):
        return False, f"{field_name} must be a number"
    
    if age < MIN_AGE:
        return False, f"{field_name} must be at least {MIN_AGE}"
    
    if age > MAX_AGE:
        return False, f"{field_name} cannot exceed {MAX_AGE}"
    
    return True, None


def validate_age_range(
    current_age: int,
    retirement_age: int,
    end_age: Optional[int] = None
) -> Tuple[bool, Optional[str]]:
    """
    Validate age progression makes sense
    
    Returns:
        (is_valid, error_message)
    """
    # Validate individual ages
    valid, msg = validate_age(current_age, "Current age")
    if not valid:
        return False, msg
    
    valid, msg = validate_age(retirement_age, "Retirement age")
    if not valid:
        return False, msg
    
    if end_age:
        valid, msg = validate_age(end_age, "End age")
        if not valid:
            return False, msg
    
    # Validate progression
    if retirement_age <= current_age:
        return False, "Retirement age must be greater than current age"
    
    if end_age and end_age <= retirement_age:
        return False, "End age must be greater than retirement age"
    
    return True, None


def validate_positive_amount(
    amount: float,
    field_name: str = "Amount",
    allow_zero: bool = False
) -> Tuple[bool, Optional[str]]:
    """
    Validate amount is positive
    
    Returns:
        (is_valid, error_message)
    """
    if not isinstance(amount, (int, float)):
        return False, f"{field_name} must be a number"
    
    if allow_zero:
        if amount < 0:
            return False, f"{field_name} cannot be negative"
    else:
        if amount <= 0:
            return False, f"{field_name} must be positive"
    
    return True, None


def validate_percentage(
    value: float,
    field_name: str = "Percentage",
    min_val: float = 0.0,
    max_val: float = 1.0
) -> Tuple[bool, Optional[str]]:
    """
    Validate value is a valid percentage (as decimal)
    
    Args:
        value: Decimal value (e.g., 0.15 for 15%)
        field_name: Name for error message
        min_val: Minimum allowed value
        max_val: Maximum allowed value
    
    Returns:
        (is_valid, error_message)
    """
    if not isinstance(value, (int, float)):
        return False, f"{field_name} must be a number"
    
    if value < min_val:
        return False, f"{field_name} must be at least {min_val*100}%"
    
    if value > max_val:
        return False, f"{field_name} cannot exceed {max_val*100}%"
    
    return True, None


def validate_simulation_count(count: int) -> Tuple[bool, Optional[str]]:
    """
    Validate number of Monte Carlo simulations
    
    Returns:
        (is_valid, error_message)
    """
    if not isinstance(count, int):
        return False, "Simulation count must be an integer"
    
    if count < MIN_SIMULATIONS:
        return False, f"Must run at least {MIN_SIMULATIONS} simulations"
    
    if count > MAX_SIMULATIONS:
        return False, f"Cannot exceed {MAX_SIMULATIONS} simulations"
    
    return True, None


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Basic email validation
    
    Returns:
        (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    if '@' not in email:
        return False, "Invalid email format"
    
    parts = email.split('@')
    if len(parts) != 2:
        return False, "Invalid email format"
    
    if not parts[0] or not parts[1]:
        return False, "Invalid email format"
    
    if '.' not in parts[1]:
        return False, "Invalid email domain"
    
    return True, None


def validate_password(password: str, min_length: int = 8) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength
    
    Returns:
        (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters"
    
    # Check for at least one number
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    # Check for at least one letter
    if not any(c.isalpha() for c in password):
        return False, "Password must contain at least one letter"
    
    return True, None


def validate_username(username: str, min_length: int = 3) -> Tuple[bool, Optional[str]]:
    """
    Validate username
    
    Returns:
        (is_valid, error_message)
    """
    if not username:
        return False, "Username is required"
    
    if len(username) < min_length:
        return False, f"Username must be at least {min_length} characters"
    
    # Check for valid characters (alphanumeric, underscore, hyphen)
    if not all(c.isalnum() or c in ['_', '-'] for c in username):
        return False, "Username can only contain letters, numbers, underscore, and hyphen"
    
    return True, None


# ============================================================================
# Export
# ============================================================================

__all__ = [
    'validate_age',
    'validate_age_range',
    'validate_positive_amount',
    'validate_percentage',
    'validate_simulation_count',
    'validate_email',
    'validate_password',
    'validate_username',
]
