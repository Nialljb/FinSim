#!/bin/bash
set -e

echo "================================================"
echo "Installing system dependencies for Kaleido..."
echo "================================================"

# Update package list
apt-get update -qq

# Install Chrome/Chromium dependencies required by Kaleido
apt-get install -y -qq \
    libx11-6 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    libnss3 \
    libnspr4 \
    libglib2.0-0 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libatk1.0-0 \
    libcairo-gobject2 \
    libcairo2 \
    libfontconfig1 \
    libfreetype6 \
    libasound2 \
    libdbus-1-3 \
    libexpat1 \
    libuuid1

echo "✅ System dependencies installed successfully"
echo "================================================"
echo "Installing Python packages..."
echo "================================================"

pip install -r requirements.txt

echo "✅ Python packages installed successfully"
echo "================================================"
echo "Build complete!"
echo "================================================"
