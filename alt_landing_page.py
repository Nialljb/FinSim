"""
Improved Landing Page with Layout Control
Handles width, theming, and responsive design better
"""

import streamlit as st
from auth import initialize_session_state, login_user, register_user, logout


def show_landing_page():
    """
    Professional landing page with controlled layout and light theme
    """
    initialize_session_state()
    
    # Force wide layout and light theme
    st.set_page_config(
        page_title="FinSim - Financial Planning Simulator",
        page_icon="🦉",
        layout="wide",
        # initial_sidebar_state="collapsed"  # Hide sidebar on landing page
    )
    
    # Custom CSS for landing page with width control
    st.markdown("""
        <style>
        /* Force light theme colors */
        :root {
            --background-color: #ffffff;
            --secondary-background-color: #f8f9fa;
            --text-color: #262730;
        }
        
        /* Main container - control max width */
        .main .block-container {
            max-width: 1200px;
            padding-top: 2rem;
            padding-bottom: 2rem;
            margin: 0 auto;
        }
        
        /* Force light backgrounds */
        .stApp {
            background-color: #ffffff;
        }
        
        section[data-testid="stSidebar"] {
            display: none;  /* Hide sidebar on landing page */
        }
        
        /* Hero section */
        .hero {
            text-align: center;
            padding: 4rem 2rem;
            background: linear-gradient(135deg, #1e293b 0%, #4c1d95 100%);  /* Dark slate to purple */
            color: white;
            border-radius: 15px;
            margin-bottom: 3rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .hero h1 {
            font-size: 3.5rem;
            margin-bottom: 1rem;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .hero-subtitle {
            font-size: 1.5rem;
            margin-bottom: 1rem;
            opacity: 0.95;
        }
        
        .hero-description {
            font-size: 1.1rem;
            opacity: 0.9;
            max-width: 800px;
            margin: 0 auto;
        }
        
        /* Feature boxes */
        .feature-box {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: transform 0.2s;
        }
        
        .feature-box:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .feature-box h3 {
            color: #667eea;
            margin-bottom: 0.5rem;
            font-size: 1.3rem;
        }
        
        .feature-box p {
            color: #4a5568;
            margin: 0;
            line-height: 1.6;
        }
        
        /* Stats */
        .stat-container {
            display: flex;
            justify-content: space-around;
            margin: 3rem 0;
            flex-wrap: wrap;
            gap: 2rem;
        }
        
        .stat-box {
            text-align: center;
            padding: 1.5rem;
            background: #f8f9fa;
            border-radius: 10px;
            min-width: 150px;
            flex: 1;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .stat-number {
            font-size: 3rem;
            font-weight: bold;
            color: #667eea;
            line-height: 1;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            color: #4a5568;
            font-size: 1rem;
            font-weight: 500;
        }
        
        /* Login/Register section */
        .auth-section {
            background: #ffffff;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border: 1px solid #e2e8f0;
        }
        
        /* Form styling */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input {
            background-color: #ffffff !important;
            color: #262730 !important;
        }
        
        /* Button styling */
        .stButton > button {
            width: 100%;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            transition: all 0.2s;
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        
        /* Testimonial */
        .testimonial {
            background: #ffffff;
            padding: 1.5rem;
            border-radius: 10px;
            border: 2px solid #e2e8f0;
            margin: 1rem 0;
            font-style: italic;
            color: #4a5568;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .testimonial-author {
            font-weight: bold;
            color: #667eea;
            margin-top: 0.75rem;
            font-style: normal;
            font-size: 0.95rem;
        }
        
        /* How it works section */
        .how-it-works {
            background: #f8f9fa;
            padding: 2rem;
            border-radius: 10px;
            margin: 2rem 0;
        }
        
        .step-box {
            text-align: center;
            padding: 1rem;
        }
        
        .step-number {
            font-size: 2.5rem;
            color: #667eea;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .step-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 0.5rem;
        }
        
        .step-description {
            color: #4a5568;
            font-size: 0.95rem;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .hero h1 {
                font-size: 2rem;
            }
            
            .hero-subtitle {
                font-size: 1.2rem;
            }
            
            .stat-container {
                flex-direction: column;
            }
            
            .stat-box {
                width: 100%;
            }
        }
        
        /* Tab styling - force light theme */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #f8f9fa;
        }
        
        .stTabs [data-baseweb="tab"] {
            color: #4a5568;
            background-color: transparent;
            font-size: 1.1rem;
            font-weight: 500;
        }
        
        .stTabs [aria-selected="true"] {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        
        /* Larger font for form labels and inputs */
        .auth-section label {
            font-size: 1.05rem !important;
            font-weight: 500 !important;
        }
        
        .auth-section input {
            font-size: 1rem !important;
        }
        
        .auth-section .stTextInput label,
        .auth-section .stNumberInput label {
            font-size: 1.05rem !important;
        }
        
        /* Larger font for form section headers */
        .auth-section .stMarkdown p strong {
            font-size: 1.1rem !important;
        }
        
                /* Remove extra spacing around tabs */
        .stTabs {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        
        /* Remove space above tab content */
        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 1rem !important;
        }
                
        /* Remove extra spacing around tabs */
        .stTabs {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }

        /* Remove space above tab content */
        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 1rem !important;
        }
        
        /* Remove empty div spacing */
        div[data-testid="stVerticalBlock"] > div:empty {
            display: none !important;
        }
        
        /* Remove empty elements before auth section */
        .auth-section > div:empty,
        .auth-section > div > div:empty {
            display: none !important;
        }
        
        /* Tighten up auth section */
        .auth-section > div:first-child {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        
        .auth-section h3 {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        
        /* Remove spacing around markdown elements in auth section */
        .auth-section [data-testid="stMarkdown"] {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        
        /* Remove any extra vertical blocks */
        [data-testid="column"] > [data-testid="stVerticalBlock"] > div:first-child:empty {
            display: none !important;
        }
        
        /* Info/warning boxes - ensure visibility in light theme */
        .stAlert {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Hero Section
    st.markdown("""
        <div class="hero">
            <h1>🦉 FinSim</h1>
            <div class="hero-subtitle">Plan Your Financial Future with Confidence</div>
            <div class="hero-description">
                Monte Carlo simulations • Retirement planning • Real estate modeling • Multi-currency support • 100% Free
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Social Proof Stats
    st.markdown("""
        <div class="stat-container">
            <div class="stat-box">
                <div class="stat-number">100+</div>
                <div class="stat-label">Simulations Run</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">10</div>
                <div class="stat-label">Free per Month</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">35+</div>
                <div class="stat-label">Year Projections</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">15</div>
                <div class="stat-label">Currencies</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Main content area - Login and Features side by side
    col_left, col_spacer, col_right = st.columns([5, 1, 6])
    
    with col_left:
        st.markdown('''
        <div class="auth-section">
            <h3 style="margin-top: 0; padding-top: 0;">🔐 Get Started</h3>
        </div>
        ''', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Create Account"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    submit = st.form_submit_button("Login", type="primary", use_container_width=True)
                
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
            
            # Demo account info
            st.info("💡 **Try it out:**\n\nUsername: `testuser`\n\nPassword: `password123`")
        
        with tab2:
            with st.form("register_form"):
                st.markdown("**Account Information**")
                new_username = st.text_input("Username*", key="reg_username")
                new_email = st.text_input("Email*", key="reg_email")
                
                col1, col2 = st.columns(2)
                with col1:
                    new_password = st.text_input("Password*", type="password", key="reg_password")
                with col2:
                    confirm_password = st.text_input("Confirm*", type="password", key="reg_confirm")
                
                st.markdown("**Your Planning Profile**")
                col1, col2 = st.columns(2)
                with col1:
                    current_age = st.number_input("Current Age*", min_value=18, max_value=100, value=30, key="reg_age")
                with col2:
                    target_retirement_age = st.number_input("Retirement Age*", min_value=50, max_value=100, value=65, key="reg_retire")
                
                country = st.text_input("Country (Optional)", key="reg_country", placeholder="e.g., Canada")
                
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                with col1:
                    consent = st.checkbox("Anonymized data sharing", key="consent", value=False)
                with col2:
                    terms = st.checkbox("Terms & Privacy", key="terms", value=False)
                
                submit_register = st.form_submit_button("Create Free Account", type="primary", use_container_width=True)
                
                if submit_register:
                    if not new_username or not new_email or not new_password:
                        st.error("Please fill in all required fields")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(new_password) < 8:
                        st.error("Password must be at least 8 characters")
                    elif not consent:
                        st.error("Please agree to data sharing")
                    elif not terms:
                        st.error("Please agree to Terms")
                    else:
                        success, message = register_user(
                            new_username, new_email, new_password,
                            current_age, target_retirement_age,
                            country if country else None
                        )
                        
                        if success:
                            st.success(message)
                            st.info("👉 Switch to Login tab")
                        else:
                            st.error(message)
    
    with col_right:
        st.markdown("### ✨ Key Features")
        
        st.markdown("""
        <div class="feature-box">
            <h3>🎲 Monte Carlo Simulation</h3>
            <p>Run thousands of scenarios to understand the range of possible outcomes for your financial future.</p>
        </div>
        
        <div class="feature-box">
            <h3>🏠 Real Estate Planning</h3>
            <p>Model property purchases, sales, mortgages, and rental income in your projections.</p>
        </div>
        
        <div class="feature-box">
            <h3>👨‍👩‍👧 Life Events</h3>
            <p>Plan for children, career changes, international moves, and major expenses.</p>
        </div>
        
        <div class="feature-box">
            <h3>💱 Multi-Currency</h3>
            <p>Support for 15+ currencies including USD, CAD, EUR, GBP, AUD, and more.</p>
        </div>
        
        <div class="feature-box">
            <h3>📊 Export Results</h3>
            <p>Download detailed Excel spreadsheets with all your projections and data.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # How It Works Section
    st.markdown("---")
    st.markdown('<div class="how-it-works">', unsafe_allow_html=True)
    st.markdown("### 🎯 How It Works")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="step-box">
                <div class="step-number">1</div>
                <div class="step-title">Enter Your Info</div>
                <div class="step-description">Current wealth, income, expenses, and retirement goals</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="step-box">
                <div class="step-number">2</div>
                <div class="step-title">Add Life Events</div>
                <div class="step-description">Property purchases, children, career changes, moves</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="step-box">
                <div class="step-number">3</div>
                <div class="step-title">Plan Your Future</div>
                <div class="step-description">View projections, percentiles, and export results</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Testimonials
    st.markdown("---")
    st.markdown("### 💬 What Users Say")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="testimonial">
            "FinSim helped me understand Monte Carlo simulations!"
            <div class="testimonial-author">— Niall, FinSim Developer</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="testimonial">
            "Hmmm."
            <div class="testimonial-author">— Helen, Data Wizard</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #718096; padding: 2rem 0;">
            <p style="font-size: 1.1rem; font-weight: 600; color: #2d3748; margin-bottom: 1rem;">
                <strong>FinSim</strong> - Plan Your Financial Future with Confidence
            </p>
            <p style="font-size: 0.95rem; margin-bottom: 1rem;">
                <a href="#" style="color: #667eea; text-decoration: none; margin: 0 0.75rem;">About</a> • 
                <a href="#" style="color: #667eea; text-decoration: none; margin: 0 0.75rem;">Privacy</a> • 
                <a href="#" style="color: #667eea; text-decoration: none; margin: 0 0.75rem;">Terms</a> • 
                <a href="#" style="color: #667eea; text-decoration: none; margin: 0 0.75rem;">Contact</a>
            </p>
            <p style="font-size: 0.85rem; opacity: 0.8;">
                Educational tool only. Not financial advice. Consult a professional advisor.
            </p>
        </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# IMPORTANT: Page config must be set BEFORE landing page
# ==============================================================================

"""
In your wealth_simulator.py, the structure should be:

# At the very top, before anything else:
import streamlit as st

st.set_page_config(
    page_title="FinSim - Financial Planning",
    page_icon="💰",
    layout="wide",  # ✅ Force wide layout
    initial_sidebar_state="collapsed"  # ✅ Hide sidebar on landing
)

# Then your imports
from auth import ...
from landing_page import show_landing_page

# Then authentication check
if not st.session_state.get('authenticated', False):
    show_landing_page()
    st.stop()

# After login, show sidebar for the main app
st.set_page_config(layout="wide", initial_sidebar_state="expanded")
"""