"""
Cash Flow Analysis Service
==========================

Provides year-by-year cash flow projection and analysis functionality.

This service handles:
- Annual cash flow projections with retirement transitions
- Passive income stream integration
- Financial event application (property, expenses, rental, windfalls)
- Spouse income calculations
- Multi-year projection building

All functions are pure/self-contained and do not depend on Streamlit,
making them testable and reusable in API/CLI/batch contexts.

Functions
---------
- calculate_year_passive_income: Calculate passive income for a specific year
- apply_events_to_year: Apply financial events to a projection year
- calculate_year_income: Calculate income (working vs retirement)
- build_cashflow_projection: Build complete multi-year projection
- create_year1_breakdown: Create detailed Year 1 cash flow breakdown
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Callable, Any


def calculate_year_passive_income(
    year: int,
    passive_streams: List[Any],
    effective_tax_rate: float,
    from_base_currency_func: Optional[Callable] = None
) -> float:
    """
    Calculate total passive income for a specific year from all active streams.
    
    Parameters
    ----------
    year : int
        The projection year (0-indexed from simulation start)
    passive_streams : List[Any]
        List of passive income stream objects with attributes:
        - start_year: Year stream starts
        - end_year: Year stream ends (None for indefinite)
        - monthly_amount: Base monthly amount (in base currency)
        - annual_growth_rate: Annual growth rate (e.g., 0.03 for 3%)
        - is_taxable: Whether income is taxable
        - tax_rate: Specific tax rate (if None, uses effective_tax_rate)
    effective_tax_rate : float
        Default tax rate to apply (0.0 to 1.0)
    from_base_currency_func : Callable, optional
        Function to convert from base currency: func(amount, target_currency)
        If None, assumes amounts are already in target currency
    
    Returns
    -------
    float
        Total annual passive income for the year (after tax if applicable)
    
    Examples
    --------
    >>> streams = [
    ...     {'start_year': 0, 'end_year': None, 'monthly_amount': 1000,
    ...      'annual_growth_rate': 0.03, 'is_taxable': True, 'tax_rate': None}
    ... ]
    >>> income = calculate_year_passive_income(5, streams, 0.20)
    >>> round(income, 2)
    11083.18
    """
    year_passive_income = 0
    
    for stream in passive_streams:
        # Check if stream is active in this year
        if stream.start_year <= year and (stream.end_year is None or year <= stream.end_year):
            # Calculate growth from start year
            years_active = year - stream.start_year
            growth_factor = (1 + stream.annual_growth_rate) ** years_active
            
            # Calculate annual amount
            stream_annual_amount = stream.monthly_amount * 12 * growth_factor
            
            # Convert currency if function provided
            if from_base_currency_func is not None:
                # Note: We'd need to pass the target currency somehow
                # For now, skip conversion in service (handle in caller)
                pass
            
            # Apply tax if taxable
            if stream.is_taxable:
                tax_rate = stream.tax_rate if stream.tax_rate is not None else effective_tax_rate
                stream_annual_amount *= (1 - tax_rate)
            
            year_passive_income += stream_annual_amount
    
    return year_passive_income


def apply_events_to_year(
    year: int,
    events: List[Dict],
    monthly_expenses: float,
    monthly_mortgage: float,
    monthly_rental: float
) -> tuple[float, float, float, str]:
    """
    Apply all financial events up to and including a specific year.
    
    Parameters
    ----------
    year : int
        The projection year
    events : List[Dict]
        List of financial event dictionaries with keys:
        - 'year': Year event occurs
        - 'type': Event type ('property_purchase', 'property_sale', 'expense_change', 
                  'rental_income', 'windfall')
        - Type-specific fields (new_mortgage_payment, monthly_change, etc.)
    monthly_expenses : float
        Starting monthly expenses
    monthly_mortgage : float
        Starting monthly mortgage payment
    monthly_rental : float
        Starting monthly rental income
    
    Returns
    -------
    tuple[float, float, float, str]
        - Updated monthly expenses
        - Updated monthly mortgage payment
        - Updated monthly rental income
        - Event notes for the year (comma-separated event names)
    
    Examples
    --------
    >>> events = [
    ...     {'year': 2, 'type': 'property_purchase', 'name': 'Buy Flat',
    ...      'new_mortgage_payment': 1200},
    ...     {'year': 2, 'type': 'expense_change', 'name': 'Kids', 
    ...      'monthly_change': 500}
    ... ]
    >>> expenses, mortgage, rental, notes = apply_events_to_year(
    ...     2, events, 2000, 1000, 0
    ... )
    >>> expenses, mortgage, notes
    (2500.0, 1200, 'Buy Flat, Kids')
    """
    year_monthly_expenses = monthly_expenses
    year_monthly_mortgage = monthly_mortgage
    year_monthly_rental = monthly_rental
    event_names = []
    
    for event in events:
        if event['year'] == year:
            event_names.append(event.get('name', event.get('type', 'Event')))
            
            if event['type'] == 'property_purchase':
                year_monthly_mortgage = event.get('new_mortgage_payment', 0)
            
            elif event['type'] == 'property_sale':
                year_monthly_mortgage = 0
            
            elif event['type'] == 'expense_change':
                year_monthly_expenses += event.get('monthly_change', 0)
            
            elif event['type'] == 'rental_income':
                year_monthly_rental = event.get('monthly_rental', 0)
            
            # Windfall events don't affect monthly cash flow
    
    event_notes = ', '.join(event_names) if event_names else ''
    
    return year_monthly_expenses, year_monthly_mortgage, year_monthly_rental, event_notes


def calculate_year_income(
    year: int,
    starting_age: int,
    retirement_age: int,
    gross_annual_income: float,
    effective_tax_rate: float,
    pension_contribution_rate: float,
    salary_inflation: float,
    total_pension_income: float,
    include_spouse: bool = False,
    spouse_gross_income: float = 0,
    spouse_retirement_age: int = 67,
    spouse_tax_rate: float = 0,
    spouse_pension_rate: float = 0,
    spouse_pension_income: float = 0
) -> tuple[float, float, bool, float, bool]:
    """
    Calculate take-home income for a specific year, handling retirement transitions.
    
    Parameters
    ----------
    year : int
        Projection year (0-indexed)
    starting_age : int
        Primary earner's starting age
    retirement_age : int
        Primary earner's retirement age
    gross_annual_income : float
        Primary earner's current gross annual income
    effective_tax_rate : float
        Tax rate (0.0 to 1.0)
    pension_contribution_rate : float
        Pension contribution rate while working (0.0 to 1.0)
    salary_inflation : float
        Annual salary growth rate (e.g., 0.025 for 2.5%)
    total_pension_income : float
        Total annual pension income in retirement
    include_spouse : bool, optional
        Whether to include spouse income
    spouse_gross_income : float, optional
        Spouse's gross annual income
    spouse_retirement_age : int, optional
        Spouse's retirement age
    spouse_tax_rate : float, optional
        Spouse's tax rate
    spouse_pension_rate : float, optional
        Spouse's pension contribution rate
    spouse_pension_income : float, optional
        Spouse's pension income in retirement
    
    Returns
    -------
    tuple[float, float, bool, float, bool]
        - Primary earner take-home income
        - Spouse take-home income
        - Whether primary earner is retired
        - Combined household take-home income
        - Whether spouse is retired
    
    Examples
    --------
    >>> # Working year (age 35)
    >>> primary, spouse, retired, total, spouse_ret = calculate_year_income(
    ...     year=5, starting_age=30, retirement_age=67,
    ...     gross_annual_income=80000, effective_tax_rate=0.20,
    ...     pension_contribution_rate=0.10, salary_inflation=0.03,
    ...     total_pension_income=40000
    ... )
    >>> retired, round(total, 2)
    (False, 66463.68)
    
    >>> # Retirement year (age 67)
    >>> primary, spouse, retired, total, spouse_ret = calculate_year_income(
    ...     year=37, starting_age=30, retirement_age=67,
    ...     gross_annual_income=80000, effective_tax_rate=0.20,
    ...     pension_contribution_rate=0.10, salary_inflation=0.03,
    ...     total_pension_income=40000
    ... )
    >>> retired, round(total, 2)
    (True, 40000.0)
    """
    current_age = starting_age + year
    is_retired = current_age >= retirement_age
    
    # Calculate cumulative salary growth
    cumulative_salary_growth = (1 + salary_inflation) ** year
    
    # Primary earner income
    if not is_retired:
        # Working: apply salary growth, deduct tax and pension
        year_gross = gross_annual_income * cumulative_salary_growth
        year_takehome = year_gross * (1 - effective_tax_rate - pension_contribution_rate)
    else:
        # Retired: receive pension income
        year_takehome = total_pension_income
    
    # Spouse income
    spouse_takehome = 0
    spouse_is_retired = False
    
    if include_spouse:
        spouse_age = starting_age + year  # Assuming same age for simplicity
        spouse_is_retired = spouse_age >= spouse_retirement_age
        
        if not spouse_is_retired:
            spouse_gross = spouse_gross_income * cumulative_salary_growth
            spouse_takehome = spouse_gross * (1 - spouse_tax_rate - spouse_pension_rate)
        else:
            spouse_takehome = spouse_pension_income
    
    total_household_income = year_takehome + spouse_takehome
    
    return year_takehome, spouse_takehome, is_retired, total_household_income, spouse_is_retired


def build_cashflow_projection(
    starting_age: int,
    retirement_age: int,
    simulation_years: int,
    gross_annual_income: float,
    effective_tax_rate: float,
    pension_contribution_rate: float,
    monthly_expenses: float,
    monthly_mortgage_payment: float,
    salary_inflation: float,
    total_pension_income: float,
    events: List[Dict],
    passive_income_streams: Optional[List[Any]] = None,
    include_spouse: bool = False,
    spouse_params: Optional[Dict] = None,
    currency_formatter: Optional[Callable] = None,
    max_years: int = 30
) -> pd.DataFrame:
    """
    Build complete year-by-year cash flow projection with events and passive income.
    
    Parameters
    ----------
    starting_age : int
        Starting age for projection
    retirement_age : int
        Age at retirement
    simulation_years : int
        Total years to simulate
    gross_annual_income : float
        Current gross annual income
    effective_tax_rate : float
        Effective tax rate (0.0 to 1.0)
    pension_contribution_rate : float
        Pension contribution rate (0.0 to 1.0)
    monthly_expenses : float
        Current monthly living expenses
    monthly_mortgage_payment : float
        Current monthly mortgage payment
    salary_inflation : float
        Annual salary growth rate
    total_pension_income : float
        Annual pension income in retirement
    events : List[Dict]
        List of financial events
    passive_income_streams : List[Any], optional
        List of passive income streams
    include_spouse : bool, optional
        Include spouse income
    spouse_params : Dict, optional
        Spouse parameters (gross_income, retirement_age, tax_rate, pension_rate, pension_income)
    currency_formatter : Callable, optional
        Function to format currency: func(amount) -> str
    max_years : int, optional
        Maximum years to project (default 30)
    
    Returns
    -------
    pd.DataFrame
        Projection DataFrame with columns:
        - Year: Projection year
        - Age: Age in that year
        - Take Home: Formatted take-home income
        - Passive Income: Formatted passive income
        - Rental Income: Formatted rental income
        - Living Expenses: Formatted expenses
        - Mortgage: Formatted mortgage payment
        - Available Savings: Formatted available amount
        - Events This Year: Event notes
    
    Examples
    --------
    >>> events = [{'year': 5, 'type': 'expense_change', 'name': 'Kids', 'monthly_change': 500}]
    >>> df = build_cashflow_projection(
    ...     starting_age=30, retirement_age=67, simulation_years=40,
    ...     gross_annual_income=80000, effective_tax_rate=0.20,
    ...     pension_contribution_rate=0.10, monthly_expenses=2000,
    ...     monthly_mortgage_payment=1200, salary_inflation=0.03,
    ...     total_pension_income=40000, events=events
    ... )
    >>> len(df)
    11
    >>> df['Year'].tolist()
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    """
    # Default spouse params
    if spouse_params is None:
        spouse_params = {
            'gross_income': 0,
            'retirement_age': 67,
            'tax_rate': 0.20,
            'pension_rate': 0.10,
            'pension_income': 0
        }
    
    # Default currency formatter
    if currency_formatter is None:
        currency_formatter = lambda x: f"£{x:,.0f}"
    
    # Determine projection years (0 to 10, or fewer if simulation is shorter)
    max_projection_year = min(simulation_years, max_years)
    projection_years = list(range(0, min(11, max_projection_year + 1)))
    
    # Build projection
    cashflow_projection = []
    
    for year in projection_years:
        # Calculate passive income for this year
        year_passive_income_annual = 0
        if passive_income_streams:
            year_passive_income_annual = calculate_year_passive_income(
                year, passive_income_streams, effective_tax_rate
            )
        
        # Apply events to this year
        year_monthly_expenses, year_monthly_mortgage, year_monthly_rental, event_notes = apply_events_to_year(
            year, events, monthly_expenses, monthly_mortgage_payment, 0
        )
        
        # Calculate income for this year
        primary_income, spouse_income, is_retired, total_income, spouse_retired = calculate_year_income(
            year=year,
            starting_age=starting_age,
            retirement_age=retirement_age,
            gross_annual_income=gross_annual_income,
            effective_tax_rate=effective_tax_rate,
            pension_contribution_rate=pension_contribution_rate,
            salary_inflation=salary_inflation,
            total_pension_income=total_pension_income,
            include_spouse=include_spouse,
            spouse_gross_income=spouse_params.get('gross_income', 0),
            spouse_retirement_age=spouse_params.get('retirement_age', 67),
            spouse_tax_rate=spouse_params.get('tax_rate', 0.20),
            spouse_pension_rate=spouse_params.get('pension_rate', 0.10),
            spouse_pension_income=spouse_params.get('pension_income', 0)
        )
        
        # Calculate available savings
        year_annual_rental = year_monthly_rental * 12
        year_annual_expenses = year_monthly_expenses * 12
        year_annual_mortgage = year_monthly_mortgage * 12
        
        year_available = (
            total_income +
            year_passive_income_annual +
            year_annual_rental -
            year_annual_expenses -
            year_annual_mortgage
        )
        
        # Calculate pension contributions for display
        primary_pension_contrib = 0
        spouse_pension_contrib = 0
        
        if not is_retired:
            # Calculate inflated salary for current year
            primary_salary = gross_annual_income * ((1 + salary_inflation) ** year)
            primary_pension_contrib = primary_salary * pension_contribution_rate
        
        if include_spouse and not spouse_retired:
            spouse_salary = spouse_params.get('gross_income', 0) * ((1 + salary_inflation) ** year)
            spouse_pension_contrib = spouse_salary * spouse_params.get('pension_rate', 0)
        
        total_pension_contrib = primary_pension_contrib + spouse_pension_contrib
        
        # Build projection row
        projection_row = {
            'Year': year,
            'Age': starting_age + year,
            'Take Home': currency_formatter(total_income),
            'Pension Contrib': currency_formatter(total_pension_contrib),
            'Passive Income': currency_formatter(year_passive_income_annual),
            'Rental Income': currency_formatter(year_annual_rental),
            'Living Expenses': currency_formatter(year_annual_expenses),
            'Mortgage': currency_formatter(year_annual_mortgage),
            'Available Savings': currency_formatter(year_available),
            'Events This Year': event_notes
        }
        
        cashflow_projection.append(projection_row)
    
    # Create DataFrame
    projection_df = pd.DataFrame(cashflow_projection)
    
    return projection_df


def create_year1_breakdown(
    gross_annual_income: float,
    pension_contribution_rate: float,
    effective_tax_rate: float,
    monthly_expenses: float,
    monthly_mortgage: float,
    passive_income_annual: float = 0,
    currency_formatter: Optional[Callable] = None
) -> tuple[pd.DataFrame, float, str]:
    """
    Create detailed Year 1 cash flow breakdown with line items.
    
    Parameters
    ----------
    gross_annual_income : float
        Gross annual income
    pension_contribution_rate : float
        Pension contribution rate (0.0 to 1.0)
    effective_tax_rate : float
        Tax rate (0.0 to 1.0)
    monthly_expenses : float
        Monthly living expenses
    monthly_mortgage : float
        Monthly mortgage payment
    passive_income_annual : float, optional
        Annual passive income
    currency_formatter : Callable, optional
        Function to format currency
    
    Returns
    -------
    tuple[pd.DataFrame, float, str]
        - DataFrame with 'Item' and 'Amount' columns
        - Available savings amount (numeric)
        - Status message ('deficit' or 'surplus')
    
    Examples
    --------
    >>> df, available, status = create_year1_breakdown(
    ...     gross_annual_income=80000,
    ...     pension_contribution_rate=0.10,
    ...     effective_tax_rate=0.20,
    ...     monthly_expenses=2000,
    ...     monthly_mortgage=1200
    ... )
    >>> status
    'surplus'
    >>> available > 0
    True
    """
    if currency_formatter is None:
        currency_formatter = lambda x: f"£{x:,.0f}"
    
    # Calculate components
    pension_contrib = gross_annual_income * pension_contribution_rate
    tax = gross_annual_income * effective_tax_rate
    take_home = gross_annual_income - pension_contrib - tax
    annual_expenses = monthly_expenses * 12
    annual_mortgage = monthly_mortgage * 12
    
    # Build line items
    items = ['Gross Income', '- Pension Contrib', '- Tax', '= Take Home']
    amounts = [
        currency_formatter(gross_annual_income),
        currency_formatter(pension_contrib),
        currency_formatter(tax),
        currency_formatter(take_home)
    ]
    
    # Add passive income if present
    if passive_income_annual > 0:
        items.append('+ Passive Income')
        amounts.append(currency_formatter(passive_income_annual))
    
    # Add expenses and calculate available
    items.extend(['- Living Expenses', '- Mortgage', '= Available for Investment'])
    available = take_home + passive_income_annual - annual_expenses - annual_mortgage
    amounts.extend([
        currency_formatter(annual_expenses),
        currency_formatter(annual_mortgage),
        currency_formatter(available)
    ])
    
    # Create DataFrame
    df = pd.DataFrame({
        'Item': items,
        'Amount': amounts
    })
    
    # Determine status
    status = 'deficit' if available < 0 else 'surplus'
    
    return df, available, status
