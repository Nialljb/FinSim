"""
Currency Manager Module
=======================
Implements canonical base currency storage to avoid conversion drift.

Design principles:
1. All amounts stored in EUR (BASE_CURRENCY)
2. Convert from display currency → BASE on input
3. Convert from BASE → display currency on output
4. No repeated multiplications that cause drift
"""

import streamlit as st
from typing import Dict, List, Optional
from currency_converter import get_exchange_rates, convert_currency

# Canonical base currency - all values stored in this currency internally
BASE_CURRENCY = 'EUR'

# Currency symbols for display formatting
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


def format_currency(amount, currency_code='EUR'):
    """
    Format amount with appropriate currency symbol
    
    Args:
        amount: Numeric amount to format
        currency_code: Currency code (e.g., 'EUR', 'USD')
        
    Returns:
        Formatted string with currency symbol and thousands separator
    """
    symbol = CURRENCY_SYMBOLS.get(currency_code, '€')
    
    if amount < 0:
        return f"-{symbol}{abs(amount):,.0f}"
    return f"{symbol}{amount:,.0f}"


# Keys for financial values stored in base currency
BASE_CURRENCY_KEYS = [
    'base_liquid_wealth',
    'base_property_value',
    'base_mortgage',
    'base_annual_income',
    'base_monthly_expenses',
]

# Display keys (what user sees in widgets)
DISPLAY_KEYS = [
    'display_liquid_wealth',
    'display_property_value', 
    'display_mortgage',
    'display_annual_income',
    'display_monthly_expenses',
]


def initialize_currency_system():
    """Initialize the currency system in session state"""
    
    # Set default currency if not exists
    if 'selected_currency' not in st.session_state:
        st.session_state.selected_currency = BASE_CURRENCY
    
    # Initialize base currency values (stored in EUR)
    if 'base_liquid_wealth' not in st.session_state:
        st.session_state.base_liquid_wealth = 50000.0  # in EUR
    if 'base_property_value' not in st.session_state:
        st.session_state.base_property_value = 0.0
    if 'base_mortgage' not in st.session_state:
        st.session_state.base_mortgage = 0.0
    if 'base_annual_income' not in st.session_state:
        st.session_state.base_annual_income = 60000.0
    if 'base_monthly_expenses' not in st.session_state:
        st.session_state.base_monthly_expenses = 2500.0
    
    # Initialize currency change tracker
    if 'previous_currency' not in st.session_state:
        st.session_state.previous_currency = BASE_CURRENCY


def to_base_currency(amount: float, from_currency: str) -> float:
    """
    Convert an amount from any currency to base currency (EUR)
    
    Args:
        amount: Amount in source currency
        from_currency: Source currency code
        
    Returns:
        Amount in base currency (EUR)
    """
    if from_currency == BASE_CURRENCY:
        return float(amount)
    
    try:
        return convert_currency(amount, from_currency, BASE_CURRENCY)
    except Exception as e:
        # Try fallback rates before giving up
        from currency_converter import FALLBACK_RATES
        if from_currency in FALLBACK_RATES:
            amount_in_eur = amount / FALLBACK_RATES[from_currency]
            st.warning(f"Using fallback rate for {from_currency}")
            return amount_in_eur
        # If no fallback, re-raise to prevent corruption
        st.error(f"Cannot convert {from_currency} to EUR: {e}")
        raise

def from_base_currency(amount: float, to_currency: str) -> float:
    """
    Convert an amount from base currency (EUR) to display currency
    
    Args:
        amount: Amount in base currency (EUR)
        to_currency: Target currency code
        
    Returns:
        Amount in target currency
    """
    if to_currency == BASE_CURRENCY:
        return float(amount)
    
    try:
        return convert_currency(amount, BASE_CURRENCY, to_currency)
    except Exception as e:
        error_msg = f"Error converting {amount} from {BASE_CURRENCY} to {to_currency}: {e}"
        st.error(error_msg)
        raise ValueError(error_msg) from e


def store_user_input(widget_key: str, base_key: str, value: float, currency: str):
    """
    Store user input by converting to base currency
    
    Args:
        widget_key: Key for the widget (not used in base approach but kept for compatibility)
        base_key: Key for base currency storage
        value: Amount entered by user
        currency: Currency the user entered the amount in
    """
    # Convert to base and store
    base_value = to_base_currency(value, currency)
    st.session_state[base_key] = base_value


def get_display_value(base_key: str, display_currency: str) -> float:
    """
    Get display value by converting from base currency
    
    Args:
        base_key: Key for base currency value
        display_currency: Currency to display in
        
    Returns:
        Value in display currency
    """
    base_value = st.session_state.get(base_key, 0.0)
    return from_base_currency(base_value, display_currency)


def handle_currency_change(old_currency: str, new_currency: str) -> bool:
    """
    Handle currency change - no conversion needed since we store in base
    Just show a notification to user
    
    Args:
        old_currency: Previous currency
        new_currency: New currency selected
        
    Returns:
        True if currency was changed, False otherwise
    """
    if old_currency == new_currency:
        return False
    
    # Update currency tracker
    st.session_state.previous_currency = new_currency
    st.session_state.selected_currency = new_currency
    
    # Show success message
    st.sidebar.success(f"✓ Currency changed: {old_currency} → {new_currency}")
    st.sidebar.info("All amounts automatically converted using current exchange rates")
    
    return True


# Schema mapping event types to their monetary field keys
EVENT_MONETARY_FIELDS = {
    'property_purchase': ['property_price', 'down_payment', 'mortgage_amount'],  # new_mortgage_payment excluded as it's pre-calculated
    'property_sale': ['sale_price', 'mortgage_payoff', 'selling_costs'],
    'one_time_expense': ['amount'],
    'expense_change': ['monthly_change'],
    'rental_income': ['monthly_rental'],
    'windfall': ['amount'],
}


def convert_events(events: List[Dict], conversion_fn, currency: str) -> List[Dict]:
    """
    Generic function to convert monetary fields in events using a conversion function
    
    Args:
        events: List of event dictionaries
        conversion_fn: Function to apply for conversion (e.g., to_base_currency or from_base_currency)
        currency: Currency code to pass to conversion function
        
    Returns:
        Events with monetary fields converted
    """
    converted_events = []
    
    for event in events:
        event_copy = event.copy()
        event_type = event.get('type')
        
        # Get the list of monetary fields for this event type
        monetary_fields = EVENT_MONETARY_FIELDS.get(event_type, [])
        
        # Convert each monetary field if it exists in the event
        for field in monetary_fields:
            if field in event_copy:
                event_copy[field] = conversion_fn(event_copy[field], currency)
        
        converted_events.append(event_copy)
    
    return converted_events


def convert_events_to_base(events: List[Dict], from_currency: str) -> List[Dict]:
    """
    Convert financial events to base currency
    
    Args:
        events: List of event dictionaries
        from_currency: Source currency
        
    Returns:
        Events with amounts converted to base currency
    """
    return convert_events(events, to_base_currency, from_currency)


def convert_events_from_base(events: List[Dict], to_currency: str) -> List[Dict]:
    """
    Convert financial events from base currency to display currency
    Used for exports and display
    
    Args:
        events: List of event dictionaries in base currency
        to_currency: Target currency for display
        
    Returns:
        Events with amounts converted to target currency
    """
    return convert_events(events, from_base_currency, to_currency)


def get_exchange_rate_display(base_amount: float = 1.0) -> str:
    """
    Get a display string showing exchange rate
    
    Args:
        base_amount: Amount in base currency to show conversion for
        
    Returns:
        Formatted string showing exchange rate
    """
    current_currency = st.session_state.get('selected_currency', BASE_CURRENCY)
    
    if current_currency == BASE_CURRENCY:
        return f"{BASE_CURRENCY} is the base currency"
    
    try:
        converted = from_base_currency(base_amount, current_currency)
        return f"€{base_amount:,.0f} = {converted:,.2f} {current_currency}"
    except Exception:
        return "Exchange rate unavailable"

def validate_exchange_rates() -> Dict[str, str]:
    """
    Validate that exchange rates are available
    
    Returns:
        Dictionary with status and message
    """
    try:
        rates = get_exchange_rates()
        if not rates:
            return {
                'status': 'error',
                'message': 'Exchange rates unavailable. Using EUR as default.'
            }
        return {
            'status': 'success',
            'message': f'Exchange rates loaded: {len(rates)} currency pairs available'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error loading exchange rates: {str(e)}'
        }


def convert_simulation_results_to_display(results: Dict, to_currency: str) -> Dict:
    """
    Convert simulation results from base currency to display currency
    
    Args:
        results: Simulation results dictionary with numpy arrays
        to_currency: Target display currency
        
    Returns:
        Results converted to target currency
    """
    if to_currency == BASE_CURRENCY:
        return results
    
    try:
        converted_results = {}
        conversion_factor = from_base_currency(1.0, to_currency)
        
        # Convert all monetary arrays
        for key in ['net_worth', 'real_net_worth', 'liquid_wealth', 
                    'pension_wealth', 'property_value', 'mortgage_balance']:
            if key in results:
                converted_results[key] = results[key] * conversion_factor
        
        # Keep non-monetary data as-is
        if 'inflation_rates' in results:
            converted_results['inflation_rates'] = results['inflation_rates']
        
        return converted_results
    except Exception as e:
        st.error(f"Error converting simulation results: {e}")
        return results


def create_currency_info_widget():
    """Create an expander widget showing current currency info and exchange rates"""
    with st.sidebar.expander("💱 Currency Information"):
        current_currency = st.session_state.get('selected_currency', BASE_CURRENCY)
        
        st.markdown(f"**Current Currency:** {current_currency}")
        st.markdown(f"**Base Currency:** {BASE_CURRENCY}")
        
        if current_currency != BASE_CURRENCY:
            st.markdown("---")
            st.markdown("**Sample Conversions:**")
            
            # Show some sample conversions
            for amount in [1000, 10000, 100000]:
                display_amount = from_base_currency(amount, current_currency)
                st.markdown(f"€{amount:,} = {display_amount:,.0f} {current_currency}")
        
        st.markdown("---")
        validation = validate_exchange_rates()
        
        if validation['status'] == 'success':
            st.success(validation['message'])
        else:
            st.warning(validation['message'])


# Debug utility
def show_debug_info():
    """Show debug information about currency state (for development)"""
    if st.sidebar.checkbox("🐛 Show Debug Info", value=False):
        with st.sidebar.expander("Debug: Currency State"):
            st.write("**Base Currency Values (EUR):**")
            for key in BASE_CURRENCY_KEYS:
                value = st.session_state.get(key, 0)
                st.write(f"{key}: €{value:,.2f}")
            
            st.write("**Display Settings:**")
            st.write(f"Selected: {st.session_state.get('selected_currency', 'N/A')}")
            st.write(f"Previous: {st.session_state.get('previous_currency', 'N/A')}")