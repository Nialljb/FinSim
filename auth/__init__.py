"""
Auth module - forwards to authentication module for compatibility
Maintains backward compatibility for 'from auth import ...' statements
"""

from authentication.auth import (
    initialize_session_state,
    show_login_page,
    show_user_header,
    check_simulation_limit,
    increment_simulation_count,
    increment_export_count,
    reset_simulation_count,
    login_user,
    register_user,
    logout,
    verify_email,
    resend_verification_email,
    request_password_reset,
    hash_password,
)

__all__ = [
    'initialize_session_state',
    'show_login_page',
    'show_user_header',
    'check_simulation_limit',
    'increment_simulation_count',
    'increment_export_count',
    'reset_simulation_count',
    'login_user',
    'register_user',
    'logout',
    'verify_email',
    'resend_verification_email',
    'request_password_reset',
    'hash_password',
]
