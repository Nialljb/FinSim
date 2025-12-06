# For local database
python view_database.py

# For Render database (get connection string from Render dashboard)
export DATABASE_URL="postgresql://user:pass@host:5432/finsim"
python view_database.py

# Specific views
python view_database.py users          # Just users
python view_database.py simulations    # Recent simulations
python view_database.py analytics      # Analytics dashboard
python view_database.py export         # Export to CSV