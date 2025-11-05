# ProofOfFace Runtime Configuration Guide

## Overview

This document explains how the ProofOfFace pallet is integrated into the Substrate runtime and provides instructions for building and running the node.

## Runtime Integration

### 1. Cargo.toml Dependencies ✅

The `runtime/Cargo.toml` includes the ProofOfFace pallet:

```toml
[dependencies]
# Local dependencies
pallet-proofofface = { path = "../pallets/proofofface", default-features = false }

[features]
std = [
    # ... other pallets
    "pallet-proofofface/std",
]
runtime-benchmarks = [
    # ... other pallets  
    "pallet-proofofface/runtime-benchmarks",
]
try-runtime = [
    # ... other pallets
    "pallet-proofofface/try-runtime", 
]
```

### 2. Runtime Configuration ✅

In `runtime/src/lib.rs`, the pallet is configured:

```rust
/// Configure the ProofOfFace pallet
impl pallet_proofofface::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type WeightInfo = pallet_proofofface::weights::SubstrateWeight<Runtime>;
    type MaxIpfsCidLength = ConstU32<100>;
    type MaxEvidenceUrlLength = ConstU32<256>;
    type Randomness = InsecureRandomnessCollectiveFlip;
}
```

**Configuration Parameters:**
- `RuntimeEvent`: Links pallet events to runtime event system
- `WeightInfo`: Provides transaction weight calculations
- `MaxIpfsCidLength`: Maximum IPFS CID length (100 bytes)
- `MaxEvidenceUrlLength`: Maximum evidence URL length (256 bytes)  
- `Randomness`: Source for generating unique dispute IDs

### 3. Runtime Construction ✅

The pallet is included in the runtime:

```rust
construct_runtime!(
    pub enum Runtime where
        Block = Block,
        NodeBlock = opaque::Block,
        UncheckedExtrinsic = UncheckedExtrinsic,
    {
        System: frame_system,
        // ... other pallets
        ProofOfFace: pallet_proofofface,  // 👈 Our pallet
    }
);
```

### 4. Genesis Configuration ✅

In `node/src/chain_spec.rs`, genesis state is configured:

```rust
use proofofface_runtime::{
    // ... other imports
    ProofOfFaceConfig,  // 👈 Added
};

fn testnet_genesis(/* ... */) -> GenesisConfig {
    GenesisConfig {
        // ... other pallets
        proof_of_face: ProofOfFaceConfig {
            // Empty initial state - users register through extrinsics
            _phantom: Default::default(),
        },
    }
}
```

### 5. Benchmarking Integration ✅

Runtime benchmarks include ProofOfFace:

```rust
#[cfg(feature = "runtime-benchmarks")]
mod benches {
    define_benchmarks!(
        [frame_benchmarking, BaselineBench::<Runtime>]
        [frame_system, SystemBench::<Runtime>]
        [pallet_balances, Balances]
        [pallet_timestamp, Timestamp]
        [pallet_proofofface, ProofOfFace]  // 👈 Benchmarks
    );
}
```

## Type Configuration

### Core Types Used

```rust
/// Block number type
pub type BlockNumber = u32;

/// Account identifier type  
pub type AccountId = <<Signature as Verify>::Signer as IdentifyAccount>::AccountId;

/// Hash type for biometric data
pub type Hash = sp_core::H256;

/// Balance type for transaction fees
pub type Balance = u128;
```

These types are automatically available to the ProofOfFace pallet through the runtime configuration.

## Building the Runtime

### Method 1: Using Build Script (Recommended)

```bash
# Navigate to substrate-node directory
cd substrate-node

# Run build script
./build-runtime.sh
```

### Method 2: Manual Build

```bash
# Navigate to substrate-node directory
cd substrate-node

# Build in release mode
cargo build --release
```

**Build Output:**
- Binary: `./target/release/proofofface-node`
- Build time: ~5-15 minutes (first build)
- Size: ~50-100 MB

## Running the Development Node

### Method 1: Using Run Script (Recommended)

```bash
# Navigate to substrate-node directory  
cd substrate-node

# Start development node
./run-dev-node.sh
```

### Method 2: Manual Run

```bash
# Navigate to substrate-node directory
cd substrate-node

# Start node manually
./target/release/proofofface-node --dev --tmp
```

### Development Node Configuration

```bash
./target/release/proofofface-node \
    --dev \                    # Development mode
    --tmp \                    # Temporary storage
    --ws-external \            # External WebSocket access
    --rpc-external \           # External RPC access  
    --rpc-cors all \           # Allow all CORS origins
    --alice \                  # Use Alice as validator
    -lruntime=debug           # Debug runtime logs
```

**Network Endpoints:**
- WebSocket: `ws://localhost:9944`
- HTTP RPC: `http://localhost:9933`
- P2P: `30333`

## Verifying Pallet Integration

### 1. Check Runtime Logs

When starting the node, look for these log entries:

```
✅ EXPECTED LOGS:
2024-01-XX XX:XX:XX [Runtime] 📦 Highest known block at #0
2024-01-XX XX:XX:XX [Runtime] 🔨 Initializing Genesis block/state
2024-01-XX XX:XX:XX [Runtime] 📋 Runtime version: proofofface 100 (proofofface-1.tx1.au1)

✅ PALLET LOADED INDICATORS:
- No compilation errors
- Node starts successfully  
- WebSocket connects on port 9944
```

### 2. Check Metadata

Connect to the node and verify ProofOfFace pallet is included:

```javascript
// Using Polkadot.js API
const api = await ApiPromise.create({ 
    provider: new WsProvider('ws://localhost:9944') 
});

// Check if ProofOfFace pallet exists
console.log('ProofOfFace pallet:', api.tx.proofOfFace ? '✅ Found' : '❌ Missing');

// List available extrinsics
console.log('Available extrinsics:', Object.keys(api.tx.proofOfFace || {}));
// Expected: ['registerIdentity', 'verifyIdentity', 'createDispute', 'voteOnDispute']
```

### 3. Test Extrinsic Submission

```javascript
// Test registering an identity
const biometricHash = '0x1234567890abcdef...'; // 32-byte hash
const ipfsCid = 'QmTestHash123456789abcdef';

const tx = api.tx.proofOfFace.registerIdentity(biometricHash, ipfsCid);
await tx.signAndSend(keyring.alice);
```

## Troubleshooting

### Common Build Issues

#### 1. Compilation Errors

```bash
❌ ERROR: failed to compile pallet-proofofface
```

**Solutions:**
- Check Rust version: `rustup update`
- Clean build: `cargo clean && cargo build --release`
- Check pallet dependencies in `pallets/proofofface/Cargo.toml`

#### 2. Runtime Integration Errors

```bash
❌ ERROR: trait bound not satisfied
```

**Solutions:**
- Verify `Config` trait implementation in `runtime/src/lib.rs`
- Check all required associated types are provided
- Ensure proper imports

#### 3. Genesis Configuration Errors

```bash
❌ ERROR: GenesisConfig field not found
```

**Solutions:**
- Add `ProofOfFaceConfig` import to `chain_spec.rs`
- Verify genesis configuration structure
- Check pallet genesis implementation

### Runtime Issues

#### 1. Pallet Not Found

```bash
❌ Node starts but pallet missing from metadata
```

**Solutions:**
- Verify pallet is in `construct_runtime!` macro
- Check pallet name matches exactly
- Rebuild runtime: `cargo build --release`

#### 2. Extrinsic Failures

```bash
❌ Extrinsics fail with "Module not found"
```

**Solutions:**
- Check pallet configuration parameters
- Verify storage items are properly defined
- Check error handling in pallet functions

#### 3. Event Issues

```bash
❌ Events not emitting or wrong format
```

**Solutions:**
- Verify `RuntimeEvent` configuration
- Check event definitions in pallet
- Ensure proper event emission in functions

## Development Workflow

### 1. Code Changes

```bash
# After modifying pallet code
cd substrate-node

# Rebuild runtime
cargo build --release

# Restart node
./run-dev-node.sh
```

### 2. Testing Changes

```bash
# Run pallet tests
cd pallets/proofofface
cargo test

# Run runtime tests  
cd ../../
cargo test
```

### 3. Benchmarking

```bash
# Run benchmarks
cargo build --release --features runtime-benchmarks

# Generate weights
./target/release/proofofface-node benchmark pallet \
    --chain dev \
    --pallet pallet_proofofface \
    --extrinsic "*" \
    --steps 50 \
    --repeat 20
```

## Production Considerations

### 1. Security

- [ ] Review all `ensure!` checks in pallet functions
- [ ] Validate input parameters thoroughly  
- [ ] Test edge cases and error conditions
- [ ] Audit cryptographic operations

### 2. Performance

- [ ] Optimize storage access patterns
- [ ] Minimize computational complexity
- [ ] Use appropriate weight calculations
- [ ] Test with large datasets

### 3. Governance

- [ ] Consider upgrade mechanisms
- [ ] Plan for parameter adjustments
- [ ] Design emergency stop procedures
- [ ] Document operational procedures

## Next Steps

1. **Frontend Integration**: Connect web interface to runtime
2. **AI Service Integration**: Link biometric processing to pallet
3. **Testing**: Comprehensive integration testing
4. **Documentation**: API documentation and user guides
5. **Deployment**: Testnet and mainnet deployment planning

---

## Quick Reference

### Build Commands
```bash
# Build runtime
cargo build --release

# Clean build  
cargo clean && cargo build --release

# Build with benchmarks
cargo build --release --features runtime-benchmarks
```

### Run Commands
```bash
# Development node
./target/release/proofofface-node --dev --tmp

# With external access
./target/release/proofofface-node --dev --tmp --ws-external --rpc-external

# With debug logs
./target/release/proofofface-node --dev --tmp -lruntime=debug
```

### Test Commands
```bash
# Pallet tests
cd pallets/proofofface && cargo test

# Runtime tests
cargo test

# All tests
cargo test --all
```

The ProofOfFace runtime is now fully configured and ready for development! 🚀