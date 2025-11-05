#!/bin/bash

# ProofOfFace Setup Script
# Automated setup for development environment

set -e

echo "🚀 Setting up ProofOfFace development environment..."

# Check if required tools are installed
check_dependency() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is not installed. Please install it first."
        exit 1
    fi
}

echo "📋 Checking dependencies..."
check_dependency "cargo"
check_dependency "node"
check_dependency "python3"
check_dependency "git"

# Setup Substrate node
echo "🔧 Setting up Substrate node..."
cd substrate-node
if [ ! -f "Cargo.lock" ]; then
    echo "Installing Rust targets..."
    rustup target add wasm32-unknown-unknown
    echo "Building Substrate node (this may take a while)..."
    cargo build --release
fi
cd ..

# Setup AI service
echo "🤖 Setting up AI service..."
cd ai-service
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
echo "Installing Python dependencies..."
pip install -r requirements.txt
cd ..

# Setup frontend
echo "🎨 Setting up frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi
cd ..

# Setup smart contracts
echo "📜 Setting up smart contracts..."
if ! command -v cargo-contract &> /dev/null; then
    echo "Installing cargo-contract..."
    cargo install --force --locked cargo-contract
fi

cd contracts
echo "Building smart contracts..."
cargo contract build
cd ..

# Create environment files
echo "📝 Creating environment files..."

# AI service .env
cat > ai-service/.env << EOF
FLASK_ENV=development
IPFS_NODE_URL=http://localhost:5001
POSTGRES_URL=postgresql://user:pass@localhost/proofofface
FACE_RECOGNITION_TOLERANCE=0.6
PORT=5000
EOF

# Frontend .env
cat > frontend/.env << EOF
REACT_APP_SUBSTRATE_WS_URL=ws://localhost:9944
REACT_APP_AI_SERVICE_URL=http://localhost:5000
REACT_APP_IPFS_GATEWAY=https://ipfs.io/ipfs/
EOF

echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Start Substrate node: cd substrate-node && ./target/release/proofofface-node --dev"
echo "2. Start AI service: cd ai-service && source venv/bin/activate && python app.py"
echo "3. Start frontend: cd frontend && npm start"
echo ""
echo "📖 Check docs/setup.md for detailed instructions"