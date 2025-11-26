"""
Currency Conversion Module
Real-time exchange rate conversion for FinSim
"""

import requests
import streamlit as st
from datetime import datetime, timedelta
import json

# Fallback exchange rates (if API fails)
FALLBACK_RATES = {
    'EUR': 1.0,
    'USD': 1.08,
    'GBP': 0.85,
    'CAD': 1.47,
    'AUD': 1.63,
    'NZD': 1.77,
    'CHF': 0.95,
    'SEK': 11.25,
    'NOK': 11.45,
    'DKK': 7.45,
    'JPY': 159.50,
    'CNY': 7.75,
    'INR': 89.50,
    'SGD': 1.45,
    'HKD': 8.45
}


def fetch_exchange_rates():
    """
    Fetch current exchange rates from API
    Returns rates relative to EUR as base
    """
    try:
        # Using exchangerate-api.com free tier (no API key needed for basic)
        # Alternative: https://api.frankfurter.app/latest (EU-based, no key needed)
        
        url = "https://api.frankfurter.app/latest"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            rates = data.get('rates', {})
            rates['EUR'] = 1.0  # Base currency
            
            # Cache the rates with timestamp
            st.session_state.exchange_rates = rates
            st.session_state.rates_updated_at = datetime.now()
            
            return rates
        else:
            return FALLBACK_RATES
            
    except Exception as e:
        print(f"Exchange rate fetch failed: {e}")
        return FALLBACK_RATES


def get_exchange_rates():
    """
    Get exchange rates from cache or fetch new ones
    Rates are cached for 1 hour
    """
    # Check if we have cached rates
    if 'exchange_rates' in st.session_state and 'rates_updated_at' in st.session_state:
        # Check if rates are less than 1 hour old
        age = datetime.now() - st.session_state.rates_updated_at
        if age < timedelta(hours=1):
            return st.session_state.exchange_rates
    
    # Fetch new rates
    return fetch_exchange_rates()


def convert_currency(amount, from_currency, to_currency):
    """
    Convert amount from one currency to another
    
    Args:
        amount: The amount to convert
        from_currency: Source currency code (e.g., 'USD')
        to_currency: Target currency code (e.g., 'EUR')
    
    Returns:
        Converted amount as float
    """
    if from_currency == to_currency:
        return amount
    
    rates = get_exchange_rates()
    
    # Convert to EUR first (base currency)
    amount_in_eur = amount / rates.get(from_currency, 1.0)
    
    # Then convert to target currency
    converted_amount = amount_in_eur * rates.get(to_currency, 1.0)
    
    return converted_amount


def get_exchange_rate(from_currency, to_currency):
    """
    Get the exchange rate between two currencies
    
    Args:
        from_currency: Source currency code
        to_currency: Target currency code
    
    Returns:
        Exchange rate as float
    """
    if from_currency == to_currency:
        return 1.0
    
    rates = get_exchange_rates()
    
    # Get rate via EUR
    rate = rates.get(to_currency, 1.0) / rates.get(from_currency, 1.0)
    
    return rate


def show_currency_info(selected_currency):
    """
    Display currency information and last update time
    """
    rates = get_exchange_rates()
    
    if 'rates_updated_at' in st.session_state:
        update_time = st.session_state.rates_updated_at
        time_ago = datetime.now() - update_time
        
        if time_ago < timedelta(minutes=1):
            time_str = "just now"
        elif time_ago < timedelta(hours=1):
            time_str = f"{int(time_ago.total_seconds() / 60)} minutes ago"
        else:
            time_str = f"{int(time_ago.total_seconds() / 3600)} hours ago"
        
        st.caption(f"💱 Exchange rates updated {time_str}")
    
    # Show key exchange rates
    with st.expander("📊 Current Exchange Rates (vs EUR)"):
        cols = st.columns(4)
        major_currencies = ['USD', 'GBP', 'CAD', 'JPY', 'CHF', 'AUD', 'CNY', 'INR']
        
        for idx, curr in enumerate(major_currencies):
            if curr in rates:
                with cols[idx % 4]:
                    rate = rates[curr]
                    st.metric(
                        curr,
                        f"{rate:.4f}",
                        help=f"1 EUR = {rate:.4f} {curr}"
                    )


def convert_budget_to_currency(budget_dict, from_currency, to_currency):
    """
    Convert all values in a budget dictionary to another currency
    
    Args:
        budget_dict: Dictionary with category: amount pairs
        from_currency: Current currency of the budget
        to_currency: Target currency
    
    Returns:
        New dictionary with converted amounts
    """
    if from_currency == to_currency:
        return budget_dict.copy()
    
    converted = {}
    for category, amount in budget_dict.items():
        converted[category] = convert_currency(amount, from_currency, to_currency)
    
    return converted


def format_currency_with_conversion(amount, currency_code, base_currency='EUR', show_conversion=True):
    """
    Format currency with optional conversion display
    
    Args:
        amount: Amount to format
        currency_code: Currency to display in
        base_currency: Base currency for comparison
        show_conversion: Whether to show conversion
    
    Returns:
        Formatted string
    """
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
    
    symbol = CURRENCY_SYMBOLS.get(currency_code, currency_code)
    
    if amount < 0:
        formatted = f"-{symbol}{abs(amount):,.0f}"
    else:
        formatted = f"{symbol}{amount:,.0f}"
    
    # Add conversion if different from base
    if show_conversion and currency_code != base_currency:
        converted = convert_currency(amount, currency_code, base_currency)
        base_symbol = CURRENCY_SYMBOLS.get(base_currency, base_currency)
        formatted += f" (≈ {base_symbol}{converted:,.0f})"
    
    return formatted


# Initialize exchange rates on module load
if 'exchange_rates' not in st.session_state:
    get_exchange_rates()


if __name__ == "__main__":
    # Test the module
    st.title("Currency Conversion Test")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        from_curr = st.selectbox("From", ['EUR', 'USD', 'GBP', 'CAD', 'JPY'])
    
    with col2:
        to_curr = st.selectbox("To", ['EUR', 'USD', 'GBP', 'CAD', 'JPY'])
    
    with col3:
        amount = st.number_input("Amount", value=1000)
    
    if st.button("Convert"):
        converted = convert_currency(amount, from_curr, to_curr)
        rate = get_exchange_rate(from_curr, to_curr)
        
        st.success(f"{amount:,.2f} {from_curr} = {converted:,.2f} {to_curr}")
        st.info(f"Exchange rate: 1 {from_curr} = {rate:.4f} {to_curr}")
    
    show_currency_info(from_curr)