#!/usr/bin/env python3
"""
Database Inspector
Inspect database structure and contents
"""

import os
from sqlalchemy import create_engine, inspect, MetaData, Table
from sqlalchemy.orm import sessionmaker

# Get database URL from environment or use default
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///finsim.db')

# Create engine
engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

print("\n" + "="*100)
print("🔍 DATABASE INSPECTOR")
print("="*100)

# Show database info
if 'DATABASE_URL' in os.environ:
    db_url = os.environ['DATABASE_URL']
    if '@' in db_url:
        masked = db_url.split('@')[1]
        print(f"📍 Connected to: {masked}")
    else:
        print(f"📍 Connected to: Production database")
else:
    print("📍 Connected to: Local database (finsim.db)")

# List all tables
print("\n📋 TABLES IN DATABASE:")
print("="*100)
table_names = inspector.get_table_names()
if table_names:
    for i, table_name in enumerate(table_names, 1):
        print(f"{i}. {table_name}")
else:
    print("No tables found!")
print("="*100)

# For each table, show schema and row count
for table_name in table_names:
    print(f"\n📊 TABLE: {table_name}")
    print("="*100)
    
    # Get columns
    columns = inspector.get_columns(table_name)
    print("\n  COLUMNS:")
    for col in columns:
        nullable = "NULL" if col['nullable'] else "NOT NULL"
        col_type = str(col['type'])
        default = f" DEFAULT {col.get('default', 'None')}" if col.get('default') else ""
        print(f"    - {col['name']:<30} {col_type:<20} {nullable}{default}")
    
    # Get primary keys
    pk = inspector.get_pk_constraint(table_name)
    if pk and pk['constrained_columns']:
        print(f"\n  PRIMARY KEY: {', '.join(pk['constrained_columns'])}")
    
    # Get foreign keys
    fks = inspector.get_foreign_keys(table_name)
    if fks:
        print("\n  FOREIGN KEYS:")
        for fk in fks:
            print(f"    - {', '.join(fk['constrained_columns'])} -> {fk['referred_table']}.{', '.join(fk['referred_columns'])}")
    
    # Get indexes
    indexes = inspector.get_indexes(table_name)
    if indexes:
        print("\n  INDEXES:")
        for idx in indexes:
            unique = "UNIQUE" if idx['unique'] else ""
            print(f"    - {idx['name']}: {', '.join(idx['column_names'])} {unique}")
    
    # Count rows
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=engine)
        count = session.query(table).count()
        session.close()
        print(f"\n  ROW COUNT: {count}")
        
        # Show sample data if there are rows
        if count > 0:
            session = Session()
            sample = session.query(table).limit(3).all()
            if sample:
                print(f"\n  SAMPLE DATA (first {min(3, count)} rows):")
                for i, row in enumerate(sample, 1):
                    print(f"\n    Row {i}:")
                    # Convert row to dict
                    row_dict = dict(row._mapping) if hasattr(row, '_mapping') else dict(zip(table.columns.keys(), row))
                    for key, value in row_dict.items():
                        # Truncate long values
                        val_str = str(value)
                        if len(val_str) > 100:
                            val_str = val_str[:100] + "..."
                        print(f"      {key}: {val_str}")
            session.close()
    except Exception as e:
        print(f"\n  ⚠️  Could not count rows: {str(e)}")
    
    print("="*100)

print("\n✅ Database inspection complete!")
print("\n💡 Tip: Use 'python view_database.py users' to view user data\n")