#!/bin/bash

# Student Platform API Startup Script

echo "🚀 Starting Student Platform API..."

# Check if virtual environment exists
if [ ! -d "project_env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv project_env
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source project_env/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Reset database
echo "🗄️  Setting up database..."
python database_utils.py reset

# Run tests
echo "🧪 Running tests..."
pytest tests/ -v

# Start the application
echo "🌟 Starting Flask application..."
echo "   API will be available at: http://localhost:5000"
echo "   Health check: http://localhost:5000/api/health/"
echo "   Press Ctrl+C to stop the server"
echo ""

python app.py
