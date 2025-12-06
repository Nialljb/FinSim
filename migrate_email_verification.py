"""
Migration script to add email_verifications table
Run this once to update the database schema
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

def get_database_url():
    """Get database URL from environment or use default local SQLite."""
    db_url = os.environ.get('DATABASE_URL')
    
    if db_url:
        # Render uses postgres:// but SQLAlchemy needs postgresql://
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        print(f"Using database: {db_url.split('@')[1] if '@' in db_url else 'local'}")
    else:
        db_url = 'sqlite:///finsim.db'
        print(f"Using local SQLite database: {db_url}")
    
    return db_url

def table_exists(inspector, table_name):
    """Check if a table exists."""
    return table_name in inspector.get_table_names()

def add_email_verification_table():
    """Add email_verifications table to database."""
    try:
        db_url = get_database_url()
        engine = create_engine(db_url)
        inspector = inspect(engine)
        
        print("\n🔍 Checking for email_verifications table...")
        
        if table_exists(inspector, 'email_verifications'):
            print("⏭️  Table 'email_verifications' already exists, skipping")
            return True
        
        print("➕ Creating email_verifications table...")
        
        with engine.connect() as conn:
            if 'postgresql' in db_url:
                # PostgreSQL version
                create_table_sql = text("""
                    CREATE TABLE email_verifications (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES users(id),
                        email VARCHAR(255) NOT NULL,
                        token VARCHAR(255) UNIQUE NOT NULL,
                        is_used BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                        verified_at TIMESTAMP WITH TIME ZONE
                    );
                    
                    CREATE INDEX ix_email_verifications_user_id ON email_verifications(user_id);
                    CREATE INDEX ix_email_verifications_email ON email_verifications(email);
                    CREATE INDEX ix_email_verifications_token ON email_verifications(token);
                """)
                conn.execute(create_table_sql)
                conn.commit()
            else:
                # SQLite version - execute statements separately
                conn.execute(text("""
                    CREATE TABLE email_verifications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        email VARCHAR(255) NOT NULL,
                        token VARCHAR(255) UNIQUE NOT NULL,
                        is_used BOOLEAN DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL,
                        verified_at TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                """))
                conn.commit()
                
                conn.execute(text("CREATE INDEX ix_email_verifications_user_id ON email_verifications(user_id)"))
                conn.commit()
                
                conn.execute(text("CREATE INDEX ix_email_verifications_email ON email_verifications(email)"))
                conn.commit()
                
                conn.execute(text("CREATE INDEX ix_email_verifications_token ON email_verifications(token)"))
                conn.commit()
            
            print("✅ Created email_verifications table")
        
        print("\n" + "="*60)
        print("✅ Migration complete!")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("Email Verification Table Migration")
    print("="*60)
    
    success = add_email_verification_table()
    
    if not success:
        sys.exit(1)
    
    print("\n✅ Migration completed successfully!")
    sys.exit(0)
