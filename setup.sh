#!/bin/bash
# Quick setup script for LP Alerts 24H

echo "🚀 LP Alerts 24H - Setup Script"
echo "================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "✅ Python 3 found"
python3 --version

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Virtual environment created"
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo "✅ Dependencies installed"

# Create .env file
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your credentials:"
    echo "   - GEOEDGE_API_KEY"
    echo "   - MYSQL credentials"
    echo "   - ALERT_EMAIL"
else
    echo "✅ .env file already exists"
fi

# Run system test
echo ""
echo "🧪 Running system test..."
python3 test_system.py

echo ""
echo "================================"
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your credentials"
echo "2. Run: python main.py"
echo ""
echo "To activate virtual environment in future:"
echo "  source venv/bin/activate"
