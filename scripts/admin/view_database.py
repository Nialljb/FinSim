#!/usr/bin/env python3
"""
FinSim Database Viewer
View users, simulations, and analytics from your database
"""

import os
import sys
from data_layer.database import SessionLocal, User, Simulation, UsageStats
import pandas as pd
from datetime import datetime
from sqlalchemy import func, Integer


def view_all_users():
    """View all registered users"""
    db = SessionLocal()
    try:
        users = db.query(User).order_by(User.created_at.desc()).all()
        
        data = []
        for user in users:
            data.append({
                'ID': user.id,
                'Username': user.username,
                'Email': user.email,
                'Age': user.current_age,
                'Retirement Age': user.target_retirement_age,
                'Country': user.country or 'N/A',
                'Created': user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else 'N/A',
                'Last Login': user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never'
            })
        
        df = pd.DataFrame(data)
        print("\n" + "="*100)
        print("📊 ALL USERS")
        print("="*100)
        if len(df) > 0:
            print(df.to_string(index=False))
            print(f"\n✅ Total Users: {len(df)}")
        else:
            print("No users found")
        print("="*100)
        
        return df
    finally:
        db.close()


def view_recent_simulations(limit=20):
    """View recent simulations"""
    db = SessionLocal()
    try:
        sims = db.query(Simulation).order_by(
            Simulation.created_at.desc()
        ).limit(limit).all()
        
        data = []
        for sim in sims:
            user = db.query(User).filter(User.id == sim.user_id).first()
            
            data.append({
                'ID': sim.id,
                'User': user.username if user else 'Unknown',
                'Name': sim.name[:30] if sim.name else 'N/A',
                'Currency': sim.currency,
                'Years': sim.parameters.get('simulation_years', 'N/A') if sim.parameters else 'N/A',
                'Events': sim.number_of_events,
                'Created': sim.created_at.strftime('%Y-%m-%d %H:%M') if sim.created_at else 'N/A'
            })
        
        df = pd.DataFrame(data)
        print("\n" + "="*100)
        print(f"🎲 RECENT SIMULATIONS (Last {limit})")
        print("="*100)
        if len(df) > 0:
            print(df.to_string(index=False))
            print(f"\n✅ Showing: {len(df)} simulations")
        else:
            print("No simulations found")
        print("="*100)
        
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
        ).outerjoin(Simulation, User.id == Simulation.user_id).group_by(
            User.id, User.username, User.email, 
            User.current_age, User.target_retirement_age
        ).order_by(func.count(Simulation.id).desc()).all()
        
        data = []
        for row in results:
            data.append({
                'Username': row.username,
                'Email': row.email,
                'Age': row.current_age,
                'Retirement': row.target_retirement_age,
                'Simulations': row.sim_count,
                'Last Simulation': row.last_sim.strftime('%Y-%m-%d') if row.last_sim else 'Never'
            })
        
        df = pd.DataFrame(data)
        print("\n" + "="*100)
        print("👥 USER ACTIVITY SUMMARY")
        print("="*100)
        if len(df) > 0:
            print(df.to_string(index=False))
            print(f"\n✅ Total Users: {len(df)}")
        else:
            print("No activity data")
        print("="*100)
        
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
                'User': user.username if user else f'User {stat.user_id}',
                'Month': stat.current_month,
                'Simulations': stat.simulations_this_month,
                'Exports': stat.exports_this_month,
                'Last Sim': stat.last_simulation_date.strftime('%Y-%m-%d') if stat.last_simulation_date else 'N/A'
            })
        
        df = pd.DataFrame(data)
        print("\n" + "="*100)
        print("📈 USAGE STATISTICS (Current Month)")
        print("="*100)
        if len(df) > 0:
            print(df.to_string(index=False))
            print(f"\n✅ Total Active Users: {len(df)}")
        else:
            print("No usage data")
        print("="*100)
        
        return df
    finally:
        db.close()


def get_analytics():
    """Get aggregated analytics"""
    db = SessionLocal()
    try:
        from sqlalchemy import func
        
        # Total counts
        total_users = db.query(func.count(User.id)).scalar() or 0
        total_sims = db.query(func.count(Simulation.id)).scalar() or 0
        
        # Average simulations per user
        avg_sims = total_sims / total_users if total_users > 0 else 0
        
        # Popular currencies
        currencies = db.query(
            Simulation.currency,
            func.count(Simulation.id).label('count')
        ).group_by(Simulation.currency).order_by(func.count(Simulation.id).desc()).all()
        
        # Age statistics
        age_stats = db.query(
            func.count(User.id).label('count'),
            func.avg(User.current_age).label('avg_age'),
            func.avg(User.target_retirement_age).label('avg_retirement'),
            func.min(User.current_age).label('min_age'),
            func.max(User.current_age).label('max_age')
        ).first()
        
        # Event statistics - count where True
        property_purchases = db.query(func.count(Simulation.id)).filter(Simulation.has_property_purchase == True).scalar() or 0
        has_children = db.query(func.count(Simulation.id)).filter(Simulation.has_children == True).scalar() or 0
        international_moves = db.query(func.count(Simulation.id)).filter(Simulation.has_international_move == True).scalar() or 0
        avg_events = db.query(func.avg(Simulation.number_of_events)).scalar() or 0
        
        # Create a simple object to match existing code structure
        class EventStats:
            pass
        event_stats = EventStats()
        event_stats.property_purchases = property_purchases
        event_stats.has_children = has_children
        event_stats.international_moves = international_moves
        event_stats.avg_events = avg_events
        
        print("\n" + "="*100)
        print("📊 ANALYTICS DASHBOARD")
        print("="*100)
        
        
    finally:
        db.close()


def export_all_data():
    """Export all data to CSV files"""
    import os
    
    # Create exports directory
    os.makedirs('exports', exist_ok=True)
    
    print("\n📦 Exporting data...")
    
    # Export users
    users_df = view_all_users()
    users_df.to_csv('exports/users.csv', index=False)
    print("✅ Exported: exports/users.csv")
    
    # Export simulations
    sims_df = view_recent_simulations(limit=10000)
    sims_df.to_csv('exports/simulations.csv', index=False)
    print("✅ Exported: exports/simulations.csv")
    
    # Export activity
    activity_df = view_user_activity()
    activity_df.to_csv('exports/user_activity.csv', index=False)
    print("✅ Exported: exports/user_activity.csv")
    
    # Export usage
    usage_df = view_usage_stats()
    usage_df.to_csv('exports/usage_stats.csv', index=False)
    print("✅ Exported: exports/usage_stats.csv")
    
    print("\n✅ All data exported to 'exports/' directory")


def show_help():
    """Show usage help"""
    print("""
FinSim Database Viewer
=====================

Usage: python view_database.py [command]

Commands:
  users         - View all registered users
  simulations   - View recent simulations
  activity      - View user activity summary
  usage         - View usage statistics
  analytics     - View analytics dashboard
  export        - Export all data to CSV files
  help          - Show this help

Examples:
  python view_database.py                 # Show everything
  python view_database.py users           # Just users
  python view_database.py analytics       # Just analytics
  python view_database.py export          # Export to CSV

For production database:
  export DATABASE_URL="postgresql://user:pass@host:port/db"
  python view_database.py
    """)


if __name__ == "__main__":
    print("\n🗄️  FinSim Database Viewer")
    
    # Check for DATABASE_URL
    if 'DATABASE_URL' in os.environ:
        db_url = os.environ['DATABASE_URL']
        # Mask password in output
        if '@' in db_url:
            masked = db_url.split('@')[1]
            print(f"📍 Connected to: {masked}")
        else:
            print(f"📍 Connected to: Production database")
    else:
        print("📍 Connected to: Local database (finsim.db)")
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'users':
            view_all_users()
        elif command == 'simulations' or command == 'sims':
            view_recent_simulations(limit=50)
        elif command == 'activity':
            view_user_activity()
        elif command == 'usage':
            view_usage_stats()
        elif command == 'analytics':
            get_analytics()
        elif command == 'export':
            export_all_data()
        elif command == 'help':
            show_help()
        else:
            print(f"❌ Unknown command: {command}")
            print("Run 'python view_database.py help' for usage")
    else:
        # Show everything
        view_all_users()
        view_recent_simulations()
        view_user_activity()
        view_usage_stats()
        get_analytics()
        
        print("\n💡 Tip: Run 'python view_database.py export' to save data to CSV files")