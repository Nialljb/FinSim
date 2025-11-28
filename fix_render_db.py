"""
Quick Fix for Render: Add missing currency column
Run this directly on Render via shell access or one-time job.

This is a minimal script to fix the immediate error.
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect

# Prevent Streamlit from auto-running
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'

# Get database URL from environment or use the helper function
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    # Try importing from database module
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from database import DATABASE_URL as DB_URL
        DATABASE_URL = DB_URL
        print(f"Using database URL from config")
    except Exception as e:
        print(f"ERROR: Could not get DATABASE_URL: {e}")
        exit(1)

# Fix for Render's postgres:// vs postgresql://
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print(f"Connecting to database...")

engine = create_engine(DATABASE_URL)

try:
    # Check if column exists
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('saved_budgets')]
    
    if 'currency' in columns:
        print("✓ Column 'currency' already exists. No action needed.")
    else:
        print("Adding 'currency' column to saved_budgets table...")
        
        with engine.connect() as conn:
            conn.execute(text(
                "ALTER TABLE saved_budgets ADD COLUMN currency VARCHAR(10) NULL"
            ))
            conn.commit()
        
        print("✓ Successfully added 'currency' column!")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
finally:
    engine.dispose()

print("\nDone! The app should now work correctly.")
