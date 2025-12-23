"""
Migration: Add preferred_currency field to users table
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text
from data_layer.database import engine

def upgrade():
    """Add preferred_currency field to users table"""
    
    with engine.connect() as conn:
        print("Starting preferred_currency migration...")
        
        # Add preferred_currency to users table
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN preferred_currency VARCHAR(10) DEFAULT 'EUR'"))
            conn.commit()
            print("✅ Added users.preferred_currency")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("ℹ️  users.preferred_currency already exists")
            else:
                print(f"⚠️  users.preferred_currency: {e}")
        
        print("✅ Successfully completed preferred_currency migration")

if __name__ == "__main__":
    print("Running migration: add_preferred_currency")
    upgrade()
    print("Migration completed!")
