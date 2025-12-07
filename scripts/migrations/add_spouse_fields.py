"""
Migration: Add spouse/partner fields to users and pension_plans tables
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text
from data_layer.database import engine

def upgrade():
    """Add spouse fields to users and pension_plans tables"""
    
    with engine.connect() as conn:
        print("Starting spouse fields migration...")
        
        # Add spouse fields to users table
        user_columns = [
            ("has_spouse", "BOOLEAN DEFAULT 0"),
            ("spouse_age", "INTEGER"),
            ("spouse_retirement_age", "INTEGER"),
            ("spouse_annual_income", "FLOAT"),
        ]
        
        for col_name, col_type in user_columns:
            try:
                conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                conn.commit()
                print(f"✅ Added users.{col_name}")
            except Exception as e:
                if "duplicate column" in str(e).lower():
                    print(f"ℹ️ users.{col_name} already exists")
                else:
                    print(f"⚠️ users.{col_name}: {e}")
        
        # Add spouse pension fields to pension_plans table
        pension_columns = [
            ("spouse_enabled", "BOOLEAN DEFAULT 0"),
            ("spouse_age", "INTEGER"),
            ("spouse_retirement_age", "INTEGER"),
            ("spouse_annual_income", "FLOAT DEFAULT 0"),
            
            # Spouse State Pension
            ("spouse_state_pension_enabled", "BOOLEAN DEFAULT 0"),
            ("spouse_state_pension_ni_years", "INTEGER DEFAULT 0"),
            ("spouse_state_pension_projected_years", "INTEGER DEFAULT 0"),
            ("spouse_state_pension_annual_amount", "FLOAT DEFAULT 0"),
            
            # Spouse USS
            ("spouse_uss_enabled", "BOOLEAN DEFAULT 0"),
            ("spouse_uss_current_salary", "FLOAT DEFAULT 0"),
            ("spouse_uss_years_in_scheme", "INTEGER DEFAULT 0"),
            ("spouse_uss_projected_annual_pension", "FLOAT DEFAULT 0"),
            ("spouse_uss_projected_lump_sum", "FLOAT DEFAULT 0"),
            ("spouse_uss_avc_enabled", "BOOLEAN DEFAULT 0"),
            ("spouse_uss_avc_annual_amount", "FLOAT DEFAULT 0"),
            ("spouse_uss_avc_current_value", "FLOAT DEFAULT 0"),
            ("spouse_uss_avc_projected_value", "FLOAT DEFAULT 0"),
            
            # Spouse SIPP
            ("spouse_sipp_enabled", "BOOLEAN DEFAULT 0"),
            ("spouse_sipp_current_value", "FLOAT DEFAULT 0"),
            ("spouse_sipp_annual_contribution", "FLOAT DEFAULT 0"),
            ("spouse_sipp_employer_contribution", "FLOAT DEFAULT 0"),
            ("spouse_sipp_projected_value", "FLOAT DEFAULT 0"),
            ("spouse_sipp_growth_rate", "FLOAT DEFAULT 0.05"),
        ]
        
        for col_name, col_type in pension_columns:
            try:
                conn.execute(text(f"ALTER TABLE pension_plans ADD COLUMN {col_name} {col_type}"))
                conn.commit()
                print(f"✅ Added pension_plans.{col_name}")
            except Exception as e:
                if "duplicate column" in str(e).lower():
                    print(f"ℹ️ pension_plans.{col_name} already exists")
                else:
                    print(f"⚠️ pension_plans.{col_name}: {e}")
        
        print("✅ Successfully completed spouse fields migration")

if __name__ == "__main__":
    print("Running migration: add_spouse_fields")
    upgrade()
    print("Migration completed!")
