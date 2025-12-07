"""
Migration: Make Feedback.user_id nullable for anonymous submissions

This migration changes the feedback.user_id column from NOT NULL to nullable,
allowing anonymous/guest users to submit feedback without requiring a user account.

SQLite Limitation: SQLite doesn't support ALTER COLUMN directly, so we need to:
1. Create a new table with the correct schema
2. Copy data from old table
3. Drop old table
4. Rename new table

Can be run safely multiple times (checks current schema first).
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import create_engine, inspect, text
from data_layer.database import DATABASE_URL

def make_feedback_user_id_nullable():
    """Make user_id nullable in feedback table"""
    
    print("=" * 60)
    print("MIGRATION: Make Feedback.user_id Nullable")
    print("=" * 60)
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL, echo=False)
        inspector = inspect(engine)
        
        # Check if feedback table exists
        if 'feedback' not in inspector.get_table_names():
            print("⚠️  Feedback table doesn't exist. Run add_feedback_table.py first.")
            return False
        
        # Check current schema
        columns = {col['name']: col for col in inspector.get_columns('feedback')}
        
        if 'user_id' not in columns:
            print("⚠️  user_id column doesn't exist in feedback table")
            return False
        
        # Check if already nullable
        if columns['user_id']['nullable']:
            print("✓ user_id column is already nullable")
            return True
        
        print("Making user_id nullable...")
        print("Note: SQLite doesn't support ALTER COLUMN, recreating table...")
        
        with engine.begin() as conn:
            # Step 1: Create new table with correct schema
            conn.execute(text("""
                CREATE TABLE feedback_new (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    feedback_type VARCHAR(50) NOT NULL,
                    subject VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    page_context VARCHAR(100),
                    user_email VARCHAR(255),
                    status VARCHAR(50) DEFAULT 'new',
                    admin_notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP,
                    resolved_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """))
            
            # Step 2: Copy data from old table
            conn.execute(text("""
                INSERT INTO feedback_new 
                SELECT * FROM feedback
            """))
            
            # Step 3: Drop old table
            conn.execute(text("DROP TABLE feedback"))
            
            # Step 4: Rename new table
            conn.execute(text("ALTER TABLE feedback_new RENAME TO feedback"))
            
            # Step 5: Recreate indexes
            conn.execute(text("""
                CREATE INDEX ix_feedback_id ON feedback(id)
            """))
            conn.execute(text("""
                CREATE INDEX ix_feedback_user_id ON feedback(user_id)
            """))
        
        print("✅ Successfully made user_id nullable!")
        print("\nChanges:")
        print("- user_id: Now allows NULL for anonymous submissions")
        print("- Foreign key constraint preserved")
        print("- All existing data migrated")
        print("- Indexes recreated")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = make_feedback_user_id_nullable()
    sys.exit(0 if success else 1)
