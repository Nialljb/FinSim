"""
Database Migration: Add currency column to saved_budgets table
Run this script to update the production database schema on Render.

Usage:
    python migrations/add_currency_column.py
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect

# Add parent directory to path to import database module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DATABASE_URL


def check_column_exists(engine, table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def add_currency_column():
    """Add currency column to saved_budgets table if it doesn't exist"""
    
    # Get database URL (works for both local and Render)
    database_url = DATABASE_URL
    
    print(f"Connecting to database...")
    print(f"Database: {database_url.split('@')[-1] if '@' in database_url else 'local'}")
    
    # Create engine
    engine = create_engine(database_url)
    
    try:
        # Check if column already exists
        if check_column_exists(engine, 'saved_budgets', 'currency'):
            print("✓ Column 'currency' already exists in 'saved_budgets' table")
            print("No migration needed.")
            return True
        
        print("Adding 'currency' column to 'saved_budgets' table...")
        
        # Add the column
        with engine.connect() as conn:
            conn.execute(text(
                "ALTER TABLE saved_budgets ADD COLUMN currency VARCHAR(10) NULL"
            ))
            conn.commit()
        
        # Verify the column was added
        if check_column_exists(engine, 'saved_budgets', 'currency'):
            print("✓ Successfully added 'currency' column to 'saved_budgets' table")
            return True
        else:
            print("✗ Failed to add 'currency' column")
            return False
            
    except Exception as e:
        print(f"✗ Error during migration: {e}")
        return False
    finally:
        engine.dispose()


def main():
    """Run the migration"""
    print("=" * 60)
    print("Database Migration: Add currency column")
    print("=" * 60)
    print()
    
    success = add_currency_column()
    
    print()
    print("=" * 60)
    if success:
        print("✓ Migration completed successfully!")
    else:
        print("✗ Migration failed. Please check errors above.")
    print("=" * 60)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
