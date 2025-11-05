#!/bin/bash

# ProofOfFace Runtime Build Script
# This script builds the Substrate runtime with the ProofOfFace pallet

set -e

echo "🔨 Building ProofOfFace Runtime..."
echo "=================================="

# Navigate to substrate-node directory
cd "$(dirname "$0")"

# Clean previous builds (optional - comment out for faster builds)
echo "🧹 Cleaning previous builds..."
cargo clean

# Build the runtime in release mode
echo "🚀 Building runtime with ProofOfFace pallet..."
cargo build --release

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Runtime build completed successfully!"
    echo ""
    echo "📦 Binary location: ./target/release/proofofface-node"
    echo ""
    echo "🎯 Next steps:"
    echo "  1. Run local development node: ./run-dev-node.sh"
    echo "  2. Or run manually: ./target/release/proofofface-node --dev --tmp"
    echo ""
else
    echo "❌ Runtime build failed!"
    exit 1
fi