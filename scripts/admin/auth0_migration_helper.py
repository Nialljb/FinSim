"""
User Migration Helper for Auth0 Integration

This script helps migrate existing users to use Auth0 authentication
while maintaining backward compatibility with traditional auth.
"""

import sys
import os

# Add parent directories to path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, parent_dir)

from data_layer.database import SessionLocal, User
from sqlalchemy import text


def check_migration_status():
    """Check how many users have auth0_id vs traditional auth"""
    
    db = SessionLocal()
    try:
        # Count users with auth0_id
        auth0_users = db.query(User).filter(User.auth0_id.isnot(None)).count()
        
        # Count users without auth0_id (traditional auth)
        traditional_users = db.query(User).filter(User.auth0_id.is_(None)).count()
        
        # Total users
        total_users = db.query(User).count()
        
        print("=" * 60)
        print("User Migration Status")
        print("=" * 60)
        print(f"Total Users:          {total_users}")
        print(f"Auth0 Users:          {auth0_users} ({auth0_users/total_users*100:.1f}%)" if total_users > 0 else "Auth0 Users:          0 (0%)")
        print(f"Traditional Users:    {traditional_users} ({traditional_users/total_users*100:.1f}%)" if total_users > 0 else "Traditional Users:    0 (0%)")
        print("=" * 60)
        print()
        
        if traditional_users > 0:
            print("📌 Migration Options:")
            print("   1. Keep dual authentication (recommended)")
            print("      - Existing users continue with username/password")
            print("      - New users can choose Auth0 or traditional")
            print()
            print("   2. Gradual migration")
            print("      - Prompt users to link Auth0 account on next login")
            print("      - Send migration emails to active users")
            print()
            print("   3. Contact migration")
            print("      - Email users about Auth0 benefits")
            print("      - Provide self-service linking tool")
            print()
        else:
            print("✓ All users are using Auth0 authentication")
        
        return {
            'total': total_users,
            'auth0': auth0_users,
            'traditional': traditional_users
        }
        
    finally:
        db.close()


def list_traditional_users(limit=10):
    """List traditional auth users who could be migrated"""
    
    db = SessionLocal()
    try:
        users = db.query(User).filter(
            User.auth0_id.is_(None),
            User.is_active == True
        ).order_by(User.last_login.desc()).limit(limit).all()
        
        if users:
            print(f"\nRecent Traditional Auth Users (last {limit}):")
            print("-" * 80)
            print(f"{'ID':<6} {'Username':<20} {'Email':<30} {'Last Login':<20}")
            print("-" * 80)
            
            for user in users:
                last_login = user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "Never"
                print(f"{user.id:<6} {user.username:<20} {user.email:<30} {last_login:<20}")
            
            print("-" * 80)
        else:
            print("\n✓ No traditional auth users found")
        
    finally:
        db.close()


def create_migration_email_template():
    """Generate email template for user migration notification"""
    
    template = """
Subject: Upgrade to Secure Single Sign-On with Auth0

Dear {username},

We're excited to announce a new, more secure way to access FinSTK!

🔐 What's New?
- Sign in with Auth0 (Google, Microsoft, Apple, and more)
- Enhanced security with multi-factor authentication
- Faster login experience
- One account for multiple devices

📝 How to Upgrade:
1. Visit https://finstk.com
2. Click "Link Auth0 Account" in your profile
3. Choose your preferred sign-in method
4. You're all set!

⚠️ Don't worry - your existing username/password will continue to work. 
We're simply offering you a more convenient and secure option.

Questions? Reply to this email or contact us at support@finstk.com

Best regards,
The FinSTK Team

---
This is a one-time notification about our new authentication system.
"""
    
    print("\n" + "=" * 60)
    print("Migration Email Template")
    print("=" * 60)
    print(template)
    print("=" * 60)
    
    return template


def generate_migration_plan():
    """Generate a step-by-step migration plan"""
    
    plan = """
    
╔══════════════════════════════════════════════════════════════╗
║        Auth0 Migration Plan for FinSTK                       ║
╚══════════════════════════════════════════════════════════════╝

Phase 1: Preparation (Week 1)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Database schema updated (auth0_id column)
✓ Auth0 application configured
✓ Testing environment ready
□ Migration documentation prepared
□ Support team briefed

Phase 2: Soft Launch (Week 2-3)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ Enable Auth0 for new registrations only
□ Add "Link Auth0 Account" in user settings
□ Monitor for issues
□ Collect user feedback

Phase 3: User Communication (Week 4)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ Send migration announcement email
□ Add in-app notification banner
□ Update documentation
□ Publish blog post about benefits

Phase 4: Active Migration (Month 2)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ Prompt users to link Auth0 on login
□ Send reminder emails to active users
□ Offer incentives (e.g., extended trial)
□ Track migration progress weekly

Phase 5: Long-term Support (Ongoing)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ Maintain dual authentication indefinitely
□ Gradually deprecate password resets
□ Monitor security metrics
□ Review quarterly

Key Metrics to Track:
━━━━━━━━━━━━━━━━━━━━
• Auth0 adoption rate
• Login success rate
• Support ticket volume
• User satisfaction scores
• Security incident rate

Rollback Plan:
━━━━━━━━━━━━━
If issues arise:
1. Disable Auth0 in settings (ENABLE_AUTH0=False)
2. All users revert to traditional auth
3. Investigate and fix issues
4. Re-enable when ready

"""
    
    print(plan)
    return plan


if __name__ == "__main__":
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "FinSTK Auth0 Migration Helper" + " " * 19 + "║")
    print("╚" + "═" * 58 + "╝\n")
    
    # Check current status
    stats = check_migration_status()
    
    # Show recent traditional users
    if stats['traditional'] > 0:
        list_traditional_users(limit=10)
        
        # Generate resources
        print("\n")
        create_migration_email_template()
        
        print("\n")
        generate_migration_plan()
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("1. Review the migration plan above")
    print("2. Configure Auth0 in your .env file:")
    print("   - ENABLE_AUTH0=True")
    print("   - AUTH0_DOMAIN=your-tenant.auth0.com")
    print("   - AUTH0_CLIENT_ID=your_client_id")
    print("   - AUTH0_CLIENT_SECRET=your_client_secret")
    print("3. Run database migration: python scripts/migrations/add_auth0_column.py")
    print("4. Test Auth0 login in development")
    print("5. Deploy to production when ready")
    print("=" * 60 + "\n")
