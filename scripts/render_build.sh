#!/bin/bash
set -e

echo "Installing Python packages..."
pip install -r requirements.txt

echo "Running database migrations..."
python migrate_postgres_budget_columns.py
python migrate_email_verification.py

echo "Modifying Streamlit to inject custom meta tags..."

# Find Streamlit's index.html template
STREAMLIT_PATH=$(python -c "import streamlit; import os; print(os.path.dirname(streamlit.__file__))")
INDEX_HTML="$STREAMLIT_PATH/static/index.html"

if [ -f "$INDEX_HTML" ]; then
    echo "Found Streamlit index.html at: $INDEX_HTML"
    
    # Inject meta tags into the head section
    sed -i '/<head>/a \
    <meta property="og:title" content="FinSTK - Financial Simulation Toolkit" />\
    <meta property="og:description" content="Plan your financial future with Monte Carlo simulations" />\
    <meta property="og:image" content="https://raw.githubusercontent.com/Nialljb/FinSim/design/assets/preview.png" />\
    <meta property="og:url" content="https://www.finstk.com" />\
    <meta property="og:type" content="website" />\
    <meta property="og:image:width" content="1200" />\
    <meta property="og:image:height" content="630" />\
    <meta name="twitter:card" content="summary_large_image" />\
    <meta name="twitter:image" content="https://raw.githubusercontent.com/Nialljb/FinSim/design/assets/preview.png" />' "$INDEX_HTML"
    
    echo "✅ Meta tags injected into Streamlit index.html"
else
    echo "⚠️  Could not find Streamlit index.html"
fi

echo "Build complete!"
