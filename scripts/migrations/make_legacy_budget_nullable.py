"""
Migration: Make legacy budget columns nullable in saved_budgets table
SQLite doesn't support ALTER COLUMN, so we need to recreate the table
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text
from data_layer.database import engine

def upgrade():
    """Make legacy budget columns nullable"""
    
    with engine.connect() as conn:
        try:
            print("Starting migration to make legacy columns nullable...")
            
            # SQLite doesn't support ALTER COLUMN, so we need to:
            # 1. Create new table with correct schema
            # 2. Copy data
            # 3. Drop old table
            # 4. Rename new table
            
            # Step 1: Create new table with all columns nullable
            conn.execute(text("""
                CREATE TABLE saved_budgets_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    currency VARCHAR(10),
                    current_month VARCHAR(7),
                    budget_expected JSON,
                    budget_actuals JSON,
                    budget_now JSON,
                    budget_1yr JSON,
                    budget_5yr JSON,
                    life_events JSON,
                    is_active BOOLEAN DEFAULT 1,
                    is_default BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """))
            print("✅ Created new table structure")
            
            # Step 2: Copy data from old table
            conn.execute(text("""
                INSERT INTO saved_budgets_new 
                SELECT * FROM saved_budgets
            """))
            print("✅ Copied existing data")
            
            # Step 3: Drop old table
            conn.execute(text("DROP TABLE saved_budgets"))
            print("✅ Dropped old table")
            
            # Step 4: Rename new table
            conn.execute(text("ALTER TABLE saved_budgets_new RENAME TO saved_budgets"))
            print("✅ Renamed new table")
            
            # Step 5: Recreate indexes
            conn.execute(text("CREATE INDEX ix_saved_budgets_user_id ON saved_budgets(user_id)"))
            conn.execute(text("CREATE INDEX ix_saved_budgets_id ON saved_budgets(id)"))
            print("✅ Recreated indexes")
            
            conn.commit()
            print("✅ Successfully completed migration - legacy columns are now nullable")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error: {e}")
            raise

if __name__ == "__main__":
    print("Running migration: make_legacy_budget_nullable")
    upgrade()
    print("Migration completed!")
