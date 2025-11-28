"""
Migration script to add currency column to saved_budgets table
"""

import sqlite3
import os

def migrate_database():
    """Add currency column to saved_budgets table if it doesn't exist"""
    
    # Get database path
    db_path = os.path.join(os.path.dirname(__file__), 'finsim.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        print("No migration needed - database will be created fresh.")
        return
    
    print(f"Migrating database at: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(saved_budgets)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'currency' in columns:
            print("✅ Currency column already exists - no migration needed")
        else:
            print("Adding currency column to saved_budgets table...")
            cursor.execute("""
                ALTER TABLE saved_budgets 
                ADD COLUMN currency VARCHAR(10)
            """)
            
            # Set default value for existing records
            cursor.execute("""
                UPDATE saved_budgets 
                SET currency = 'EUR' 
                WHERE currency IS NULL
            """)
            
            conn.commit()
            print("✅ Successfully added currency column")
            print("✅ Set default currency to 'EUR' for existing budgets")
        
        conn.close()
        print("\n✅ Migration complete!")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        if conn:
            conn.rollback()
            conn.close()
        raise

if __name__ == "__main__":
    migrate_database()
