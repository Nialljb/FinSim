#!/bin/bash
set -e

echo "================================================"
echo "Installing Python dependencies..."
echo "================================================"

# Note: Kaleido 0.2.1.post1 bundles Chrome binaries
# No system dependencies required for this version
# (Kaleido 1.x+ would require external Chrome installation)
pip install -r requirements.txt

echo "✅ Python packages installed successfully"
echo "================================================"
echo "Build complete!"
echo "================================================"
