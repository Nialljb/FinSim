"""
Monte Carlo Simulation Engine
Extracted from wealth_simulator.py for better testability and reusability.
"""
import numpy as np


def run_monte_carlo(initial_liquid_wealth, initial_property_value, initial_mortgage,
                    gross_annual_income, effective_tax_rate, pension_contribution_rate,
                    monthly_expenses, monthly_mortgage_payment,
                    property_appreciation, mortgage_interest_rate,
                    expected_return, return_volatility, expected_inflation, inflation_volatility,
                    salary_inflation, years, n_simulations, events, random_seed,
                    starting_age=30, retirement_age=65, pension_income=0, passive_income_streams=None,
                    include_spouse=False, spouse_age=None, spouse_retirement_age=None, spouse_annual_income=0):
    """Run Monte Carlo simulation for wealth paths
    
    Args:
        initial_liquid_wealth: Starting liquid assets (cash, investments, etc.)
        initial_property_value: Starting property value
        initial_mortgage: Starting mortgage balance
        gross_annual_income: Annual gross income
        effective_tax_rate: Tax rate as decimal (e.g., 0.25 for 25%)
        pension_contribution_rate: Pension contribution rate as decimal
        monthly_expenses: Monthly living expenses
        monthly_mortgage_payment: Monthly mortgage payment
        property_appreciation: Annual property appreciation rate
        mortgage_interest_rate: Annual mortgage interest rate
        expected_return: Expected annual investment return
        return_volatility: Investment return volatility (standard deviation)
        expected_inflation: Expected annual inflation rate
        inflation_volatility: Inflation volatility (standard deviation)
        salary_inflation: Annual salary growth rate
        years: Number of years to simulate
        n_simulations: Number of Monte Carlo paths to generate
        events: List of financial events (property purchases, sales, etc.)
        random_seed: Random seed for reproducibility
        starting_age: Current age
        retirement_age: Age when employment income stops
        pension_income: Annual pension income after retirement (in base currency)
        passive_income_streams: List of passive income stream objects
        include_spouse: Whether to include spouse in simulation
        spouse_age: Current age of spouse
        spouse_retirement_age: Retirement age of spouse
        spouse_annual_income: Spouse's annual gross income
        
    Returns:
        Dictionary containing simulation results:
        - net_worth: Total net worth paths (n_simulations x years+1)
        - real_net_worth: Inflation-adjusted net worth paths
        - liquid_wealth: Liquid wealth paths
        - pension_wealth: Pension wealth paths
        - property_value: Property value paths
        - mortgage_balance: Mortgage balance paths
        - inflation_rates: Inflation rates used (n_simulations x years)
    """
    np.random.seed(random_seed)
    
    # Initialize wealth tracking arrays
    liquid_wealth_paths = np.zeros((n_simulations, years + 1))
    property_value_paths = np.zeros((n_simulations, years + 1))
    mortgage_balance_paths = np.zeros((n_simulations, years + 1))
    pension_wealth_paths = np.zeros((n_simulations, years + 1))
    
    # Track monthly cash flows
    monthly_expenses_tracker = np.full((n_simulations, years + 1), monthly_expenses, dtype=float)
    monthly_mortgage_tracker = np.full((n_simulations, years + 1), monthly_mortgage_payment, dtype=float)
    monthly_rental_tracker = np.zeros((n_simulations, years + 1))
    monthly_passive_income_tracker = np.zeros((n_simulations, years + 1))
    
    # Initialize passive income streams
    if passive_income_streams is None:
        passive_income_streams = []
    
    # Set initial values
    liquid_wealth_paths[:, 0] = initial_liquid_wealth
    property_value_paths[:, 0] = initial_property_value
    mortgage_balance_paths[:, 0] = initial_mortgage
    pension_wealth_paths[:, 0] = 0
    
    net_worth_paths = np.zeros((n_simulations, years + 1))
    net_worth_paths[:, 0] = initial_liquid_wealth + initial_property_value - initial_mortgage
    
    real_net_worth_paths = np.zeros((n_simulations, years + 1))
    real_net_worth_paths[:, 0] = net_worth_paths[:, 0]
    
    # Generate random returns and inflation for all simulations
    portfolio_returns = np.random.normal(expected_return, return_volatility, (n_simulations, years))
    pension_returns = np.random.normal(expected_return, return_volatility, (n_simulations, years))
    inflation_rates = np.random.normal(expected_inflation, inflation_volatility, (n_simulations, years))
    inflation_rates = np.maximum(inflation_rates, -0.05)  # Floor inflation at -5%
    
    # Organize events by year for efficient lookup
    events_by_year = {}
    for event in events:
        year = event['year']
        if year not in events_by_year:
            events_by_year[year] = []
        events_by_year[year].append(event)
    
    # Simulate each year
    for year in range(1, years + 1):
        # Calculate cumulative inflation and salary growth
        cumulative_inflation = np.prod(1 + inflation_rates[:, :year], axis=1)
        cumulative_salary_growth = (1 + salary_inflation) ** year
        
        # Get current tracked values
        current_monthly_expenses = monthly_expenses_tracker[:, year - 1]
        current_monthly_mortgage = monthly_mortgage_tracker[:, year - 1]
        current_monthly_rental = monthly_rental_tracker[:, year - 1]
        current_monthly_passive = monthly_passive_income_tracker[:, year - 1]
        
        # Calculate passive income for this year
        year_passive_income = 0
        for stream in passive_income_streams:
            # Check if stream is active this year
            if stream.start_year <= year and (stream.end_year is None or year <= stream.end_year):
                # Calculate growth since start
                years_active = year - stream.start_year
                growth_factor = (1 + stream.annual_growth_rate) ** years_active
                stream_annual_amount = stream.monthly_amount * 12 * growth_factor
                
                # Apply tax if applicable
                if stream.is_taxable:
                    tax_rate = stream.tax_rate if stream.tax_rate is not None else effective_tax_rate
                    stream_annual_amount *= (1 - tax_rate)
                
                year_passive_income += stream_annual_amount
        
        # Passive income is the same for all simulation paths (not random)
        # Adjust for inflation to get real value
        year_passive_income_adjusted = year_passive_income * cumulative_inflation
        
        # Calculate current age for this year
        current_age = starting_age + year
        
        # Determine if in retirement
        is_retired = current_age > retirement_age
        
        # Calculate spouse current age and retirement status (if applicable)
        spouse_is_retired = False
        if include_spouse and spouse_age is not None and spouse_retirement_age is not None:
            spouse_current_age = spouse_age + year
            spouse_is_retired = spouse_current_age > spouse_retirement_age
        
        # Calculate household income
        year_gross_income = 0
        year_pension_contribution = 0
        year_take_home = 0
        
        # Primary income
        if not is_retired:
            # Pre-retirement: employment income
            primary_gross = gross_annual_income * cumulative_salary_growth
            primary_pension_contrib = primary_gross * pension_contribution_rate
            primary_take_home = primary_gross * (1 - effective_tax_rate - pension_contribution_rate)
            
            year_gross_income += primary_gross
            year_pension_contribution += primary_pension_contrib
            year_take_home += primary_take_home
        else:
            # Post-retirement: pension income only
            years_since_retirement = current_age - retirement_age
            retirement_inflation = np.prod(1 + inflation_rates[:, retirement_age-starting_age:year], axis=1) if years_since_retirement > 0 else 1.0
            year_take_home += pension_income * retirement_inflation
        
        # Spouse income (if enabled)
        if include_spouse and spouse_annual_income > 0:
            if not spouse_is_retired:
                # Spouse working: employment income
                spouse_gross = spouse_annual_income * cumulative_salary_growth
                spouse_pension_contrib = spouse_gross * pension_contribution_rate
                spouse_take_home = spouse_gross * (1 - effective_tax_rate - pension_contribution_rate)
                
                year_gross_income += spouse_gross
                year_pension_contribution += spouse_pension_contrib
                year_take_home += spouse_take_home
            # Note: spouse pension income will be handled separately via pension planner integration
        
        # Calculate annual expenses and income
        year_expenses = current_monthly_expenses * 12 * cumulative_inflation
        year_mortgage_payment = current_monthly_mortgage * 12
        year_rental_income = current_monthly_rental * 12 * cumulative_inflation
        
        year_available_savings = year_take_home + year_rental_income + year_passive_income_adjusted - year_expenses - year_mortgage_payment
        
        # Update pension wealth
        if not is_retired:
            # Pre-retirement: accumulate contributions
            pension_wealth_paths[:, year] = (
                pension_wealth_paths[:, year - 1] * (1 + pension_returns[:, year - 1]) +
                year_pension_contribution
            )
        else:
            # Post-retirement: draw down pension income from the pot
            if pension_income > 0:
                # Calculate inflation-adjusted withdrawal amount
                years_since_retirement = current_age - retirement_age
                retirement_inflation = np.prod(1 + inflation_rates[:, retirement_age-starting_age:year], axis=1) if years_since_retirement > 0 else 1.0
                pension_withdrawal = pension_income * retirement_inflation
                
                # Apply growth first to beginning balance
                after_growth = pension_wealth_paths[:, year - 1] * (1 + pension_returns[:, year - 1])
                
                # Then withdraw (can't withdraw more than available after growth)
                pension_withdrawal = np.minimum(pension_withdrawal, after_growth)
                pension_wealth_paths[:, year] = after_growth - pension_withdrawal
            else:
                # No pension income configured, pot just grows
                pension_wealth_paths[:, year] = (
                    pension_wealth_paths[:, year - 1] * (1 + pension_returns[:, year - 1])
                )
        
        # Update liquid wealth
        liquid_wealth_paths[:, year] = (
            liquid_wealth_paths[:, year - 1] * (1 + portfolio_returns[:, year - 1]) +
            year_available_savings
        )
        
        # Update property value
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
        
        # Process financial events for this year
        if year in events_by_year:
            for event in events_by_year[year]:
                if event['type'] == 'property_purchase':
                    liquid_wealth_paths[:, year] -= event['down_payment']
                    property_value_paths[:, year] += event['property_price']
                    mortgage_balance_paths[:, year] += event['mortgage_amount']
                    # Add new mortgage payment to existing payment (supports multiple properties)
                    new_total_payment = current_monthly_mortgage + event['new_mortgage_payment']
                    # Broadcast the new payment to all remaining years
                    remaining_years = years + 1 - year
                    monthly_mortgage_tracker[:, year:] = np.repeat(new_total_payment[:, np.newaxis], remaining_years, axis=1)
                    
                elif event['type'] == 'property_sale':
                    net_proceeds = (event['sale_price'] - event['mortgage_payoff'] - event['selling_costs'])
                    liquid_wealth_paths[:, year] += net_proceeds
                    property_value_paths[:, year] = 0
                    mortgage_balance_paths[:, year] = np.maximum(
                        mortgage_balance_paths[:, year] - event['mortgage_payoff'], 0
                    )
                    if event['mortgage_payoff'] >= mortgage_balance_paths[:, year].mean():
                        monthly_mortgage_tracker[:, year:] = 0
                    
                elif event['type'] == 'one_time_expense':
                    liquid_wealth_paths[:, year] -= event['amount']
                    
                elif event['type'] == 'expense_change':
                    monthly_expenses_tracker[:, year:] += event['monthly_change']
                    
                elif event['type'] == 'rental_income':
                    monthly_rental_tracker[:, year:] += event['monthly_rental']
                    
                elif event['type'] == 'windfall':
                    liquid_wealth_paths[:, year] += event['amount']
        
        # Calculate total net worth
        net_worth_paths[:, year] = (
            liquid_wealth_paths[:, year] +
            pension_wealth_paths[:, year] +
            property_value_paths[:, year] -
            mortgage_balance_paths[:, year]
        )
        
        # Calculate real (inflation-adjusted) net worth
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


def calculate_mortgage_payment(principal, annual_rate, years):
    """Calculate monthly mortgage payment using standard amortization formula
    
    Args:
        principal: Loan amount
        annual_rate: Annual interest rate as decimal (e.g., 0.035 for 3.5%)
        years: Loan term in years
        
    Returns:
        Monthly payment amount
    """
    if principal <= 0 or years <= 0:
        return 0
    
    monthly_rate = annual_rate / 12
    n_payments = years * 12
    
    if monthly_rate > 0:
        payment = principal * (monthly_rate * (1 + monthly_rate)**n_payments) / ((1 + monthly_rate)**n_payments - 1)
    else:
        payment = principal / n_payments
    
    return payment
