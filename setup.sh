#!/bin/bash

# MLB Hall of Fame Database Setup Script

echo "Setting up MLB Hall of Fame Database..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Make app.py executable
chmod +x app.py

echo "Setup complete!"
echo ""
echo "To start the application:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run with Python: python3 app.py"
echo "3. Or run with Gunicorn: gunicorn -c gunicorn.conf.py app:run_server"
echo ""
echo "The application will be available at: http://localhost:8000" 