"""
Application-wide constants
Central location for magic numbers and configuration values
"""

# ============================================================================
# Currency Constants
# ============================================================================

BASE_CURRENCY = "GBP"

CURRENCY_INFO = {
    'EUR': {'symbol': '€', 'name': 'Euro', 'locale': 'de_DE'},
    'GBP': {'symbol': '£', 'name': 'British Pound', 'locale': 'en_GB'},
    'CAD': {'symbol': 'C$', 'name': 'Canadian Dollar', 'locale': 'en_CA'},
    'USD': {'symbol': '$', 'name': 'US Dollar', 'locale': 'en_US'},
    'AUD': {'symbol': 'A$', 'name': 'Australian Dollar', 'locale': 'en_AU'},
    'NZD': {'symbol': 'NZ$', 'name': 'New Zealand Dollar', 'locale': 'en_NZ'},
    'CHF': {'symbol': 'CHF', 'name': 'Swiss Franc', 'locale': 'de_CH'},
    'SEK': {'symbol': 'kr', 'name': 'Swedish Krona', 'locale': 'sv_SE'},
    'NOK': {'symbol': 'kr', 'name': 'Norwegian Krone', 'locale': 'nb_NO'},
    'DKK': {'symbol': 'kr', 'name': 'Danish Krone', 'locale': 'da_DK'},
    'JPY': {'symbol': '¥', 'name': 'Japanese Yen', 'locale': 'ja_JP'},
    'CNY': {'symbol': '¥', 'name': 'Chinese Yuan', 'locale': 'zh_CN'},
}

# ============================================================================
# Simulation Constants
# ============================================================================

# Monte Carlo simulation defaults
DEFAULT_NUM_SIMULATIONS = 1000
MIN_SIMULATIONS = 100
MAX_SIMULATIONS = 10000

# Age constraints
MIN_AGE = 18
MAX_AGE = 100
DEFAULT_CURRENT_AGE = 30
DEFAULT_RETIREMENT_AGE = 65
DEFAULT_END_AGE = 95

# Financial defaults
DEFAULT_ANNUAL_RETURN = 0.07  # 7%
DEFAULT_VOLATILITY = 0.15     # 15%
DEFAULT_INFLATION = 0.02      # 2%

# ============================================================================
# UK Pension Constants
# ============================================================================

# State Pension (2024/25 values)
FULL_STATE_PENSION_WEEKLY = 221.20
FULL_STATE_PENSION_ANNUAL = FULL_STATE_PENSION_WEEKLY * 52
QUALIFYING_YEARS_FOR_FULL_PENSION = 35
MINIMUM_QUALIFYING_YEARS = 10

# State Pension Age (simplified - actual calculation more complex)
STATE_PENSION_AGE_DEFAULT = 67

# USS (Universities Superannuation Scheme)
USS_EMPLOYEE_CONTRIBUTION_RATE = 0.096  # 9.6%
USS_EMPLOYER_CONTRIBUTION_RATE = 0.216  # 21.6%
USS_ACCRUAL_RATE = 1/75  # Career revalued benefits

# SIPP (Self-Invested Personal Pension)
SIPP_TAX_RELIEF_BASIC = 0.20   # 20% basic rate
SIPP_TAX_RELIEF_HIGHER = 0.40  # 40% higher rate
SIPP_TAX_RELIEF_ADDITIONAL = 0.45  # 45% additional rate
SIPP_ANNUAL_ALLOWANCE = 60000  # £60k annual allowance (2024/25)

# ============================================================================
# Tax Bands (UK 2024/25)
# ============================================================================

PERSONAL_ALLOWANCE = 12570
BASIC_RATE_THRESHOLD = 50270
HIGHER_RATE_THRESHOLD = 125140

TAX_RATES = {
    'basic': 0.20,
    'higher': 0.40,
    'additional': 0.45
}

# ============================================================================
# Property Constants
# ============================================================================

TYPICAL_MORTGAGE_TERM_YEARS = 25
TYPICAL_MORTGAGE_RATE = 0.04  # 4%
TYPICAL_PROPERTY_APPRECIATION = 0.03  # 3% per year

# ============================================================================
# Export
# ============================================================================

__all__ = [
    'BASE_CURRENCY',
    'CURRENCY_INFO',
    'DEFAULT_NUM_SIMULATIONS',
    'MIN_SIMULATIONS',
    'MAX_SIMULATIONS',
    'MIN_AGE',
    'MAX_AGE',
    'DEFAULT_CURRENT_AGE',
    'DEFAULT_RETIREMENT_AGE',
    'DEFAULT_END_AGE',
    'DEFAULT_ANNUAL_RETURN',
    'DEFAULT_VOLATILITY',
    'DEFAULT_INFLATION',
    'FULL_STATE_PENSION_ANNUAL',
    'STATE_PENSION_AGE_DEFAULT',
    'USS_EMPLOYEE_CONTRIBUTION_RATE',
    'USS_EMPLOYER_CONTRIBUTION_RATE',
    'SIPP_ANNUAL_ALLOWANCE',
    'PERSONAL_ALLOWANCE',
    'TAX_RATES',
]
