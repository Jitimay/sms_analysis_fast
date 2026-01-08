#!/bin/bash

echo "🚀 Starting RouterX Backend..."

# Navigate to backend directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
pip install -r requirements.txt

# Start the server
echo "Backend running at http://localhost:8000"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
