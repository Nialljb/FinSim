"""
Migration: Add simulation_end_age to pension_plans table
Date: 2025-12-01
Description: Adds field for storing the end age for retirement simulations
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data_layer.database import engine, SessionLocal
from sqlalchemy import text, inspect


def run_migration():
    """Add simulation_end_age column to pension_plans table"""
    
    db = SessionLocal()
    try:
        inspector = inspect(engine)
        
        # Check if pension_plans table exists
        if 'pension_plans' not in inspector.get_table_names():
            print("❌ pension_plans table does not exist. Run add_pension_plans_table.py first.")
            return False
        
        # Check if column already exists
        columns = [col['name'] for col in inspector.get_columns('pension_plans')]
        
        if 'simulation_end_age' in columns:
            print("✓ simulation_end_age column already exists")
            return True
        
        # Add column
        try:
            sql = "ALTER TABLE pension_plans ADD COLUMN simulation_end_age INTEGER DEFAULT 0"
            db.execute(text(sql))
            db.commit()
            print("✓ Added column: simulation_end_age")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("✓ Column simulation_end_age already exists")
                db.rollback()
            else:
                raise e
        
        print("✓ Simulation end age migration completed successfully")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Migration failed: {str(e)}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("Running simulation end age migration...")
    success = run_migration()
    if success:
        print("✅ Migration completed!")
    else:
        print("❌ Migration failed!")
