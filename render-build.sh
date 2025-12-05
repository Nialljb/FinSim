#!/bin/bash
set -e

echo "================================================"
echo "Installing Python dependencies..."
echo "================================================"

# Note: Kaleido 1.2.0+ bundles its own Chrome binaries
# No system dependencies required (pure Python package)
pip install -r requirements.txt

echo "✅ Python packages installed successfully"
echo "================================================"
echo "Build complete!"
echo "================================================"
