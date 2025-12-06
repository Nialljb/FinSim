"""
Migration script to add currency column to saved_budgets table
Works with both SQLite (local) and PostgreSQL (Render)
"""

import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

def migrate_database():
    """Add currency column to saved_budgets table if it doesn't exist"""
    
    # Get database URL from environment or default to SQLite
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///finsim.db')
    
    # Fix for Render PostgreSQL URL format
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    print(f"Migrating database: {DATABASE_URL.split('@')[0] if '@' in DATABASE_URL else 'SQLite'}...")
    
    # Check which database type we're using
    is_postgres = DATABASE_URL.startswith('postgresql://')
    
    if is_postgres:
        # PostgreSQL migration using SQLAlchemy
        from sqlalchemy import create_engine, text
        
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='saved_budgets' AND column_name='currency'
            """))
            
            if result.fetchone():
                print("✅ Currency column already exists - no migration needed")
            else:
                print("Adding currency column to saved_budgets table...")
                
                # Add column with default value
                conn.execute(text(
                    "ALTER TABLE saved_budgets ADD COLUMN currency VARCHAR(10) DEFAULT 'EUR'"
                ))
                
                # Update existing rows
                conn.execute(text(
                    "UPDATE saved_budgets SET currency = 'EUR' WHERE currency IS NULL"
                ))
                
                conn.commit()
                print("✅ Successfully added currency column (PostgreSQL)")
    
    else:
        # SQLite migration (original code)
        db_path = os.path.join(os.path.dirname(__file__), 'finsim.db')
        
        if not os.path.exists(db_path):
            print(f"Database not found at {db_path}")
            print("No migration needed - database will be created fresh.")
            return
        
        print(f"Migrating database at: {db_path}")
        
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
            print("✅ Successfully added currency column (SQLite)")
            print("✅ Set default currency to 'EUR' for existing budgets")
        
        conn.close()
    
    print("\n✅ Migration complete!")

if __name__ == "__main__":
    migrate_database()
