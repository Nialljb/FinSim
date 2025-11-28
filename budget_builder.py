"""
Budget Builder - WORKING VERSION
All issues fixed: sidebar, template loading, value persistence
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import json
from currency_converter import convert_currency
from currency_manager import format_currency
from database import save_budget, get_user_budgets, load_budget, delete_budget

# Budget templates (in Euros)
BUDGET_TEMPLATES = {
    'EUR': {
        '20k-30k': {
            'Housing': 600,
            'Utilities': 100,
            'Groceries': 250,
            'Transportation': 100,
            'Healthcare': 50,
            'Entertainment': 80,
            'Dining Out': 100,
            'Personal Care': 40,
            'Clothing': 60,
            'Insurance': 60,
            'Other': 80
        },
        '30k-40k': {
            'Housing': 900,
            'Utilities': 150,
            'Groceries': 350,
            'Transportation': 150,
            'Healthcare': 80,
            'Entertainment': 120,
            'Dining Out': 150,
            'Personal Care': 60,
            'Clothing': 90,
            'Insurance': 90,
            'Other': 100
        },
        '40k-50k': {
            'Housing': 1200,
            'Utilities': 180,
            'Groceries': 450,
            'Transportation': 200,
            'Healthcare': 100,
            'Entertainment': 180,
            'Dining Out': 250,
            'Personal Care': 80,
            'Clothing': 120,
            'Insurance': 120,
            'Other': 150
        },
        '50k-60k': {
            'Housing': 1500,
            'Utilities': 220,
            'Groceries': 550,
            'Transportation': 250,
            'Healthcare': 120,
            'Entertainment': 250,
            'Dining Out': 350,
            'Personal Care': 100,
            'Clothing': 150,
            'Insurance': 150,
            'Other': 200
        },
        '60k+': {
            'Housing': 2000,
            'Utilities': 280,
            'Groceries': 650,
            'Transportation': 350,
            'Healthcare': 150,
            'Entertainment': 350,
            'Dining Out': 500,
            'Personal Care': 150,
            'Clothing': 250,
            'Insurance': 200,
            'Other': 300
        }
    }
}

PAY_BRACKETS = {
    '20k-30k': '€20,000 - €30,000',
    '30k-40k': '€30,000 - €40,000',
    '40k-50k': '€40,000 - €50,000',
    '50k-60k': '€50,000 - €60,000',
    '60k+': '€60,000+'
}

LIFE_EVENT_IMPACTS = {
    'property_purchase': {
        'description': 'Property Purchase',
        'simulation_type': 'property_purchase',
        'needs_details': True,
        'changes': {'Utilities': 100, 'Maintenance': 300, 'Insurance': 100},
        'one_time_costs': 0,
        'duration': 30
    },
    'property_sale': {
        'description': 'Property Sale',
        'simulation_type': 'property_sale',
        'needs_details': True,
        'changes': {'Utilities': -100, 'Maintenance': -300, 'Insurance': -100},
        'one_time_costs': 0,
        'duration': None
    },
    'one_time_expense': {
        'description': 'One-Time Expense',
        'simulation_type': 'one_time_expense',
        'needs_details': True,
        'changes': {},
        'one_time_costs': 0,
        'duration': None
    },
    'expense_change': {
        'description': 'Monthly Expense Change',
        'simulation_type': 'expense_change',
        'needs_details': True,
        'changes': {},
        'one_time_costs': 0,
        'duration': None
    },
    'rental_income': {
        'description': 'Rental Income',
        'simulation_type': 'rental_income',
        'needs_details': True,
        'changes': {},
        'one_time_costs': 0,
        'duration': None
    },
    'windfall': {
        'description': 'Windfall/Inheritance',
        'simulation_type': 'windfall',
        'needs_details': True,
        'changes': {},
        'one_time_costs': 0,
        'duration': None
    },
    'first_child': {
        'description': 'First Child',
        'simulation_type': 'expense_change',
        'needs_details': False,
        'changes': {'Childcare': 1200, 'Groceries': 200, 'Healthcare': 100, 'Utilities': 50, 'Entertainment': -100},
        'one_time_costs': 5000,
        'duration': 18
    },
    'second_child': {
        'description': 'Second Child',
        'simulation_type': 'expense_change',
        'needs_details': False,
        'changes': {'Childcare': 800, 'Groceries': 150, 'Healthcare': 80, 'Utilities': 30, 'Housing': 200},
        'one_time_costs': 3000,
        'duration': 18
    }
}


def show_budget_builder():
    """Main budget builder interface"""
    
    st.title("💰 Budget Builder")
    st.markdown("Build detailed monthly budgets and plan life events")
    
    # Save/Load Budget Controls
    if st.session_state.get('authenticated', False):
        with st.expander("💾 Save / Load Budgets", expanded=False):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("📥 Load Budget")
                
                # Get user's saved budgets
                user_budgets = get_user_budgets(st.session_state.user_id, limit=20)
                
                if user_budgets:
                    budget_options = {f"{budget.name} ({budget.created_at.strftime('%Y-%m-%d %H:%M')})": budget.id for budget in user_budgets}
                    
                    selected_budget_name = st.selectbox(
                        "Select a saved budget",
                        options=[""] + list(budget_options.keys()),
                        key="load_budget_selector"
                    )
                    
                    col_load, col_delete = st.columns([1, 1])
                    
                    with col_load:
                        if st.button("Load", type="primary", disabled=not selected_budget_name, use_container_width=True, key="load_budget_btn"):
                            if selected_budget_name:
                                budget_id = budget_options[selected_budget_name]
                                success, data = load_budget(st.session_state.user_id, budget_id)
                                
                                if success:
                                    # Get current currency
                                    current_currency = st.session_state.get('selected_currency', 'EUR')
                                    saved_currency = data.get('currency', 'EUR')
                                    
                                    # Restore budget data to session state
                                    st.session_state.bb_now = data['budget_now']
                                    st.session_state.bb_1yr = data['budget_1yr']
                                    st.session_state.bb_5yr = data['budget_5yr']
                                    st.session_state.bb_events = data['life_events']
                                    
                                    # Increment counter to force widget refresh with loaded values
                                    if 'bb_counter' not in st.session_state:
                                        st.session_state.bb_counter = 0
                                    st.session_state.bb_counter += 1
                                    
                                    # Update the last currency tracker to match saved currency
                                    st.session_state.bb_last_currency = saved_currency
                                    
                                    success_msg = f"✅ Loaded: {data['name']}"
                                    if saved_currency != current_currency:
                                        st.warning(f"⚠️ Budget was saved in {saved_currency}, but current currency is {current_currency}. Values displayed in current currency.")
                                    else:
                                        st.success(success_msg)
                                    
                                    st.rerun()
                                else:
                                    st.error(f"❌ {data}")
                    
                    with col_delete:
                        if st.button("Delete", type="secondary", disabled=not selected_budget_name, use_container_width=True, key="delete_budget_btn"):
                            if selected_budget_name:
                                budget_id = budget_options[selected_budget_name]
                                success, message = delete_budget(st.session_state.user_id, budget_id)
                                if success:
                                    st.success(f"✅ {message}")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {message}")
                else:
                    st.info("No saved budgets yet. Create a budget and save it!")
            
            with col2:
                st.subheader("💾 Save Current Budget")
                
                # Check if there's a budget to save
                has_budget = (st.session_state.get('bb_now') or 
                             st.session_state.get('bb_1yr') or 
                             st.session_state.get('bb_5yr'))
                
                if has_budget:
                    save_budget_name = st.text_input(
                        "Budget Name",
                        value=f"Budget {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                        key="save_budget_name"
                    )
                    
                    save_budget_desc = st.text_area(
                        "Description (optional)",
                        key="save_budget_desc",
                        height=60
                    )
                    
                    if st.button("Save Budget", type="primary", use_container_width=True, key="save_budget_btn"):
                        # Get current currency
                        current_currency = st.session_state.get('selected_currency', 'EUR')
                        
                        success, result = save_budget(
                            st.session_state.user_id,
                            save_budget_name,
                            st.session_state.get('bb_now', {}),
                            st.session_state.get('bb_1yr', {}),
                            st.session_state.get('bb_5yr', {}),
                            st.session_state.get('bb_events', []),
                            save_budget_desc if save_budget_desc else None,
                            current_currency  # Pass the currency
                        )
                        
                        if success:
                            st.success(f"✅ Saved as: {save_budget_name} ({current_currency})")
                        else:
                            st.error(f"❌ Error: {result}")
                else:
                    st.info("Create a budget first to save it")
    
    # Get currency from session state (set by simulation tab)
    currency_code = st.session_state.get('selected_currency', 'EUR')
    
    # Track currency changes for auto-refresh
    if 'bb_last_currency' not in st.session_state:
        st.session_state.bb_last_currency = currency_code
    
    # If currency changed, clear budget state and rerun
    if st.session_state.bb_last_currency != currency_code:
        old_currency = st.session_state.bb_last_currency
        
        # Clear all budget values to prevent semantic currency flip
        st.session_state.bb_now = {}
        st.session_state.bb_1yr = {}
        st.session_state.bb_5yr = {}
        st.session_state.bb_events = []
        
        # Update currency tracker
        st.session_state.bb_last_currency = currency_code
        
        # Inform user
        st.warning(f"💱 Currency changed from {old_currency} to {currency_code}. Budget values have been cleared.")
        st.rerun()
    
    # Define currency symbols
    CURRENCY_SYMBOLS = {
        'EUR': '€',
        'GBP': '£',
        'USD': '$',
        'CAD': 'C$',
        'AUD': 'A$',
        'NZD': 'NZ$',
        'CHF': 'CHF',
        'SEK': 'kr',
        'NOK': 'kr',
        'DKK': 'kr',
        'JPY': '¥',
        'CNY': '¥',
        'INR': '₹',
        'SGD': 'S$',
        'HKD': 'HK$'
    }
    
    currency_symbol = CURRENCY_SYMBOLS.get(currency_code, '€')
    
    # Dynamic pay brackets based on currency
    PAY_BRACKETS_DISPLAY = {
        '20k-30k': f'{currency_symbol}20,000 - {currency_symbol}30,000',
        '30k-40k': f'{currency_symbol}30,000 - {currency_symbol}40,000',
        '40k-50k': f'{currency_symbol}40,000 - {currency_symbol}50,000',
        '50k-60k': f'{currency_symbol}50,000 - {currency_symbol}60,000',
        '60k+': f'{currency_symbol}60,000+'
    }
    
    # Show current currency
    st.info(f"💱 Using currency: **{currency_code}** ({currency_symbol}). Change in Simulation tab sidebar.")
    
    # Debug: Show what's in session state
    with st.expander("🔍 Debug - Currency Info"):
        st.write(f"Session state currency: {st.session_state.get('selected_currency', 'Not set')}")
        st.write(f"Local currency_code: {currency_code}")
        st.write(f"Local currency_symbol: {currency_symbol}")
        st.write(f"Test format_currency(1000, '{currency_code}'): {format_currency(1000, currency_code)}")
    
    # Initialize session state
    if 'bb_now' not in st.session_state:
        st.session_state.bb_now = {}
    if 'bb_1yr' not in st.session_state:
        st.session_state.bb_1yr = {}
    if 'bb_5yr' not in st.session_state:
        st.session_state.bb_5yr = {}
    if 'bb_events' not in st.session_state:
        st.session_state.bb_events = []
    if 'bb_counter' not in st.session_state:
        st.session_state.bb_counter = 0
    
    # Template selection
    st.subheader("🎯 Quick Start with Template")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        pay_bracket = st.selectbox(
            "Annual Pay Bracket",
            options=list(PAY_BRACKETS_DISPLAY.keys()),
            format_func=lambda x: PAY_BRACKETS_DISPLAY[x],
            key="bb_pay_bracket"
        )
    
    with col2:
        if st.button("📋 Load Template", use_container_width=True, key="bb_load_btn"):
            # Get EUR template
            template = BUDGET_TEMPLATES['EUR'][pay_bracket]
            
            # Convert template values to selected currency if not EUR
            if currency_code != 'EUR':
                converted_template = {}
                for category, amount in template.items():
                    try:
                        # Convert from EUR to selected currency
                        converted_amount = convert_currency(amount, 'EUR', currency_code)
                        # Round to nearest integer for cleaner display
                        converted_template[category] = round(converted_amount)
                    except (ValueError, KeyError, TypeError) as e:
                        st.warning(f"Error converting {category}: {e}")
                        converted_template[category] = amount
                
                st.session_state.bb_now = converted_template
                st.session_state.bb_1yr = dict(converted_template)
                st.session_state.bb_5yr = dict(converted_template)
                st.success(f"✅ Template loaded and converted to {currency_code}!")
            else:
                # EUR - use template as-is
                st.session_state.bb_now = dict(template)
                st.session_state.bb_1yr = dict(template)
                st.session_state.bb_5yr = dict(template)
                st.success("✅ Template loaded!")
            
            st.session_state.bb_counter += 1  # Force widget refresh
            st.rerun()
    
    with col3:
        if st.button("🗑️ Clear All", use_container_width=True, key="bb_clear_btn"):
            st.session_state.bb_now = {}
            st.session_state.bb_1yr = {}
            st.session_state.bb_5yr = {}
            st.session_state.bb_events = []
            st.session_state.bb_counter += 1
            st.success("✅ Cleared!")
            st.rerun()
    
    st.markdown("---")
    st.subheader("📊 Monthly Budget Timeline")
    
    # Get all categories
    all_categories = set(st.session_state.bb_now.keys()) | set(st.session_state.bb_1yr.keys()) | set(st.session_state.bb_5yr.keys())
    
    if not all_categories:
        for cat in ['Housing', 'Utilities', 'Groceries', 'Transportation', 'Healthcare', 
                   'Entertainment', 'Dining Out', 'Personal Care', 'Clothing', 'Insurance', 'Other']:
            st.session_state.bb_now[cat] = 0
            st.session_state.bb_1yr[cat] = 0
            st.session_state.bb_5yr[cat] = 0
        all_categories = set(st.session_state.bb_now.keys())
    
    categories_sorted = sorted(all_categories)
    
    # Headers
    col_now, col_1yr, col_5yr = st.columns(3)
    with col_now:
        st.markdown("### 📅 Now")
    with col_1yr:
        st.markdown("### 📅 1 Year")
    with col_5yr:
        st.markdown("### 📅 5 Years")
    
    # Build inputs - use counter to force refresh
    for category in categories_sorted:
        col_now, col_1yr, col_5yr = st.columns(3)
        
        with col_now:
            val = st.number_input(
                category,
                min_value=0,
                value=int(st.session_state.bb_now.get(category, 0)),
                step=50,
                key=f"bb_now_{category}_{st.session_state.bb_counter}"
            )
            st.session_state.bb_now[category] = val
        
        with col_1yr:
            val = st.number_input(
                category,
                min_value=0,
                value=int(st.session_state.bb_1yr.get(category, 0)),
                step=50,
                key=f"bb_1yr_{category}_{st.session_state.bb_counter}",
                # label_visibility="collapsed"
            )
            st.session_state.bb_1yr[category] = val
        
        with col_5yr:
            val = st.number_input(
                category,
                min_value=0,
                value=int(st.session_state.bb_5yr.get(category, 0)),
                step=50,
                key=f"bb_5yr_{category}_{st.session_state.bb_counter}",
                # label_visibility="collapsed"
            )
            st.session_state.bb_5yr[category] = val
    
    # Add custom category
    st.markdown("---")
    col_add1, col_add2 = st.columns([3, 1])
    with col_add1:
        new_category = st.text_input("Add Custom Category", placeholder="e.g., Pet Care", key="bb_new_cat")
    with col_add2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Add", use_container_width=True, key="bb_add_cat"):
            if new_category and new_category not in st.session_state.bb_now:
                st.session_state.bb_now[new_category] = 0
                st.session_state.bb_1yr[new_category] = 0
                st.session_state.bb_5yr[new_category] = 0
                st.session_state.bb_counter += 1
                st.success(f"✅ Added {new_category}")
                st.rerun()
    
    # Calculate totals from session state
    total_now = sum(st.session_state.bb_now.values())
    total_1yr = sum(st.session_state.bb_1yr.values())
    total_5yr = sum(st.session_state.bb_5yr.values())
    
    st.markdown("---")
    st.subheader("📈 Budget Summary")
    
    sum_col1, sum_col2, sum_col3 = st.columns(3)
    with sum_col1:
        st.metric("Now (Monthly)", format_currency(total_now, currency_code))
        st.caption(f"Annual: {format_currency(total_now * 12, currency_code)}")
    with sum_col2:
        delta_1yr = total_1yr - total_now
        st.metric("1 Year (Monthly)", format_currency(total_1yr, currency_code), 
                 delta=format_currency(delta_1yr, currency_code))
        st.caption(f"Annual: {format_currency(total_1yr * 12, currency_code)}")
    with sum_col3:
        delta_5yr = total_5yr - total_now
        st.metric("5 Years (Monthly)", format_currency(total_5yr, currency_code), 
                 delta=format_currency(delta_5yr, currency_code))
        st.caption(f"Annual: {format_currency(total_5yr * 12, currency_code)}")
    
    # Visualization
    st.markdown("---")
    st.subheader("📊 Budget Breakdown")
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Now', x=categories_sorted,
        y=[st.session_state.bb_now.get(cat, 0) for cat in categories_sorted], marker_color='lightblue'))
    fig.add_trace(go.Bar(name='1 Year', x=categories_sorted,
        y=[st.session_state.bb_1yr.get(cat, 0) for cat in categories_sorted], marker_color='lightgreen'))
    fig.add_trace(go.Bar(name='5 Years', x=categories_sorted,
        y=[st.session_state.bb_5yr.get(cat, 0) for cat in categories_sorted], marker_color='lightcoral'))
    fig.update_layout(barmode='group', title="Monthly Budget Comparison", 
                     xaxis_title="Category", yaxis_title=f"Amount ({currency_symbol})", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Life Events
    st.markdown("---")
    st.subheader("🎯 Financial Events Planning")
    
    col_e1, col_e2, col_e3, col_e4 = st.columns([2, 1, 2, 1])
    
    with col_e1:
        event_type = st.selectbox("Event Type", options=list(LIFE_EVENT_IMPACTS.keys()),
            format_func=lambda x: LIFE_EVENT_IMPACTS[x]['description'], key="bb_event_type")
    with col_e2:
        event_year = st.number_input("Year", min_value=0, max_value=30, value=2, key="bb_event_year")
    with col_e3:
        event_name = st.text_input("Custom Name", placeholder=LIFE_EVENT_IMPACTS[event_type]['description'], key="bb_event_name")
    
    event_config = LIFE_EVENT_IMPACTS[event_type]
    event_details = {}
    
    if event_config['needs_details']:
        st.markdown("#### Event Details")
        if event_type == 'property_purchase':
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                event_details['property_price'] = st.number_input(f"Price ({currency_symbol})", 0, 5000000, 500000, key=f"bb_prop_price_{currency_code}")
            with c2:
                event_details['down_payment'] = st.number_input(f"Down ({currency_symbol})", 0, 1000000, 500000, key=f"bb_down_{currency_code}")
            with c3:
                event_details['mortgage_amount'] = st.number_input(f"Mortgage ({currency_symbol})", 0, 4000000, 0, key=f"bb_mort_{currency_code}")
            with c4:
                event_details['mortgage_years'] = st.number_input("Years", 1, 35, 25, key="bb_mort_yrs")
        elif event_type == 'property_sale':
            c1, c2, c3 = st.columns(3)
            with c1:
                event_details['sale_price'] = st.number_input(f"Sale Price ({currency_symbol})", 0, 6000000, 600000, key=f"bb_sale_{currency_code}")
            with c2:
                event_details['mortgage_payoff'] = st.number_input(f"Payoff ({currency_symbol})", 0, 3500000, 350000, key=f"bb_payoff_{currency_code}")
            with c3:
                event_details['selling_costs'] = st.number_input(f"Costs ({currency_symbol})", 0, 300000, 30000, key=f"bb_costs_{currency_code}")
        elif event_type == 'one_time_expense':
            event_details['amount'] = st.number_input(f"Amount ({currency_symbol})", 0, 300000, 30000, key=f"bb_exp_amt_{currency_code}")
        elif event_type == 'expense_change':
            event_details['monthly_change'] = st.number_input(f"Monthly Change ({currency_symbol})", value=1000, step=100, key=f"bb_mon_chg_{currency_code}")
        elif event_type == 'rental_income':
            event_details['monthly_rental'] = st.number_input(f"Monthly Rental ({currency_symbol})", 0, 20000, 2000, key=f"bb_rental_{currency_code}")
        elif event_type == 'windfall':
            event_details['amount'] = st.number_input(f"Amount ({currency_symbol})", 0, 500000, 50000, key=f"bb_wind_{currency_code}")
    
    with col_e4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Add Event", use_container_width=True, key="bb_add_event"):
            event = {
                'type': event_type,
                'simulation_type': event_config['simulation_type'],
                'year': event_year,
                'name': event_name if event_name else event_config['description'],
                'impacts': event_config,
                'details': event_details,
                'currency': currency_code  # Store the currency this event was created in
            }
            st.session_state.bb_events.append(event)
            st.success(f"✅ Added: {event['name']}")
            st.rerun()
    
    # Display events
    if st.session_state.bb_events:
        st.markdown("### Planned Financial Events")
        for idx, event in enumerate(st.session_state.bb_events):
            c1, c2, c3, c4 = st.columns([1, 3, 3, 1])
            with c1:
                st.write(f"**Y{event['year']}**")
            with c2:
                st.write(f"**{event['name']}**")
                st.caption(f"Type: {event['impacts']['description']}")
            with c3:
                if event['details']:
                    details_text = ", ".join([f"{k}: {format_currency(v, currency_code) if isinstance(v, (int, float)) and k != 'mortgage_years' else v}" 
                                            for k, v in event['details'].items()])
                    st.write(details_text)
                else:
                    monthly_impact = sum(event['impacts']['changes'].values())
                    st.write(f"Monthly: {format_currency(monthly_impact, currency_code)}")
            with c4:
                if st.button("🗑️", key=f"bb_del_{idx}"):
                    st.session_state.bb_events.pop(idx)
                    st.rerun()
    
    # Integration
    st.markdown("---")
    st.subheader("🔗 Use in Simulation")
    
    col_int1, col_int2 = st.columns(2)
    with col_int1:
        st.metric("Monthly Expenses to Use", format_currency(total_now, currency_code))
    with col_int2:
        st.metric("Financial Events", len(st.session_state.bb_events))
    
    if st.button("🚀 Go to Simulation with This Budget", type="primary", use_container_width=True, key="bb_go_sim"):
        if total_now <= 0:
            st.error("⚠️ Please set budget values before using in simulation.")
        else:
            # Store in different keys to avoid conflicts
            st.session_state.use_budget_builder = True
            st.session_state.budget_monthly_expenses = int(total_now)
            st.session_state.budget_currency = currency_code  # Store the currency the budget was created in
            st.session_state.budget_events_list = [e.copy() for e in st.session_state.bb_events]
            
            # Set flags for user feedback
            st.session_state.just_set_budget = True
            
            st.success(f"✅ Budget ready! Monthly: {format_currency(total_now, currency_code)}")
            st.info("👈 Switch to the **Simulation** tab to use this budget")
            
            # Note: Streamlit tabs don't support programmatic switching,
            # but we show a clear message to guide the user


if __name__ == "__main__":
    show_budget_builder()