"""
UK Pension Planning Module for FinSim
Handles State Pension, USS, and SIPP calculations
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ============================================================================
# UK STATE PENSION CONSTANTS (2025/26 Tax Year)
# ============================================================================

STATE_PENSION_FULL_AMOUNT = 11502.40  # Annual full new State Pension 2025/26
STATE_PENSION_WEEKLY = 221.20  # Weekly amount
STATE_PENSION_AGE_DEFAULT = 67  # Current UK State Pension age
QUALIFYING_YEARS_FULL = 35  # Years needed for full State Pension
QUALIFYING_YEARS_MIN = 10  # Minimum years for any State Pension

# National Insurance thresholds 2025/26
NI_LOWER_EARNINGS_LIMIT = 6396  # Annual
NI_PRIMARY_THRESHOLD = 12570  # Annual (when you start paying NI)
NI_UPPER_EARNINGS_LIMIT = 50270  # Annual


# ============================================================================
# USS PENSION CONSTANTS (Universities Superannuation Scheme)
# ============================================================================

USS_ACCRUAL_RATE = 1/85  # Builds up 1/85th of salary per year
USS_LUMP_SUM_MULTIPLE = 3  # Can take 3x pension as lump sum
USS_EMPLOYER_CONTRIBUTION = 0.145  # 14.5% employer contribution
USS_EMPLOYEE_CONTRIBUTION = 0.061  # 6.1% employee contribution (flat rate)
USS_THRESHOLD = 43143  # USS threshold salary 2024/25 (for reference)
USS_REVALUATION_RATE = 0.025  # CPI + 2.5% (approximate)
USS_RETIREMENT_AGE = 65  # Normal pension age


# ============================================================================
# SIPP CONSTANTS (Self-Invested Personal Pension)
# ============================================================================

SIPP_TAX_RELIEF_BASIC = 0.20  # 20% basic rate tax relief
SIPP_TAX_RELIEF_HIGHER = 0.40  # 40% higher rate tax relief
SIPP_TAX_RELIEF_ADDITIONAL = 0.45  # 45% additional rate tax relief
SIPP_ANNUAL_ALLOWANCE = 60000  # Annual allowance 2025/26
SIPP_LIFETIME_ALLOWANCE_ABOLISHED = True  # Abolished April 2024
SIPP_MIN_PENSION_AGE = 55  # Rising to 57 in 2028
SIPP_LUMP_SUM_TAX_FREE = 0.25  # 25% tax-free lump sum


# ============================================================================
# UK STATE PENSION CALCULATOR
# ============================================================================

def calculate_state_pension_age(date_of_birth):
    """
    Calculate UK State Pension age based on date of birth
    
    Args:
        date_of_birth: datetime.date object
        
    Returns:
        int: State Pension age
    """
    birth_year = date_of_birth.year
    birth_month = date_of_birth.month
    
    # Current rules (simplified - actual rules more complex)
    if birth_year < 1954:
        return 65
    elif birth_year < 1960:
        return 66
    elif birth_year < 1977:
        if birth_year < 1961:
            return 66
        return 67
    else:
        return 68  # Proposed for those born after 1977
    
    return 67  # Default


def estimate_ni_qualifying_years(current_age, employment_start_age=18, current_employment_status="Employed"):
    """
    Estimate National Insurance qualifying years
    
    Args:
        current_age: Current age
        employment_start_age: Age started working
        current_employment_status: Employment status
        
    Returns:
        int: Estimated qualifying years
    """
    if current_employment_status in ["Employed", "Self-Employed"]:
        years_worked = max(0, current_age - employment_start_age)
        return min(years_worked, QUALIFYING_YEARS_FULL)
    elif current_employment_status == "Unemployed (claiming credits)":
        # May still get NI credits
        years_worked = max(0, current_age - employment_start_age)
        return min(years_worked * 0.8, QUALIFYING_YEARS_FULL)  # Reduced estimate
    else:
        return 0


def calculate_state_pension_amount(qualifying_years):
    """
    Calculate annual State Pension based on qualifying years
    
    Args:
        qualifying_years: Number of NI qualifying years
        
    Returns:
        float: Annual State Pension amount
    """
    if qualifying_years < QUALIFYING_YEARS_MIN:
        return 0
    
    if qualifying_years >= QUALIFYING_YEARS_FULL:
        return STATE_PENSION_FULL_AMOUNT
    
    # Pro-rata for partial years
    return STATE_PENSION_FULL_AMOUNT * (qualifying_years / QUALIFYING_YEARS_FULL)


def forecast_state_pension(date_of_birth, current_ni_years, projected_future_years):
    """
    Forecast State Pension at retirement
    
    Args:
        date_of_birth: Date of birth
        current_ni_years: Current NI qualifying years
        projected_future_years: Additional years expected to contribute
        
    Returns:
        dict: Pension forecast details
    """
    pension_age = calculate_state_pension_age(date_of_birth)
    total_years = min(current_ni_years + projected_future_years, QUALIFYING_YEARS_FULL)
    annual_amount = calculate_state_pension_amount(total_years)
    
    return {
        'pension_age': pension_age,
        'qualifying_years': total_years,
        'annual_amount': annual_amount,
        'weekly_amount': annual_amount / 52,
        'monthly_amount': annual_amount / 12,
        'is_full_pension': total_years >= QUALIFYING_YEARS_FULL
    }


# ============================================================================
# USS PENSION CALCULATOR
# ============================================================================

def calculate_uss_contributions(salary, years_in_scheme, avc_amount=0):
    """
    Calculate USS pension contributions
    
    Args:
        salary: Annual salary
        years_in_scheme: Years of USS membership
        avc_amount: Annual Additional Voluntary Contribution (goes to investment builder)
        
    Returns:
        dict: Contribution details
    """
    # Employee contributions (flat 6.1% rate)
    employee_contribution = salary * USS_EMPLOYEE_CONTRIBUTION
    
    # Employer contributions (flat 14.5% rate)
    employer_contribution = salary * USS_EMPLOYER_CONTRIBUTION
    
    # Total annual contributions (standard USS only)
    total_contribution = employee_contribution + employer_contribution
    
    # Calculate rates (avoid division by zero)
    employee_rate = (employee_contribution / salary) * 100 if salary > 0 else 0
    total_rate = (total_contribution / salary) * 100 if salary > 0 else 0
    avc_rate = (avc_amount / salary) * 100 if salary > 0 else 0
    
    return {
        'employee_annual': employee_contribution,
        'employee_monthly': employee_contribution / 12,
        'employer_annual': employer_contribution,
        'employer_monthly': employer_contribution / 12,
        'total_annual': total_contribution,
        'total_monthly': total_contribution / 12,
        'employee_rate': employee_rate,
        'employer_rate': USS_EMPLOYER_CONTRIBUTION * 100,
        'total_rate': total_rate,
        'avc_annual': avc_amount,
        'avc_monthly': avc_amount / 12,
        'avc_rate': avc_rate
    }


def calculate_uss_pension_value(salary, years_in_scheme, salary_history=None):
    """
    Calculate USS pension value at retirement
    
    Args:
        salary: Final salary (or current if projecting)
        years_in_scheme: Total years in USS
        salary_history: Optional list of annual salaries for more accurate calculation
        
    Returns:
        dict: Pension value details
    """
    # Simple calculation: 1/85th of salary per year
    annual_pension = (salary * years_in_scheme) / 85
    
    # Optional lump sum (3x annual pension)
    lump_sum_available = annual_pension * USS_LUMP_SUM_MULTIPLE
    
    # If taking maximum lump sum, pension reduces
    reduced_annual_pension = 0  # Taking max lump sum means no annual pension in this simple model
    # In reality, you can take partial lump sum - this is simplified
    
    return {
        'annual_pension': annual_pension,
        'monthly_pension': annual_pension / 12,
        'lump_sum_available': lump_sum_available,
        'years_in_scheme': years_in_scheme,
        'accrual_rate': USS_ACCRUAL_RATE,
        'retirement_age': USS_RETIREMENT_AGE
    }


def project_uss_pension(current_salary, current_age, years_in_scheme, retirement_age, salary_growth=0.02):
    """
    Project USS pension to retirement
    
    Args:
        current_salary: Current annual salary
        current_age: Current age
        years_in_scheme: Current years in USS
        retirement_age: Target retirement age
        salary_growth: Annual salary growth rate
        
    Returns:
        dict: Projected pension details
    """
    years_to_retirement = max(0, retirement_age - current_age)
    total_years_in_scheme = years_in_scheme + years_to_retirement
    
    # Project final salary
    final_salary = current_salary * ((1 + salary_growth) ** years_to_retirement)
    
    # Calculate pension
    pension_details = calculate_uss_pension_value(final_salary, total_years_in_scheme)
    
    # Add projection details
    pension_details['current_salary'] = current_salary
    pension_details['final_salary'] = final_salary
    pension_details['years_to_retirement'] = years_to_retirement
    pension_details['total_years_in_scheme'] = total_years_in_scheme
    pension_details['salary_growth_rate'] = salary_growth
    
    return pension_details


def calculate_current_uss_pension_value(current_salary, years_in_scheme):
    """
    Calculate the current accrued USS pension value (not projected)
    
    Args:
        current_salary: Current annual salary
        years_in_scheme: Years already in USS
        
    Returns:
        dict: Current pension entitlement
    """
    return calculate_uss_pension_value(current_salary, years_in_scheme)


def project_avc_growth(current_avc_value, annual_contribution, years_to_retirement, growth_rate=0.05):
    """
    Project AVC pot growth to retirement
    
    Args:
        current_avc_value: Current AVC pot value
        annual_contribution: Annual AVC contribution
        years_to_retirement: Years until retirement
        growth_rate: Annual investment growth rate (default 5%)
        
    Returns:
        dict: AVC projection details
    """
    if years_to_retirement <= 0:
        return {
            'current_value': current_avc_value,
            'projected_value': current_avc_value,
            'total_contributions': 0,
            'investment_growth': 0,
            'annual_drawdown_4pct': current_avc_value * 0.04,
            'monthly_drawdown_4pct': (current_avc_value * 0.04) / 12
        }
    
    # Future value of current pot
    fv_current = current_avc_value * ((1 + growth_rate) ** years_to_retirement)
    
    # Future value of annual contributions (annuity formula)
    if growth_rate > 0:
        fv_contributions = annual_contribution * (((1 + growth_rate) ** years_to_retirement - 1) / growth_rate)
    else:
        fv_contributions = annual_contribution * years_to_retirement
    
    total_projected = fv_current + fv_contributions
    total_contributions = (current_avc_value + (annual_contribution * years_to_retirement))
    investment_growth = total_projected - total_contributions
    
    return {
        'current_value': current_avc_value,
        'projected_value': total_projected,
        'total_contributions': total_contributions,
        'investment_growth': investment_growth,
        'growth_rate': growth_rate,
        'years_to_retirement': years_to_retirement,
        'annual_drawdown_4pct': total_projected * 0.04,
        'monthly_drawdown_4pct': (total_projected * 0.04) / 12,
        'tax_free_lump_sum': total_projected * 0.25
    }


# ============================================================================
# SIPP CALCULATOR
# ============================================================================

def calculate_sipp_tax_relief(contribution, income):
    """
    Calculate tax relief on SIPP contribution
    
    Args:
        contribution: Gross contribution amount
        income: Annual income
        
    Returns:
        dict: Tax relief details
    """
    # Determine tax bracket
    if income <= 50270:
        tax_rate = SIPP_TAX_RELIEF_BASIC
        bracket = "Basic Rate"
    elif income <= 125140:
        tax_rate = SIPP_TAX_RELIEF_HIGHER
        bracket = "Higher Rate"
    else:
        tax_rate = SIPP_TAX_RELIEF_ADDITIONAL
        bracket = "Additional Rate"
    
    # Tax relief (automatically added for basic rate, claim higher/additional)
    basic_rate_relief = contribution * SIPP_TAX_RELIEF_BASIC
    additional_relief = contribution * (tax_rate - SIPP_TAX_RELIEF_BASIC) if tax_rate > SIPP_TAX_RELIEF_BASIC else 0
    total_relief = contribution * tax_rate
    
    # Net cost to you
    net_cost = contribution - total_relief
    
    return {
        'gross_contribution': contribution,
        'tax_bracket': bracket,
        'tax_rate': tax_rate * 100,
        'basic_rate_relief': basic_rate_relief,
        'additional_relief': additional_relief,
        'total_tax_relief': total_relief,
        'net_cost': net_cost,
        'effective_bonus': (total_relief / net_cost) * 100
    }


def project_sipp_growth(annual_contribution, years, growth_rate=0.05, current_value=0):
    """
    Project SIPP pot growth with compound returns
    
    Args:
        annual_contribution: Annual contribution amount
        years: Years until retirement
        growth_rate: Expected annual growth rate
        current_value: Current SIPP value
        
    Returns:
        dict: Projection details with year-by-year breakdown
    """
    values = [current_value]
    contributions = [0]
    growth = [0]
    
    for year in range(1, years + 1):
        previous_value = values[-1]
        contribution = annual_contribution
        investment_growth = previous_value * growth_rate
        new_value = previous_value + contribution + investment_growth
        
        values.append(new_value)
        contributions.append(contribution)
        growth.append(investment_growth)
    
    final_value = values[-1]
    total_contributions = annual_contribution * years
    total_growth = final_value - current_value - total_contributions
    
    # Calculate tax-free lump sum available
    tax_free_lump_sum = final_value * SIPP_LUMP_SUM_TAX_FREE
    remaining_pot = final_value - tax_free_lump_sum
    
    return {
        'final_value': final_value,
        'total_contributions': total_contributions,
        'total_growth': total_growth,
        'tax_free_lump_sum': tax_free_lump_sum,
        'remaining_pot': remaining_pot,
        'values_by_year': values,
        'contributions_by_year': contributions,
        'growth_by_year': growth,
        'growth_rate': growth_rate
    }


# ============================================================================
# PENSION INCOME DRAWDOWN
# ============================================================================

def calculate_pension_drawdown(pension_pot, annual_withdrawal, years, growth_rate=0.04):
    """
    Calculate pension drawdown sustainability
    
    Args:
        pension_pot: Starting pension pot value
        annual_withdrawal: Annual withdrawal amount
        years: Number of years to model
        growth_rate: Expected growth rate during drawdown
        
    Returns:
        dict: Drawdown projection
    """
    remaining_pot = [pension_pot]
    withdrawals = [0]
    
    for year in range(1, years + 1):
        previous_pot = remaining_pot[-1]
        
        if previous_pot <= 0:
            remaining_pot.append(0)
            withdrawals.append(0)
            continue
        
        # Withdrawal at start of year
        withdrawal = min(annual_withdrawal, previous_pot)
        after_withdrawal = previous_pot - withdrawal
        
        # Growth during year
        growth = after_withdrawal * growth_rate
        new_pot = after_withdrawal + growth
        
        remaining_pot.append(max(0, new_pot))
        withdrawals.append(withdrawal)
    
    years_sustainable = next((i for i, pot in enumerate(remaining_pot) if pot <= 0), len(remaining_pot))
    
    return {
        'remaining_pot_by_year': remaining_pot,
        'withdrawals_by_year': withdrawals,
        'years_sustainable': years_sustainable - 1 if years_sustainable > 0 else years,
        'is_sustainable': years_sustainable > years,
        'withdrawal_rate': (annual_withdrawal / pension_pot) * 100 if pension_pot > 0 else 0
    }


def safe_withdrawal_rate(pension_pot, years_needed, growth_rate=0.04):
    """
    Calculate safe withdrawal rate for given period
    Uses simple calculation: pot * (1 + growth)^years = pot - (withdrawal * years)
    
    Args:
        pension_pot: Starting pension pot
        years_needed: Years pension needs to last
        growth_rate: Expected growth rate
        
    Returns:
        float: Safe annual withdrawal amount
    """
    # Using annuity formula for simplification
    # A = P * r * (1+r)^n / ((1+r)^n - 1)
    r = growth_rate
    n = years_needed
    
    if r == 0:
        return pension_pot / years_needed
    
    safe_withdrawal = pension_pot * (r * (1 + r)**n) / ((1 + r)**n - 1)
    return safe_withdrawal


# ============================================================================
# COMBINED PENSION INCOME CALCULATOR
# ============================================================================

def calculate_total_retirement_income(state_pension, uss_pension, sipp_drawdown):
    """
    Calculate total retirement income from all sources
    
    Args:
        state_pension: Annual State Pension amount
        uss_pension: Annual USS pension amount
        sipp_drawdown: Annual SIPP drawdown amount
        
    Returns:
        dict: Combined income details
    """
    total_annual = state_pension + uss_pension + sipp_drawdown
    
    return {
        'state_pension_annual': state_pension,
        'uss_pension_annual': uss_pension,
        'sipp_drawdown_annual': sipp_drawdown,
        'total_annual': total_annual,
        'total_monthly': total_annual / 12,
        'state_pension_percentage': (state_pension / total_annual * 100) if total_annual > 0 else 0,
        'uss_pension_percentage': (uss_pension / total_annual * 100) if total_annual > 0 else 0,
        'sipp_percentage': (sipp_drawdown / total_annual * 100) if total_annual > 0 else 0
    }


# ============================================================================
# VISUALIZATION HELPERS
# ============================================================================

def create_pension_projection_chart(years, state_values, uss_values, sipp_values):
    """Create stacked area chart showing pension growth"""
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=years,
        y=state_values,
        name='State Pension',
        mode='lines',
        line=dict(width=0.5, color='rgb(76, 175, 80)'),
        stackgroup='one',
        fillcolor='rgba(76, 175, 80, 0.5)'
    ))
    
    fig.add_trace(go.Scatter(
        x=years,
        y=uss_values,
        name='USS Pension',
        mode='lines',
        line=dict(width=0.5, color='rgb(33, 150, 243)'),
        stackgroup='one',
        fillcolor='rgba(33, 150, 243, 0.5)'
    ))
    
    fig.add_trace(go.Scatter(
        x=years,
        y=sipp_values,
        name='SIPP',
        mode='lines',
        line=dict(width=0.5, color='rgb(255, 152, 0)'),
        stackgroup='one',
        fillcolor='rgba(255, 152, 0, 0.5)'
    ))
    
    fig.update_layout(
        title='Projected Pension Income by Source',
        xaxis_title='Years to Retirement',
        yaxis_title='Annual Pension Income (£)',
        hovermode='x unified',
        showlegend=True,
        height=400
    )
    
    return fig


def create_pension_pie_chart(state_amount, uss_amount, sipp_amount, uss_avc_amount=0):
    """Create pie chart showing pension income sources"""
    
    labels = []
    values = []
    colors = []
    
    if state_amount > 0:
        labels.append('State Pension')
        values.append(state_amount)
        colors.append('rgb(76, 175, 80)')
    
    if uss_amount > 0:
        labels.append('USS Pension')
        values.append(uss_amount)
        colors.append('rgb(33, 150, 243)')
    
    if uss_avc_amount > 0:
        labels.append('USS AVC')
        values.append(uss_avc_amount)
        colors.append('rgb(156, 39, 176)')
    
    if sipp_amount > 0:
        labels.append('SIPP Drawdown')
        values.append(sipp_amount)
        colors.append('rgb(255, 152, 0)')
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker_colors=colors,
        hole=.4
    )])
    
    fig.update_layout(
        title='Retirement Income Sources',
        showlegend=True,
        height=400
    )
    
    return fig
