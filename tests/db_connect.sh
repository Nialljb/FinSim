# For local database
python view_database.py

# For Render database (get connection string from Render dashboard)
# SECURITY: Never commit actual credentials! Use environment variables or .env file
# export DATABASE_URL="postgresql://user:password@host/database"
# Get your DATABASE_URL from: Render Dashboard > FinSim Database > Connection String
python view_database.py

# Specific views
python view_database.py users          # Just users
python view_database.py simulations    # Recent simulations
python view_database.py analytics      # Analytics dashboard
python view_database.py export         # Export to CSV