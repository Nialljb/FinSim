"""
Authentication module for FinSim
Handles user registration, login, and session management
"""

import bcrypt
import streamlit as st
from datetime import datetime
from database import SessionLocal, User, UsageStats


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


def check_simulation_limit(user_id: int, limit: int = 5) -> tuple:
    """Check if user has reached simulation limit"""
    stats_data = get_user_usage_stats(user_id)
    remaining = limit - stats_data['simulations_this_month']
    
    if remaining <= 0:
        return False, 0, "Monthly simulation limit reached"
    else:
        return True, remaining, f"{remaining} simulations remaining this month"


def initialize_session_state():
    """Initialize Streamlit session state for authentication"""
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


def logout():
    """Logout user and clear session state"""
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.user_email = None
    st.session_state.current_age = None
    st.session_state.target_retirement_age = None


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
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"👤 **{st.session_state.username}**")
        
        with col2:
            # Show usage stats
            stats_data = get_user_usage_stats(st.session_state.user_id)
            st.caption(f"📊 Simulations: {stats_data['simulations_this_month']}/5")
        
        with col3:
            if st.button("Logout"):
                logout()
                st.rerun()