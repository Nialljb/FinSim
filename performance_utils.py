"""
Performance utilities for FinSim
Provides caching and optimization helpers
"""

import streamlit as st
import hashlib
import json
from functools import wraps
from typing import Any, Callable


def cache_simulation_results(func: Callable) -> Callable:
    """
    Decorator to cache Monte Carlo simulation results
    Uses simulation parameters as cache key
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create cache key from parameters
        cache_key = _create_cache_key(kwargs)
        
        # Check if result exists in session state
        if 'simulation_cache' not in st.session_state:
            st.session_state.simulation_cache = {}
        
        if cache_key in st.session_state.simulation_cache:
            return st.session_state.simulation_cache[cache_key]
        
        # Run simulation and cache result
        result = func(*args, **kwargs)
        st.session_state.simulation_cache[cache_key] = result
        
        # Limit cache size to prevent memory issues
        if len(st.session_state.simulation_cache) > 5:
            # Remove oldest entry
            oldest_key = next(iter(st.session_state.simulation_cache))
            del st.session_state.simulation_cache[oldest_key]
        
        return result
    
    return wrapper


def _create_cache_key(params: dict) -> str:
    """Create a hash key from simulation parameters"""
    # Convert params to JSON string and hash it
    params_str = json.dumps(params, sort_keys=True, default=str)
    return hashlib.md5(params_str.encode()).hexdigest()


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_cached_exchange_rates():
    """Cache exchange rates to reduce API calls"""
    from currency_converter import get_exchange_rates
    return get_exchange_rates()


@st.cache_data(ttl=86400)  # Cache for 24 hours
def load_static_data(data_type: str) -> Any:
    """Cache static data like currency symbols, etc."""
    if data_type == 'currencies':
        return {
            'EUR': {'symbol': '€', 'name': 'Euro', 'locale': 'de_DE'},
            'GBP': {'symbol': '£', 'name': 'British Pound', 'locale': 'en_GB'},
            'CAD': {'symbol': 'C$', 'name': 'Canadian Dollar', 'locale': 'en_CA'},
            'USD': {'symbol': '$', 'name': 'US Dollar', 'locale': 'en_US'},
            'AUD': {'symbol': 'A$', 'name': 'Australian Dollar', 'locale': 'en_AU'},
            'NZD': {'symbol': 'NZ$', 'name': 'New Zealand Dollar', 'locale': 'en_NZ'},
            'CHF': {'symbol': 'CHF', 'name': 'Swiss Franc', 'locale': 'de_CH'},
            'SEK': {'symbol': 'kr', 'name': 'Swedish Krona', 'locale': 'sv_SE'},
            'NOK': {'symbol': 'kr', 'name': 'Norwegian Krone', 'locale': 'nb_NO'},
        }
    return None


def clear_simulation_cache():
    """Clear cached simulation results"""
    if 'simulation_cache' in st.session_state:
        st.session_state.simulation_cache = {}


def show_progress_with_steps(steps: list, current_step: int):
    """
    Show a visual progress indicator with steps
    
    Args:
        steps: List of step names
        current_step: Index of current step (0-based)
    """
    cols = st.columns(len(steps))
    for idx, (col, step) in enumerate(zip(cols, steps)):
        with col:
            if idx < current_step:
                st.markdown(f"✅ {step}")
            elif idx == current_step:
                st.markdown(f"⏳ **{step}**")
            else:
                st.markdown(f"⚪ {step}")


def optimize_dataframe_display(df, max_rows: int = 1000):
    """
    Optimize large dataframe display
    
    Args:
        df: DataFrame to display
        max_rows: Maximum rows to show at once
    """
    if len(df) > max_rows:
        st.warning(f"Showing first {max_rows} rows of {len(df)} total rows")
        return df.head(max_rows)
    return df


def lazy_import(module_name: str):
    """
    Lazy import heavy modules only when needed
    
    Usage:
        reportlab = lazy_import('reportlab')
    """
    import importlib
    return importlib.import_module(module_name)


class PerformanceMonitor:
    """Monitor and display performance metrics"""
    
    def __init__(self):
        if 'perf_metrics' not in st.session_state:
            st.session_state.perf_metrics = []
    
    def log_metric(self, name: str, value: float):
        """Log a performance metric"""
        st.session_state.perf_metrics.append({
            'name': name,
            'value': value,
            'timestamp': pd.Timestamp.now()
        })
    
    def show_metrics(self):
        """Display performance metrics in sidebar"""
        if st.session_state.perf_metrics:
            with st.sidebar.expander("⚡ Performance Metrics"):
                for metric in st.session_state.perf_metrics[-5:]:  # Show last 5
                    st.caption(f"{metric['name']}: {metric['value']:.2f}s")
