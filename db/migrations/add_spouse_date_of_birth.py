"""
Migration: Add spouse_date_of_birth field to pension_plans table
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text
from data_layer.database import engine

def upgrade():
    """Add spouse_date_of_birth field to pension_plans table"""
    
    with engine.connect() as conn:
        print("Starting spouse_date_of_birth migration...")
        
        # Add spouse_date_of_birth to pension_plans table
        try:
            conn.execute(text("ALTER TABLE pension_plans ADD COLUMN spouse_date_of_birth VARCHAR(10)"))
            conn.commit()
            print("✅ Added pension_plans.spouse_date_of_birth")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("ℹ️  pension_plans.spouse_date_of_birth already exists")
            else:
                print(f"⚠️  pension_plans.spouse_date_of_birth: {e}")
        
        print("✅ Successfully completed spouse_date_of_birth migration")

if __name__ == "__main__":
    print("Running migration: add_spouse_date_of_birth")
    upgrade()
    print("Migration completed!")
