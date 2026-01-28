#!/bin/bash

# Quick Start Script for FPL League Match Reports Streamlit App
# This script sets up and runs the development environment

set -e

echo "🚀 FPL League Match Reports - Quick Start"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "✅ Virtual environment activated"
echo ""

# Install/upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✅ pip upgraded"
echo ""

# Install dependencies
echo "📦 Installing dependencies from requirements.txt..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Check if config files exist
if [ ! -f "fpl_data/config.json" ]; then
    echo "⚠️  fpl_data/config.json not found"
    echo "   Copy from fpl_data/config_template.json and edit with your settings"
fi

if [ ! -f "fpl_data/bios.json" ]; then
    echo "⚠️  fpl_data/bios.json not found"
    echo "   Copy from fpl_data/bios_template.json and edit with your team info"
fi

echo ""
echo "=========================================="
echo "🎉 Setup complete!"
echo "=========================================="
echo ""
echo "To start the Streamlit app, run:"
echo "   streamlit run app.py"
echo ""
echo "The app will open at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server when done."
echo ""
