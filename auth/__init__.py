"""
Auth module - temporary forwarding to root auth.py during migration
This allows both old and new import paths to work
"""

import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import from root auth.py and re-export
# This is a temporary bridge during the refactoring process
try:
    # Import from the auth.py file in parent directory
    import importlib.util
    spec = importlib.util.spec_from_file_location("auth_root", os.path.join(parent_dir, "auth.py"))
    auth_root = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(auth_root)
    
    # Re-export all functions from root auth.py
    initialize_session_state = auth_root.initialize_session_state
    show_login_page = auth_root.show_login_page
    show_user_header = auth_root.show_user_header
    check_simulation_limit = auth_root.check_simulation_limit
    increment_simulation_count = auth_root.increment_simulation_count
    increment_export_count = auth_root.increment_export_count
    reset_simulation_count = auth_root.reset_simulation_count
    login_user = auth_root.login_user
    register_user = auth_root.register_user
    logout = auth_root.logout
    verify_email = auth_root.verify_email
    resend_verification_email = auth_root.resend_verification_email
    request_password_reset = getattr(auth_root, 'request_password_reset', None)
    
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
    ]
    
except Exception as e:
    print(f"Warning: Could not import from root auth.py: {e}")
    raise
