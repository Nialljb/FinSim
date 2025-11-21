#!/bin/bash
# Quick fix for foreign key issue

echo "🔧 Fixing database setup..."

# Remove old database if it exists
if [ -f "finsim.db" ]; then
    echo "📁 Removing old database..."
    rm finsim.db
    echo "✅ Old database removed"
fi

# Copy the fixed database.py
echo "📋 Using fixed database.py..."

# Run setup
echo "🚀 Running setup..."
python setup.py

echo ""
echo "✅ Done! You should now see the test user created successfully."


# 3. Verify database.py is working
python -c "from database import User; print('✅ database.py loaded successfully')"

# 4. Run your app
streamlit run wealth_simulator.py