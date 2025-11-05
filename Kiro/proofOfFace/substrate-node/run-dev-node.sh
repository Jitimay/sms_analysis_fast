#!/bin/bash

# ProofOfFace Development Node Runner
# This script starts a local development node with the ProofOfFace pallet

set -e

echo "🚀 Starting ProofOfFace Development Node..."
echo "=========================================="

# Navigate to substrate-node directory
cd "$(dirname "$0")"

# Check if binary exists
if [ ! -f "./target/release/proofofface-node" ]; then
    echo "❌ Binary not found! Please build first:"
    echo "   ./build-runtime.sh"
    exit 1
fi

echo "🔧 Configuration:"
echo "  - Chain: Development"
echo "  - Storage: Temporary (--tmp)"
echo "  - RPC: ws://localhost:9944"
echo "  - Validator: Alice (--alice)"
echo ""

echo "📡 Starting node..."
echo "Press Ctrl+C to stop"
echo ""

# Start the development node
./target/release/proofofface-node \
    --dev \
    --tmp \
    --ws-external \
    --rpc-external \
    --rpc-cors all \
    --alice \
    -lruntime=debug