# 📊 Viewing Database Data on Render

## Method 1: Render Dashboard SQL Editor (Easiest)

### Access Built-in SQL Editor:

1. Go to https://dashboard.render.com
2. Click on your **finsim-db** database
3. Click **"Connect"** tab
4. Scroll down to **"SQL Editor"** section
5. Click **"Open SQL Editor"**

### Run Queries:

```sql
-- View all users
SELECT id, username, email, current_age, target_retirement_age, created_at, last_login
FROM users
ORDER BY created_at DESC;

-- Count total users
SELECT COUNT(*) as total_users FROM users;

-- View recent simulations
SELECT 
    s.id,
    s.name,
    u.username,
    s.currency,
    s.simulation_years,
    s.created_at
FROM simulations s
JOIN users u ON s.user_id = u.id
ORDER BY s.created_at DESC
LIMIT 20;

-- User activity summary
SELECT 
    u.username,
    u.email,
    u.current_age,
    u.target_retirement_age,
    COUNT(s.id) as simulation_count,
    MAX(s.created_at) as last_simulation
FROM users u
LEFT JOIN simulations s ON u.id = s.user_id
GROUP BY u.id, u.username, u.email, u.current_age, u.target_retirement_age
ORDER BY simulation_count DESC;

-- Usage statistics
SELECT 
    user_id,
    simulations_this_month,
    exports_this_month,
    current_month
FROM usage_stats
ORDER BY simulations_this_month DESC;

-- Aggregated insights
SELECT 
    income_bracket,
    COUNT(*) as count
FROM simulations
GROUP BY income_bracket
ORDER BY count DESC;
```

---

## Method 2: Connect via psql (Command Line)

### Get Connection String:

1. In Render dashboard → Your database
2. Click **"Connect"** tab
3. Copy the **"External Database URL"**

### Connect:

```bash
# Mac/Linux
psql postgresql://username:password@hostname:port/database

# Or using the full connection string from Render
psql <paste-connection-string-here>
```

### Example Commands:

```sql
-- List all tables
\dt

-- Describe table structure
\d users
\d simulations

-- Run queries
SELECT * FROM users LIMIT 5;

-- Export to CSV
\copy (SELECT * FROM users) TO 'users.csv' CSV HEADER;

-- Exit
\q
```

---

## Method 3: Python Script (Recommended for Analysis)

### Create a database viewer script:

```python
# view_database.py
from database import SessionLocal, User, Simulation, UsageStats
import pandas as pd
from datetime import datetime

def view_all_users():
    """View all registered users"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        
        data = []
        for user in users:
            data.append({
                'ID': user.id,
                'Username': user.username,
                'Email': user.email,
                'Age': user.current_age,
                'Retirement Age': user.target_retirement_age,
                'Country': user.country,
                'Created': user.created_at,
                'Last Login': user.last_login
            })
        
        df = pd.DataFrame(data)
        print("\n📊 ALL USERS")
        print("=" * 80)
        print(df.to_string(index=False))
        print(f"\nTotal Users: {len(df)}")
        
        return df
    finally:
        db.close()


def view_recent_simulations(limit=20):
    """View recent simulations"""
    db = SessionLocal()
    try:
        from sqlalchemy.orm import joinedload
        
        sims = db.query(Simulation).options(
            joinedload(Simulation.user)
        ).order_by(Simulation.created_at.desc()).limit(limit).all()
        
        data = []
        for sim in sims:
            data.append({
                'ID': sim.id,
                'User': sim.user.username,
                'Name': sim.name,
                'Currency': sim.currency,
                'Years': sim.parameters.get('simulation_years', 'N/A') if sim.parameters else 'N/A',
                'Events': sim.number_of_events,
                'Created': sim.created_at
            })
        
        df = pd.DataFrame(data)
        print("\n🎲 RECENT SIMULATIONS")
        print("=" * 80)
        print(df.to_string(index=False))
        
        return df
    finally:
        db.close()


def view_user_activity():
    """View user activity summary"""
    db = SessionLocal()
    try:
        from sqlalchemy import func
        
        results = db.query(
            User.username,
            User.email,
            User.current_age,
            User.target_retirement_age,
            func.count(Simulation.id).label('sim_count'),
            func.max(Simulation.created_at).label('last_sim')
        ).outerjoin(Simulation).group_by(
            User.id, User.username, User.email, 
            User.current_age, User.target_retirement_age
        ).all()
        
        data = []
        for row in results:
            data.append({
                'Username': row.username,
                'Email': row.email,
                'Age': row.current_age,
                'Retirement': row.target_retirement_age,
                'Simulations': row.sim_count,
                'Last Simulation': row.last_sim
            })
        
        df = pd.DataFrame(data)
        print("\n👥 USER ACTIVITY SUMMARY")
        print("=" * 80)
        print(df.to_string(index=False))
        
        return df
    finally:
        db.close()


def view_usage_stats():
    """View current month usage statistics"""
    db = SessionLocal()
    try:
        stats = db.query(UsageStats).all()
        
        data = []
        for stat in stats:
            user = db.query(User).filter(User.id == stat.user_id).first()
            data.append({
                'User': user.username if user else 'Unknown',
                'Month': stat.current_month,
                'Simulations': stat.simulations_this_month,
                'Exports': stat.exports_this_month,
                'Last Sim': stat.last_simulation_date
            })
        
        df = pd.DataFrame(data)
        print("\n📈 USAGE STATISTICS")
        print("=" * 80)
        print(df.to_string(index=False))
        
        return df
    finally:
        db.close()


def get_analytics():
    """Get aggregated analytics"""
    db = SessionLocal()
    try:
        from sqlalchemy import func
        
        # Total counts
        total_users = db.query(func.count(User.id)).scalar()
        total_sims = db.query(func.count(Simulation.id)).scalar()
        
        # Average simulations per user
        avg_sims = total_sims / total_users if total_users > 0 else 0
        
        # Popular currencies
        currencies = db.query(
            Simulation.currency,
            func.count(Simulation.id).label('count')
        ).group_by(Simulation.currency).all()
        
        # Age ranges
        age_ranges = db.query(
            func.count(User.id).label('count'),
            func.avg(User.current_age).label('avg_age'),
            func.avg(User.target_retirement_age).label('avg_retirement')
        ).first()
        
        print("\n📊 ANALYTICS DASHBOARD")
        print("=" * 80)
        print(f"Total Users: {total_users}")
        print(f"Total Simulations: {total_sims}")
        print(f"Avg Simulations per User: {avg_sims:.2f}")
        print(f"\nAverage Current Age: {age_ranges.avg_age:.1f}" if age_ranges.avg_age else "N/A")
        print(f"Average Retirement Age: {age_ranges.avg_retirement:.1f}" if age_ranges.avg_retirement else "N/A")
        
        print("\nCurrency Distribution:")
        for curr in currencies:
            print(f"  {curr.currency}: {curr.count} simulations")
        
    finally:
        db.close()


def export_all_data():
    """Export all data to CSV files"""
    import os
    
    # Create exports directory
    os.makedirs('exports', exist_ok=True)
    
    # Export users
    users_df = view_all_users()
    users_df.to_csv('exports/users.csv', index=False)
    
    # Export simulations
    sims_df = view_recent_simulations(limit=1000)
    sims_df.to_csv('exports/simulations.csv', index=False)
    
    # Export activity
    activity_df = view_user_activity()
    activity_df.to_csv('exports/user_activity.csv', index=False)
    
    # Export usage
    usage_df = view_usage_stats()
    usage_df.to_csv('exports/usage_stats.csv', index=False)
    
    print("\n✅ Data exported to 'exports/' directory")


if __name__ == "__main__":
    import sys
    
    # Set DATABASE_URL for production
    # os.environ['DATABASE_URL'] = 'postgresql://...'  # Use your Render connection string
    
    print("🗄️  FinSim Database Viewer")
    print("=" * 80)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'users':
            view_all_users()
        elif command == 'simulations':
            view_recent_simulations()
        elif command == 'activity':
            view_user_activity()
        elif command == 'usage':
            view_usage_stats()
        elif command == 'analytics':
            get_analytics()
        elif command == 'export':
            export_all_data()
        else:
            print(f"Unknown command: {command}")
    else:
        # Show everything
        view_all_users()
        print("\n")
        view_recent_simulations()
        print("\n")
        view_user_activity()
        print("\n")
        view_usage_stats()
        print("\n")
        get_analytics()
```

### Usage:

```bash
# Set your database URL (get from Render)
export DATABASE_URL="postgresql://user:pass@host:port/db"

# View everything
python view_database.py

# View specific data
python view_database.py users
python view_database.py simulations
python view_database.py activity
python view_database.py analytics
python view_database.py export  # Export to CSV
```

---

## Method 4: Database GUI Tools

### Using TablePlus (Recommended - Beautiful UI)

1. Download: https://tableplus.com (Free tier available)
2. Create new connection → PostgreSQL
3. Get connection details from Render:
   - Host: (from Render connection string)
   - Port: 5432
   - Database: finsim
   - User: (from Render)
   - Password: (from Render)
4. Click "Connect"
5. Browse tables visually

### Using pgAdmin (Free, Full-featured)

1. Download: https://www.pgadmin.org
2. Add new server
3. Use connection details from Render
4. Browse, query, export

### Using DBeaver (Free, Multi-database)

1. Download: https://dbeaver.io
2. New Database Connection → PostgreSQL
3. Enter Render connection details
4. Connect and explore

---

## Method 5: Add Admin Dashboard to Your App

### Create an admin page in Streamlit:

```python
# admin.py
import streamlit as st
from database import SessionLocal, User, Simulation
import pandas as pd

def show_admin_dashboard():
    """Admin dashboard (add authentication!)"""
    
    st.title("🔐 Admin Dashboard")
    
    # Check admin password
    admin_pass = st.sidebar.text_input("Admin Password", type="password")
    if admin_pass != "your-secret-admin-password":  # Change this!
        st.error("Unauthorized")
        return
    
    tab1, tab2, tab3 = st.tabs(["Users", "Simulations", "Analytics"])
    
    with tab1:
        st.subheader("👥 Registered Users")
        
        db = SessionLocal()
        users = db.query(User).all()
        
        data = [{
            'ID': u.id,
            'Username': u.username,
            'Email': u.email,
            'Age': u.current_age,
            'Retirement': u.target_retirement_age,
            'Created': u.created_at,
            'Last Login': u.last_login
        } for u in users]
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        st.metric("Total Users", len(df))
        
        db.close()
    
    with tab2:
        st.subheader("🎲 Recent Simulations")
        
        db = SessionLocal()
        sims = db.query(Simulation).order_by(
            Simulation.created_at.desc()
        ).limit(100).all()
        
        data = [{
            'ID': s.id,
            'User ID': s.user_id,
            'Name': s.name,
            'Currency': s.currency,
            'Events': s.number_of_events,
            'Created': s.created_at
        } for s in sims]
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        st.metric("Total Simulations", len(df))
        
        db.close()
    
    with tab3:
        st.subheader("📊 Analytics")
        # Add your analytics here


# In wealth_simulator.py, add a secret admin route:
if st.session_state.get('username') == 'admin':
    show_admin_dashboard()
```

---

## Quick Reference: Common Queries

```sql
-- Active users (logged in last 30 days)
SELECT COUNT(*) FROM users 
WHERE last_login > NOW() - INTERVAL '30 days';

-- Simulations by day
SELECT 
    DATE(created_at) as date,
    COUNT(*) as count
FROM simulations
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Popular event types
SELECT 
    has_property_purchase,
    has_children,
    COUNT(*) as count
FROM simulations
GROUP BY has_property_purchase, has_children;

-- Delete test user
DELETE FROM users WHERE username = 'testuser';
```

---

## Security Notes

⚠️ **Important:**
- Never expose database credentials in your code
- Use environment variables for connection strings
- Add authentication to any admin dashboard
- Use read-only credentials for analytics if possible
- Enable SSL for database connections in production

---

## Recommended Workflow

**For quick checks:**
→ Use Render SQL Editor (Method 1)

**For analysis:**
→ Use Python script (Method 3) or GUI tool (Method 4)

**For ongoing monitoring:**
→ Add admin dashboard to app (Method 5)

**For exports:**
→ Python script with CSV export (Method 3)
