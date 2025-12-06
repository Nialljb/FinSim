"""
Migration: Add Feedback table for user feedback and issue reporting

This migration adds the 'feedback' table to store user feedback,
bug reports, feature requests, and issues.

Can be run safely multiple times (checks if table exists first).
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, inspect, text
from database import DATABASE_URL, Base, Feedback

def add_feedback_table():
    """Add feedback table to database if it doesn't exist"""
    
    print("=" * 60)
    print("MIGRATION: Add Feedback Table")
    print("=" * 60)
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL, echo=False)
        inspector = inspect(engine)
        
        # Check if feedback table already exists
        if 'feedback' in inspector.get_table_names():
            print("✓ Feedback table already exists")
            return True
        
        print("Creating feedback table...")
        
        # Create only the Feedback table
        Feedback.__table__.create(engine)
        
        print("✅ Successfully created feedback table!")
        print("\nTable structure:")
        print("- id: Primary key")
        print("- user_id: Foreign key to users table")
        print("- feedback_type: Type (bug, feature, general, issue)")
        print("- subject: Brief title/subject")
        print("- message: Detailed feedback message")
        print("- page_context: Where the feedback was submitted from")
        print("- user_email: Email for follow-up")
        print("- status: Status (new, reviewed, resolved, closed)")
        print("- admin_notes: Notes from admin review")
        print("- created_at: Timestamp of submission")
        print("- updated_at: Timestamp of last update")
        print("- resolved_at: Timestamp when resolved")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating feedback table: {str(e)}")
        return False

if __name__ == "__main__":
    success = add_feedback_table()
    sys.exit(0 if success else 1)
