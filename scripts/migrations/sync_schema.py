"""
Database Schema Validator and Auto-Migration
Checks if the database schema matches the SQLAlchemy models and applies missing changes.

This script:
1. Compares database schema with SQLAlchemy models
2. Identifies missing columns
3. Adds missing columns automatically
4. Provides a report of changes

Usage:
    python migrations/sync_schema.py
"""

import os
import sys
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.schema import CreateTable

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DATABASE_URL, Base, User, Simulation, SavedBudget, UsageStats


def get_model_columns(model):
    """Extract column definitions from SQLAlchemy model"""
    columns = {}
    for column in model.__table__.columns:
        columns[column.name] = {
            'type': str(column.type),
            'nullable': column.nullable,
            'primary_key': column.primary_key
        }
    return columns


def get_database_columns(inspector, table_name):
    """Get existing columns from database"""
    try:
        db_columns = inspector.get_columns(table_name)
        return {col['name']: col for col in db_columns}
    except Exception as e:
        print(f"Warning: Could not inspect table '{table_name}': {e}")
        return {}


def compare_schemas(engine):
    """Compare model schemas with database schemas"""
    inspector = inspect(engine)
    models = [User, Simulation, SavedBudget, UsageStats]
    
    differences = {}
    
    for model in models:
        table_name = model.__tablename__
        model_columns = get_model_columns(model)
        db_columns = get_database_columns(inspector, table_name)
        
        missing_columns = []
        for col_name, col_info in model_columns.items():
            if col_name not in db_columns:
                missing_columns.append({
                    'name': col_name,
                    'info': col_info,
                    'column_obj': model.__table__.columns[col_name]
                })
        
        if missing_columns:
            differences[table_name] = missing_columns
    
    return differences


def generate_add_column_sql(table_name, column):
    """Generate SQL to add a column"""
    col_type = str(column.type)
    nullable = "NULL" if column.nullable else "NOT NULL"
    
    # Handle default values
    default = ""
    if column.default is not None:
        if hasattr(column.default, 'arg'):
            if callable(column.default.arg):
                # Server-side defaults like func.now()
                if 'now' in str(column.default.arg).lower():
                    default = "DEFAULT CURRENT_TIMESTAMP"
            else:
                default = f"DEFAULT {repr(column.default.arg)}"
    
    sql = f"ALTER TABLE {table_name} ADD COLUMN {column.name} {col_type} {nullable} {default}".strip()
    return sql


def apply_migrations(engine, differences):
    """Apply missing columns to database"""
    if not differences:
        print("✓ Database schema is up to date!")
        return True
    
    print(f"\nFound {sum(len(cols) for cols in differences.values())} missing columns across {len(differences)} tables")
    print("\nApplying migrations...\n")
    
    success_count = 0
    fail_count = 0
    
    with engine.connect() as conn:
        for table_name, missing_columns in differences.items():
            print(f"Table: {table_name}")
            for col_info in missing_columns:
                col_name = col_info['name']
                column = col_info['column_obj']
                
                try:
                    sql = generate_add_column_sql(table_name, column)
                    print(f"  Adding column '{col_name}'...")
                    print(f"    SQL: {sql}")
                    
                    conn.execute(text(sql))
                    conn.commit()
                    
                    print(f"  ✓ Successfully added '{col_name}'")
                    success_count += 1
                    
                except Exception as e:
                    print(f"  ✗ Failed to add '{col_name}': {e}")
                    fail_count += 1
            print()
    
    return fail_count == 0


def create_missing_tables(engine):
    """Create any missing tables"""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    models = [User, Simulation, SavedBudget, UsageStats]
    missing_tables = []
    
    for model in models:
        if model.__tablename__ not in existing_tables:
            missing_tables.append(model)
    
    if missing_tables:
        print(f"\nCreating {len(missing_tables)} missing tables...")
        for model in missing_tables:
            print(f"  Creating table: {model.__tablename__}")
            model.__table__.create(engine)
            print(f"  ✓ Created {model.__tablename__}")
        return True
    
    return False


def main():
    """Run schema validation and migration"""
    print("=" * 70)
    print("Database Schema Sync - FinSim")
    print("=" * 70)
    print()
    
    # Get database connection
    database_url = DATABASE_URL
    print(f"Database: {database_url.split('@')[-1] if '@' in database_url else 'local'}")
    print()
    
    engine = create_engine(database_url)
    
    try:
        # Step 1: Create missing tables
        print("Step 1: Checking for missing tables...")
        tables_created = create_missing_tables(engine)
        if not tables_created:
            print("✓ All tables exist")
        print()
        
        # Step 2: Check for missing columns
        print("Step 2: Checking for missing columns...")
        differences = compare_schemas(engine)
        
        if not differences:
            print("✓ All columns exist")
            print()
            print("=" * 70)
            print("✓ Database schema is fully synchronized!")
            print("=" * 70)
            return 0
        
        # Step 3: Apply migrations
        print("\nMissing columns detected:")
        for table_name, missing_columns in differences.items():
            print(f"\n  {table_name}:")
            for col_info in missing_columns:
                print(f"    - {col_info['name']} ({col_info['info']['type']})")
        
        print("\n" + "=" * 70)
        response = input("Apply these migrations? (yes/no): ").strip().lower()
        
        if response in ['yes', 'y']:
            success = apply_migrations(engine, differences)
            
            print("=" * 70)
            if success:
                print("✓ All migrations applied successfully!")
            else:
                print("✗ Some migrations failed. Please check errors above.")
            print("=" * 70)
            
            return 0 if success else 1
        else:
            print("\nMigration cancelled by user.")
            return 1
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        engine.dispose()


if __name__ == "__main__":
    sys.exit(main())
