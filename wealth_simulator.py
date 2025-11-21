import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page config
st.set_page_config(page_title="Wealth Path Simulator", layout="wide")

# Title
st.title("30-Year Wealth Path Simulator")
st.markdown("Interactive Monte Carlo simulation to explore your financial future")

# Sidebar controls
st.sidebar.header("Initial Position")

# Initial liquid wealth
initial_liquid_wealth = st.sidebar.number_input(
    "Initial Liquid Wealth ($)",
    min_value=0,
    value=20000,
    step=10000,
    help="Cash, investments, and other liquid assets"
)

# Initial property
initial_property_value = st.sidebar.number_input(
    "Initial Property Value ($)",
    min_value=0,
    value=300000,
    step=25000,
    help="Current market value of property"
)

initial_mortgage = st.sidebar.number_input(
    "Initial Mortgage Balance ($)",
    min_value=0,
    value=200000,
    step=25000,
    help="Outstanding mortgage debt"
)

initial_mortgage_amortization = st.sidebar.number_input(
    "Initial Mortgage Amortization (years)",
    min_value=0,
    max_value=35,
    value=25,
    step=1,
    help="Years remaining on mortgage"
)

mortgage_interest_rate = st.sidebar.slider(
    "Mortgage Interest Rate (%)",
    min_value=0.0,
    max_value=10.0,
    value=4.5,
    step=0.25
) / 100

# Calculate initial monthly mortgage payment if there's a mortgage
if initial_mortgage > 0 and initial_mortgage_amortization > 0:
    # Monthly payment formula: P * [r(1+r)^n] / [(1+r)^n - 1]
    monthly_rate = mortgage_interest_rate / 12
    n_payments = initial_mortgage_amortization * 12
    if monthly_rate > 0:
        calculated_payment = initial_mortgage * (monthly_rate * (1 + monthly_rate)**n_payments) / ((1 + monthly_rate)**n_payments - 1)
    else:
        calculated_payment = initial_mortgage / n_payments
else:
    calculated_payment = 0

# Income and tax
st.sidebar.header("Income & Tax")

gross_annual_income = st.sidebar.number_input(
    "Gross Annual Income ($)",
    min_value=0,
    value=75000,
    step=5000
)

effective_tax_rate = st.sidebar.slider(
    "Effective Tax Rate (%)",
    min_value=0.0,
    max_value=50.0,
    value=24.0,
    step=1.0,
    help="Average tax rate on income"
) / 100

pension_contribution_rate = st.sidebar.slider(
    "Pension Contribution (% of gross)",
    min_value=0.0,
    max_value=30.0,
    value=15.0,
    step=1.0,
    help="Pre-tax pension contribution as % of gross income"
) / 100

# Monthly expenses and savings
st.sidebar.header("Monthly Budget")

monthly_expenses = st.sidebar.number_input(
    "Monthly Living Expenses ($)",
    min_value=0,
    value=2000,
    step=250,
    help="Regular monthly expenses (excluding mortgage)"
)

if calculated_payment > 0:
    st.sidebar.info(f"💡 Calculated mortgage payment: ${calculated_payment:,.2f}/month")

monthly_mortgage_payment = calculated_payment

# Property assumptions
st.sidebar.header("Property Assumptions")

property_appreciation = st.sidebar.slider(
    "Annual Property Appreciation (%)",
    min_value=-5.0,
    max_value=15.0,
    value=3.0,
    step=0.5
) / 100

# Investment parameters
st.sidebar.subheader("Investment Assumptions")

expected_return = st.sidebar.slider(
    "Expected Annual Return (%)",
    min_value=0.0,
    max_value=15.0,
    value=4.0,
    step=0.5,
    help="Average expected portfolio return"
) / 100

return_volatility = st.sidebar.slider(
    "Return Volatility (Std Dev %)",
    min_value=0.0,
    max_value=30.0,
    value=15.0,
    step=1.0,
    help="Standard deviation of annual returns"
) / 100


# Helper function to calculate mortgage payment
def calculate_mortgage_payment(principal, annual_rate, years):
    """Calculate monthly mortgage payment using amortization formula"""
    if principal <= 0 or years <= 0:
        return 0
    monthly_rate = annual_rate / 12
    n_payments = years * 12
    if monthly_rate > 0:
        payment = principal * (monthly_rate * (1 + monthly_rate)**n_payments) / ((1 + monthly_rate)**n_payments - 1)
    else:
        payment = principal / n_payments
    return payment

# Inflation
st.sidebar.subheader("Inflation")

expected_inflation = st.sidebar.slider(
    "Expected Inflation (%)",
    min_value=0.0,
    max_value=10.0,
    value=2.5,
    step=0.25
) / 100

inflation_volatility = st.sidebar.slider(
    "Inflation Volatility (Std Dev %)",
    min_value=0.0,
    max_value=5.0,
    value=1.0,
    step=0.25
) / 100

salary_inflation = st.sidebar.slider(
    "Salary Inflation (%)",
    min_value=0.0,
    max_value=10.0,
    value=2.5,
    step=0.25,
    help="Annual salary increase (separate from general inflation)"
) / 100

# Simulation parameters
st.sidebar.subheader("Simulation Settings")

n_simulations = st.sidebar.select_slider(
    "Number of Simulations",
    options=[100, 500, 1000, 2000, 5000],
    value=1000
)

years = 30
random_seed = st.sidebar.number_input(
    "Random Seed (for reproducibility)",
    min_value=0,
    value=42,
    step=1
)

# Major events section
st.sidebar.subheader("Major Financial Events")
n_events = st.sidebar.number_input("Number of Events", min_value=0, max_value=15, value=0, step=1)

events = []
for i in range(n_events):
    with st.sidebar.expander(f"Event {i+1}"):
        event_type = st.selectbox(
            "Event Type",
            ["Property Purchase", "Property Sale", "One-Time Expense", "Expense Change", "Rental Income", "Windfall"],
            key=f"type_{i}"
        )
        
        event_year = st.number_input(
            "Year", 
            min_value=1, 
            max_value=30, 
            value=min(5*(i+1), 30), 
            key=f"year_{i}"
        )
        
        event_name = st.text_input(
            "Description", 
            value=f"{event_type} {i+1}", 
            key=f"name_{i}"
        )
        
        if event_type == "Property Purchase":
            property_price = st.number_input(
                "Property Price ($)", 
                min_value=0, 
                value=500000, 
                step=25000, 
                key=f"prop_price_{i}"
            )
            down_payment = st.number_input(
                "Down Payment ($)", 
                min_value=0, 
                value=100000, 
                step=10000, 
                key=f"down_pmt_{i}",
                help="Cash paid upfront (reduces liquid wealth)"
            )
            mortgage_amount = st.number_input(
                "Mortgage Amount ($)", 
                min_value=0, 
                value=400000, 
                step=25000, 
                key=f"mortgage_{i}",
                help="Loan amount (added to mortgage balance)"
            )
            mortgage_amortization = st.number_input(
                "Mortgage Amortization (years)",
                min_value=1,
                max_value=35,
                value=25,
                step=1,
                key=f"amort_{i}",
                help="Length of mortgage in years"
            )
            
            # Calculate the mortgage payment automatically
            calculated_new_payment = calculate_mortgage_payment(
                mortgage_amount, 
                mortgage_interest_rate, 
                mortgage_amortization
            )
            
            # Show calculated payment
            if mortgage_amount > 0:
                st.info(f"💡 Calculated payment: ${calculated_new_payment:,.2f}/month based on {mortgage_interest_rate*100:.2f}% rate and {mortgage_amortization} year amortization")
            
            # Add existing mortgage payment to new one
            total_mortgage_payment = calculated_payment + calculated_new_payment
            
            if initial_mortgage > 0 and calculated_payment > 0:
                st.caption(f"📋 Total mortgage: ${calculated_payment:,.2f} (existing) + ${calculated_new_payment:,.2f} (new) = ${total_mortgage_payment:,.2f}/month")
            
            events.append({
                "type": "property_purchase",
                "year": event_year,
                "name": event_name,
                "property_price": property_price,
                "down_payment": down_payment,
                "mortgage_amount": mortgage_amount,
                "new_mortgage_payment": total_mortgage_payment
            })
            
        elif event_type == "Property Sale":
            sale_price = st.number_input(
                "Sale Price ($)", 
                min_value=0, 
                value=600000, 
                step=25000, 
                key=f"sale_price_{i}"
            )
            mortgage_payoff = st.number_input(
                "Mortgage Payoff ($)", 
                min_value=0, 
                value=350000, 
                step=25000, 
                key=f"payoff_{i}",
                help="Mortgage balance paid off from proceeds"
            )
            selling_costs = st.number_input(
                "Selling Costs ($)", 
                min_value=0, 
                value=30000, 
                step=5000, 
                key=f"costs_{i}",
                help="Agent fees, legal costs, etc."
            )
            events.append({
                "type": "property_sale",
                "year": event_year,
                "name": event_name,
                "sale_price": sale_price,
                "mortgage_payoff": mortgage_payoff,
                "selling_costs": selling_costs
            })
            
        elif event_type == "One-Time Expense":
            expense_amount = st.number_input(
                "Expense Amount ($)", 
                min_value=0, 
                value=30000, 
                step=5000, 
                key=f"expense_{i}",
                help="One-time reduction in liquid wealth (e.g., vehicle, renovation)"
            )
            events.append({
                "type": "one_time_expense",
                "year": event_year,
                "name": event_name,
                "amount": expense_amount
            })
            
        elif event_type == "Expense Change":
            monthly_change = st.number_input(
                "Monthly Expense Change ($)", 
                value=1000, 
                step=100, 
                key=f"monthly_change_{i}",
                help="Increase (positive) or decrease (negative) in monthly expenses from this year forward"
            )
            events.append({
                "type": "expense_change",
                "year": event_year,
                "name": event_name,
                "monthly_change": monthly_change
            })
            
        elif event_type == "Rental Income":
            monthly_rental = st.number_input(
                "Monthly Rental Income ($)", 
                min_value=0,
                value=2000, 
                step=100, 
                key=f"monthly_rental_{i}",
                help="Ongoing monthly rental income from this year forward"
            )
            events.append({
                "type": "rental_income",
                "year": event_year,
                "name": event_name,
                "monthly_rental": monthly_rental
            })
            
        else:  # Windfall
            windfall_amount = st.number_input(
                "Windfall Amount ($)", 
                min_value=0, 
                value=50000, 
                step=10000, 
                key=f"windfall_{i}",
                help="One-time addition to liquid wealth (e.g., inheritance, bonus)"
            )
            events.append({
                "type": "windfall",
                "year": event_year,
                "name": event_name,
                "amount": windfall_amount
            })


def run_monte_carlo(initial_liquid_wealth, initial_property_value, initial_mortgage,
                   gross_annual_income, effective_tax_rate, pension_contribution_rate,
                   monthly_expenses, monthly_mortgage_payment,
                   property_appreciation, mortgage_interest_rate,
                   expected_return, return_volatility, expected_inflation, inflation_volatility,
                   salary_inflation, years, n_simulations, events, random_seed):
    """
    Run Monte Carlo simulation for wealth paths with detailed financial modeling
    """
    np.random.seed(random_seed)
    
    # Initialize arrays for tracking different wealth components
    liquid_wealth_paths = np.zeros((n_simulations, years + 1))
    property_value_paths = np.zeros((n_simulations, years + 1))
    mortgage_balance_paths = np.zeros((n_simulations, years + 1))
    pension_wealth_paths = np.zeros((n_simulations, years + 1))
    
    # Track variable expenses and mortgage payments (can change via events)
    monthly_expenses_tracker = np.full((n_simulations, years + 1), monthly_expenses)
    monthly_mortgage_tracker = np.full((n_simulations, years + 1), monthly_mortgage_payment)
    monthly_rental_tracker = np.zeros((n_simulations, years + 1))  # Track rental income
    
    # Set initial values
    liquid_wealth_paths[:, 0] = initial_liquid_wealth
    property_value_paths[:, 0] = initial_property_value
    mortgage_balance_paths[:, 0] = initial_mortgage
    pension_wealth_paths[:, 0] = 0  # Start with no pension wealth
    
    # Calculate net worth paths
    net_worth_paths = np.zeros((n_simulations, years + 1))
    net_worth_paths[:, 0] = (initial_liquid_wealth + initial_property_value - 
                             initial_mortgage)
    
    # Store real (inflation-adjusted) net worth
    real_net_worth_paths = np.zeros((n_simulations, years + 1))
    real_net_worth_paths[:, 0] = net_worth_paths[:, 0]
    
    # Generate random returns and inflation for all simulations
    portfolio_returns = np.random.normal(expected_return, return_volatility, (n_simulations, years))
    pension_returns = np.random.normal(expected_return, return_volatility, (n_simulations, years))
    inflation_rates = np.random.normal(expected_inflation, inflation_volatility, (n_simulations, years))
    
    # Ensure inflation doesn't go too negative
    inflation_rates = np.maximum(inflation_rates, -0.05)
    
    # Organize events by year
    events_by_year = {}
    for event in events:
        year = event['year']
        if year not in events_by_year:
            events_by_year[year] = []
        events_by_year[year].append(event)
    
    # Calculate annual values (will be inflated each year)
    base_pension_contribution = gross_annual_income * pension_contribution_rate
    base_take_home = gross_annual_income * (1 - effective_tax_rate - pension_contribution_rate)
    base_annual_expenses = monthly_expenses * 12
    base_annual_mortgage = monthly_mortgage_payment * 12
    
    # Simulate each year
    for year in range(1, years + 1):
        # Current year's inflation adjustment
        cumulative_inflation = np.prod(1 + inflation_rates[:, :year], axis=1)
        
        # Salary grows with salary inflation (not general inflation)
        cumulative_salary_growth = (1 + salary_inflation) ** year
        
        # Use tracked expenses/mortgage/rental (may have been modified by events)
        current_monthly_expenses = monthly_expenses_tracker[:, year - 1]
        current_monthly_mortgage = monthly_mortgage_tracker[:, year - 1]
        current_monthly_rental = monthly_rental_tracker[:, year - 1]
        
        # Inflate income with salary inflation, expenses with general inflation
        year_gross_income = gross_annual_income * cumulative_salary_growth
        year_pension_contribution = year_gross_income * pension_contribution_rate
        year_take_home = year_gross_income * (1 - effective_tax_rate - pension_contribution_rate)
        year_expenses = current_monthly_expenses * 12 * cumulative_inflation
        year_mortgage_payment = current_monthly_mortgage * 12 * cumulative_inflation
        year_rental_income = current_monthly_rental * 12 * cumulative_inflation
        
        # Calculate available savings (can be negative if overspending)
        year_available_savings = year_take_home + year_rental_income - year_expenses - year_mortgage_payment
        
        # Update pension wealth: previous balance * (1 + return) + contribution
        pension_wealth_paths[:, year] = (
            pension_wealth_paths[:, year - 1] * (1 + pension_returns[:, year - 1]) +
            year_pension_contribution
        )
        
        # Update liquid wealth: previous balance * (1 + return) + available savings
        liquid_wealth_paths[:, year] = (
            liquid_wealth_paths[:, year - 1] * (1 + portfolio_returns[:, year - 1]) +
            year_available_savings
        )
        
        # Update property value with appreciation (if property exists)
        property_value_paths[:, year] = (
            property_value_paths[:, year - 1] * (1 + property_appreciation)
        )
        
        # Update mortgage balance
        if mortgage_balance_paths[:, year - 1].mean() > 0:
            year_interest = mortgage_balance_paths[:, year - 1] * mortgage_interest_rate
            year_principal = np.maximum(year_mortgage_payment - year_interest, 0)
            mortgage_balance_paths[:, year] = np.maximum(
                mortgage_balance_paths[:, year - 1] - year_principal, 0
            )
        else:
            mortgage_balance_paths[:, year] = 0
        
        # Process events for this year AFTER normal updates
        if year in events_by_year:
            for event in events_by_year[year]:
                if event['type'] == 'property_purchase':
                    # Reduce liquid wealth by down payment
                    liquid_wealth_paths[:, year] -= event['down_payment']
                    # Add property value
                    property_value_paths[:, year] += event['property_price']
                    # Add mortgage debt
                    mortgage_balance_paths[:, year] += event['mortgage_amount']
                    # Update mortgage payment going forward
                    monthly_mortgage_tracker[:, year:] = event['new_mortgage_payment']
                    
                elif event['type'] == 'property_sale':
                    # Calculate net proceeds
                    net_proceeds = (event['sale_price'] - 
                                  event['mortgage_payoff'] - 
                                  event['selling_costs'])
                    # Add to liquid wealth
                    liquid_wealth_paths[:, year] += net_proceeds
                    # Remove property value
                    property_value_paths[:, year] = 0
                    # Reduce mortgage by payoff amount
                    mortgage_balance_paths[:, year] = np.maximum(
                        mortgage_balance_paths[:, year] - event['mortgage_payoff'], 0
                    )
                    # Set mortgage payment to 0 if fully paid off
                    if event['mortgage_payoff'] >= mortgage_balance_paths[:, year].mean():
                        monthly_mortgage_tracker[:, year:] = 0
                    
                elif event['type'] == 'one_time_expense':
                    # Reduce liquid wealth
                    liquid_wealth_paths[:, year] -= event['amount']
                    
                elif event['type'] == 'expense_change':
                    # Adjust ongoing monthly expenses (for next year forward)
                    monthly_expenses_tracker[:, year:] += event['monthly_change']
                    
                elif event['type'] == 'rental_income':
                    # Add ongoing monthly rental income (for this year forward)
                    monthly_rental_tracker[:, year:] += event['monthly_rental']
                    
                elif event['type'] == 'windfall':
                    # Add to liquid wealth
                    liquid_wealth_paths[:, year] += event['amount']
        
        # Calculate total net worth
        net_worth_paths[:, year] = (
            liquid_wealth_paths[:, year] +
            pension_wealth_paths[:, year] +
            property_value_paths[:, year] -
            mortgage_balance_paths[:, year]
        )
        
        # Calculate real net worth (deflated by cumulative inflation)
        real_net_worth_paths[:, year] = net_worth_paths[:, year] / cumulative_inflation
    
    return {
        'net_worth': net_worth_paths,
        'real_net_worth': real_net_worth_paths,
        'liquid_wealth': liquid_wealth_paths,
        'pension_wealth': pension_wealth_paths,
        'property_value': property_value_paths,
        'mortgage_balance': mortgage_balance_paths,
        'inflation_rates': inflation_rates
    }


# Run simulation button
if st.sidebar.button("Run Simulation", type="primary"):
    with st.spinner("Running Monte Carlo simulation..."):
        results = run_monte_carlo(
            initial_liquid_wealth, initial_property_value, initial_mortgage,
            gross_annual_income, effective_tax_rate, pension_contribution_rate,
            monthly_expenses, monthly_mortgage_payment,
            property_appreciation, mortgage_interest_rate,
            expected_return, return_volatility, expected_inflation, inflation_volatility,
            salary_inflation, years, n_simulations, events, random_seed
        )
        
        # Store in session state
        st.session_state['results'] = results
        st.session_state['sim_complete'] = True

# Display results if simulation has been run
if st.session_state.get('sim_complete', False):
    results = st.session_state['results']
    
    # Toggle for nominal vs real and what to show
    col1, col2, col3 = st.columns([2, 2, 3])
    with col1:
        show_real = st.checkbox("Show Real (Inflation-Adjusted)", value=True)
    with col2:
        view_type = st.selectbox(
            "View",
            ["Total Net Worth", "Liquid Wealth", "Property Equity", "Pension Wealth"]
        )
    
    # Select which paths to plot based on view type
    if view_type == "Total Net Worth":
        paths_to_plot = results['real_net_worth'] if show_real else results['net_worth']
        y_label = "Net Worth"
    elif view_type == "Liquid Wealth":
        paths_to_plot = results['liquid_wealth']
        if show_real:
            cumulative_inflation = np.cumprod(
                1 + results['inflation_rates'], axis=1
            )
            cumulative_inflation = np.column_stack([
                np.ones(n_simulations), cumulative_inflation
            ])
            paths_to_plot = paths_to_plot / cumulative_inflation
        y_label = "Liquid Wealth"
    elif view_type == "Property Equity":
        paths_to_plot = results['property_value'] - results['mortgage_balance']
        if show_real:
            cumulative_inflation = np.cumprod(
                1 + results['inflation_rates'], axis=1
            )
            cumulative_inflation = np.column_stack([
                np.ones(n_simulations), cumulative_inflation
            ])
            paths_to_plot = paths_to_plot / cumulative_inflation
        y_label = "Property Equity"
    else:  # Pension Wealth
        paths_to_plot = results['pension_wealth']
        if show_real:
            cumulative_inflation = np.cumprod(
                1 + results['inflation_rates'], axis=1
            )
            cumulative_inflation = np.column_stack([
                np.ones(n_simulations), cumulative_inflation
            ])
            paths_to_plot = paths_to_plot / cumulative_inflation
        y_label = "Pension Wealth"
    
    # Calculate percentiles
    percentiles = [10, 25, 50, 75, 90]
    percentile_data = np.percentile(paths_to_plot, percentiles, axis=0)
    
    # Create main visualization
    fig = go.Figure()
    
    # Add sample paths (random selection for visualization)
    n_sample_paths = min(100, n_simulations)
    sample_indices = np.random.choice(n_simulations, n_sample_paths, replace=False)
    
    for idx in sample_indices:
        fig.add_trace(go.Scatter(
            x=list(range(years + 1)),
            y=paths_to_plot[idx],
            mode='lines',
            line=dict(color='lightblue', width=0.5),
            opacity=0.3,
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Add percentile bands
    colors = ['rgba(255,0,0,0.1)', 'rgba(255,165,0,0.15)', 'rgba(0,128,0,0.2)', 
              'rgba(255,165,0,0.15)', 'rgba(255,0,0,0.1)']
    
    # Fill between percentiles
    fig.add_trace(go.Scatter(
        x=list(range(years + 1)),
        y=percentile_data[0],
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    for i in range(len(percentiles)-1):
        fig.add_trace(go.Scatter(
            x=list(range(years + 1)),
            y=percentile_data[i+1],
            mode='lines',
            line=dict(width=0),
            fill='tonexty',
            fillcolor=colors[i],
            name=f'{percentiles[i]}-{percentiles[i+1]}th percentile',
            hoverinfo='skip'
        ))
    
    # Add median line
    fig.add_trace(go.Scatter(
        x=list(range(years + 1)),
        y=percentile_data[2],
        mode='lines',
        line=dict(color='darkgreen', width=3),
        name='Median (50th percentile)'
    ))
    
    # Add event markers with different colors by type
    event_colors = {
        'property_purchase': 'blue',
        'property_sale': 'green',
        'one_time_expense': 'red',
        'expense_change': 'orange',
        'rental_income': 'teal',
        'windfall': 'purple'
    }
    
    for event in events:
        event_type = event.get('type', 'unknown')
        color = event_colors.get(event_type, 'gray')
        
        fig.add_vline(
            x=event['year'],
            line_dash="dash",
            line_color=color,
            annotation_text=event['name'],
            annotation_position="top"
        )
    
    fig.update_layout(
        title=f"{y_label} Trajectory over 30 Years ({'Real' if show_real else 'Nominal'} Values)",
        xaxis_title="Year",
        yaxis_title=f"{y_label} ({' Real' if show_real else 'Nominal'} $)",
        hovermode='x unified',
        height=600,
        showlegend=True
    )
    
    # Format y-axis as currency
    fig.update_yaxes(tickformat="$,.0f")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Key metrics
    st.subheader("Key Statistics")
    
    # Use net worth for statistics
    net_worth_paths = results['real_net_worth'] if show_real else results['net_worth']
    final_net_worth = net_worth_paths[:, -1]
    initial_net_worth = net_worth_paths[:, 0]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Median Final Net Worth", f"${np.median(final_net_worth):,.0f}")
    
    with col2:
        st.metric("Mean Final Net Worth", f"${np.mean(final_net_worth):,.0f}")
    
    with col3:
        prob_growth = (final_net_worth > initial_net_worth).mean() * 100
        st.metric("Probability of Growth", f"{prob_growth:.1f}%")
    
    with col4:
        prob_double = (final_net_worth > initial_net_worth * 2).mean() * 100
        st.metric("Probability of 2x Growth", f"{prob_double:.1f}%")
    
    # Wealth composition breakdown (median path)
    st.subheader("Wealth Composition Over Time (Median Scenario)")
    
    # Create figure with line chart instead of stacked area to handle negative values
    fig_composition = go.Figure()
    
    median_liquid = np.median(results['liquid_wealth'], axis=0)
    median_pension = np.median(results['pension_wealth'], axis=0)
    median_property = np.median(results['property_value'], axis=0)
    median_mortgage = np.median(results['mortgage_balance'], axis=0)
    median_equity = median_property - median_mortgage
    median_net_worth = median_liquid + median_pension + median_equity
    
    if show_real:
        # Adjust for inflation
        inflation_adjustment = np.concatenate([
            [1], 
            np.cumprod(1 + np.median(results['inflation_rates'], axis=0))
        ])
        median_liquid = median_liquid / inflation_adjustment
        median_pension = median_pension / inflation_adjustment
        median_equity = median_equity / inflation_adjustment
        median_net_worth = median_net_worth / inflation_adjustment
    
    # Add individual components as lines
    fig_composition.add_trace(go.Scatter(
        x=list(range(years + 1)),
        y=median_liquid,
        mode='lines',
        name='Liquid Wealth',
        line=dict(color='#1f77b4', width=2),
        fill='tozeroy',
        fillcolor='rgba(31, 119, 180, 0.3)'
    ))
    
    fig_composition.add_trace(go.Scatter(
        x=list(range(years + 1)),
        y=median_pension,
        mode='lines',
        name='Pension',
        line=dict(color='#ff7f0e', width=2)
    ))
    
    fig_composition.add_trace(go.Scatter(
        x=list(range(years + 1)),
        y=median_equity,
        mode='lines',
        name='Property Equity',
        line=dict(color='#2ca02c', width=2)
    ))
    
    fig_composition.add_trace(go.Scatter(
        x=list(range(years + 1)),
        y=median_net_worth,
        mode='lines',
        name='Total Net Worth',
        line=dict(color='black', width=3, dash='dash')
    ))
    
    # Add zero line for reference
    fig_composition.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.5)
    
    fig_composition.update_layout(
        title=f"Median Wealth Components ({'Real' if show_real else 'Nominal'} Values)",
        xaxis_title="Year",
        yaxis_title=f"Value ({' Real' if show_real else 'Nominal'} $)",
        hovermode='x unified',
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig_composition.update_yaxes(tickformat="$,.0f")
    
    st.plotly_chart(fig_composition, use_container_width=True)
    
    # Add cash flow summary
    st.subheader("Annual Cash Flow Available for Savings")
    
    # Calculate median available cash flow over time
    # We need to recalculate this based on the simulation parameters
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Current Year 1 Cash Flow**")
        year1_income = gross_annual_income
        year1_pension = year1_income * pension_contribution_rate
        year1_tax = year1_income * effective_tax_rate
        year1_takehome = year1_income - year1_pension - year1_tax
        year1_expenses = monthly_expenses * 12
        year1_mortgage = monthly_mortgage_payment * 12
        year1_available = year1_takehome - year1_expenses - year1_mortgage
        
        cashflow_df = pd.DataFrame({
            'Item': ['Gross Income', '- Pension Contrib', '- Tax', '= Take Home', 
                    '- Living Expenses', '- Mortgage', '= Available for Investment'],
            'Amount': [
                f"${year1_income:,.0f}",
                f"${year1_pension:,.0f}",
                f"${year1_tax:,.0f}",
                f"${year1_takehome:,.0f}",
                f"${year1_expenses:,.0f}",
                f"${year1_mortgage:,.0f}",
                f"${year1_available:,.0f}"
            ]
        })
        st.dataframe(cashflow_df, use_container_width=True, hide_index=True)
        
        if year1_available < 0:
            st.error(f"⚠️ Cash flow deficit: ${abs(year1_available):,.0f}/year")
        else:
            st.success(f"✓ Annual savings: ${year1_available:,.0f} (${year1_available/12:,.0f}/month)")
    
    with col2:
        st.markdown("**Liquid Wealth Warning Check**")
        min_liquid = np.median(results['liquid_wealth'], axis=0).min()
        if show_real:
            inflation_adj = np.concatenate([[1], np.cumprod(1 + np.median(results['inflation_rates'], axis=0))])
            min_liquid = (np.median(results['liquid_wealth'], axis=0) / inflation_adj).min()
        
        if min_liquid < 0:
            st.error(f"⚠️ Liquid wealth goes negative!\nMinimum: ${min_liquid:,.0f}")
            st.markdown("**Recommendations:**")
            st.markdown("- Reduce monthly expenses")
            st.markdown("- Reduce monthly savings target")
            st.markdown("- Increase income")
            st.markdown("- Review major financial events")
        else:
            st.success(f"✓ Liquid wealth stays positive\nMinimum: ${min_liquid:,.0f}")
            
        # Show final liquid wealth
        final_liquid = np.median(results['liquid_wealth'], axis=0)[-1]
        if show_real:
            final_liquid = final_liquid / inflation_adj[-1]
        st.metric("Median Final Liquid Wealth", f"${final_liquid:,.0f}")
    
    # Add detailed cash flow projection table
    st.subheader("Cash Flow Projection with Financial Events")
    
    # Build year-by-year cash flow projection
    # First 10 years: every year, then 5-year intervals
    projection_years = list(range(0, 11)) + [15, 20, 25, 30]
    
    cashflow_projection = []
    
    for year in projection_years:
        # Apply all events up to this year
        year_monthly_expenses = monthly_expenses
        year_monthly_mortgage = monthly_mortgage_payment
        year_monthly_rental = 0
        event_notes = []
        
        for event in events:
            if event['year'] <= year:
                if event['type'] == 'property_purchase':
                    year_monthly_mortgage = event['new_mortgage_payment']
                    if event['year'] == year:
                        event_notes.append(f"🏠 {event['name']}")
                elif event['type'] == 'property_sale':
                    year_monthly_mortgage = 0
                    if event['year'] == year:
                        event_notes.append(f"💰 {event['name']}")
                elif event['type'] == 'expense_change':
                    year_monthly_expenses += event['monthly_change']
                    if event['year'] == year:
                        event_notes.append(f"📊 {event['name']}")
                elif event['type'] == 'rental_income':
                    year_monthly_rental += event['monthly_rental']
                    if event['year'] == year:
                        event_notes.append(f"🏘️ {event['name']}")
                elif event['type'] == 'one_time_expense' and event['year'] == year:
                    event_notes.append(f"💸 {event['name']}")
                elif event['type'] == 'windfall' and event['year'] == year:
                    event_notes.append(f"💵 {event['name']}")
        
        # Calculate cash flow (with salary inflation, expense inflation)
        cumulative_salary_growth = (1 + salary_inflation) ** year
        year_income = gross_annual_income * cumulative_salary_growth
        year_pension = year_income * pension_contribution_rate
        year_tax = year_income * effective_tax_rate
        year_takehome = year_income - year_pension - year_tax
        year_rental_annual = year_monthly_rental * 12
        year_expenses_annual = year_monthly_expenses * 12
        year_mortgage_annual = year_monthly_mortgage * 12
        year_available = year_takehome + year_rental_annual - year_expenses_annual - year_mortgage_annual
        
        cashflow_projection.append({
            'Year': year,
            'Take Home': f"${year_takehome:,.0f}",
            'Rental Income': f"${year_rental_annual:,.0f}" if year_rental_annual > 0 else "-",
            'Living Expenses': f"${year_expenses_annual:,.0f}",
            'Mortgage': f"${year_mortgage_annual:,.0f}",
            'Available Savings': f"${year_available:,.0f}",
            'Monthly Savings': f"${year_available/12:,.0f}",
            'Events This Year': ', '.join(event_notes) if event_notes else '-'
        })
    
    projection_df = pd.DataFrame(cashflow_projection)
    
    # Style the dataframe to highlight negative values
    def highlight_negative(val):
        if isinstance(val, str) and val.startswith('$-'):
            return 'background-color: #ffcccc'
        return ''
    
    st.dataframe(
        projection_df.style.applymap(highlight_negative, subset=['Available Savings', 'Monthly Savings']),
        use_container_width=True,
        hide_index=True
    )
    
    st.caption("💡 Take-home income grows with salary inflation. Expenses and mortgage shown in current dollars (not inflation-adjusted).")
    st.caption("📝 Events: 🏠 Property Purchase, 💰 Property Sale, 📊 Expense Change, 🏘️ Rental Income, 💸 One-Time Expense, 💵 Windfall")
    
    # Distribution at key years
    st.subheader("Wealth Distribution at Key Milestones")
    
    milestone_years = [5, 10, 15, 20, 25, 30]
    
    fig_dist = make_subplots(
        rows=2, cols=3,
        subplot_titles=[f"Year {y}" for y in milestone_years]
    )
    
    for idx, year in enumerate(milestone_years):
        row = idx // 3 + 1
        col = idx % 3 + 1
        
        fig_dist.add_trace(
            go.Histogram(
                x=paths_to_plot[:, year],
                nbinsx=50,
                name=f"Year {year}",
                showlegend=False
            ),
            row=row, col=col
        )
    
    fig_dist.update_layout(height=500, showlegend=False)
    fig_dist.update_xaxes(tickformat="$,.0f")
    
    st.plotly_chart(fig_dist, use_container_width=True)
    
    # Detailed percentile table
    st.subheader("Detailed Percentile Breakdown")
    
    milestone_data = []
    for year in milestone_years:
        year_wealth = paths_to_plot[:, year]
        milestone_data.append({
            'Year': year,
            '10th': f"${np.percentile(year_wealth, 10):,.0f}",
            '25th': f"${np.percentile(year_wealth, 25):,.0f}",
            '50th': f"${np.percentile(year_wealth, 50):,.0f}",
            '75th': f"${np.percentile(year_wealth, 75):,.0f}",
            '90th': f"${np.percentile(year_wealth, 90):,.0f}",
        })
    
    st.dataframe(pd.DataFrame(milestone_data), use_container_width=True, hide_index=True)

else:
    st.info("👈 Set your parameters in the sidebar and click 'Run Simulation' to begin")
    
    # Show cash flow summary based on current inputs
    st.subheader("Annual Cash Flow Summary")
    
    # Calculate Year 1 cash flow
    pension_contrib = gross_annual_income * pension_contribution_rate
    tax = gross_annual_income * effective_tax_rate
    take_home = gross_annual_income - pension_contrib - tax
    annual_expenses_calc = monthly_expenses * 12
    annual_mortgage_calc = monthly_mortgage_payment * 12
    annual_available_yr1 = take_home - annual_expenses_calc - annual_mortgage_calc
    
    # Check for property events that will change mortgage payments
    future_mortgage_changes = []
    for event in events:
        if event.get('type') == 'property_purchase':
            future_mortgage_changes.append({
                'year': event['year'],
                'new_payment': event['new_mortgage_payment'],
                'description': event['name']
            })
        elif event.get('type') == 'property_sale':
            future_mortgage_changes.append({
                'year': event['year'],
                'new_payment': 0,
                'description': event['name']
            })
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Year 1 Cash Flow**")
        income_df = pd.DataFrame({
            'Item': ['Gross Income', '- Pension Contrib', '- Tax', '= Take Home', 
                    '- Living Expenses', '- Mortgage', '= Available for Investment'],
            'Amount': [
                f"${gross_annual_income:,.0f}",
                f"${pension_contrib:,.0f}",
                f"${tax:,.0f}",
                f"${take_home:,.0f}",
                f"${annual_expenses_calc:,.0f}",
                f"${annual_mortgage_calc:,.0f}",
                f"${annual_available_yr1:,.0f}"
            ]
        })
        st.dataframe(income_df, use_container_width=True, hide_index=True)
        
        if annual_available_yr1 < 0:
            st.error(f"⚠️ Cash flow deficit: ${abs(annual_available_yr1):,.0f}/year (${abs(annual_available_yr1)/12:,.0f}/month)")
        else:
            st.success(f"✓ Annual savings: ${annual_available_yr1:,.0f} (${annual_available_yr1/12:,.0f}/month)")
    
    with col2:
        if len(future_mortgage_changes) > 0:
            st.markdown("**Cash Flow After Property Events**")
            
            # Find the earliest property event
            earliest_event = min(future_mortgage_changes, key=lambda x: x['year'])
            year = earliest_event['year']
            new_monthly_mortgage = earliest_event['new_payment']
            
            # Calculate cash flow after the event
            # Account for expense changes up to that year
            adjusted_monthly_expenses = monthly_expenses
            for event in events:
                if event.get('type') == 'expense_change' and event['year'] <= year:
                    adjusted_monthly_expenses += event['monthly_change']
            
            annual_mortgage_new = new_monthly_mortgage * 12
            annual_expenses_adjusted = adjusted_monthly_expenses * 12
            annual_available_new = take_home - annual_expenses_adjusted - annual_mortgage_new
            
            event_df = pd.DataFrame({
                'Item': [
                    f'After {earliest_event["description"]} (Year {year})',
                    '= Take Home',
                    '- Living Expenses',
                    '- New Mortgage',
                    '= Available for Investment'
                ],
                'Amount': [
                    '',
                    f"${take_home:,.0f}",
                    f"${annual_expenses_adjusted:,.0f}",
                    f"${annual_mortgage_new:,.0f}",
                    f"${annual_available_new:,.0f}"
                ]
            })
            st.dataframe(event_df, use_container_width=True, hide_index=True)
            
            delta = annual_available_new - annual_available_yr1
            if annual_available_new < 0:
                st.error(f"⚠️ Cash flow becomes deficit: ${abs(annual_available_new):,.0f}/year")
            elif delta < 0:
                st.warning(f"Savings reduced by ${abs(delta):,.0f}/year (${abs(delta)/12:,.0f}/month)")
            else:
                st.success(f"Savings increased by ${delta:,.0f}/year (${delta/12:,.0f}/month)")
        else:
            st.markdown("**No Property Events Configured**")
            st.info("Add property purchase or sale events to see how they affect cash flow")
    
    # Initial net worth
    st.subheader("Initial Net Worth")
    net_worth_df = pd.DataFrame({
        'Component': ['Liquid Wealth', 'Property Value', 'Mortgage Debt', 'Net Worth'],
        'Amount': [
            f"${initial_liquid_wealth:,.0f}",
            f"${initial_property_value:,.0f}",
            f"-${initial_mortgage:,.0f}",
            f"${initial_liquid_wealth + initial_property_value - initial_mortgage:,.0f}"
        ]
    })
    st.dataframe(net_worth_df, use_container_width=True, hide_index=True)
    
    # Show configured events if any
    if len(events) > 0:
        st.subheader("Configured Financial Events")
        event_summary = []
        for event in events:
            if event['type'] == 'property_purchase':
                details = f"Price: ${event['property_price']:,.0f}, Down: ${event['down_payment']:,.0f}, Mortgage: ${event['mortgage_amount']:,.0f}"
            elif event['type'] == 'property_sale':
                details = f"Sale: ${event['sale_price']:,.0f}, Payoff: ${event['mortgage_payoff']:,.0f}, Costs: ${event['selling_costs']:,.0f}"
            elif event['type'] == 'one_time_expense':
                details = f"Expense: ${event['amount']:,.0f}"
            elif event['type'] == 'expense_change':
                details = f"Monthly Change: ${event['monthly_change']:+,.0f}"
            elif event['type'] == 'rental_income':
                details = f"Monthly Rental: ${event['monthly_rental']:,.0f}"
            elif event['type'] == 'windfall':
                details = f"Amount: ${event['amount']:,.0f}"
            else:
                details = ""
            
            event_summary.append({
                'Year': event['year'],
                'Type': event['type'].replace('_', ' ').title(),
                'Description': event['name'],
                'Details': details
            })
        
        events_df = pd.DataFrame(event_summary)
        st.dataframe(events_df, use_container_width=True, hide_index=True)
    
    # Show instructions
    st.markdown("---")
    
    # Show instructions
    st.markdown("---")
    st.markdown("""
    ### How to Use This Tool
    
    1. **Set Initial Position**: Enter your current liquid wealth, property value, and mortgage balance
    2. **Configure Income & Tax**: Set gross income, tax rate, and pension contribution rate
    3. **Monthly Budget**: Enter living expenses, mortgage payment, and monthly savings amount
    4. **Property Assumptions**: Set expected property appreciation and mortgage interest rate
    5. **Investment Returns**: Configure expected portfolio returns and volatility
    6. **Inflation**: Set inflation expectations and variability
    7. **Add Major Events**: Include large transactions like property purchases, relocations, windfalls
    8. **Run Simulation**: Click the button to generate Monte Carlo paths
    
    The simulation will show you:
    - Total net worth evolution (liquid + pension + property equity)
    - Separate views for each wealth component
    - Range of possible outcomes (percentile bands)
    - Wealth composition breakdown over time
    - Probability of reaching various milestones
    - Distributions at key future dates
    
    **Tips:**
    - Verify your cash flows balance in the summary above
    - Use "Real" values to understand purchasing power
    - Add major events for property transactions, relocations, etc.
    - Compare different scenarios by adjusting parameters and re-running
    """)