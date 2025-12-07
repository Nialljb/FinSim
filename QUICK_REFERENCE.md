# FinSim - Quick Reference Guide

## 🚀 Getting Started

### Running the Application

```bash
# Primary entry point (RECOMMENDED - fully functional)
streamlit run wealth_simulator.py

# Alternative entry point (shows migration info)
streamlit run app/Home.py
```

**Use `wealth_simulator.py`** - it has all the features working!

The `app/Home.py` was created to demonstrate the new architecture but currently redirects to the main app. Future phases could migrate the simulation logic into modular services, but for now, `wealth_simulator.py` works perfectly with the new structure.

---

## 📦 Import Patterns

### Monte Carlo Service

```python
# Extracted simulation engine - now independently testable!
from services.monte_carlo import run_monte_carlo, calculate_mortgage_payment

# Calculate mortgage payment
payment = calculate_mortgage_payment(
    principal=300000,
    annual_rate=0.035,
    years=25
)  # Returns monthly payment

# Run simulation
results = run_monte_carlo(
    initial_liquid_wealth=100000,
    initial_property_value=500000,
    initial_mortgage=400000,
    gross_annual_income=75000,
    effective_tax_rate=0.25,
    pension_contribution_rate=0.10,
    monthly_expenses=3000,
    monthly_mortgage_payment=2000,
    property_appreciation=0.03,
    mortgage_interest_rate=0.035,
    expected_return=0.07,
    return_volatility=0.15,
    expected_inflation=0.025,
    inflation_volatility=0.01,
    salary_inflation=0.025,
    years=30,
    n_simulations=1000,
    events=[],
    random_seed=42
)
# Returns: dict with net_worth, liquid_wealth, pension_wealth, etc.
```

### Visualization Service

```python
# Extracted chart generation - now independently testable!
from services.visualization import (
    create_wealth_trajectory_chart,
    create_wealth_composition_chart,
    create_distribution_chart,
    get_view_type_paths
)

# Get paths for specific view type
paths, label = get_view_type_paths(
    "Total Net Worth",
    display_results,
    results,
    n_simulations=1000,
    show_real=True
)

# Create wealth trajectory chart
fig = create_wealth_trajectory_chart(
    paths_to_plot=paths,
    years=30,
    n_simulations=1000,
    events=[],
    y_label="Net Worth",
    currency_symbol="£",
    starting_age=35,
    retirement_age=65,
    end_age=85
)

# Create wealth composition chart
fig_comp = create_wealth_composition_chart(
    display_results=display_results,
    results=results,
    years=30,
    starting_age=35,
    end_age=85,
    currency_symbol="£"
)

# Create distribution chart
fig_dist = create_distribution_chart(
    paths_to_plot=paths,
    simulation_years=30,
    starting_age=35,
    currency_symbol="£"
)
```

### Authentication

```python
# Both work - use whichever you prefer
from auth import login_user, register_user              # Legacy (via symlink)
from authentication import login_user, register_user     # Modern (preferred)

# Available functions:
initialize_session_state()
show_login_page()
show_user_header()
login_user(username, password)
register_user(username, email, password, age, retirement_age)
logout()
verify_email(token)
resend_verification_email(email)
check_simulation_limit(user_id)
increment_simulation_count(user_id)
increment_export_count(user_id)
reset_simulation_count(user_id)
```

### Database

```python
from database import User, Simulation, SessionLocal, init_db

# Or use the repository pattern (new)
from data_layer.repositories.user_repository import UserRepository

repo = UserRepository()
user = repo.get_by_username("johndoe")
```

### Configuration

```python
from config.settings import (
    APP_NAME,           # "FinSTK"
    BASE_URL,           # Your deployment URL
    SECRET_KEY,         # For sessions
    FREE_SIMULATION_LIMIT,
    ENABLE_PDF_EXPORT,
    DEFAULT_CURRENCY,
    SUPPORTED_CURRENCIES
)

from config.database import (
    engine,
    SessionLocal,
    Base,
    init_db,
    get_db
)

from config.smtp import (
    SMTP_SERVER,
    SMTP_PORT,
    SENDER_EMAIL,
    is_email_configured,
    validate_email_config
)
```

### Utilities

```python
from lib.constants import (
    CURRENCY_INFO,           # Dict of all currency info
    DEFAULT_NUM_SIMULATIONS,
    DEFAULT_ANNUAL_RETURN,
    DEFAULT_VOLATILITY,
    FULL_STATE_PENSION_ANNUAL,
    TAX_RATES,
    PERSONAL_ALLOWANCE
)

from lib.formatters import (
    format_currency,         # format_currency(1000, 'GBP') → "£1,000"
    format_percentage,       # format_percentage(0.15) → "15.0%"
    format_large_number,     # format_large_number(1500000) → "1.5M"
    parse_currency_input     # parse_currency_input("£1,000.50") → 1000.5
)

from lib.validators import (
    validate_age,
    validate_email,
    validate_password,
    validate_percentage,
    validate_simulation_count
)
```

### Services

```python
from services.email_service import (
    send_verification_email,
    send_welcome_email,
    generate_verification_token
)

# Future services (ready for extraction):
# from services.monte_carlo import run_monte_carlo_simulation
# from services.pension_calculator import calculate_pension
# from services.budget_service import analyze_budget
```

---

## 🗂️ Directory Structure

```
FinSim/
├── app/                    # 🎨 Streamlit UI
├── authentication/         # 🔐 Auth (modern path)
├── auth -> authentication  # 🔗 Compatibility symlink
├── services/               # 💼 Business logic
├── data_layer/            # 💾 Data access
├── data -> data_layer     # 🔗 Compatibility symlink
├── config/                # ⚙️ Configuration
├── lib/                   # 🛠️ Utilities
├── db/                    # 🗄️ Database scripts
├── tests/                 # 🧪 Tests
├── docs/                  # 📖 Documentation
└── wealth_simulator.py    # Original entry point
```

---

## 🧪 Testing

### Unit Testing
```bash
# Run specific test file
python -m pytest tests/unit/test_formatters.py

# Run all unit tests
python -m pytest tests/unit/

# With coverage
python -m pytest --cov=lib tests/unit/
```

### Manual Testing
```python
# Test imports
python3 -c "from auth import login_user; print('✅ Works')"

# Test formatters
python3 -c "from lib.formatters import format_currency; print(format_currency(1000, 'GBP'))"

# Test config
python3 -c "from config.settings import APP_NAME; print(APP_NAME)"
```

---

## 🔧 Development Workflow

### Adding a New Feature

1. **Business Logic** → Add to `services/`
   ```python
   # services/my_feature.py
   def calculate_something(param1, param2):
       """Your logic here"""
       return result
   ```

2. **UI Components** → Add to `app/components/`
   ```python
   # app/components/my_widget.py
   import streamlit as st
   from services.my_feature import calculate_something
   
   def show_my_widget():
       st.write("My Widget")
       result = calculate_something(a, b)
       st.write(result)
   ```

3. **Page** → Add to `app/pages/`
   ```python
   # app/pages/My_Feature.py
   from app.components.my_widget import show_my_widget
   
   show_my_widget()
   ```

### Adding Configuration

```python
# config/settings.py
MY_NEW_SETTING = os.getenv('MY_SETTING', 'default_value')

# Use it:
from config.settings import MY_NEW_SETTING
```

### Adding Utilities

```python
# lib/my_utils.py
def my_helper_function(param):
    """
    Description of what this does.
    
    Args:
        param: Description
        
    Returns:
        Description
    """
    return result

# Use it:
from lib.my_utils import my_helper_function
```

---

## 📝 Best Practices

### Imports
```python
# ✅ Good - Modern imports
from authentication import login_user
from config.settings import BASE_URL
from lib.formatters import format_currency

# ⚠️ OK - Legacy imports (still work via symlinks)
from auth import login_user
from database import User

# ❌ Avoid - Direct file imports for new code
import auth_module
```

### Code Organization
```python
# ✅ Good - Separated concerns
# services/calculation.py - Pure business logic
# app/pages/Results.py - UI only
# config/settings.py - Configuration

# ❌ Avoid - Mixed concerns
# Everything in one big file
```

### Configuration
```python
# ✅ Good - Use environment variables
from config.settings import DATABASE_URL

# ❌ Avoid - Hardcoded values
DATABASE_URL = "postgresql://..."
```

---

## 🐛 Troubleshooting

### Import Errors

**Problem:** `ImportError: cannot import name 'X' from 'auth'`

**Solution:**
```python
# Check if symlink exists
ls -la | grep auth
# Should see: auth -> authentication

# If missing, recreate:
ln -s authentication auth
```

**Problem:** `ModuleNotFoundError: No module named 'authentication'`

**Solution:**
```python
# Make sure you're in the project root
cd /path/to/FinSim

# Check Python path
python3 -c "import sys; print(sys.path)"

# Add parent to path if needed:
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
```

### Streamlit Issues

**Problem:** Changes not reflecting

**Solution:**
```bash
# Clear cache
streamlit cache clear

# Or restart with --server.runOnSave true
streamlit run wealth_simulator.py --server.runOnSave true
```

**Problem:** Multiple instances running

**Solution:**
```bash
# Kill all Streamlit processes
pkill -f "streamlit run"

# Start fresh
streamlit run wealth_simulator.py
```

---

## 📚 Documentation

### Main Documents
- `README.md` - Project overview
- `REFACTORING_COMPLETE.md` - Full refactoring summary
- `PHASE_3_COMPLETE.md` - Phase 3 details
- `CONTRIBUTING.md` - Contribution guidelines

### Developer Docs
- `docs/dev/architecture.md` - Architecture overview
- `docs/dev/setup.md` - Development setup
- `docs/dev/api.md` - Internal API docs

### User Docs
- `docs/user/getting_started.md` - User guide
- `docs/user/features.md` - Feature documentation
- `docs/user/faq.md` - Common questions

---

## 🚢 Deployment

### Current Setup (Render)
```yaml
# render.yaml
services:
  - type: web
    name: finsim
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run wealth_simulator.py
```

**No changes needed!** The refactoring is fully backward compatible.

### Environment Variables
Required for production:
```bash
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=noreply@yourapp.com
BASE_URL=https://yourapp.com
```

---

## 🎯 Quick Commands

```bash
# Run application
streamlit run wealth_simulator.py

# Run tests
python -m pytest

# Check Python version
python3 --version

# Install dependencies
pip install -r requirements.txt

# Database initialization
python3 -c "from database import init_db; init_db()"

# Test imports
python3 -c "from auth import login_user; print('✅')"

# Kill Streamlit
pkill -f "streamlit run"

# Clear Streamlit cache
streamlit cache clear
```

---

## 💡 Tips

1. **Use modern imports** for new code
2. **Legacy imports still work** via symlinks
3. **Both entry points work** (wealth_simulator.py and app/Home.py)
4. **Configuration in config/** not in code
5. **Utilities in lib/** for reusability
6. **Services in services/** for business logic
7. **Tests in tests/** following structure
8. **Documentation in docs/** organized by audience

---

## 🆘 Need Help?

- Check `REFACTORING_COMPLETE.md` for full context
- See `PHASE_3_COMPLETE.md` for technical details
- Read `docs/dev/troubleshooting.md` for common issues
- Open GitHub issue for bugs
- Check existing documentation in `docs/`

---

**Last Updated:** December 6, 2025  
**Version:** 2.0 (Post-Refactoring)  
**Status:** Production Ready ✅
