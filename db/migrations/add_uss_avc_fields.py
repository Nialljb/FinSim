"""
Migration: Add USS AVC fields to pension_plans table
Date: 2025-12-01
Description: Adds fields for tracking Additional Voluntary Contributions (AVCs) to USS pensions
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import engine, SessionLocal
from sqlalchemy import text, inspect


def run_migration():
    """Add USS AVC columns to pension_plans table"""
    
    db = SessionLocal()
    try:
        inspector = inspect(engine)
        
        # Check if pension_plans table exists
        if 'pension_plans' not in inspector.get_table_names():
            print("❌ pension_plans table does not exist. Run add_pension_plans_table.py first.")
            return False
        
        # Check if columns already exist
        columns = [col['name'] for col in inspector.get_columns('pension_plans')]
        
        columns_to_add = []
        if 'uss_avc_enabled' not in columns:
            columns_to_add.append(('uss_avc_enabled', 'BOOLEAN DEFAULT FALSE'))
        if 'uss_avc_annual_amount' not in columns:
            columns_to_add.append(('uss_avc_annual_amount', 'FLOAT DEFAULT 0'))
        if 'uss_avc_percentage' not in columns:
            columns_to_add.append(('uss_avc_percentage', 'FLOAT DEFAULT 0'))
        if 'uss_avc_current_value' not in columns:
            columns_to_add.append(('uss_avc_current_value', 'FLOAT DEFAULT 0'))
        if 'uss_avc_projected_value' not in columns:
            columns_to_add.append(('uss_avc_projected_value', 'FLOAT DEFAULT 0'))
        
        if not columns_to_add:
            print("✓ USS AVC columns already exist")
            return True
        
        # Add columns
        for column_name, column_type in columns_to_add:
            try:
                # SQLite syntax
                sql = f"ALTER TABLE pension_plans ADD COLUMN {column_name} {column_type}"
                db.execute(text(sql))
                db.commit()
                print(f"✓ Added column: {column_name}")
            except Exception as e:
                # If column already exists, continue
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    print(f"✓ Column {column_name} already exists")
                    db.rollback()
                else:
                    raise e
        
        print("✓ USS AVC migration completed successfully")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Migration failed: {str(e)}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("Running USS AVC migration...")
    success = run_migration()
    if success:
        print("✅ Migration completed!")
    else:
        print("❌ Migration failed!")
