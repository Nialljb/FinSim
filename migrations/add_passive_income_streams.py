"""
Migration: Add passive_income_streams table
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, Base, PassiveIncomeStream

def upgrade():
    """Add passive_income_streams table"""
    
    try:
        # Create only the PassiveIncomeStream table
        PassiveIncomeStream.__table__.create(engine, checkfirst=True)
        print("✅ Successfully created passive_income_streams table")
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        raise

if __name__ == "__main__":
    print("Running migration: add_passive_income_streams")
    upgrade()
    print("Migration completed!")
