# ProofOfFace Runtime - Quick Start Guide

## 🚀 Ready to Use Commands

### 1. Verify Integration
```bash
cd substrate-node
chmod +x *.sh
./verify-integration.sh
```

### 2. Build Runtime
```bash
./build-runtime.sh
```

### 3. Start Development Node
```bash
./run-dev-node.sh
```

### 4. Connect Frontend
- **WebSocket**: `ws://localhost:9944`
- **HTTP RPC**: `http://localhost:9933`

## 📁 Files Created/Modified

### Runtime Configuration:
- ✅ `runtime/Cargo.toml` - Added pallet dependency
- ✅ `runtime/src/lib.rs` - Added pallet configuration
- ✅ `node/src/chain_spec.rs` - Added genesis configuration

### Scripts:
- ✅ `build-runtime.sh` - Automated build script
- ✅ `run-dev-node.sh` - Development node runner
- ✅ `verify-integration.sh` - Integration verification

### Documentation:
- ✅ `RUNTIME_CONFIGURATION.md` - Detailed setup guide
- ✅ `INTEGRATION_SUMMARY.md` - Complete integration summary
- ✅ `QUICK_START.md` - This quick start guide

## 🧪 Available Extrinsics

Once the node is running, these functions are available:

```javascript
// Register new identity
api.tx.proofOfFace.registerIdentity(biometricHash, ipfsCid)

// Verify existing identity  
api.tx.proofOfFace.verifyIdentity(biometricHash)

// Create dispute against identity
api.tx.proofOfFace.createDispute(faceProofId, evidenceUrl)

// Vote on pending dispute
api.tx.proofOfFace.voteOnDispute(disputeId, vote)
```

## 🔧 Configuration Summary

### Pallet Configuration:
```rust
impl pallet_proofofface::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type WeightInfo = pallet_proofofface::weights::SubstrateWeight<Runtime>;
    type MaxIpfsCidLength = ConstU32<100>;
    type MaxEvidenceUrlLength = ConstU32<256>;
    type Randomness = InsecureRandomnessCollectiveFlip;
}
```

### Network Settings:
- **Chain ID**: `proofofface_dev`
- **Block Time**: 6 seconds
- **Validator**: Alice account
- **Pre-funded**: Alice, Bob, Charlie, Dave, Eve, Ferdie

## ✅ Integration Status: COMPLETE

The ProofOfFace pallet is fully integrated and ready for development!

**Start with:** `./build-runtime.sh && ./run-dev-node.sh`