#!/bin/bash

# ProofOfFace AI Service Startup Script
# This script starts the AI service with proper configuration

set -e

echo "🚀 Starting ProofOfFace AI Service..."
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Set default environment variables if not set
export FLASK_ENV=${FLASK_ENV:-development}
export HOST=${HOST:-0.0.0.0}
export PORT=${PORT:-5000}
export LOG_LEVEL=${LOG_LEVEL:-INFO}

# Generate encryption key if not set
if [ -z "$ENCRYPTION_KEY" ]; then
    echo "🔐 Generating encryption key..."
    export ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    echo "⚠️  Generated encryption key: $ENCRYPTION_KEY"
    echo "⚠️  Save this key securely for production use!"
fi

# Generate secret key if not set
if [ -z "$SECRET_KEY" ]; then
    echo "🔑 Generating secret key..."
    export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
fi

echo ""
echo "🔧 Configuration:"
echo "   Environment: $FLASK_ENV"
echo "   Host: $HOST"
echo "   Port: $PORT"
echo "   Log Level: $LOG_LEVEL"
echo ""

# Check if running in development or production
if [ "$FLASK_ENV" = "development" ]; then
    echo "🔨 Starting development server..."
    python app.py
else
    echo "🚀 Starting production server with Gunicorn..."
    gunicorn \
        --bind $HOST:$PORT \
        --workers 2 \
        --worker-class sync \
        --timeout 120 \
        --keepalive 5 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --preload \
        --access-logfile - \
        --error-logfile - \
        app:app
fi