#!/usr/bin/env python3
"""
Migration: Add budget_min, budget_max, budget_target columns to saved_budgets table
Run this script to update your local SQLite database
"""

import sqlite3
import os

def migrate_database():
    db_path = 'finsim.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database {db_path} not found")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(saved_budgets)")
        columns = [col[1] for col in cursor.fetchall()]
        
        columns_to_add = []
        if 'budget_min' not in columns:
            columns_to_add.append('budget_min')
        if 'budget_max' not in columns:
            columns_to_add.append('budget_max')
        if 'budget_target' not in columns:
            columns_to_add.append('budget_target')
        
        if not columns_to_add:
            print("✅ All columns already exist - no migration needed")
            return True
        
        print(f"Adding columns: {', '.join(columns_to_add)}")
        
        # Add missing columns
        for column in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE saved_budgets ADD COLUMN {column} JSON")
                print(f"  ✅ Added {column}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"  ⏭️  {column} already exists")
                else:
                    raise
        
        # Update existing rows to have empty JSON objects for new columns
        cursor.execute("""
            UPDATE saved_budgets 
            SET budget_min = '{}', 
                budget_max = '{}', 
                budget_target = '{}'
            WHERE budget_min IS NULL 
               OR budget_max IS NULL 
               OR budget_target IS NULL
        """)
        
        conn.commit()
        print(f"✅ Migration complete! Updated {cursor.rowcount} existing rows")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("FinSim Database Migration: Add budget columns")
    print("=" * 60)
    success = migrate_database()
    print("=" * 60)
    if success:
        print("✅ Ready to run the app!")
    else:
        print("❌ Migration failed - please check errors above")
