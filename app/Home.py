"""
FinSim - Financial Simulation Toolkit
Main entry point for the Streamlit application

This is the new modular entry point following best practices.
Uses the new directory structure with proper imports.
"""

import streamlit as st

# ============================================================================
# Page Configuration (must be first Streamlit command)
# ============================================================================

st.set_page_config(
    page_title="FinSTK - Financial Simulation Toolkit",
    page_icon="assets/favicon.png",
    layout="wide",
    menu_items={
        'Get Help': 'https://www.finstk.com/docs',
        'Report a bug': 'mailto:support@finstk.com',
        'About': """
        # FinSTK - Financial Simulation Toolkit
        
        Plan your financial future with Monte Carlo simulations, retirement planning, 
        real estate modeling, and life event forecasting.
        
        **Version 2.0** - Refactored Architecture
        
        For Educational Purposes Only - Not Financial Advice
        """
    },
    initial_sidebar_state="expanded"
)

# ============================================================================
# Imports (after page config)
# ============================================================================

import sys
import os

# Add parent directory to path to import from root modules
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import from root-level .py files (not the auth/ directory)
# During transition, we still use the original monolithic files
import auth as auth_module
import database as database_module
import landing_page as landing_page_module
import currency_manager as currency_module

# Extract needed functions
initialize_session_state = auth_module.initialize_session_state
show_user_header = auth_module.show_user_header
init_db = database_module.init_db
show_landing_page = landing_page_module.show_landing_page
initialize_currency_system = currency_module.initialize_currency_system

# ============================================================================
# Database Initialization
# ============================================================================

try:
    init_db()
except Exception as e:
    st.error(f"Database initialization failed: {e}")

# ============================================================================
# Session State Initialization
# ============================================================================

initialize_session_state()
initialize_currency_system()

# ============================================================================
# Authentication Check
# ============================================================================

if not st.session_state.get('authenticated', False):
    show_landing_page()
    st.stop()

# ============================================================================
# Main Application (Authenticated Users)
# ============================================================================

# Show user header with logout button
show_user_header()

# Global CSS for better UI
st.markdown("""
    <style>
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
    }
    
    /* Main container padding */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Success/info box styling */
    .stAlert {
        border-radius: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# Home Page Content
# ============================================================================

st.title("🎯 FinSTK - Financial Simulation Toolkit")

st.markdown("""
Welcome to your personal financial planning toolkit! Choose a tool from the sidebar to get started.
""")

# Feature cards
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 💰 Wealth Simulator
    Run Monte Carlo simulations to project your financial future with:
    - Probability-based wealth projections
    - Property and mortgage modeling  
    - Life event planning
    - Multiple currency support
    
    📊 **Navigate to:** Wealth Simulator page
    """)
    
    st.markdown("""
    ### 📊 Budget Builder
    Track and plan your monthly budget with:
    - Detailed expense categories
    - Monthly tracking
    - Historical comparisons
    - Budget vs. actual analysis
    
    💰 **Navigate to:** Budget Builder page
    """)

with col2:
    st.markdown("""
    ### 🏦 Pension Planner
    Calculate your UK pension entitlements:
    - State Pension projections
    - USS (Universities Superannuation)
    - SIPP (Self-Invested Personal Pension)
    - Combined retirement income
    
    🔮 **Navigate to:** Pension Planner page
    """)
    
    st.markdown("""
    ### 📈 Analytics
    View your financial data and statistics:
    - Simulation history
    - Budget trends
    - Progress tracking
    - Export capabilities
    
    📉 **Navigate to:** Analytics page
    """)

# ============================================================================
# Getting Started Guide
# ============================================================================

with st.expander("📖 Getting Started"):
    st.markdown("""
    ### Welcome to FinSTK!
    
    Here's how to get the most out of your financial planning toolkit:
    
    #### 1. Start with the Wealth Simulator
    - Input your current financial situation
    - Set your goals and timeline
    - Run simulations to see probable outcomes
    - Save scenarios for comparison
    
    #### 2. Build Your Budget
    - Track monthly income and expenses
    - Set category budgets
    - Monitor spending patterns
    - Identify savings opportunities
    
    #### 3. Plan Your Pension
    - Calculate State Pension entitlement
    - Model workplace pensions (USS)
    - Plan private pensions (SIPP)
    - Project total retirement income
    
    #### 4. Track Progress
    - Review saved simulations
    - Compare different scenarios
    - Export results for records
    - Adjust plans as needed
    
    #### Tips for Best Results
    - 📊 Run multiple scenarios (best/worst/expected)
    - 💾 Save important simulations for future reference
    - 🔄 Update regularly as circumstances change
    - 📧 Export results before major financial decisions
    
    #### Need Help?
    - Check the documentation in each tool
    - Contact support: support@finstk.com
    - Report issues via the feedback button
    """)

# ============================================================================
# User Stats Summary
# ============================================================================

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    sim_count = st.session_state.get('simulation_count', 0)
    st.metric("Simulations Run", sim_count)

with col2:
    export_count = st.session_state.get('export_count', 0)
    st.metric("Exports Created", export_count)

with col3:
    st.metric("Account Age", f"{st.session_state.get('current_age', 'N/A')} years")

with col4:
    retirement_age = st.session_state.get('target_retirement_age', 'N/A')
    st.metric("Target Retirement", f"{retirement_age} years")

# ============================================================================
# Footer
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8rem;'>
    <p>FinSTK - Financial Simulation Toolkit | Version 2.0</p>
    <p>For educational purposes only - not financial advice</p>
    <p>© 2025 FinSTK. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
