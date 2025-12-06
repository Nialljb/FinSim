# 🚀 Database Management on Render - Deployment Guide

## Overview

When deploying to Render, your app switches from **SQLite** (local file) to **PostgreSQL** (cloud database). This guide covers all considerations for pushing to GitHub and running analytics on Render.

---

## 🔄 Key Differences: Local vs. Render

| Aspect | Local Development | Render Production |
|--------|------------------|-------------------|
| **Database** | SQLite (`finsim.db` file) | PostgreSQL (managed database) |
| **Connection** | `sqlite:///finsim.db` | `DATABASE_URL` env variable |
| **File System** | Persistent | **Ephemeral** (resets on deploy) |
| **Exports Location** | `exports/` directory | Must use external storage |
| **Database Access** | Direct file access | psql or Render Dashboard |
| **Migrations** | Run manually | Must run via Render Shell |

---

## ⚠️ Critical Considerations for Render

### 1. **File System is Ephemeral**

**Problem:** Render's file system resets on every deployment. The `exports/analytics/` directory will be deleted.

**Solutions:**

#### Option A: Database-Based Export Storage (Recommended)
Store exports in the PostgreSQL database instead of files:

```python
# Add new model to database.py
class AnalyticsExport(Base):
    __tablename__ = "analytics_exports"
    
    id = Column(Integer, primary_key=True)
    export_type = Column(String(100))  # "age_segmented", "income_analysis", etc.
    export_date = Column(DateTime, default=datetime.utcnow)
    data = Column(JSON)  # Store CSV data as JSON
    created_by = Column(Integer, ForeignKey('users.id'))
```

#### Option B: Use External Storage (S3, Cloud Storage)
Upload CSV files to AWS S3 or similar:

```python
import boto3
from io import StringIO

def upload_to_s3(df, filename):
    s3_client = boto3.client('s3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
        aws_secret_access_key=os.getenv('AWS_SECRET_KEY')
    )
    
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    
    s3_client.put_object(
        Bucket='finsim-exports',
        Key=f'analytics/{filename}',
        Body=csv_buffer.getvalue()
    )
```

#### Option C: Streamlit Download Buttons (Simplest)
Generate CSVs on-demand and let users download them:

```python
import streamlit as st

# In your Streamlit app
df = generate_analytics_dataframe()
csv = df.to_csv(index=False)
st.download_button(
    label="📥 Download Analytics CSV",
    data=csv,
    file_name="simulation_analytics.csv",
    mime="text/csv"
)
```

---

### 2. **Database Migration Strategy**

Your migration scripts (like `migrate_add_currency_to_budgets.py`) need to run on Render's PostgreSQL database.

#### Method 1: Alembic (Professional Approach)

**Install Alembic:**
```bash
pip install alembic
pip freeze > requirements.txt
```

**Initialize Alembic:**
```bash
alembic init alembic
```

**Create migration:**
```python
# alembic/versions/001_add_currency_to_budgets.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('saved_budgets', 
        sa.Column('currency', sa.String(10), server_default='EUR')
    )

def downgrade():
    op.drop_column('saved_budgets', 'currency')
```

**Update `render.yaml` buildCommand:**
```yaml
buildCommand: |
  pip install -r requirements.txt
  alembic upgrade head  # Run migrations on deploy
```

#### Method 2: Manual via Render Shell

**Access Render Shell:**
1. Go to Render Dashboard → Your Web Service
2. Click **"Shell"** tab
3. Click **"Open Shell"**

**Run migration:**
```bash
python migrate_add_currency_to_budgets.py
```

**⚠️ Note:** This only works if your migration script checks for PostgreSQL:

```python
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///finsim.db')

# Fix for Render PostgreSQL URL
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Check if column exists (works for both SQLite and PostgreSQL)
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='saved_budgets' AND column_name='currency'
    """))
    
    if not result.fetchone():
        conn.execute(text("ALTER TABLE saved_budgets ADD COLUMN currency VARCHAR(10) DEFAULT 'EUR'"))
        conn.commit()
```

---

### 3. **Environment Variables Configuration**

**Required Environment Variables on Render:**

| Variable | Value | Set In |
|----------|-------|--------|
| `DATABASE_URL` | Auto-set by Render | Database connection |
| `SECRET_KEY` | Auto-generated | render.yaml |
| `FREE_SIMULATION_LIMIT` | `10` | render.yaml |
| `AWS_ACCESS_KEY` | Your AWS key | Render Dashboard (if using S3) |
| `AWS_SECRET_KEY` | Your AWS secret | Render Dashboard |
| `S3_BUCKET_NAME` | `finsim-exports` | Render Dashboard |

**Update database.py for PostgreSQL compatibility:**

```python
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///finsim.db')

# Fix Render's postgres:// → postgresql:// URL format
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

engine = create_engine(DATABASE_URL, echo=False)
```

---

### 4. **Analytics Export on Render**

Since the file system is ephemeral, modify `export_analytics.py` to work on Render:

#### Updated Implementation:

```python
import os
import streamlit as st
from io import StringIO
import pandas as pd

def export_analytics_for_render():
    """
    Generate analytics DataFrames and return them
    No file writing - returns dict of DataFrames
    """
    db = SessionLocal()
    try:
        exports = {}
        
        # Generate all analytics DataFrames
        exports['user_demographics'] = generate_user_demographics_df(db)
        exports['simulation_details'] = generate_simulation_details_df(db)
        exports['age_segmented'] = generate_age_segmented_df(db)
        exports['income_segmented'] = generate_income_segmented_df(db)
        exports['property_ownership'] = generate_property_ownership_df(db)
        exports['retirement_planning'] = generate_retirement_planning_df(db)
        exports['savings_behavior'] = generate_savings_behavior_df(db)
        exports['summary_stats'] = generate_summary_stats_df(db)
        
        return exports
    finally:
        db.close()


def create_download_buttons(exports):
    """
    Create Streamlit download buttons for all exports
    """
    st.subheader("📥 Download Analytics Reports")
    
    cols = st.columns(2)
    
    for idx, (name, df) in enumerate(exports.items()):
        col = cols[idx % 2]
        csv = df.to_csv(index=False)
        
        col.download_button(
            label=f"📊 {name.replace('_', ' ').title()}",
            data=csv,
            file_name=f"{name}.csv",
            mime="text/csv",
            key=f"download_{name}"
        )
```

**Add to your Streamlit app:**

```python
# In wealth_simulator.py or a new analytics page

if st.session_state.get('logged_in'):
    with st.expander("📊 Export Analytics Data"):
        if st.button("Generate Analytics Reports"):
            with st.spinner("Generating analytics..."):
                exports = export_analytics_for_render()
                create_download_buttons(exports)
                st.success("✅ Analytics ready for download!")
```

---

## 📊 Viewing Database on Render

### Option 1: Render Dashboard SQL Editor (Easiest)

1. **Navigate:** Dashboard → `finsim-db` → **Connect** tab
2. **Open SQL Editor**
3. **Run queries:**

```sql
-- User demographics
SELECT current_age, target_retirement_age, country, COUNT(*) 
FROM users 
GROUP BY current_age, target_retirement_age, country;

-- Simulation summary
SELECT 
    currency,
    income_bracket,
    COUNT(*) as simulations,
    AVG(probability_of_success) as avg_success_rate
FROM simulations
GROUP BY currency, income_bracket;

-- Age-based wealth analysis
SELECT 
    FLOOR(u.current_age / 5) * 5 as age_bracket,
    s.initial_liquid_wealth_bracket,
    COUNT(*) as count
FROM users u
JOIN simulations s ON u.id = s.user_id
GROUP BY age_bracket, s.initial_liquid_wealth_bracket
ORDER BY age_bracket;
```

### Option 2: psql Command Line

```bash
# Get connection string from Render Dashboard → Database → Connect
psql postgresql://finsim_user:password@hostname:5432/finsim

# Run queries
\dt  # List tables
SELECT * FROM users LIMIT 5;
```

### Option 3: DBeaver / TablePlus (GUI)

1. Download [DBeaver](https://dbeaver.io/) or [TablePlus](https://tableplus.com/)
2. Create new PostgreSQL connection
3. Copy connection details from Render Dashboard
4. Browse tables visually, run queries, export data

---

## 🔒 Security Considerations

### 1. **Never Commit Sensitive Data**

Add to `.gitignore`:
```
# Local database
finsim.db
*.db

# Environment variables
.env

# Local exports
exports/
```

### 2. **Use Environment Variables**

```python
# ✅ Good
DATABASE_URL = os.getenv('DATABASE_URL')
SECRET_KEY = os.getenv('SECRET_KEY')

# ❌ Bad
DATABASE_URL = "postgresql://user:password@host/db"
```

### 3. **SQL Injection Protection**

SQLAlchemy ORM protects you, but if writing raw SQL:

```python
# ✅ Good - parameterized query
from sqlalchemy import text
result = conn.execute(text("SELECT * FROM users WHERE id = :user_id"), 
                      {"user_id": user_id})

# ❌ Bad - string concatenation
result = conn.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

---

## 📦 Deployment Checklist

### Before Pushing to GitHub:

- [ ] Update `.gitignore` (exclude `finsim.db`, `.env`, `exports/`)
- [ ] Update `database.py` to handle PostgreSQL URLs
- [ ] Update `requirements.txt` with all dependencies
- [ ] Test migrations work with PostgreSQL
- [ ] Modify export scripts for ephemeral file system
- [ ] Add download buttons for analytics in Streamlit UI

### After Deploying to Render:

- [ ] Verify `DATABASE_URL` is set correctly
- [ ] Run migrations via Render Shell or Alembic
- [ ] Test user registration creates database entries
- [ ] Test simulation save/load functionality
- [ ] Test analytics export downloads
- [ ] Check database via SQL Editor
- [ ] Set up regular database backups (Render Dashboard → Database → Backups)

---

## 🛠 Troubleshooting

### "No such table" Error

**Cause:** Database tables not created

**Solution:**
```bash
# In Render Shell
python -c "from database import init_db; init_db()"
```

### "Column does not exist" Error

**Cause:** Migration not run

**Solution:**
```bash
# Run migration script
python migrate_add_currency_to_budgets.py
```

### Export Files Disappear

**Cause:** Ephemeral file system

**Solution:** Implement download buttons or S3 storage (see above)

### Database Connection Timeout

**Cause:** Free tier database sleeps after inactivity

**Solution:** 
- Upgrade to paid tier ($7/month)
- Add connection retry logic:

```python
from sqlalchemy.exc import OperationalError
import time

def get_db_with_retry(max_retries=3):
    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            return db
        except OperationalError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
```

---

## 📚 Additional Resources

- [Render PostgreSQL Documentation](https://render.com/docs/databases)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
- [Streamlit File Downloads](https://docs.streamlit.io/library/api-reference/widgets/st.download_button)

---

## 🎯 Recommended Architecture for Production

```
┌─────────────────────────────────────────────────┐
│         GitHub Repository (Source)              │
│  - All code                                     │
│  - render.yaml (deployment config)              │
│  - alembic/ (migrations)                        │
│  - .gitignore (excludes local DB)               │
└─────────────────────────────────────────────────┘
                     ↓ (push)
┌─────────────────────────────────────────────────┐
│              Render Platform                     │
│  ┌─────────────────────────────────────────┐   │
│  │  Web Service (finsim-app)               │   │
│  │  - Streamlit app                        │   │
│  │  - Analytics UI                         │   │
│  │  - Download buttons for exports         │   │
│  └─────────────────────────────────────────┘   │
│                     ↓                            │
│  ┌─────────────────────────────────────────┐   │
│  │  PostgreSQL Database (finsim-db)        │   │
│  │  - Users                                │   │
│  │  - Simulations                          │   │
│  │  - SavedBudgets                         │   │
│  │  - UsageStats                           │   │
│  │  - (Optional) AnalyticsExports table    │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
                     ↓ (backup)
┌─────────────────────────────────────────────────┐
│     External Storage (Optional)                  │
│  - AWS S3 (for large exports)                   │
│  - Render Backups (automatic)                   │
└─────────────────────────────────────────────────┘
```

---

**Questions?** Check the [DATABASE_ACCESS_GUIDE.md](./DATABASE_ACCESS_GUIDE.md) for SQL query examples.
