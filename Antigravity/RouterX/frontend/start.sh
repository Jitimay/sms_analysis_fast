#!/bin/bash

echo "🎨 Starting RouterX Frontend..."

# Navigate to frontend directory
cd "$(dirname "$0")"

# Install dependencies if needed
npm install

# Start development server
echo "Frontend running at http://localhost:5173"
npm run dev
