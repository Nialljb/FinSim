# 📊 Developer Data Access Guide

## Overview

All user data is **permanently stored** in the PostgreSQL database and accessible for analysis. No data is deleted unless explicitly requested by users.

## Data Collection

### What We Store

1. **Users Table**
   - Demographics (age, retirement plans, country)
   - Account activity (created_at, last_login)
   - Authentication (username, email, hashed passwords)

2. **Simulations Table**
   - Full simulation parameters (JSON)
   - Results and projections
   - Anonymized brackets (wealth, income, property)
   - Event flags (property, children, moves)
   - Success probabilities

3. **SavedBudgets Table**
   - Budget configurations (Now, 1yr, 5yr)
   - Currency preferences
   - Life events planned

4. **UsageStats Table**
   - Monthly simulation counts
   - Export activity
   - User engagement metrics

### Data Privacy

- All data is **user-specific** (filtered by `user_id`)
- Financial amounts are **anonymized to brackets** for analytics
- Users consent to data sharing during registration
- Data used for research and product improvement only

---

## Access Methods

### 1. Admin Analytics Dashboard (Easiest)

**Access:** Log in as admin user → Sidebar → "📊 Admin Analytics Dashboard"

**Admin Users:**
- Add usernames to `admin_users` list in `wealth_simulator.py` (line 928)
- Current: `['admin', 'nbourke', 'testuser']`

**Features:**
- 📥 One-click CSV exports of all analytics
- 👥 User behavior dashboards
- 💰 Financial analytics visualizations
- 📊 Raw database table viewer
- 🔍 Custom SQL query builder

**Files:**
- `admin_analytics.py` - Full dashboard
- `analytics_module.py` - Data generation functions

---

### 2. Direct Database Access

#### On Render (Production):

**Method A: Render SQL Editor**
1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Navigate to your `finsim-db` database
3. Click **Connect** tab
4. Scroll to **SQL Editor**
5. Run queries directly

**Method B: psql CLI**
```bash
# Get connection string from Render Dashboard
psql postgresql://user:password@host:port/finsim

# Example queries
SELECT COUNT(*) FROM users;
SELECT * FROM simulations ORDER BY created_at DESC LIMIT 10;
```

**Method C: GUI Tools**
- Download [DBeaver](https://dbeaver.io/) (free) or [TablePlus](https://tableplus.com/)
- Create new PostgreSQL connection
- Copy connection details from Render Dashboard → Database → Connect

#### Locally (Development):

```bash
# SQLite database
sqlite3 finsim.db

# View tables
.tables

# Query
SELECT * FROM users;
```

---

### 3. Programmatic Access

#### Python Script Example:

```python
from database import SessionLocal, User, Simulation
from analytics_module import export_all_analytics
import pandas as pd

# Get all analytics
exports = export_all_analytics()

# Access specific dataset
user_demographics = exports['user_demographics']
simulation_details = exports['simulation_details']

# Custom query
db = SessionLocal()
try:
    users = db.query(User).all()
    for user in users:
        print(f"{user.username}: {user.current_age} years old")
finally:
    db.close()
```

#### Run Analytics Export:

```bash
# Local
python analytics_module.py

# Render (via Shell)
# Dashboard → Web Service → Shell
python analytics_module.py
```

---

## Available Analytics Datasets

### 1. User Demographics
- Current age, retirement age, years to retirement
- Country distribution
- Account creation dates
- Activity timeline

### 2. Simulation Details (30 fields)
- Starting age, retirement age, simulation years
- Initial wealth, property value, mortgage
- Income, expenses, savings (monthly & annual)
- **Calculated:** Savings rate %, LTV ratio, net worth
- Event flags (property, children, moves)
- Outcomes (final net worth, success probability)

### 3. Age-Segmented Analysis
- Financial metrics grouped by age brackets (25-29, 30-34, etc.)
- Liquid wealth, income, expenses by age
- Property ownership by age
- Savings behavior by age

### 4. Income-Segmented Analysis
- Behavior patterns by income bracket
- Savings rates by income level
- Property ownership by income
- Age distribution by income

### 5. Property Ownership Summary
- Average age with property
- Property values and mortgage sizes
- LTV ratios
- Mortgage prevalence

### 6. Retirement Planning Summary
- Target retirement ages
- Years to retirement distributions
- Early/standard/late retirement percentages

### 7. Savings Behavior Analysis
- Grouped by savings rate (Deficit, 0-10%, 10-20%, etc.)
- Income and expense patterns
- Liquid wealth by savings rate

### 8. Summary Statistics
- Platform-wide KPIs
- Total users, simulations, engagement
- Averages across all metrics

---

## Example SQL Queries

### User Analysis

```sql
-- User demographics
SELECT 
    current_age,
    target_retirement_age,
    country,
    COUNT(*) as user_count
FROM users
GROUP BY current_age, target_retirement_age, country;

-- User activity timeline
SELECT 
    DATE(created_at) as signup_date,
    COUNT(*) as new_users
FROM users
GROUP BY signup_date
ORDER BY signup_date;

-- Active users
SELECT 
    u.username,
    COUNT(s.id) as simulation_count,
    MAX(s.created_at) as last_simulation
FROM users u
LEFT JOIN simulations s ON u.id = s.user_id
GROUP BY u.username
ORDER BY simulation_count DESC;
```

### Financial Analysis

```sql
-- Savings rate distribution
SELECT 
    CASE 
        WHEN CAST(parameters->>'gross_annual_income' AS NUMERIC) = 0 THEN 'No Income'
        WHEN (CAST(parameters->>'gross_annual_income' AS NUMERIC) - 
              CAST(parameters->>'monthly_expenses' AS NUMERIC) * 12) < 0 THEN 'Deficit'
        WHEN (CAST(parameters->>'gross_annual_income' AS NUMERIC) - 
              CAST(parameters->>'monthly_expenses' AS NUMERIC) * 12) / 
              CAST(parameters->>'gross_annual_income' AS NUMERIC) < 0.1 THEN '0-10%'
        WHEN (CAST(parameters->>'gross_annual_income' AS NUMERIC) - 
              CAST(parameters->>'monthly_expenses' AS NUMERIC) * 12) / 
              CAST(parameters->>'gross_annual_income' AS NUMERIC) < 0.2 THEN '10-20%'
        ELSE '20%+'
    END as savings_rate_category,
    COUNT(*) as count
FROM simulations
WHERE parameters->>'gross_annual_income' IS NOT NULL
GROUP BY savings_rate_category;

-- Property ownership by age
SELECT 
    FLOOR(u.current_age / 5) * 5 as age_bracket,
    COUNT(CASE WHEN s.has_property_purchase THEN 1 END) as with_property,
    COUNT(*) as total_simulations,
    ROUND(100.0 * COUNT(CASE WHEN s.has_property_purchase THEN 1 END) / COUNT(*), 2) as pct
FROM users u
JOIN simulations s ON u.id = s.user_id
GROUP BY age_bracket
ORDER BY age_bracket;

-- Income vs wealth correlation
SELECT 
    s.income_bracket,
    s.initial_liquid_wealth_bracket,
    COUNT(*) as count
FROM simulations s
GROUP BY s.income_bracket, s.initial_liquid_wealth_bracket
ORDER BY s.income_bracket, s.initial_liquid_wealth_bracket;
```

### Behavioral Analysis

```sql
-- Most common life events
SELECT 
    SUM(CASE WHEN has_property_purchase THEN 1 ELSE 0 END) as property_purchases,
    SUM(CASE WHEN has_property_sale THEN 1 ELSE 0 END) as property_sales,
    SUM(CASE WHEN has_children THEN 1 ELSE 0 END) as children_events,
    SUM(CASE WHEN has_international_move THEN 1 ELSE 0 END) as international_moves,
    COUNT(*) as total_simulations
FROM simulations;

-- Currency preferences
SELECT 
    currency,
    COUNT(*) as simulation_count,
    COUNT(DISTINCT user_id) as unique_users
FROM simulations
GROUP BY currency
ORDER BY simulation_count DESC;

-- Simulation success rates by age
SELECT 
    FLOOR(CAST(parameters->>'starting_age' AS NUMERIC) / 5) * 5 as age_bracket,
    AVG(probability_of_success) as avg_success_rate,
    COUNT(*) as simulations
FROM simulations
WHERE parameters->>'starting_age' IS NOT NULL
GROUP BY age_bracket
ORDER BY age_bracket;
```

---

## Data Export Workflows

### Regular Reporting

**Weekly:**
```bash
# Export all data
python analytics_module.py

# Files created in exports/analytics/:
# - user_demographics.csv
# - simulation_details.csv
# - age_segmented_analysis.csv
# - income_segmented_analysis.csv
# - property_ownership_summary.csv
# - retirement_planning_summary.csv
# - savings_behavior_analysis.csv
# - summary_statistics.csv
```

**Monthly:**
- Review user growth trends
- Analyze engagement metrics
- Identify popular features
- Check for data quality issues

**Quarterly:**
- Deep dive financial behavior analysis
- Age cohort comparisons
- Feature usage patterns
- Success rate trends

### Research Projects

1. **Generate hypothesis** from dashboard visualizations
2. **Export detailed data** via CSV downloads
3. **Run custom SQL queries** for specific analyses
4. **Document findings** for product decisions

---

## Adding New Analytics

### 1. Add Database Fields

Update `database.py` to track new data:

```python
# Add column to Simulation model
new_metric = Column(Float, nullable=True)
```

### 2. Update Data Collection

Modify `data_tracking.py`:

```python
def save_simulation(..., new_metric=None):
    # Store new metric
    sim.new_metric = new_metric
```

### 3. Create Analytics Function

Add to `analytics_module.py`:

```python
def generate_new_metric_analysis(db=None):
    # Query and analyze new metric
    # Return DataFrame
```

### 4. Add to Admin Dashboard

Update `admin_analytics.py` to display new analysis.

---

## Security & Privacy

### Best Practices

✅ **DO:**
- Filter by `user_id` for user-specific queries
- Use anonymized brackets for public reporting
- Export aggregated data only
- Keep connection strings secret
- Use read-only database users when possible

❌ **DON'T:**
- Share raw database dumps publicly
- Include PII in exported CSVs
- Hard-code credentials in scripts
- Run UPDATE/DELETE queries without backups

### Data Retention

- **Users:** Retained until account deletion request
- **Simulations:** Retained indefinitely for research
- **Budgets:** Retained until deletion request
- **Usage Stats:** Retained indefinitely for analytics

### Compliance

- Users consent to anonymized data sharing during registration
- Financial amounts stored as brackets for privacy
- No PII shared externally
- Data used for product improvement only

---

## Troubleshooting

### "Permission denied" when accessing database

**Solution:** Verify you're using correct credentials from Render Dashboard

### "No such table" error

**Solution:** Run migrations first:
```bash
python -c "from database import init_db; init_db()"
python migrate_add_currency_to_budgets.py
```

### Empty analytics exports

**Solution:** Check if simulations exist:
```sql
SELECT COUNT(*) FROM simulations;
```

### Slow queries on large datasets

**Solution:** Add indexes or use pre-aggregated analytics tables

---

## Support

- **Documentation:** `docs/RENDER_DATABASE_MANAGEMENT.md`
- **SQL Examples:** `docs/DATABASE_ACCESS_GUIDE.md`
- **Deployment:** `DEPLOYMENT_CHECKLIST.md`

---

**Last Updated:** November 28, 2025
