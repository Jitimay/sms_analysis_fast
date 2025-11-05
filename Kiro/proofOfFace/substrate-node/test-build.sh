#!/bin/bash

# Simple test script to verify Substrate node builds
set -e

echo "🔍 Testing ProofOfFace Substrate Node Build..."

# Check Rust toolchain
echo "📋 Checking Rust toolchain..."
rustc --version
cargo --version

# Check WebAssembly target
echo "📋 Checking WebAssembly target..."
rustup target list --installed | grep wasm32-unknown-unknown || {
    echo "❌ WebAssembly target not found. Installing..."
    rustup target add wasm32-unknown-unknown
}

# Test pallet compilation
echo "🔧 Testing pallet compilation..."
cd pallets/proofofface
timeout 300 cargo check || {
    echo "⚠️  Pallet build timed out or failed"
    exit 1
}

echo "✅ Pallet check completed"

# Test runtime compilation  
echo "🔧 Testing runtime compilation..."
cd ../../runtime
timeout 300 cargo check --no-default-features || {
    echo "⚠️  Runtime build timed out or failed"
    exit 1
}

echo "✅ Runtime check completed"

# Test node compilation
echo "🔧 Testing node compilation..."
cd ../node
timeout 300 cargo check || {
    echo "⚠️  Node build timed out or failed"
    exit 1
}

echo "✅ Node check completed"

echo "🎉 All components compiled successfully!"
echo ""
echo "Next steps:"
echo "1. Run full build: cargo build --release"
echo "2. Start node: ./target/release/proofofface-node --dev --tmp"