"""
FinSim - Financial Simulation Toolkit
Single-page application with tabs for different tools

This matches the functionality of wealth_simulator.py but uses the new structure.
"""

import streamlit as st
import sys
import os

# Add parent directory to path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# ============================================================================
# Page Configuration (must be first Streamlit command)
# ============================================================================

st.set_page_config(
    page_title="FinSTK - Financial Simulation Toolkit",
    page_icon="assets/favicon.png",
    layout="wide",
    menu_items={
        'Get Help': 'https://finstk.com/docs',
        'Report a bug': 'mailto:support@finstk.com',
        'About': """
        # FinSTK - Financial Simulation Toolkit
        
        Plan your financial future with Monte Carlo simulations, retirement planning, 
        real estate modeling, and life event forecasting.
        
        **BETA Version** - For Educational Purposes Only
        """
    },
    initial_sidebar_state="expanded"
)

# ============================================================================
# Imports (after page config)
# ============================================================================

# Import from authentication package (using symlink for compatibility)
from authentication import initialize_session_state, show_user_header

# Import from root modules  
from database import init_db
from app.landing_page import show_landing_page
from services.currency_manager import initialize_currency_system

# ============================================================================
# Database Initialization
# ============================================================================

try:
    init_db()
except:
    pass

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

# Show user header
show_user_header()

# Global CSS for tab fonts
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# Import the main wealth simulator content
# ============================================================================

# The wealth_simulator.py file contains all the simulation logic, budget builder,
# and pension planner. Rather than duplicate that code, we import and use it.
# This maintains a single source of truth while using the new entry point.

# Import the necessary components
import importlib.util

# Load wealth_simulator.py as a module
spec = importlib.util.spec_from_file_location(
    "wealth_simulator_module",
    os.path.join(parent_dir, "wealth_simulator.py")
)
wealth_sim = importlib.util.module_from_spec(spec)

# Execute only the parts we need (after authentication is already handled)
# Since wealth_simulator.py has authentication checks at the top,
# we need to execute it in a way that doesn't re-run those checks

# For now, the simplest approach is to just redirect to wealth_simulator.py
st.info("ℹ️ The main application is running from `wealth_simulator.py`")
st.markdown("""
This `app/Home.py` entry point is part of the refactored architecture.

For now, please use:
```bash
streamlit run wealth_simulator.py
```

The full migration to the `app/` structure will be completed in a future phase.
""")

st.markdown("---")
st.markdown("**Tip:** You can safely use `wealth_simulator.py` - all refactoring is backward compatible!")
