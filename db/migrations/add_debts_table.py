"""
Migration: Add debts table for debt tracking and management
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text
from data_layer.database import engine

def upgrade():
    """Add debts table"""
    
    with engine.connect() as conn:
        print("Starting debts table migration...")
        
        # Create debts table
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS debts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    debt_type VARCHAR(50) NOT NULL,
                    principal_amount FLOAT DEFAULT 0,
                    current_balance FLOAT DEFAULT 0,
                    interest_rate FLOAT DEFAULT 0,
                    monthly_payment FLOAT DEFAULT 0,
                    minimum_payment FLOAT DEFAULT 0,
                    term_months INTEGER,
                    remaining_months INTEGER,
                    start_date VARCHAR(10),
                    property_value FLOAT,
                    down_payment FLOAT,
                    allows_extra_payments BOOLEAN DEFAULT 1,
                    extra_payment_amount FLOAT DEFAULT 0,
                    credit_limit FLOAT,
                    lender VARCHAR(255),
                    notes TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """))
            conn.commit()
            print("✅ Created debts table")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("ℹ️  debts table already exists")
            else:
                print(f"⚠️  debts table: {e}")
        
        # Create index on user_id
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_debts_user_id ON debts(user_id)"))
            conn.commit()
            print("✅ Created index on debts.user_id")
        except Exception as e:
            print(f"ℹ️  Index may already exist: {e}")
        
        print("✅ Successfully completed debts table migration")

if __name__ == "__main__":
    print("Running migration: add_debts_table")
    upgrade()
    print("Migration completed!")
