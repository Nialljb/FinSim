"""
Professional Landing Page for FinSim with integrated static pages
"""

import streamlit as st
from authentication.auth import initialize_session_state, login_user, register_user, logout, request_password_reset


def show_about_page():
    """About page content"""
    from static_pages.about import show_about
    show_about()


def show_privacy_page():
    """Privacy policy page content"""
    from static_pages.privacy import show_privacy
    show_privacy()


def show_terms_page():
    """Terms of service page content"""
    from static_pages.terms import show_terms
    show_terms()


def show_contact_page():
    """Contact page content"""
    from static_pages.contact import show_contact
    show_contact()


def show_docs_page():
    """Documentation page content"""
    from app.static.docs import show_docs
    show_docs()


def show_landing_page():
    """
    Professional landing page with login and routing
    Combines marketing + authentication + static pages
    """
    initialize_session_state()
    
    # If user is already authenticated, redirect to main app
    if st.session_state.get('authenticated', False):
        st.info("You are already logged in. Redirecting to app...")
        import time
        time.sleep(1)
        st.rerun()
        return
    
    # Check for email verification FIRST (before other routing)
    try:
        query_params = st.query_params
        if 'verify' in query_params:
            # Handle email verification on landing page
            from auth import show_login_page
            show_login_page()
            return
    except:
        pass
    
    # Check for query parameters to route to different pages
    try:
        query_params = st.query_params
        # In Streamlit 1.51+, query_params is a dict-like object
        if hasattr(query_params, 'get_all'):
            # Newer API
            page_list = query_params.get_all('page')
            page = page_list[0] if page_list else None
        else:
            # Fallback
            page = query_params.get('page', None)
    except:
        page = None
    
    if page == 'about':
        show_about_page()
        return
    elif page == 'privacy':
        show_privacy_page()
        return
    elif page == 'terms':
        show_terms_page()
        return
    elif page == 'contact':
        show_contact_page()
        return
    elif page == 'docs':
        show_docs_page()
        return
    
    # Main landing page content
    # Custom CSS for landing page
    st.markdown("""
        <style>
        /* Main container */
        .main {
            padding: 0rem 1rem;
        }
        
        /* Hero section */
        .hero {
            text-align: center;
            padding: 3rem 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        
        .hero h1 {
            font-size: 3rem;
            margin-bottom: 1rem;
            font-weight: 700;
        }
        
        .hero p {
            font-size: 1.3rem;
            margin-bottom: 2rem;
            opacity: 0.95;
        }
        
        /* Feature boxes */
        .feature-box {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            border-left: 4px solid #667eea;
        }
        
        .feature-box h3 {
            color: #667eea;
            margin-bottom: 0.5rem;
        }
        
        /* Stats */
        .stat-container {
            display: flex;
            justify-content: space-around;
            margin: 2rem 0;
            flex-wrap: wrap;
        }
        
        .stat-box {
            text-align: center;
            padding: 1rem;
            min-width: 150px;
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9rem;
        }
        
        /* CTA buttons */
        .stButton > button {
            width: 100%;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
            font-weight: 600;
        }
        
        /* Testimonial */
        .testimonial {
            background: #fff;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            margin: 1rem 0;
            font-style: italic;
        }
        
        .testimonial-author {
            font-weight: bold;
            color: #667eea;
            margin-top: 0.5rem;
            font-style: normal;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Hero Section
    st.markdown("""
        <div class="hero">
            <h1>🐬 FinSTK</h1>
            <p>Plan Your Financial Future with The Financial Simulation Toolkit</p>
            <p style="font-size: 1rem; opacity: 0.9;">
                Monte Carlo simulations • Retirement planning • Real estate modeling • Life event forecasting
            </p>
            <p style="font-size: 1rem; opacity: 0.9;">
                *BETA Version - For Educational Purposes Only  • Some Features May Be Incomplete Or Subject To Change*
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Social Proof Stats
    st.markdown("""
        <div class="stat-container">
            <div class="stat-box">
                <div class="stat-number">1000+</div>
                <div class="stat-label">Simulations Run</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">10</div>
                <div class="stat-label">Free per Month</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">30+</div>
                <div class="stat-label">Year Projections</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Login/Register Section
    st.markdown("---")
    
    # Quick info links
    link_col1, link_col2 = st.columns(2)
    with link_col1:
        if st.button("📚 Documentation & User Guide", key="nav_docs", use_container_width=True, type="secondary"):
            st.query_params['page'] = 'docs'
            st.rerun()
    with link_col2:
        if st.button("ℹ️ About FinSim", key="nav_about", use_container_width=True, type="secondary"):
            st.query_params['page'] = 'about'
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Two column layout for login and features
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("### 🔐 Get Started")
        
        tab1, tab2, tab3 = st.tabs(["Login", "Create Account", "Forgot Password"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
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
            
            st.caption("Forgot your password? Use the 'Forgot Password' tab or contact niall@finstk.com")
        
        with tab2:
            with st.form("register_form"):
                st.markdown("**Account Information**")
                new_username = st.text_input("Username*", key="reg_username")
                new_email = st.text_input("Email*", key="reg_email")
                new_password = st.text_input("Password*", type="password", key="reg_password")
                confirm_password = st.text_input("Confirm Password*", type="password", key="reg_confirm")
                
                st.markdown("**Your Planning Profile**")
                col1, col2 = st.columns(2)
                with col1:
                    current_age = st.number_input("Current Age*", min_value=18, max_value=100, value=30, key="reg_age")
                with col2:
                    target_retirement_age = st.number_input("Retirement Age*", min_value=50, max_value=100, value=65, key="reg_retire")
                
                country = st.text_input("Country (Optional)", key="reg_country")
                
                st.markdown("---")
                
                # Note about legal docs
                st.markdown("""
                    <p style="font-size: 0.85rem; text-align: center; color: #666;">
                        By creating an account, you agree to our Terms and Privacy Policy<br>
                        (Use footer buttons to view these documents)
                    </p>
                """, unsafe_allow_html=True)
                
                consent = st.checkbox(
                    "I agree to share anonymized data for research (helps keep FinSim free)",
                    key="consent"
                )
                
                terms = st.checkbox("I agree to Terms of Service and Privacy Policy", key="terms")
                
                submit_register = st.form_submit_button("Create Free Account", type="primary", use_container_width=True)
                
                if submit_register:
                    if not new_username or not new_email or not new_password:
                        st.error("Please fill in all required fields")
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
                            new_username, new_email, new_password,
                            current_age, target_retirement_age,
                            country if country else None
                        )
                        
                        if success:
                            st.success(message)
                            st.info("👉 Switch to Login tab to sign in")
                        else:
                            st.error(message)
        
        with tab3:
            st.markdown("### 🔑 Password Recovery")
            st.markdown("Enter your email address to recover your username. For password resets, contact niall@finstk.com")
            
            with st.form("password_recovery_form"):
                recovery_email = st.text_input("Email Address", key="recovery_email", placeholder="your.email@example.com")
                submit_recovery = st.form_submit_button("Recover Username", type="primary", use_container_width=True)
                
                if submit_recovery:
                    if not recovery_email:
                        st.error("Please enter your email address")
                    else:
                        success, result = request_password_reset(recovery_email)
                        if success:
                            if "Account found" in result:
                                st.success(result)
                                st.info("If you've forgotten your password, please contact niall@finstk.com with your username.")
                            else:
                                st.info(result)
                        else:
                            st.error(result)
            
            st.markdown("---")
            st.markdown("**Need help?**")
            st.markdown("Contact us at **niall@finstk.com** for password resets and account assistance.")
    
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
            <p>Support for 15+ currencies including USD, CAD, EUR, GBP, and more.</p>
        </div>
        
        <div class="feature-box">
            <h3>📊 Export Results</h3>
            <p>Download detailed Excel spreadsheets and professional PDF reports.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # How It Works Section
    st.markdown("---")
    st.markdown("### 🎯 How It Works")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 1️⃣ Enter Your Info")
        st.write("Current wealth, income, expenses, and goals")
    
    with col2:
        st.markdown("#### 2️⃣ Add Life Events")
        st.write("Property purchases, children, career changes")
    
    with col3:
        st.markdown("#### 3️⃣ Plan Your Financial Future")
        st.write("View projections, percentiles, and export results")
    
    # Testimonials
    st.markdown("---")
    st.markdown("### 💬 What Users Say")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="testimonial">
            "FinSTK helped me understand Monte Carlo simulations"
            <div class="testimonial-author">— Niall, FinSTK Developer</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="testimonial">
            "An amazing tool for financial planning!"
            <div class="testimonial-author">— Helen, Data Scientist</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #666; padding: 2rem 0;">
            <p><strong>FinSim</strong> - Plan Your Financial Future with Confidence</p>
            <p style="font-size: 0.9rem; margin: 1rem 0;">
                Educational tool only. Not financial advice. Consult a professional advisor.
            </p>
            <p style="font-size: 0.9rem; margin-top: 1.5rem;">
                <a href="?page=about" style="color: #667eea; text-decoration: none; margin: 0 1rem;">About</a>
                <a href="?page=privacy" style="color: #667eea; text-decoration: none; margin: 0 1rem;">Privacy</a>
                <a href="?page=terms" style="color: #667eea; text-decoration: none; margin: 0 1rem;">Terms</a>
                <a href="?page=contact" style="color: #667eea; text-decoration: none; margin: 0 1rem;">Contact</a>
            </p>
        </div>
    """, unsafe_allow_html=True)


# Run the app when executed directly
if __name__ == "__main__":
    show_landing_page()



