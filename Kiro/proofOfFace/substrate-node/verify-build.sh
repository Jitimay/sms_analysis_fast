#!/bin/bash

# ProofOfFace Node Verification Script
set -e

echo "🔍 Verifying ProofOfFace Substrate Node Build..."

# Check Rust version
echo "📋 Rust version:"
rustc --version

# Check if node binary exists
if [ -f "target/release/proofofface-node" ]; then
    echo "✅ Node binary found"
    
    # Test node help
    echo "📋 Testing node help command..."
    ./target/release/proofofface-node --help | head -10
    
    # Test node version
    echo "📋 Testing node version..."
    ./target/release/proofofface-node --version
    
    echo "✅ Node binary is functional"
else
    echo "❌ Node binary not found. Build may have failed."
    exit 1
fi

# Test if we can start the node (quick test)
echo "🚀 Testing node startup (5 second test)..."
timeout 5s ./target/release/proofofface-node --dev --tmp || {
    if [ $? -eq 124 ]; then
        echo "✅ Node started successfully (timed out as expected)"
    else
        echo "❌ Node failed to start"
        exit 1
    fi
}

echo ""
echo "🎉 ProofOfFace node verification complete!"
echo ""
echo "To run the node:"
echo "  ./target/release/proofofface-node --dev --tmp"
echo ""
echo "To connect frontend:"
echo "  ./target/release/proofofface-node --dev --tmp --ws-external --rpc-external --rpc-cors all"