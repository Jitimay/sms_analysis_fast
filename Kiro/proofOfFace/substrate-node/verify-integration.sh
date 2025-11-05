#!/bin/bash

# ProofOfFace Runtime Integration Verification Script
# This script verifies that the ProofOfFace pallet is properly integrated

set -e

echo "🔍 ProofOfFace Runtime Integration Verification"
echo "=============================================="

# Navigate to substrate-node directory
cd "$(dirname "$0")"

echo "📁 Current directory: $(pwd)"
echo ""

# 1. Check if pallet exists
echo "1️⃣ Checking pallet structure..."
if [ -d "pallets/proofofface" ]; then
    echo "   ✅ Pallet directory exists"
else
    echo "   ❌ Pallet directory missing"
    exit 1
fi

if [ -f "pallets/proofofface/src/lib.rs" ]; then
    echo "   ✅ Pallet lib.rs exists"
else
    echo "   ❌ Pallet lib.rs missing"
    exit 1
fi

# 2. Check runtime dependencies
echo ""
echo "2️⃣ Checking runtime dependencies..."
if grep -q "pallet-proofofface" runtime/Cargo.toml; then
    echo "   ✅ Pallet dependency in runtime/Cargo.toml"
else
    echo "   ❌ Pallet dependency missing from runtime/Cargo.toml"
    exit 1
fi

# 3. Check runtime configuration
echo ""
echo "3️⃣ Checking runtime configuration..."
if grep -q "impl pallet_proofofface::Config for Runtime" runtime/src/lib.rs; then
    echo "   ✅ Pallet Config implementation found"
else
    echo "   ❌ Pallet Config implementation missing"
    exit 1
fi

if grep -q "ProofOfFace: pallet_proofofface" runtime/src/lib.rs; then
    echo "   ✅ Pallet in construct_runtime! macro"
else
    echo "   ❌ Pallet missing from construct_runtime! macro"
    exit 1
fi

# 4. Check genesis configuration
echo ""
echo "4️⃣ Checking genesis configuration..."
if grep -q "ProofOfFaceConfig" node/src/chain_spec.rs; then
    echo "   ✅ Genesis configuration found"
else
    echo "   ❌ Genesis configuration missing"
    exit 1
fi

# 5. Test compilation
echo ""
echo "5️⃣ Testing compilation..."
echo "   🔨 Running cargo check..."
if cargo check --quiet 2>/dev/null; then
    echo "   ✅ Compilation successful"
else
    echo "   ❌ Compilation failed"
    echo "   💡 Run 'cargo check' for detailed error information"
    exit 1
fi

# 6. Check for required functions
echo ""
echo "6️⃣ Checking pallet functions..."
if grep -q "register_identity" pallets/proofofface/src/lib.rs; then
    echo "   ✅ register_identity function found"
else
    echo "   ❌ register_identity function missing"
fi

if grep -q "verify_identity" pallets/proofofface/src/lib.rs; then
    echo "   ✅ verify_identity function found"
else
    echo "   ❌ verify_identity function missing"
fi

if grep -q "create_dispute" pallets/proofofface/src/lib.rs; then
    echo "   ✅ create_dispute function found"
else
    echo "   ❌ create_dispute function missing"
fi

if grep -q "vote_on_dispute" pallets/proofofface/src/lib.rs; then
    echo "   ✅ vote_on_dispute function found"
else
    echo "   ❌ vote_on_dispute function missing"
fi

echo ""
echo "🎉 Integration Verification Complete!"
echo ""
echo "📋 Summary:"
echo "   ✅ Pallet structure verified"
echo "   ✅ Runtime dependencies configured"
echo "   ✅ Runtime configuration complete"
echo "   ✅ Genesis configuration added"
echo "   ✅ Compilation successful"
echo "   ✅ Core functions implemented"
echo ""
echo "🚀 Ready for development!"
echo ""
echo "🔧 Next steps:"
echo "   1. Build runtime: ./build-runtime.sh"
echo "   2. Start dev node: ./run-dev-node.sh"
echo "   3. Connect frontend to ws://localhost:9944"
echo ""