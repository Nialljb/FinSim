"""
Debt Management Service
Handles debt calculations, amortization schedules, and payoff strategies
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


def calculate_monthly_payment(principal, annual_rate, term_months):
    """
    Calculate monthly payment for a loan
    
    Args:
        principal: Loan amount
        annual_rate: Annual interest rate (as decimal, e.g., 0.05 for 5%)
        term_months: Loan term in months
        
    Returns:
        float: Monthly payment amount
    """
    if annual_rate == 0:
        return principal / term_months if term_months > 0 else 0
    
    monthly_rate = annual_rate / 12
    if term_months <= 0:
        return 0
    
    payment = principal * (monthly_rate * (1 + monthly_rate)**term_months) / \
              ((1 + monthly_rate)**term_months - 1)
    return payment


def generate_amortization_schedule(principal, annual_rate, term_months, extra_payment=0, start_date=None):
    """
    Generate complete amortization schedule
    
    Args:
        principal: Loan amount
        annual_rate: Annual interest rate (as decimal)
        term_months: Loan term in months
        extra_payment: Extra monthly payment amount
        start_date: Start date (datetime object or None)
        
    Returns:
        pd.DataFrame: Amortization schedule with columns:
            - Month, Date, Payment, Principal, Interest, Extra, Balance, Cumulative Interest
    """
    if start_date is None:
        start_date = datetime.now()
    
    monthly_rate = annual_rate / 12
    monthly_payment = calculate_monthly_payment(principal, annual_rate, term_months)
    
    schedule = []
    balance = principal
    cumulative_interest = 0
    month = 0
    
    while balance > 0 and month < term_months * 2:  # Safety limit
        month += 1
        payment_date = start_date + relativedelta(months=month-1)
        
        # Calculate interest for this period
        interest_payment = balance * monthly_rate
        
        # Principal payment is the remainder
        principal_payment = monthly_payment - interest_payment
        
        # Add extra payment to principal
        total_principal = principal_payment + extra_payment
        
        # Don't overpay
        if total_principal > balance:
            total_principal = balance
            actual_extra = balance - principal_payment
            actual_payment = interest_payment + balance
        else:
            actual_extra = extra_payment
            actual_payment = monthly_payment + extra_payment
        
        # Update balance
        balance = max(0, balance - total_principal)
        cumulative_interest += interest_payment
        
        schedule.append({
            'Month': month,
            'Date': payment_date.strftime('%Y-%m-%d'),
            'Payment': actual_payment,
            'Principal': principal_payment if actual_extra == extra_payment else principal_payment + (actual_extra - extra_payment),
            'Interest': interest_payment,
            'Extra_Payment': actual_extra if actual_extra > 0 else 0,
            'Balance': balance,
            'Cumulative_Interest': cumulative_interest
        })
        
        if balance == 0:
            break
    
    return pd.DataFrame(schedule)


def calculate_payoff_date(current_balance, annual_rate, monthly_payment, extra_payment=0):
    """
    Calculate when a debt will be paid off
    
    Args:
        current_balance: Current loan balance
        annual_rate: Annual interest rate (as decimal)
        monthly_payment: Regular monthly payment
        extra_payment: Extra monthly payment
        
    Returns:
        dict: {
            'months': number of months to payoff,
            'years': number of years,
            'total_paid': total amount paid,
            'total_interest': total interest paid
        }
    """
    if monthly_payment + extra_payment <= 0:
        return None
    
    monthly_rate = annual_rate / 12
    balance = current_balance
    total_paid = 0
    total_interest = 0
    months = 0
    
    while balance > 0 and months < 1200:  # 100 year safety limit
        interest = balance * monthly_rate
        principal = (monthly_payment + extra_payment) - interest
        
        if principal <= 0:
            # Payment doesn't cover interest
            return None
        
        if principal > balance:
            # Final payment
            total_paid += balance + interest
            total_interest += interest
            balance = 0
        else:
            balance -= principal
            total_paid += monthly_payment + extra_payment
            total_interest += interest
        
        months += 1
    
    if balance > 0:
        return None
    
    years = months / 12
    
    return {
        'months': months,
        'years': round(years, 2),
        'total_paid': round(total_paid, 2),
        'total_interest': round(total_interest, 2)
    }


def compare_payoff_strategies(current_balance, annual_rate, monthly_payment, extra_payments=[0, 100, 200, 500]):
    """
    Compare different extra payment strategies
    
    Args:
        current_balance: Current loan balance
        annual_rate: Annual interest rate
        monthly_payment: Regular monthly payment
        extra_payments: List of extra payment amounts to compare
        
    Returns:
        pd.DataFrame: Comparison of strategies
    """
    results = []
    
    for extra in extra_payments:
        payoff = calculate_payoff_date(current_balance, annual_rate, monthly_payment, extra)
        if payoff:
            savings = payoff['total_interest']
            if extra == 0:
                baseline_interest = savings
            else:
                savings = baseline_interest - payoff['total_interest']
            
            results.append({
                'Extra_Payment': extra,
                'Months_to_Payoff': payoff['months'],
                'Years_to_Payoff': payoff['years'],
                'Total_Paid': payoff['total_paid'],
                'Total_Interest': payoff['total_interest'],
                'Interest_Saved': savings if extra > 0 else 0
            })
    
    return pd.DataFrame(results)


def calculate_debt_to_income_ratio(total_monthly_debt, monthly_income):
    """
    Calculate debt-to-income ratio
    
    Args:
        total_monthly_debt: Total monthly debt payments
        monthly_income: Monthly gross income
        
    Returns:
        float: DTI ratio as percentage
    """
    if monthly_income <= 0:
        return 0
    return (total_monthly_debt / monthly_income) * 100


def calculate_credit_utilization(current_balance, credit_limit):
    """
    Calculate credit utilization ratio (for credit cards)
    
    Args:
        current_balance: Current card balance
        credit_limit: Card's credit limit
        
    Returns:
        float: Utilization as percentage
    """
    if credit_limit <= 0:
        return 0
    return (current_balance / credit_limit) * 100


def create_payoff_comparison_chart(comparison_df, currency_symbol='€'):
    """
    Create chart comparing different payoff strategies
    
    Args:
        comparison_df: DataFrame from compare_payoff_strategies
        currency_symbol: Currency symbol for formatting
        
    Returns:
        plotly Figure
    """
    fig = go.Figure()
    
    # Add bars for years to payoff
    fig.add_trace(go.Bar(
        x=comparison_df['Extra_Payment'],
        y=comparison_df['Years_to_Payoff'],
        name='Years to Payoff',
        marker_color='lightblue',
        text=comparison_df['Years_to_Payoff'].round(1),
        textposition='auto',
        yaxis='y1'
    ))
    
    # Add line for interest saved
    fig.add_trace(go.Scatter(
        x=comparison_df['Extra_Payment'],
        y=comparison_df['Interest_Saved'],
        name='Interest Saved',
        mode='lines+markers',
        marker_color='green',
        line=dict(width=3),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title='Impact of Extra Payments',
        xaxis=dict(title=f'Extra Monthly Payment ({currency_symbol})'),
        yaxis=dict(title='Years to Payoff', side='left'),
        yaxis2=dict(title=f'Interest Saved ({currency_symbol})', side='right', overlaying='y'),
        hovermode='x unified',
        height=400
    )
    
    return fig


def create_amortization_chart(schedule_df, currency_symbol='€'):
    """
    Create visualization of amortization schedule
    
    Args:
        schedule_df: DataFrame from generate_amortization_schedule
        currency_symbol: Currency symbol for formatting
        
    Returns:
        plotly Figure
    """
    fig = go.Figure()
    
    # Balance over time
    fig.add_trace(go.Scatter(
        x=schedule_df['Month'],
        y=schedule_df['Balance'],
        name='Remaining Balance',
        fill='tozeroy',
        line=dict(color='red', width=2)
    ))
    
    # Cumulative interest
    fig.add_trace(go.Scatter(
        x=schedule_df['Month'],
        y=schedule_df['Cumulative_Interest'],
        name='Cumulative Interest',
        line=dict(color='orange', width=2)
    ))
    
    fig.update_layout(
        title='Loan Amortization Over Time',
        xaxis_title='Month',
        yaxis_title=f'Amount ({currency_symbol})',
        hovermode='x unified',
        height=400
    )
    
    return fig


def create_payment_breakdown_chart(schedule_df):
    """
    Create stacked area chart showing principal vs interest breakdown
    
    Args:
        schedule_df: DataFrame from generate_amortization_schedule
        
    Returns:
        plotly Figure
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=schedule_df['Month'],
        y=schedule_df['Interest'],
        name='Interest',
        fill='tozeroy',
        stackgroup='one',
        line=dict(color='orange')
    ))
    
    fig.add_trace(go.Scatter(
        x=schedule_df['Month'],
        y=schedule_df['Principal'],
        name='Principal',
        fill='tonexty',
        stackgroup='one',
        line=dict(color='blue')
    ))
    
    if schedule_df['Extra_Payment'].sum() > 0:
        fig.add_trace(go.Scatter(
            x=schedule_df['Month'],
            y=schedule_df['Extra_Payment'],
            name='Extra Payment',
            fill='tonexty',
            stackgroup='one',
            line=dict(color='green')
        ))
    
    fig.update_layout(
        title='Payment Breakdown Over Time',
        xaxis_title='Month',
        yaxis_title='Payment Amount',
        hovermode='x unified',
        height=400
    )
    
    return fig


def calculate_debt_snowball(debts, extra_payment):
    """
    Calculate debt payoff using snowball method (smallest balance first)
    
    Args:
        debts: List of dicts with keys: name, balance, rate, min_payment
        extra_payment: Extra amount to apply each month
        
    Returns:
        dict: Payoff plan with timeline and savings
    """
    # Sort by balance (smallest first)
    sorted_debts = sorted(debts, key=lambda x: x['balance'])
    
    # Implementation would track payoff of each debt in sequence
    # This is a simplified version
    return {
        'method': 'snowball',
        'order': [d['name'] for d in sorted_debts],
        'total_months': 0,  # To be calculated
        'total_interest': 0  # To be calculated
    }


def calculate_debt_avalanche(debts, extra_payment):
    """
    Calculate debt payoff using avalanche method (highest rate first)
    
    Args:
        debts: List of dicts with keys: name, balance, rate, min_payment
        extra_payment: Extra amount to apply each month
        
    Returns:
        dict: Payoff plan with timeline and savings
    """
    # Sort by interest rate (highest first)
    sorted_debts = sorted(debts, key=lambda x: x['rate'], reverse=True)
    
    return {
        'method': 'avalanche',
        'order': [d['name'] for d in sorted_debts],
        'total_months': 0,
        'total_interest': 0
    }
