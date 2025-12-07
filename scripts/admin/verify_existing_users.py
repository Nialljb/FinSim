"""
Verify existing user accounts that were created before email verification was implemented.
Run this once to allow existing users to log in.
"""

import sys
import os

# Add project root to path - works both locally and on Render
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from data_layer.database import SessionLocal, User
from datetime import datetime

def verify_all_existing_users():
    """Mark all existing users as email verified"""
    db = SessionLocal()
    try:
        # Get all users who are not verified
        unverified_users = db.query(User).filter(
            User.email_verified == False
        ).all()
        
        if not unverified_users:
            print("✅ No unverified users found. All users are already verified!")
            return
        
        print(f"Found {len(unverified_users)} unverified users:")
        print("="*60)
        
        for user in unverified_users:
            print(f"  ID: {user.id}")
            print(f"  Username: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  Created: {user.created_at}")
            print("-"*60)
        
        # Ask for confirmation
        response = input(f"\nVerify all {len(unverified_users)} users? (yes/no): ").strip().lower()
        
        if response != 'yes':
            print("❌ Cancelled. No changes made.")
            return
        
        # Verify all users
        verified_count = 0
        for user in unverified_users:
            user.email_verified = True
            verified_count += 1
        
        db.commit()
        
        print("\n" + "="*60)
        print(f"✅ Successfully verified {verified_count} users!")
        print("="*60)
        print("\nThese users can now log in.")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def verify_specific_user(email_or_username):
    """Verify a specific user by email or username"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(
            (User.email == email_or_username) | (User.username == email_or_username)
        ).first()
        
        if not user:
            print(f"❌ User not found: {email_or_username}")
            return
        
        if user.email_verified:
            print(f"✅ User '{user.username}' is already verified")
            return
        
        print(f"\nUser Details:")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Created: {user.created_at}")
        
        response = input(f"\nVerify this user? (yes/no): ").strip().lower()
        
        if response != 'yes':
            print("❌ Cancelled.")
            return
        
        user.email_verified = True
        db.commit()
        
        print(f"✅ Successfully verified user '{user.username}'!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()


def list_all_users():
    """List all users with their verification status"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        
        if not users:
            print("No users found in database.")
            return
        
        print(f"\nTotal Users: {len(users)}")
        print("="*80)
        print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Verified':<10}")
        print("="*80)
        
        for user in users:
            verified_status = "✅ Yes" if user.email_verified else "❌ No"
            print(f"{user.id:<5} {user.username:<20} {user.email:<30} {verified_status:<10}")
        
        print("="*80)
        
        verified_count = sum(1 for u in users if u.email_verified)
        unverified_count = len(users) - verified_count
        
        print(f"\nVerified: {verified_count} | Unverified: {unverified_count}")
        
    finally:
        db.close()


if __name__ == "__main__":
    print("="*60)
    print("Email Verification Management")
    print("="*60)
    print("\nOptions:")
    print("1. List all users")
    print("2. Verify all existing users")
    print("3. Verify specific user")
    print("4. Exit")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        list_all_users()
    elif choice == "2":
        verify_all_existing_users()
    elif choice == "3":
        user_identifier = input("\nEnter username or email: ").strip()
        if user_identifier:
            verify_specific_user(user_identifier)
        else:
            print("❌ No username/email provided")
    elif choice == "4":
        print("Goodbye!")
    else:
        print("❌ Invalid option")
