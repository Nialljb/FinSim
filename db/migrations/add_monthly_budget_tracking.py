"""
Migration: Add monthly budget tracking fields to saved_budgets table
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from database import engine

def upgrade():
    """Add new columns for monthly tracking"""
    
    with engine.connect() as conn:
        try:
            # For SQLite, try to add columns without IF NOT EXISTS
            try:
                conn.execute(text("ALTER TABLE saved_budgets ADD COLUMN current_month VARCHAR(7)"))
                conn.commit()
                print("✅ Added current_month column")
            except Exception as e:
                if "duplicate column" in str(e).lower():
                    print("ℹ️ current_month column already exists")
                else:
                    print(f"⚠️ current_month: {e}")
            
            try:
                conn.execute(text("ALTER TABLE saved_budgets ADD COLUMN budget_expected JSON"))
                conn.commit()
                print("✅ Added budget_expected column")
            except Exception as e:
                if "duplicate column" in str(e).lower():
                    print("ℹ️ budget_expected column already exists")
                else:
                    print(f"⚠️ budget_expected: {e}")
            
            try:
                conn.execute(text("ALTER TABLE saved_budgets ADD COLUMN budget_actuals JSON"))
                conn.commit()
                print("✅ Added budget_actuals column")
            except Exception as e:
                if "duplicate column" in str(e).lower():
                    print("ℹ️ budget_actuals column already exists")
                else:
                    print(f"⚠️ budget_actuals: {e}")
            
            print("✅ Successfully completed monthly budget tracking migration")
        except Exception as e:
            print(f"❌ Error: {e}")
            raise

if __name__ == "__main__":
    print("Running migration: add_monthly_budget_tracking")
    upgrade()
    print("Migration completed!")
