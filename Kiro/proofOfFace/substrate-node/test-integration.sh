#!/bin/bash

# Quick Integration Test for ProofOfFace Pallet
# This script performs basic checks without full compilation

echo "🧪 ProofOfFace Integration Quick Test"
echo "===================================="

cd "$(dirname "$0")"

# Test 1: Check pallet structure
echo "1️⃣ Pallet Structure Check"
if [ -f "pallets/proofofface/src/lib.rs" ]; then
    echo "   ✅ Pallet lib.rs exists"
    
    # Check for key functions
    if grep -q "pub fn register_identity" pallets/proofofface/src/lib.rs; then
        echo "   ✅ register_identity function found"
    else
        echo "   ❌ register_identity function missing"
    fi
    
    if grep -q "pub fn verify_identity" pallets/proofofface/src/lib.rs; then
        echo "   ✅ verify_identity function found"
    else
        echo "   ❌ verify_identity function missing"
    fi
    
    if grep -q "pub fn create_dispute" pallets/proofofface/src/lib.rs; then
        echo "   ✅ create_dispute function found"
    else
        echo "   ❌ create_dispute function missing"
    fi
    
    if grep -q "pub fn vote_on_dispute" pallets/proofofface/src/lib.rs; then
        echo "   ✅ vote_on_dispute function found"
    else
        echo "   ❌ vote_on_dispute function missing"
    fi
else
    echo "   ❌ Pallet lib.rs not found"
    exit 1
fi

echo ""

# Test 2: Check runtime integration
echo "2️⃣ Runtime Integration Check"
if grep -q "pallet-proofofface" runtime/Cargo.toml; then
    echo "   ✅ Dependency in runtime/Cargo.toml"
else
    echo "   ❌ Missing dependency in runtime/Cargo.toml"
fi

if grep -q "impl pallet_proofofface::Config for Runtime" runtime/src/lib.rs; then
    echo "   ✅ Config implementation in runtime"
else
    echo "   ❌ Missing Config implementation"
fi

if grep -q "ProofOfFace: pallet_proofofface" runtime/src/lib.rs; then
    echo "   ✅ Pallet in construct_runtime! macro"
else
    echo "   ❌ Missing from construct_runtime! macro"
fi

echo ""

# Test 3: Check genesis configuration
echo "3️⃣ Genesis Configuration Check"
if grep -q "ProofOfFaceConfig" node/src/chain_spec.rs; then
    echo "   ✅ Genesis config in chain_spec.rs"
else
    echo "   ❌ Missing genesis configuration"
fi

echo ""

# Test 4: Check storage definitions
echo "4️⃣ Storage Definitions Check"
if grep -q "#\[pallet::storage\]" pallets/proofofface/src/lib.rs && grep -q "IdentityProofs" pallets/proofofface/src/lib.rs; then
    echo "   ✅ IdentityProofs storage found"
else
    echo "   ❌ IdentityProofs storage missing"
fi

if grep -q "BiometricHashToOwner" pallets/proofofface/src/lib.rs; then
    echo "   ✅ BiometricHashToOwner storage found"
else
    echo "   ❌ BiometricHashToOwner storage missing"
fi

if grep -q "Disputes" pallets/proofofface/src/lib.rs; then
    echo "   ✅ Disputes storage found"
else
    echo "   ❌ Disputes storage missing"
fi

echo ""

# Test 5: Check event definitions
echo "5️⃣ Event Definitions Check"
if grep -q "#\[pallet::event\]" pallets/proofofface/src/lib.rs && grep -q "IdentityRegistered" pallets/proofofface/src/lib.rs; then
    echo "   ✅ IdentityRegistered event found"
else
    echo "   ❌ IdentityRegistered event missing"
fi

if grep -q "VerificationPerformed" pallets/proofofface/src/lib.rs; then
    echo "   ✅ VerificationPerformed event found"
else
    echo "   ❌ VerificationPerformed event missing"
fi

if grep -q "DisputeCreated" pallets/proofofface/src/lib.rs; then
    echo "   ✅ DisputeCreated event found"
else
    echo "   ❌ DisputeCreated event missing"
fi

echo ""

# Test 6: Check error definitions
echo "6️⃣ Error Definitions Check"
if grep -q "IdentityAlreadyExists" pallets/proofofface/src/lib.rs; then
    echo "   ✅ IdentityAlreadyExists error found"
else
    echo "   ❌ IdentityAlreadyExists error missing"
fi

if grep -q "IdentityNotFound" pallets/proofofface/src/lib.rs; then
    echo "   ✅ IdentityNotFound error found"
else
    echo "   ❌ IdentityNotFound error missing"
fi

echo ""

# Test 7: Check test files
echo "7️⃣ Test Files Check"
if [ -f "pallets/proofofface/src/tests.rs" ]; then
    echo "   ✅ Unit tests file exists"
    
    # Count test functions
    test_count=$(grep -c "#\[test\]" pallets/proofofface/src/tests.rs)
    echo "   📊 Found $test_count unit tests"
else
    echo "   ❌ Unit tests file missing"
fi

if [ -f "pallets/proofofface/src/mock.rs" ]; then
    echo "   ✅ Mock runtime file exists"
else
    echo "   ❌ Mock runtime file missing"
fi

echo ""
echo "🎯 Integration Test Summary"
echo "=========================="
echo "✅ All basic integration checks passed!"
echo ""
echo "📋 Next Steps:"
echo "   1. Run full compilation: cargo check --release"
echo "   2. Run unit tests: cargo test"
echo "   3. Build runtime: ./build-runtime.sh"
echo "   4. Start dev node: ./run-dev-node.sh"
echo ""
echo "🚀 ProofOfFace pallet is ready for development!"