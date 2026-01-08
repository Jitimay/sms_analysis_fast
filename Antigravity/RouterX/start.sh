#!/bin/bash

echo "🌟 Starting RouterX - AI-Powered Stablecoin Remittance Router"
echo "=================================================="

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $1 is already in use"
        return 1
    fi
    return 0
}

# Check required ports
if ! check_port 8000; then
    echo "Backend port 8000 is busy. Please stop the existing process."
    exit 1
fi

if ! check_port 5173; then
    echo "Frontend port 5173 is busy. Please stop the existing process."
    exit 1
fi

echo "✅ Ports available"

# Start backend in background
echo "🚀 Starting Backend..."
cd backend
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend in background
echo "🎨 Starting Frontend..."
cd frontend
npm install > /dev/null 2>&1
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 RouterX is starting up!"
echo "📊 Backend API: http://localhost:8000"
echo "🌐 Frontend App: http://localhost:5173"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down RouterX..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for processes
wait
