"""
Comprehensive fix for Render deployment - Add ALL missing columns

This script adds all missing columns that have been added to the codebase but not yet
migrated to the production database on Render.

Safe to run multiple times - checks for existing columns before adding.

Run this in Render Shell:
    python fix_render_all_migrations.py
"""

import os
from sqlalchemy import create_engine, text, inspect

def run_all_migrations():
    """Add all missing columns to production database"""
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    # Fix for Render's postgres:// URL (SQLAlchemy needs postgresql://)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    print("=" * 60)
    print("RENDER FIX: Adding all missing columns")
    print("=" * 60)
    
    try:
        # Create engine
        engine = create_engine(database_url, echo=False)
        inspector = inspect(engine)
        
        # ==================================================
        # 1. Add spouse fields to users table
        # ==================================================
        print("\n📋 Checking users table for spouse fields...")
        
        if 'users' in inspector.get_table_names():
            existing_user_columns = {col['name'] for col in inspector.get_columns('users')}
            
            user_spouse_fields = [
                ("has_spouse", "BOOLEAN DEFAULT FALSE"),
                ("spouse_age", "INTEGER"),
                ("spouse_retirement_age", "INTEGER"),
                ("spouse_annual_income", "FLOAT"),
            ]
            
            with engine.begin() as conn:
                for col_name, col_type in user_spouse_fields:
                    if col_name in existing_user_columns:
                        print(f"✓ users.{col_name} already exists")
                    else:
                        try:
                            conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                            print(f"✅ Added users.{col_name}")
                        except Exception as e:
                            print(f"⚠️ Error adding users.{col_name}: {e}")
        
        # ==================================================
        # 2. Add monthly budget tracking fields to saved_budgets table
        # ==================================================
        print("\n📋 Checking saved_budgets table for monthly tracking fields...")
        
        if 'saved_budgets' in inspector.get_table_names():
            existing_budget_columns = {col['name'] for col in inspector.get_columns('saved_budgets')}
            
            budget_tracking_fields = [
                ("current_month", "VARCHAR(7)"),  # Format: "2025-12"
                ("budget_expected", "JSON"),
                ("budget_actuals", "JSON"),
            ]
            
            with engine.begin() as conn:
                for col_name, col_type in budget_tracking_fields:
                    if col_name in existing_budget_columns:
                        print(f"✓ saved_budgets.{col_name} already exists")
                    else:
                        try:
                            conn.execute(text(f"ALTER TABLE saved_budgets ADD COLUMN {col_name} {col_type}"))
                            print(f"✅ Added saved_budgets.{col_name}")
                        except Exception as e:
                            print(f"⚠️ Error adding saved_budgets.{col_name}: {e}")
        
        # ==================================================
        # 3. Make feedback.user_id nullable
        # ==================================================
        print("\n📋 Checking feedback table for nullable user_id...")
        
        if 'feedback' in inspector.get_table_names():
            feedback_columns = {col['name']: col for col in inspector.get_columns('feedback')}
            
            if 'user_id' in feedback_columns:
                is_nullable = feedback_columns['user_id']['nullable']
                if is_nullable:
                    print("✓ feedback.user_id is already nullable")
                else:
                    print("ℹ️ feedback.user_id needs to be made nullable (requires table recreation for PostgreSQL)")
                    # For PostgreSQL, we can drop the NOT NULL constraint
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("ALTER TABLE feedback ALTER COLUMN user_id DROP NOT NULL"))
                            print("✅ Made feedback.user_id nullable")
                    except Exception as e:
                        print(f"⚠️ Error making feedback.user_id nullable: {e}")
        
        # ==================================================
        # 4. Add spouse fields to pension_plans table
        # ==================================================
        print("\n📋 Checking pension_plans table for spouse fields...")
        
        if 'pension_plans' in inspector.get_table_names():
            existing_pension_columns = {col['name'] for col in inspector.get_columns('pension_plans')}
            
            pension_spouse_fields = [
                ("spouse_enabled", "BOOLEAN DEFAULT FALSE"),
                ("spouse_age", "INTEGER"),
                ("spouse_retirement_age", "INTEGER"),
                ("spouse_annual_income", "FLOAT DEFAULT 0"),
                
                # Spouse State Pension
                ("spouse_state_pension_enabled", "BOOLEAN DEFAULT FALSE"),
                ("spouse_state_pension_ni_years", "INTEGER DEFAULT 0"),
                ("spouse_state_pension_projected_years", "INTEGER DEFAULT 0"),
                ("spouse_state_pension_annual_amount", "FLOAT DEFAULT 0"),
                
                # Spouse USS
                ("spouse_uss_enabled", "BOOLEAN DEFAULT FALSE"),
                ("spouse_uss_current_salary", "FLOAT DEFAULT 0"),
                ("spouse_uss_years_in_scheme", "INTEGER DEFAULT 0"),
                ("spouse_uss_projected_annual_pension", "FLOAT DEFAULT 0"),
                ("spouse_uss_projected_lump_sum", "FLOAT DEFAULT 0"),
                ("spouse_uss_avc_enabled", "BOOLEAN DEFAULT FALSE"),
                ("spouse_uss_avc_annual_amount", "FLOAT DEFAULT 0"),
                ("spouse_uss_avc_current_value", "FLOAT DEFAULT 0"),
                ("spouse_uss_avc_projected_value", "FLOAT DEFAULT 0"),
                
                # Spouse SIPP
                ("spouse_sipp_enabled", "BOOLEAN DEFAULT FALSE"),
                ("spouse_sipp_current_value", "FLOAT DEFAULT 0"),
                ("spouse_sipp_annual_contribution", "FLOAT DEFAULT 0"),
                ("spouse_sipp_employer_contribution", "FLOAT DEFAULT 0"),
                ("spouse_sipp_projected_value", "FLOAT DEFAULT 0"),
                ("spouse_sipp_growth_rate", "FLOAT DEFAULT 0.05"),
            ]
            
            with engine.begin() as conn:
                for col_name, col_type in pension_spouse_fields:
                    if col_name in existing_pension_columns:
                        print(f"✓ pension_plans.{col_name} already exists")
                    else:
                        try:
                            conn.execute(text(f"ALTER TABLE pension_plans ADD COLUMN {col_name} {col_type}"))
                            print(f"✅ Added pension_plans.{col_name}")
                        except Exception as e:
                            print(f"⚠️ Error adding pension_plans.{col_name}: {e}")
        else:
            print("ℹ️ pension_plans table doesn't exist (will be created when first used)")
        
        print("\n" + "=" * 60)
        print("✅ All migrations completed!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = run_all_migrations()
    sys.exit(0 if success else 1)
