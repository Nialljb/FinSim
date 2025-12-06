"""
Legacy auth.py module - forwards to authentication package.

This module exists only for backward compatibility during the migration period.
All new code should import from `authentication` package instead.

Example:
    # Old way (still works):
    from auth import login_user
    
    # New way (preferred):
    from authentication import login_user
"""

# Import everything from the authentication package and re-export
from authentication import *

# Explicitly list exports for clarity
__all__ = [
    # Password
    'hash_password',
    'verify_password',
    
    # User management
    'register_user',
    'login_user',
    'logout',
    'get_user_by_id',
    'get_user_usage_stats',
    
    # Email verification
    'verify_email',
    'resend_verification_email',
    'request_password_reset',
    
    # Usage tracking
    'increment_simulation_count',
    'increment_export_count',
    'check_simulation_limit',
    'reset_simulation_count',
    'submit_feedback',
    
    # Session management
    'initialize_session_state',
    'create_session_token',
    'restore_session_from_storage',
    'get_session_persistence_script',
    
    # UI
    'show_login_page',
    'show_user_header',
]
