"""
Delete user accounts from the database
Use with caution - this permanently removes users and their data
"""

import sys
import os

# Add project root to path - works both locally and on Render
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from data_layer.database import SessionLocal, User, Simulation, UsageStats, SavedBudget, PensionPlan, EmailVerification, Feedback
from sqlalchemy import func

def list_users_with_stats():
    """List all users with their data counts"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        
        if not users:
            print("No users found in database.")
            return []
        
        print(f"\nTotal Users: {len(users)}")
        print("="*100)
        print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Verified':<10} {'Sims':<6} {'Budgets':<8}")
        print("="*100)
        
        user_data = []
        for user in users:
            verified = "✅ Yes" if user.email_verified else "❌ No"
            
            # Count user's data
            sim_count = db.query(func.count(Simulation.id)).filter(Simulation.user_id == user.id).scalar() or 0
            budget_count = db.query(func.count(SavedBudget.id)).filter(SavedBudget.user_id == user.id).scalar() or 0
            
            print(f"{user.id:<5} {user.username:<20} {user.email:<30} {verified:<10} {sim_count:<6} {budget_count:<8}")
            
            user_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'verified': user.email_verified,
                'simulations': sim_count,
                'budgets': budget_count
            })
        
        print("="*100)
        return user_data
        
    finally:
        db.close()


def delete_user(user_id):
    """Delete a user and all their associated data"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            print(f"❌ User with ID {user_id} not found")
            return False
        
        print(f"\n⚠️  WARNING: You are about to delete user:")
        print(f"  ID: {user.id}")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        
        # Count associated data
        sim_count = db.query(func.count(Simulation.id)).filter(Simulation.user_id == user_id).scalar() or 0
        budget_count = db.query(func.count(SavedBudget.id)).filter(SavedBudget.user_id == user_id).scalar() or 0
        pension_count = db.query(func.count(PensionPlan.id)).filter(PensionPlan.user_id == user_id).scalar() or 0
        feedback_count = db.query(func.count(Feedback.id)).filter(Feedback.user_id == user_id).scalar() or 0
        
        print(f"\nThis will also delete:")
        print(f"  - {sim_count} simulation(s)")
        print(f"  - {budget_count} budget(s)")
        print(f"  - {pension_count} pension plan(s)")
        print(f"  - {feedback_count} feedback submission(s)")
        print(f"  - All usage statistics")
        print(f"  - All verification tokens")
        
        response = input("\n⚠️  Type 'DELETE' to confirm (or anything else to cancel): ").strip()
        
        if response != 'DELETE':
            print("❌ Cancelled. User not deleted.")
        # Delete associated data (must delete in order due to foreign key constraints)
        db.query(Feedback).filter(Feedback.user_id == user_id).delete()
        db.query(EmailVerification).filter(EmailVerification.user_id == user_id).delete()
        db.query(UsageStats).filter(UsageStats.user_id == user_id).delete()
        
        # Delete user (cascade should delete simulations, budgets, etc.)
        db.delete(user)
        db.commit()
        
        print(f"\n✅ User '{user.username}' and all associated data deleted successfully!")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error deleting user: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def delete_multiple_users(user_ids):
    """Delete multiple users at once"""
    print(f"\n⚠️  WARNING: You are about to delete {len(user_ids)} users")
    
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.id.in_(user_ids)).all()
        
        if not users:
            print("❌ No users found with those IDs")
            return False
        
        print("\nUsers to delete:")
        for user in users:
            print(f"  - {user.username} ({user.email})")
        
        response = input(f"\n⚠️  Type 'DELETE ALL' to confirm deletion of {len(users)} users: ").strip()
        
        if response != 'DELETE ALL':
            print("❌ Cancelled. No users deleted.")
            return False
        deleted_count = 0
        for user in users:
            # Delete associated data in correct order (foreign key constraints)
            db.query(Feedback).filter(Feedback.user_id == user.id).delete()
            db.query(EmailVerification).filter(EmailVerification.user_id == user.id).delete()
            db.query(UsageStats).filter(UsageStats.user_id == user.id).delete()
            db.delete(user)
            deleted_count += 1
            deleted_count += 1
        
        db.commit()
        print(f"\n✅ Successfully deleted {deleted_count} users and their data!")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("="*60)
    print("User Account Deletion Tool")
    print("="*60)
    print("\n⚠️  WARNING: Deletions are permanent and cannot be undone!")
    
    print("\nOptions:")
    print("1. List all users")
    print("2. Delete specific user by ID")
    print("3. Delete multiple users by IDs")
    print("4. Exit")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        list_users_with_stats()
        
    elif choice == "2":
        list_users_with_stats()
        user_id = input("\nEnter user ID to delete: ").strip()
        if user_id.isdigit():
            delete_user(int(user_id))
        else:
            print("❌ Invalid user ID")
            
    elif choice == "3":
        list_users_with_stats()
        user_ids_input = input("\nEnter user IDs to delete (comma-separated, e.g., 1,3,5): ").strip()
        try:
            user_ids = [int(x.strip()) for x in user_ids_input.split(',')]
            delete_multiple_users(user_ids)
        except ValueError:
            print("❌ Invalid input. Please use comma-separated numbers")
            
    elif choice == "4":
        print("Goodbye!")
    else:
        print("❌ Invalid option")
