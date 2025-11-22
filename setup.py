#!/usr/bin/env python3
"""
Setup script for FinSim
Initializes database and creates first admin user
"""

import sys
from database import init_db, SessionLocal, User
from auth import hash_password
from datetime import datetime


def setup_database():
    """Initialize database tables"""
    print("🔧 Initializing database...")
    try:
        init_db()
        print("✅ Database initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


def create_test_user():
    """Create a test user for development"""
    print("\n👤 Creating test user...")
    
    db = SessionLocal()
    try:
        # Check if test user already exists
        existing = db.query(User).filter(User.username == "testuser").first()
        if existing:
            print("ℹ️  Test user already exists")
            return True
        
        # Create test user
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash=hash_password("password123"),
            current_age=30,
            target_retirement_age=65,
            country="Canada",
            is_active=True,
            created_at=datetime.now()
        )
        
        db.add(test_user)
        db.commit()
        
        print("✅ Test user created successfully!")
        print("   Username: testuser")
        print("   Password: password123")
        print("   Email: test@example.com")
        return True
        
    except Exception as e:
        print(f"❌ Test user creation failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def verify_setup():
    """Verify the setup is complete"""
    print("\n🔍 Verifying setup...")
    
    db = SessionLocal()
    try:
        # Count users
        user_count = db.query(User).count()
        print(f"✅ Database accessible. Users in database: {user_count}")
        return True
    except Exception as e:
        print(f"❌ Setup verification failed: {e}")
        return False
    finally:
        db.close()


def main():
    """Run full setup"""
    print("🚀 FinSim Setup")
    print("=" * 50)
    
    # Step 1: Initialize database
    if not setup_database():
        print("\n❌ Setup failed at database initialization")
        sys.exit(1)
    
    # Step 2: Create test user
    if not create_test_user():
        print("\n❌ Setup failed at test user creation")
        sys.exit(1)
    
    # Step 3: Verify
    if not verify_setup():
        print("\n❌ Setup verification failed")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("\nNext steps:")
    print("1. Run: streamlit run wealth_simulator.py")
    print("2. Login with testuser/password123")
    print("3. Create your own account for production use")
    print("\n💡 Tip: Delete the test user before going to production")


if __name__ == "__main__":
    main()