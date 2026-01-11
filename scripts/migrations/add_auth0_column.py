"""
Database migration: Add auth0_id column to users table

Run this script to add Auth0 support to existing database
"""

import sys
import os

# Add parent directories to path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, parent_dir)

from sqlalchemy import text
from data_layer.database import engine, SessionLocal


def add_auth0_column():
    """Add auth0_id column to users table"""
    
    print("Adding auth0_id column to users table...")
    
    try:
        with engine.connect() as conn:
            # Check if column already exists
            if engine.name == 'postgresql':
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='users' AND column_name='auth0_id'
                """))
            else:  # SQLite
                result = conn.execute(text("PRAGMA table_info(users)"))
                columns = [row[1] for row in result]
                if 'auth0_id' in columns:
                    print("✓ Column auth0_id already exists")
                    return True
            
            # PostgreSQL check
            if engine.name == 'postgresql' and result.fetchone():
                print("✓ Column auth0_id already exists")
                return True
            
            # Add the column
            if engine.name == 'postgresql':
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN auth0_id VARCHAR(255) UNIQUE
                """))
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_users_auth0_id 
                    ON users(auth0_id)
                """))
            else:  # SQLite
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN auth0_id VARCHAR(255)
                """))
                # SQLite will need to create index separately if needed
                try:
                    conn.execute(text("""
                        CREATE UNIQUE INDEX idx_users_auth0_id 
                        ON users(auth0_id)
                    """))
                except:
                    pass  # Index might already exist
            
            conn.commit()
            print("✓ Successfully added auth0_id column")
            return True
            
    except Exception as e:
        print(f"✗ Error adding auth0_id column: {e}")
        return False


def verify_migration():
    """Verify the migration was successful"""
    
    print("\nVerifying migration...")
    
    try:
        with engine.connect() as conn:
            if engine.name == 'postgresql':
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name='users' AND column_name='auth0_id'
                """))
                row = result.fetchone()
                if row:
                    print(f"✓ Column exists: {row[0]} ({row[1]}, nullable={row[2]})")
                    return True
            else:  # SQLite
                result = conn.execute(text("PRAGMA table_info(users)"))
                for row in result:
                    if row[1] == 'auth0_id':
                        print(f"✓ Column exists: {row[1]} ({row[2]})")
                        return True
        
        print("✗ Column not found after migration")
        return False
        
    except Exception as e:
        print(f"✗ Error verifying migration: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Database Migration: Add Auth0 Support")
    print("=" * 60)
    print()
    
    # Run migration
    success = add_auth0_column()
    
    if success:
        # Verify it worked
        verify_migration()
        print()
        print("=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
    else:
        print()
        print("=" * 60)
        print("Migration failed. Please check the errors above.")
        print("=" * 60)
        sys.exit(1)
