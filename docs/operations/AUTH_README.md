# FinSim Authentication System

Complete authentication system with user registration, login, and data collection for your wealth simulator.

## 🎯 Features

- **User Registration** with email and password
- **Secure Login** with bcrypt password hashing
- **User Profiles** collecting age and retirement goals
- **Usage Tracking** - 5 free simulations per month
- **Data Collection** - Anonymized simulation data for research
- **Session Management** - Persistent login across page reloads
- **SQLite Database** - Easy local development, PostgreSQL ready for production

## 📦 What's Included

### Core Files

1. **database.py** - Database models and schema
   - User accounts
   - Simulation tracking
   - Usage statistics
   - Aggregated anonymous data

2. **auth.py** - Authentication logic
   - User registration
   - Login/logout
   - Password hashing
   - Session management
   - Usage limit checking

3. **data_tracking.py** - Data collection
   - Save simulations
   - Anonymize sensitive data
   - Aggregate insights
   - Wealth/income distributions

4. **integration_guide.py** - Integration instructions
   - Step-by-step guide to add auth to your app

5. **setup.py** - Database initialization
   - Creates tables
   - Creates test user

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

New dependencies added:
- `sqlalchemy` - Database ORM
- `bcrypt` - Password hashing
- `python-dotenv` - Environment variables
- `psycopg2-binary` - PostgreSQL support

### 2. Set Up Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration (optional for local dev)
nano .env
```

For local development, the default SQLite configuration works out of the box.

### 3. Initialize Database

```bash
python setup.py
```

This will:
- Create database tables
- Create a test user (testuser/password123)
- Verify setup

### 4. Run the App

```bash
streamlit run wealth_simulator.py
```

### 5. Test Login

Use the test account:
- **Username:** testuser
- **Password:** password123

## 🔧 Integration

Follow the step-by-step guide in `integration_guide.py` to add authentication to your `wealth_simulator.py`.

### Key Integration Points

**1. Add imports:**
```python
from auth import initialize_session_state, show_login_page, show_user_header, check_simulation_limit, increment_simulation_count
from data_tracking import save_simulation
from database import init_db
```

**2. Wrap app with authentication:**
```python
initialize_session_state()

if not st.session_state.get('authenticated', False):
    show_login_page()
    st.stop()

show_user_header()
```

**3. Check usage limits:**
```python
can_simulate, remaining, message = check_simulation_limit(st.session_state.user_id)
if not can_simulate:
    st.error(message)
```

**4. Track simulations:**
```python
increment_simulation_count(st.session_state.user_id)
save_simulation(st.session_state.user_id, simulation_params, results)
```

## 📊 Data Collection

### What We Collect

**User Profile (Identifiable):**
- Username
- Email
- Current age
- Target retirement age
- Country (optional)

**Simulation Data (Anonymized):**
- Wealth brackets (not exact amounts)
- Income brackets
- Event types (property purchase, children, etc.)
- Number of events
- Currency used
- Success probability

### What We DON'T Collect

❌ Exact financial amounts
❌ Property addresses
❌ Personal event details
❌ Names of family members
❌ Any personally identifiable information from simulations

### Example Anonymized Data

```json
{
  "user_age_range": "30-35",
  "retirement_age": 65,
  "wealth_bracket": "250k-500k",
  "income_bracket": "100k-150k",
  "has_property_purchase": true,
  "has_children": true,
  "number_of_events": 4,
  "probability_of_success": 0.87
}
```

## 🎨 Usage Limits

**Free Tier (Current Implementation):**
- 5 simulations per month
- Unlimited exports
- All features enabled

**To Implement Paid Tiers** (Future):
1. Add `subscription_tier` column to User table
2. Modify `check_simulation_limit()` in `auth.py`
3. Add payment processing (Stripe integration example provided in README.md)

## 🗄️ Database Schema

### Users Table
- `id` - Primary key
- `username` - Unique username
- `email` - Unique email
- `password_hash` - Bcrypt hashed password
- `current_age` - User's age
- `target_retirement_age` - Retirement goal
- `country` - Optional country
- `created_at` - Account creation timestamp
- `last_login` - Last login timestamp

### Simulations Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `name` - Simulation name
- `currency` - Currency used
- `*_bracket` - Anonymized wealth/income brackets
- `has_*` - Boolean flags for events
- `parameters` - Full parameters (JSON)
- `created_at` - Timestamp

### UsageStats Table
- `user_id` - Foreign key
- `simulations_this_month` - Count
- `exports_this_month` - Count
- `current_month` - Reset tracking

## 🔐 Security Features

✅ **Password Hashing** - bcrypt with salt
✅ **SQL Injection Prevention** - SQLAlchemy ORM
✅ **Session Management** - Streamlit session state
✅ **Input Validation** - Username/email/password requirements
✅ **Data Anonymization** - Bracketed financial data

## 🚢 Production Deployment

### Switch to PostgreSQL

1. **Get PostgreSQL database:**
   - Supabase (free tier): https://supabase.com
   - Neon (free tier): https://neon.tech
   - Railway: https://railway.app
   - Or any PostgreSQL provider

2. **Update .env:**
```bash
DATABASE_URL=postgresql://user:password@host:5432/database
```

3. **Run setup:**
```bash
python setup.py
```

### Environment Variables

For production, set these in your hosting platform:
```bash
DATABASE_URL=postgresql://...
SECRET_KEY=<generate-secure-key>
APP_URL=https://yourdomain.com
FREE_SIMULATION_LIMIT=5
```

## 📈 Analytics Queries

### Get Aggregated Insights

```python
from data_tracking import get_aggregated_insights, get_wealth_distribution, get_income_distribution

# Overall insights
insights = get_aggregated_insights()
print(f"Total simulations: {insights['total_simulations']}")
print(f"Property purchases: {insights['property_purchase_percentage']}%")

# Wealth distribution
wealth_dist = get_wealth_distribution()
# {'100k-250k': 150, '250k-500k': 89, ...}

# Income distribution  
income_dist = get_income_distribution()
# {'100k-150k': 200, '150k-200k': 120, ...}
```

### Custom Queries

```python
from database import SessionLocal, Simulation, User
from sqlalchemy import func

db = SessionLocal()

# Users by age range
users_by_age = db.query(
    func.floor(User.current_age / 5) * 5,
    func.count(User.id)
).group_by(func.floor(User.current_age / 5)).all()

# Most common retirement ages
retirement_ages = db.query(
    User.target_retirement_age,
    func.count(User.id)
).group_by(User.target_retirement_age).order_by(func.count(User.id).desc()).all()

db.close()
```

## 🛠️ Customization

### Change Simulation Limits

In `auth.py`, modify:
```python
def check_simulation_limit(user_id: int, limit: int = 5):  # Change default limit
```

### Add User Fields

1. Add column in `database.py`:
```python
class User(Base):
    # ... existing fields
    occupation = Column(String(100), nullable=True)
```

2. Update registration in `auth.py`:
```python
def register_user(..., occupation: str = None):
    new_user = User(
        # ... existing fields
        occupation=occupation
    )
```

### Add Simulation Metadata

In `database.py`, add columns to `Simulation`:
```python
class Simulation(Base):
    # ... existing fields
    retirement_goal_met = Column(Boolean, nullable=True)
```

## 🐛 Troubleshooting

**"No module named 'database'"**
- Make sure all new files are in the same directory as `wealth_simulator.py`

**"Table users doesn't exist"**
- Run `python setup.py` to initialize database

**"Invalid password"**
- Passwords must be at least 8 characters
- Use the test account: testuser/password123

**"Session state not working"**
- Ensure `initialize_session_state()` is called before checking authentication

## 📞 Support

For issues or questions:
1. Check the integration guide in `integration_guide.py`
2. Review example implementations in README.md
3. Open an issue on GitHub

## 📄 License

Same as main project (MIT)