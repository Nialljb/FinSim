"""
FinSim - Wealth Simulator with Authentication
Integration guide for adding authentication to wealth_simulator.py

This file shows the key changes needed to integrate authentication.
Merge these changes into your main wealth_simulator.py file.
"""

import streamlit as st
from auth import initialize_session_state, show_login_page, show_user_header, check_simulation_limit, increment_simulation_count, increment_export_count
from data_tracking import save_simulation
from database import init_db

# STEP 1: Add these imports at the top of wealth_simulator.py
# (Already shown above)

# STEP 2: Initialize database on first run
# Add this near the top of your file, before the main app code
try:
    init_db()
except:
    pass  # Database already exists

# STEP 3: Initialize session state
initialize_session_state()

# STEP 4: Check authentication - wrap your entire app
if not st.session_state.get('authenticated', False):
    # Show login/register page
    show_login_page()
    st.stop()  # Don't run the rest of the app

# STEP 5: Show user header
show_user_header()

# STEP 6: Check simulation limits BEFORE running simulation
# Add this right before your "Run Simulation" button

# In your sidebar, before the run button:
"""
# Check usage limits
can_simulate, remaining, message = check_simulation_limit(st.session_state.user_id, limit=5)

if not can_simulate:
    st.sidebar.error(message)
    st.sidebar.info("🎉 Upgrade to Pro for unlimited simulations!")
else:
    st.sidebar.success(message)
"""

# STEP 7: Modify the "Run Simulation" button section
"""
# Run simulation button
if st.sidebar.button("Run Simulation", type="primary"):
    # Check limit
    can_simulate, remaining, message = check_simulation_limit(st.session_state.user_id)
    
    if not can_simulate:
        st.error(message)
        st.info("Want unlimited simulations? Upgrade to Pro for $9.99/month")
    else:
        with st.spinner("Running Monte Carlo simulation..."):
            results = run_monte_carlo(...)
            
            # Store in session state
            st.session_state['results'] = results
            st.session_state['sim_complete'] = True
            
            # INCREMENT USAGE COUNT
            increment_simulation_count(st.session_state.user_id)
            
            # SAVE SIMULATION DATA
            simulation_params = {
                'currency': selected_currency,
                'initial_liquid_wealth': initial_liquid_wealth,
                'initial_property_value': initial_property_value,
                'initial_mortgage': initial_mortgage,
                'gross_annual_income': gross_annual_income,
                'monthly_expenses': monthly_expenses,
                'events': events,
                'expected_return': expected_return,
                'return_volatility': return_volatility,
                'expected_inflation': expected_inflation,
                # ... add all other parameters
            }
            
            save_simulation(
                st.session_state.user_id,
                simulation_params,
                results
            )
"""

# STEP 8: Track exports
"""
# In your export buttons, after generating the file:

# For Excel export:
increment_export_count(st.session_state.user_id)

# For PDF export:
increment_export_count(st.session_state.user_id)
"""

# STEP 9: Optional - Show usage in sidebar
"""
# Add this in your sidebar somewhere visible:
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Your Usage")

stats = get_user_usage_stats(st.session_state.user_id)
st.sidebar.write(f"Simulations this month: {stats.simulations_this_month}/5")
st.sidebar.write(f"Exports: {stats.exports_this_month}")

if stats.simulations_this_month >= 4:
    st.sidebar.warning("You're running low on simulations!")
    st.sidebar.button("Upgrade to Pro")
"""

# FULL INTEGRATION EXAMPLE:
# Here's how your main wealth_simulator.py structure should look:

"""
import streamlit as st
import numpy as np
import pandas as pd
# ... other imports

# NEW IMPORTS
from auth import initialize_session_state, show_login_page, show_user_header, check_simulation_limit, increment_simulation_count
from data_tracking import save_simulation
from database import init_db

# Initialize database
try:
    init_db()
except:
    pass

# Set page config
st.set_page_config(page_title="FinSim - Wealth Path Simulator", layout="wide")

# Initialize authentication
initialize_session_state()

# Check if user is logged in
if not st.session_state.get('authenticated', False):
    show_login_page()
    st.stop()

# Show user info header
show_user_header()

# Currency configuration
CURRENCIES = { ... }

# Helper functions
def format_currency(...): ...
def export_to_excel(...): ...
def export_to_pdf(...): ...

# Title
st.title("30-Year Wealth Path Simulator")
st.markdown("Interactive Monte Carlo simulation to explore your financial future")

# Sidebar - Currency Selection
st.sidebar.header("⚙️ Settings")
selected_currency = st.sidebar.selectbox(...)

# All your input parameters
initial_liquid_wealth = st.sidebar.number_input(...)
# ... etc

# Check usage before simulation
can_simulate, remaining, message = check_simulation_limit(st.session_state.user_id, limit=5)

if not can_simulate:
    st.sidebar.error(message)
    st.sidebar.info("🎉 Want unlimited simulations? Contact us about Pro!")
else:
    st.sidebar.success(message)

# Run simulation button
if st.sidebar.button("Run Simulation", type="primary", disabled=not can_simulate):
    with st.spinner("Running Monte Carlo simulation..."):
        results = run_monte_carlo(...)
        
        st.session_state['results'] = results
        st.session_state['sim_complete'] = True
        
        # Track usage
        increment_simulation_count(st.session_state.user_id)
        
        # Save simulation
        simulation_params = {
            'name': f"Simulation {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            'currency': selected_currency,
            'initial_liquid_wealth': initial_liquid_wealth,
            'initial_property_value': initial_property_value,
            'initial_mortgage': initial_mortgage,
            'gross_annual_income': gross_annual_income,
            'monthly_expenses': monthly_expenses,
            'events': events,
            'expected_return': expected_return,
            'return_volatility': return_volatility,
            'expected_inflation': expected_inflation,
            'salary_inflation': salary_inflation,
            'property_appreciation': property_appreciation,
            'mortgage_interest_rate': mortgage_interest_rate,
        }
        
        save_simulation(st.session_state.user_id, simulation_params, results)

# Display results
if st.session_state.get('sim_complete', False):
    results = st.session_state['results']
    
    # ... all your visualization code
    
    # In export buttons
    with col_exp1:
        excel_file = export_to_excel(...)
        st.download_button(...)
        # Track export
        increment_export_count(st.session_state.user_id)
    
    with col_exp2:
        pdf_file = export_to_pdf(...)
        st.download_button(...)
        # Track export
        increment_export_count(st.session_state.user_id)
"""

print("Integration guide created!")
print("Follow the steps above to add authentication to your wealth_simulator.py")