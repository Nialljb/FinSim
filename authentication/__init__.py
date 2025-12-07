"""
Authentication module - imports from local auth.py file.

This module re-exports all authentication functions from authentication/auth.py
to provide a clean public API.
"""

# Import from the local auth.py file within the authentication directory
from authentication.auth import (
    # Password utilities
    hash_password,
    verify_password,
    
    # User management
    register_user,
    login_user,
    logout,
    get_user_by_id,
    get_user_usage_stats,
    
    # Email verification
    verify_email,
    resend_verification_email,
    request_password_reset,
    
    # Usage tracking
    increment_simulation_count,
    increment_export_count,
    check_simulation_limit,
    reset_simulation_count,
    submit_feedback,
    
    # Session management  
    initialize_session_state,
    create_session_token,
    restore_session_from_storage,
    get_session_persistence_script,
    
    # UI components
    show_login_page,
    show_user_header,
)

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
