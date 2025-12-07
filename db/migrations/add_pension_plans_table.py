"""
Database migration: Add pension_plans table
Run this to add pension planning functionality to existing database
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect

load_dotenv()

# Get database URL
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///finsim.db')

# Fix for Render PostgreSQL URL format
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

engine = create_engine(DATABASE_URL, echo=True)

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def add_pension_plans_table():
    """Add pension_plans table to database"""
    
    print(f"\n{'='*60}")
    print("Adding pension_plans table...")
    print(f"{'='*60}\n")
    
    # Check if table already exists
    if check_table_exists('pension_plans'):
        print("✓ pension_plans table already exists")
        return True
    
    # Create pension_plans table
    create_table_sql = """
    CREATE TABLE pension_plans (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id),
        
        -- Plan metadata
        name VARCHAR(255) DEFAULT 'My Pension Plan',
        country VARCHAR(50) DEFAULT 'UK',
        
        -- Personal details
        date_of_birth VARCHAR(10),
        employment_start_age INTEGER DEFAULT 18,
        target_retirement_age INTEGER DEFAULT 67,
        
        -- State Pension (UK)
        state_pension_enabled BOOLEAN DEFAULT TRUE,
        state_pension_ni_years INTEGER DEFAULT 0,
        state_pension_projected_years INTEGER DEFAULT 0,
        state_pension_annual_amount FLOAT DEFAULT 0,
        
        -- USS Pension
        uss_enabled BOOLEAN DEFAULT FALSE,
        uss_current_salary FLOAT DEFAULT 0,
        uss_years_in_scheme INTEGER DEFAULT 0,
        uss_projected_annual_pension FLOAT DEFAULT 0,
        uss_projected_lump_sum FLOAT DEFAULT 0,
        
        -- SIPP
        sipp_enabled BOOLEAN DEFAULT FALSE,
        sipp_current_value FLOAT DEFAULT 0,
        sipp_annual_contribution FLOAT DEFAULT 0,
        sipp_employer_contribution FLOAT DEFAULT 0,
        sipp_projected_value FLOAT DEFAULT 0,
        sipp_growth_rate FLOAT DEFAULT 0.05,
        
        -- Other pensions
        other_pensions JSON,
        
        -- Retirement planning
        desired_retirement_income FLOAT DEFAULT 0,
        expected_total_pension_income FLOAT DEFAULT 0,
        
        -- Settings
        salary_growth_rate FLOAT DEFAULT 0.02,
        inflation_rate FLOAT DEFAULT 0.02,
        drawdown_rate FLOAT DEFAULT 0.04,
        
        -- Status
        is_active BOOLEAN DEFAULT TRUE,
        is_default BOOLEAN DEFAULT FALSE,
        
        -- Timestamps
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE,
        last_calculated TIMESTAMP WITH TIME ZONE
    );
    """
    
    # For SQLite (adjust syntax)
    if DATABASE_URL.startswith('sqlite'):
        create_table_sql = """
        CREATE TABLE pension_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            
            -- Plan metadata
            name VARCHAR(255) DEFAULT 'My Pension Plan',
            country VARCHAR(50) DEFAULT 'UK',
            
            -- Personal details
            date_of_birth VARCHAR(10),
            employment_start_age INTEGER DEFAULT 18,
            target_retirement_age INTEGER DEFAULT 67,
            
            -- State Pension (UK)
            state_pension_enabled BOOLEAN DEFAULT TRUE,
            state_pension_ni_years INTEGER DEFAULT 0,
            state_pension_projected_years INTEGER DEFAULT 0,
            state_pension_annual_amount REAL DEFAULT 0,
            
            -- USS Pension
            uss_enabled BOOLEAN DEFAULT FALSE,
            uss_current_salary REAL DEFAULT 0,
            uss_years_in_scheme INTEGER DEFAULT 0,
            uss_projected_annual_pension REAL DEFAULT 0,
            uss_projected_lump_sum REAL DEFAULT 0,
            
            -- SIPP
            sipp_enabled BOOLEAN DEFAULT FALSE,
            sipp_current_value REAL DEFAULT 0,
            sipp_annual_contribution REAL DEFAULT 0,
            sipp_employer_contribution REAL DEFAULT 0,
            sipp_projected_value REAL DEFAULT 0,
            sipp_growth_rate REAL DEFAULT 0.05,
            
            -- Other pensions
            other_pensions TEXT,
            
            -- Retirement planning
            desired_retirement_income REAL DEFAULT 0,
            expected_total_pension_income REAL DEFAULT 0,
            
            -- Settings
            salary_growth_rate REAL DEFAULT 0.02,
            inflation_rate REAL DEFAULT 0.02,
            drawdown_rate REAL DEFAULT 0.04,
            
            -- Status
            is_active BOOLEAN DEFAULT TRUE,
            is_default BOOLEAN DEFAULT FALSE,
            
            -- Timestamps
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            last_calculated TIMESTAMP
        );
        """
    
    try:
        with engine.begin() as conn:
            conn.execute(text(create_table_sql))
        print("✓ pension_plans table created successfully")
        return True
    except Exception as e:
        print(f"✗ Error creating pension_plans table: {e}")
        return False


def main():
    """Run all migrations"""
    print("\n" + "="*60)
    print("PENSION PLANS TABLE MIGRATION")
    print("="*60 + "\n")
    
    success = add_pension_plans_table()
    
    print("\n" + "="*60)
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed - please check errors above")
    print("="*60 + "\n")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
