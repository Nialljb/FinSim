import streamlit as st


def show_about():
    """Display the About page"""
    st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .hero-section {
        background: linear-gradient(135deg, #2B3447 0%, #2B3447 100%);
        color: white;
        padding: 3rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .content-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border-left: 4px solid #667eea;
    }
    </style>
    """, unsafe_allow_html=True)

    # Hero
    st.markdown("""
    <div class="hero-section">
        <h1>🐬 About FinSim</h1>
        <p style="font-size: 1.2rem;">Your Financial Future Planning Tool</p>
    </div>
    """, unsafe_allow_html=True)

    # Mission
    st.markdown("""
    <div class="content-section">
        <h2>📋 Our Mission</h2>
        <p style="font-size: 1.1rem;">
            FinSim (Financial Simulator) was created to understand factors affecting your financial future and make financial planning tools accessible to everyone. 
            We believe that understanding your financial future shouldn't require expensive software 
            or financial advisors for basic projections.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # What We Do
    st.markdown("""
    <div class="content-section">
        <h2>🎯 What We Do</h2>
        <p>FinSim uses <strong>Monte Carlo simulation</strong> to project thousands of possible financial 
        futures based on your current situation, goals, and planned life events. This gives you:</p>
        <ul>
            <li><strong>Realistic expectations:</strong> Not just one scenario, but a range of possibilities</li>
            <li><strong>Risk assessment:</strong> Understand probabilities of reaching your goals</li>
            <li><strong>Better planning:</strong> Model major life events and their financial impact</li>
            <li><strong>Informed decisions:</strong> Compare different financial strategies</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # Key Features
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="content-section">
            <h3>🎲 Monte Carlo Simulation</h3>
            <p>Run 1,000+ scenarios with varying market returns, inflation, and life events to see the full range of possible outcomes.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="content-section">
            <h3>🏠 Real Estate Modeling</h3>
            <p>Include property purchases, sales, mortgages, and rental income in your long-term projections.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="content-section">
            <h3>💰 Budget Builder</h3>
            <p>Track monthly expenses with expected vs actual budgeting across all major categories.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="content-section">
            <h3>👨‍👩‍👧 Life Events</h3>
            <p>Model children, career changes, relocations, and major expenses to see their long-term impact.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="content-section">
            <h3>💱 Multi-Currency Support</h3>
            <p>Support for 15+ currencies including USD, CAD, EUR, GBP, JPY, AUD, and more.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="content-section">
            <h3>📊 Export & Reports</h3>
            <p>Download professional PDF reports and detailed Excel spreadsheets with all your data.</p>
        </div>
        """, unsafe_allow_html=True)

    # Who It's For
    st.markdown("""
    <div class="content-section">
        <h2>👥 Who It's For</h2>
        <ul>
            <li><strong>Early Career Professionals:</strong> Starting to plan for retirement and major purchases</li>
            <li><strong>Growing Families:</strong> Planning for children's education and household expansion</li>
            <li><strong>Mid-Career Planners:</strong> Optimizing retirement strategies and life goals</li>
            <li><strong>Pre-Retirees:</strong> Validating retirement readiness and withdrawal strategies</li>
            <li><strong>International Households:</strong> Managing finances across multiple currencies</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # How It's Free
    st.markdown("""
    <div class="content-section">
        <h2>💸 How is FinSim Free?</h2>
        <p>FinSim is developed and maintained as a personal project. We keep costs low by:</p>
        <ul>
            <li>Using efficient cloud infrastructure</li>
            <li>Collecting anonymized usage data for research (with your consent)</li>
            <li>Rate limiting to 10 simulations per month for free users</li>
            <li>Keeping the codebase simple and maintainable</li>
            <li>No ads. No selling personal data. No hidden fees.</li>
        </ul>
        <p><strong>Hosting does cost money, so do your part by supporting the project if you can.</strong></p>
    </div>
    """, unsafe_allow_html=True)

    # Important Disclaimer
    st.markdown("""
    <div class="content-section" style="border-left-color: #f44336;">
        <h2>⚠️ Important Disclaimer</h2>
        <p><strong>FinSim is an educational tool only.</strong> It is NOT financial advice. Always consult 
        with qualified financial advisors before making major financial decisions.</p>
        <p>Key limitations:</p>
        <ul>
            <li>Simulations are based on historical market behavior (past ≠ future)</li>
            <li>Cannot account for all possible life events and emergencies</li>
            <li>Tax implications are simplified or not included</li>
            <li>Does not replace professional financial planning</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # The Story
    st.markdown("""
    <div class="content-section">
        <h2>📖 The Story</h2>
        <p>FinSim started as a personal project to understand Monte Carlo simulations and their 
        application to retirement planning. What began as a simple Python script evolved into 
        a comprehensive financial planning tool.</p>
        <p>Built with Python, Streamlit, and a lot of coffee ☕</p>
    </div>
    """, unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    
    # Back to home button
    if st.button("← Back to Home", key="about_back", use_container_width=True):
        st.query_params.clear()
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Footer links as buttons
    footer_col1, footer_col2, footer_col3 = st.columns(3)
    with footer_col1:
        if st.button("Privacy Policy", key="about_to_privacy", use_container_width=True):
            st.query_params['page'] = 'privacy'
            st.rerun()
    with footer_col2:
        if st.button("Terms of Service", key="about_to_terms", use_container_width=True):
            st.query_params['page'] = 'terms'
            st.rerun()
    with footer_col3:
        if st.button("Contact Us", key="about_to_contact", use_container_width=True):
            st.query_params['page'] = 'contact'
            st.rerun()
