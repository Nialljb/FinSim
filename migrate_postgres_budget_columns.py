"""
Migration script to add budget_min, budget_max, and budget_target columns to PostgreSQL database.
This script is designed to run on Render's production database.

Run this script once to update the database schema.
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

def get_database_url():
    """Get database URL from environment or use default local SQLite."""
    # Render sets DATABASE_URL automatically
    db_url = os.environ.get('DATABASE_URL')
    
    if db_url:
        # Render uses postgres:// but SQLAlchemy needs postgresql://
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        print(f"Using database: {db_url.split('@')[1] if '@' in db_url else 'local'}")
    else:
        db_url = 'sqlite:///financial_planner.db'
        print(f"Using local SQLite database: {db_url}")
    
    return db_url

def column_exists(inspector, table_name, column_name):
    """Check if a column exists in a table."""
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def add_budget_columns():
    """Add budget_min, budget_max, and budget_target columns to saved_budgets table."""
    try:
        # Get database connection
        db_url = get_database_url()
        engine = create_engine(db_url)
        inspector = inspect(engine)
        
        # Check if table exists
        if 'saved_budgets' not in inspector.get_table_names():
            print("❌ Error: saved_budgets table does not exist!")
            return False
        
        print("\n🔍 Checking existing columns...")
        
        # Columns to add
        columns_to_add = {
            'budget_min': 'JSON',
            'budget_max': 'JSON',
            'budget_target': 'JSON'
        }
        
        added_columns = []
        skipped_columns = []
        
        with engine.connect() as conn:
            for column_name, column_type in columns_to_add.items():
                if column_exists(inspector, 'saved_budgets', column_name):
                    print(f"⏭️  Column '{column_name}' already exists, skipping")
                    skipped_columns.append(column_name)
                else:
                    print(f"➕ Adding column: {column_name} ({column_type})")
                    
                    # PostgreSQL and SQLite have different JSON type handling
                    if 'postgresql' in db_url:
                        sql = text(f"ALTER TABLE saved_budgets ADD COLUMN {column_name} JSONB")
                    else:
                        sql = text(f"ALTER TABLE saved_budgets ADD COLUMN {column_name} TEXT")
                    
                    conn.execute(sql)
                    conn.commit()
                    print(f"✅ Added {column_name}")
                    added_columns.append(column_name)
            
            # Update existing rows to have empty JSON objects
            if added_columns:
                print(f"\n📝 Updating existing rows...")
                
                # Set default values for new columns
                update_sql = text("""
                    UPDATE saved_budgets 
                    SET budget_min = COALESCE(budget_min, '{}'),
                        budget_max = COALESCE(budget_max, '{}'),
                        budget_target = COALESCE(budget_target, '{}')
                    WHERE budget_min IS NULL 
                       OR budget_max IS NULL 
                       OR budget_target IS NULL
                """)
                
                result = conn.execute(update_sql)
                conn.commit()
                
                rows_updated = result.rowcount
                print(f"✅ Updated {rows_updated} existing rows with default empty objects")
        
        print("\n" + "="*60)
        if added_columns:
            print(f"✅ Migration complete! Added columns: {', '.join(added_columns)}")
        if skipped_columns:
            print(f"⏭️  Skipped existing columns: {', '.join(skipped_columns)}")
        if not added_columns and not skipped_columns:
            print("ℹ️  No changes needed - all columns already exist")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("PostgreSQL Budget Columns Migration")
    print("="*60)
    
    success = add_budget_columns()
    
    if not success:
        sys.exit(1)
    
    print("\n✅ Migration completed successfully!")
    sys.exit(0)
