"""
Authentication module for FinSim
Handles user registration, login, and session management
"""

import bcrypt
import streamlit as st
from datetime import datetime, timedelta
from database import SessionLocal, User, UsageStats, Feedback
import hashlib
import secrets


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def register_user(username: str, email: str, password: str, current_age: int, target_retirement_age: int, country: str = None):
    """Register a new user"""
    db = SessionLocal()
    try:
        # Check if username or email already exists
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            if existing_user.username == username:
                return False, "Username already exists"
            else:
                return False, "Email already registered"
        
        # Create new user
        hashed_pw = hash_password(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_pw,
            current_age=current_age,
            target_retirement_age=target_retirement_age,
            country=country,
            created_at=datetime.now()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Initialize usage stats
        current_month = datetime.now().strftime("%Y-%m")
        usage_stats = UsageStats(
            user_id=new_user.id,
            current_month=current_month,
            simulations_this_month=0,
            exports_this_month=0
        )
        db.add(usage_stats)
        db.commit()
        
        return True, "Registration successful!"
        
    except Exception as e:
        db.rollback()
        return False, f"Registration failed: {str(e)}"
    finally:
        db.close()


def login_user(username_or_email: str, password: str):
    """Authenticate user with username or email and return user data dict if successful"""
    db = SessionLocal()
    try:
        # Try to find user by username or email
        user = db.query(User).filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if not user:
            return None, "Username or email not found"
        
        if not user.is_active:
            return None, "Account is deactivated"
        
        if not verify_password(password, user.password_hash):
            return None, "Incorrect password"
        
        # Update last login
        user.last_login = datetime.now()
        db.commit()
        
        # Extract all user data before closing session
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'current_age': user.current_age,
            'target_retirement_age': user.target_retirement_age,
            'country': user.country,
            'last_login': user.last_login
        }
        
        return user_data, "Login successful"
        
    except Exception as e:
        return None, f"Login failed: {str(e)}"
    finally:
        db.close()


def get_user_by_id(user_id: int):
    """Get user data by ID"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # Extract data before closing session
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'current_age': user.current_age,
            'target_retirement_age': user.target_retirement_age,
            'country': user.country,
            'is_active': user.is_active,
            'created_at': user.created_at,
            'last_login': user.last_login
        }
        return user_data
    finally:
        db.close()


def get_user_usage_stats(user_id: int):
    """Get current month usage stats for user"""
    db = SessionLocal()
    try:
        current_month = datetime.now().strftime("%Y-%m")
        
        # Get or create usage stats for current month
        stats = db.query(UsageStats).filter(
            UsageStats.user_id == user_id,
            UsageStats.current_month == current_month
        ).first()
        
        if not stats:
            # Create new stats for current month
            stats = UsageStats(
                user_id=user_id,
                current_month=current_month,
                simulations_this_month=0,
                exports_this_month=0
            )
            db.add(stats)
            db.commit()
            db.refresh(stats)
        
        # Extract data before closing session
        stats_data = {
            'user_id': stats.user_id,
            'simulations_this_month': stats.simulations_this_month,
            'exports_this_month': stats.exports_this_month,
            'last_simulation_date': stats.last_simulation_date,
            'current_month': stats.current_month
        }
        
        return stats_data
    finally:
        db.close()


def increment_simulation_count(user_id: int):
    """Increment simulation count for user"""
    db = SessionLocal()
    try:
        current_month = datetime.now().strftime("%Y-%m")
        
        stats = db.query(UsageStats).filter(
            UsageStats.user_id == user_id,
            UsageStats.current_month == current_month
        ).first()
        
        if stats:
            stats.simulations_this_month += 1
            stats.last_simulation_date = datetime.now()
            db.commit()
        
    finally:
        db.close()


def increment_export_count(user_id: int):
    """Increment export count for user"""
    db = SessionLocal()
    try:
        current_month = datetime.now().strftime("%Y-%m")
        
        stats = db.query(UsageStats).filter(
            UsageStats.user_id == user_id,
            UsageStats.current_month == current_month
        ).first()
        
        if stats:
            stats.exports_this_month += 1
            db.commit()
        
    finally:
        db.close()


def check_simulation_limit(user_id: int, limit: int = 10, is_admin: bool = False) -> tuple:
    """Check if user has reached simulation limit
    
    Args:
        user_id: User ID to check
        limit: Maximum simulations allowed (default 10 for standard users)
        is_admin: If True, grants unlimited simulations
    
    Returns:
        tuple: (can_simulate, remaining, message)
    """
    if is_admin:
        return True, -1, "✓ Unlimited simulations (Admin)"
    
    stats_data = get_user_usage_stats(user_id)
    remaining = limit - stats_data['simulations_this_month']
    
    if remaining <= 0:
        return False, 0, "Monthly simulation limit reached"
    else:
        return True, remaining, f"{remaining} simulations remaining this month"


def reset_simulation_count(user_id: int):
    """Reset simulation count to 0 for user (for requesting more simulations)
    
    In the future, this will be tied to subscription/payment system.
    For now, it simply resets the counter to allow 10 more simulations.
    """
    db = SessionLocal()
    try:
        current_month = datetime.now().strftime("%Y-%m")
        
        stats = db.query(UsageStats).filter(
            UsageStats.user_id == user_id,
            UsageStats.current_month == current_month
        ).first()
        
        if stats:
            stats.simulations_this_month = 0
            db.commit()
            return True, "Simulation count reset! You have 10 new simulations."
        else:
            return False, "Unable to find usage statistics."
        
    except Exception as e:
        db.rollback()
        return False, f"Error resetting count: {str(e)}"
    finally:
        db.close()


def submit_feedback(user_id: int, feedback_type: str, subject: str, message: str, 
                   page_context: str = None, user_email: str = None):
    """Submit user feedback to database
    
    Args:
        user_id: User ID submitting feedback
        feedback_type: Type of feedback ('bug', 'feature', 'general', 'issue')
        subject: Brief subject/title
        message: Detailed feedback message
        page_context: Which page/feature they were using (optional)
        user_email: Email for follow-up (optional)
    
    Returns:
        tuple: (success, message)
    """
    db = SessionLocal()
    try:
        feedback = Feedback(
            user_id=user_id,
            feedback_type=feedback_type,
            subject=subject,
            message=message,
            page_context=page_context,
            user_email=user_email,
            status='new'
        )
        
        db.add(feedback)
        db.commit()
        
        return True, "Thank you for your feedback! We'll review it soon."
        
    except Exception as e:
        db.rollback()
        return False, f"Error submitting feedback: {str(e)}"
    finally:
        db.close()


def initialize_session_state():
    """Initialize Streamlit session state for authentication with persistence"""
    
    # Default initialization if values don't exist
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'current_age' not in st.session_state:
        st.session_state.current_age = None
    if 'target_retirement_age' not in st.session_state:
        st.session_state.target_retirement_age = None
    if 'session_token' not in st.session_state:
        st.session_state.session_token = None
    if 'session_restored' not in st.session_state:
        st.session_state.session_restored = False


def create_session_token(user_id: int) -> str:
    """Create a session token for persistent login"""
    # Create a simple token: user_id + random string + timestamp
    random_part = secrets.token_urlsafe(16)
    timestamp = datetime.now().isoformat()
    token_data = f"{user_id}:{random_part}:{timestamp}"
    # Hash it for security
    token = hashlib.sha256(token_data.encode()).hexdigest()
    
    # Store in session state
    st.session_state.session_token = token
    st.session_state.session_user_id = user_id
    
    return token


def restore_session_from_storage(user_id: int):
    """Restore user session from user_id"""
    try:
        user_data = get_user_by_id(user_id)
        if user_data and user_data.get('is_active', True):
            st.session_state.authenticated = True
            st.session_state.user_id = user_data['id']
            st.session_state.username = user_data['username']
            st.session_state.user_email = user_data['email']
            st.session_state.current_age = user_data['current_age']
            st.session_state.target_retirement_age = user_data['target_retirement_age']
            st.session_state.session_restored = True
            return True
    except:
        pass
    return False


def get_session_persistence_script():
    """Return JavaScript code for session persistence using localStorage"""
    return """
    <script>
        // Save session to localStorage on login
        if (window.parent.document.getElementById('save-session-data')) {
            const sessionData = window.parent.document.getElementById('save-session-data').textContent;
            if (sessionData && sessionData !== 'null') {
                localStorage.setItem('finsim_session', sessionData);
            }
        }
        
        // Load session from localStorage on page load
        const savedSession = localStorage.getItem('finsim_session');
        if (savedSession && savedSession !== 'null') {
            const sessionDisplay = window.parent.document.getElementById('restore-session-data');
            if (sessionDisplay) {
                sessionDisplay.textContent = savedSession;
            }
        }
        
        // Clear session on logout
        if (window.parent.document.getElementById('clear-session')) {
            localStorage.removeItem('finsim_session');
        }
    </script>
    """


def logout():
    """Logout user and clear session state"""
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.user_email = None
    st.session_state.current_age = None
    st.session_state.target_retirement_age = None
    st.session_state.session_token = None
    st.session_state.session_restored = False


def show_login_page():
    """Display login page"""
    initialize_session_state()
    
    st.title("🔐 Login to FinSim")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login to Your Account")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if not username or not password:
                    st.error("Please fill in all fields")
                else:
                    user_data, message = login_user(username, password)
                    
                    if user_data:
                        st.session_state.authenticated = True
                        st.session_state.user_id = user_data['id']
                        st.session_state.username = user_data['username']
                        st.session_state.user_email = user_data['email']
                        st.session_state.current_age = user_data['current_age']
                        st.session_state.target_retirement_age = user_data['target_retirement_age']
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
    
    with tab2:
        st.subheader("Create Free Account")
        
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("Username*", key="reg_username")
                new_email = st.text_input("Email*", key="reg_email")
                new_password = st.text_input("Password*", type="password", key="reg_password")
                confirm_password = st.text_input("Confirm Password*", type="password", key="reg_confirm")
            
            with col2:
                current_age = st.number_input("Current Age*", min_value=18, max_value=100, value=30, key="reg_age")
                target_retirement_age = st.number_input("Target Retirement Age*", min_value=50, max_value=100, value=65, key="reg_retire")
                country = st.text_input("Country (Optional)", key="reg_country")
            
            st.markdown("---")
            
            consent = st.checkbox(
                "I agree to share anonymized, aggregated data for research purposes. "
                "This helps us keep FinSim free. Your individual data will NEVER be sold or shared.",
                key="consent"
            )
            
            terms = st.checkbox(
                "I agree to the Terms of Service and Privacy Policy",
                key="terms"
            )
            
            submit_register = st.form_submit_button("Create Account")
            
            if submit_register:
                # Validation
                if not new_username or not new_email or not new_password:
                    st.error("Please fill in all required fields (*)")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                elif len(new_password) < 8:
                    st.error("Password must be at least 8 characters")
                elif not consent:
                    st.error("Please agree to data sharing policy")
                elif not terms:
                    st.error("Please agree to Terms of Service")
                else:
                    success, message = register_user(
                        new_username, 
                        new_email, 
                        new_password,
                        current_age,
                        target_retirement_age,
                        country if country else None
                    )
                    
                    if success:
                        st.success(message)
                        st.info("Please login with your new account")
                    else:
                        st.error(message)
        
        st.caption("*Required fields")


def request_password_reset(email: str):
    """Check if email exists and return username (simplified version without email sending)"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Don't reveal if email exists for security
            return True, "If this email is registered, you will receive password reset instructions."
        
        # In a production app, you would:
        # 1. Generate a secure reset token
        # 2. Store it in database with expiration
        # 3. Send email with reset link
        # For now, just return username as a helper
        return True, f"Account found! Your username is: {user.username}"
        
    except Exception as e:
        return False, "An error occurred. Please try again later."
    finally:
        db.close()


def show_user_header():
    """Display user info header when logged in"""
    if st.session_state.authenticated:
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            st.markdown(f"👤 **{st.session_state.username}**")
        
        with col2:
            # Show usage stats
            stats_data = get_user_usage_stats(st.session_state.user_id)
            st.caption(f"📊 Simulations: {stats_data['simulations_this_month']}/10")
        
        with col3:
            if st.button("💬 Feedback"):
                st.session_state.show_feedback_modal = True
        
        with col4:
            if st.button("Logout"):
                logout()
                st.rerun()
        
        # Feedback modal
        if st.session_state.get('show_feedback_modal', False):
            with st.expander("📝 Submit Feedback or Report Issue", expanded=True):
                st.markdown("""Choose how you'd like to share your feedback:""")
                
                feedback_method = st.radio(
                    "Feedback Method",
                    ["Quick Feedback (Internal)", "Report on GitHub Issues"],
                    help="Quick feedback is stored internally. GitHub allows public tracking and discussion."
                )
                
                if feedback_method == "Report on GitHub Issues":
                    st.markdown("""### Report on GitHub
                    
For bugs, feature requests, or public discussion, please visit our GitHub Issues page:
                    
                    👉 **[Open GitHub Issues](https://github.com/Nialljb/FinSim/issues)**
                    
                    This allows you to:
                    - Track the status of your report
                    - Participate in discussions
                    - See what others are reporting
                    """)
                    
                    if st.button("Close", key="close_github"):
                        st.session_state.show_feedback_modal = False
                        st.rerun()
                
                else:
                    # Internal feedback form
                    with st.form("feedback_form", clear_on_submit=True):
                        feedback_type = st.selectbox(
                            "Type",
                            ["General Feedback", "Bug Report", "Feature Request", "Issue/Problem"],
                            help="What kind of feedback are you providing?"
                        )
                        
                        subject = st.text_input(
                            "Subject",
                            placeholder="Brief description of your feedback",
                            max_chars=255
                        )
                        
                        message = st.text_area(
                            "Message",
                            placeholder="Please provide details about your feedback, bug, or feature request...",
                            height=150
                        )
                        
                        page_context = st.text_input(
                            "Where did this occur? (Optional)",
                            placeholder="e.g., Simulation Page, Budget Builder, etc."
                        )
                        
                        col_a, col_b = st.columns([1, 1])
                        
                        with col_a:
                            submit = st.form_submit_button("Submit Feedback", type="primary", use_container_width=True)
                        
                        with col_b:
                            cancel = st.form_submit_button("Cancel", use_container_width=True)
                        
                        if submit:
                            if not subject or not message:
                                st.error("Please fill in both subject and message")
                            else:
                                # Map friendly names to database values
                                type_map = {
                                    "General Feedback": "general",
                                    "Bug Report": "bug",
                                    "Feature Request": "feature",
                                    "Issue/Problem": "issue"
                                }
                                
                                success, result_msg = submit_feedback(
                                    user_id=st.session_state.user_id,
                                    feedback_type=type_map[feedback_type],
                                    subject=subject,
                                    message=message,
                                    page_context=page_context if page_context else None,
                                    user_email=st.session_state.user_email
                                )
                                
                                if success:
                                    st.success(result_msg)
                                    st.session_state.show_feedback_modal = False
                                    st.rerun()
                                else:
                                    st.error(result_msg)
                        
                        if cancel:
                            st.session_state.show_feedback_modal = False
                            st.rerun()