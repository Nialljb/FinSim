"""
Quick Fix for Render: Database migrations
Run this directly on Render via shell access or one-time job.

This script:
1. Adds missing currency column to saved_budgets
2. Creates feedback table for user feedback/issues
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
    inspector = inspect(engine)
    
    # MIGRATION 1: Add currency column to saved_budgets
    print("\n[Migration 1] Checking saved_budgets.currency column...")
    columns = [col['name'] for col in inspector.get_columns('saved_budgets')]
    
    if 'currency' in columns:
        print("✓ Column 'currency' already exists.")
    else:
        print("Adding 'currency' column to saved_budgets table...")
        
        with engine.connect() as conn:
            conn.execute(text(
                "ALTER TABLE saved_budgets ADD COLUMN currency VARCHAR(10) NULL"
            ))
            conn.commit()
        
        print("✓ Successfully added 'currency' column!")
    
    # MIGRATION 2: Create feedback table
    print("\n[Migration 2] Checking feedback table...")
    
    if 'feedback' in inspector.get_table_names():
        print("✓ Feedback table already exists.")
    else:
        print("Creating feedback table...")
        
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE feedback (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    feedback_type VARCHAR(50) NOT NULL,
                    subject VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    page_context VARCHAR(100),
                    user_email VARCHAR(255),
                    status VARCHAR(50) DEFAULT 'new',
                    admin_notes TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE,
                    resolved_at TIMESTAMP WITH TIME ZONE
                )
            """))
            conn.commit()
        
        print("✓ Successfully created feedback table!")
    
    print("\n✅ All migrations completed successfully!")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
finally:
    engine.dispose()

print("\nDone! The app should now work correctly.")
