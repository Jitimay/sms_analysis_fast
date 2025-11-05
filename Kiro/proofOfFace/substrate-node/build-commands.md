# ProofOfFace Substrate Node - Build Commands

## Prerequisites

Ensure you have the following installed:
- Rust (latest stable)
- WebAssembly target: `rustup target add wasm32-unknown-unknown`
- cargo-contract: `cargo install --force --locked cargo-contract`

## Build Commands

### 1. Build the Node (Release Mode)
```bash
cd substrate-node
cargo build --release
```

### 2. Build in Development Mode (Faster)
```bash
cd substrate-node
cargo build
```

### 3. Run Local Development Chain
```bash
# After building in release mode
./target/release/proofofface-node --dev --tmp

# Or with custom flags
./target/release/proofofface-node --dev --tmp --ws-external --rpc-external --rpc-cors all
```

### 4. Purge Chain Data
```bash
# Remove all chain data (useful for fresh start)
./target/release/proofofface-node purge-chain --dev

# Or with confirmation
./target/release/proofofface-node purge-chain --dev -y
```

### 5. Build Specific Components

#### Build Runtime Only
```bash
cd runtime
cargo build --release
```

#### Build Pallet Only
```bash
cd pallets/proofofface
cargo build --release
```

#### Build Node Only
```bash
cd node
cargo build --release
```

### 6. Run Tests
```bash
# Test the entire workspace
cargo test

# Test specific pallet
cd pallets/proofofface
cargo test

# Test with output
cargo test -- --nocapture
```

### 7. Check Code Quality
```bash
# Format code
cargo fmt

# Run clippy (linter)
cargo clippy

# Check without building
cargo check
```

### 8. Generate Documentation
```bash
# Generate and open documentation
cargo doc --open

# Generate docs for specific pallet
cd pallets/proofofface
cargo doc --open
```

### 9. Benchmarking (Optional)
```bash
# Build with benchmarking features
cargo build --release --features runtime-benchmarks

# Run benchmarks
./target/release/proofofface-node benchmark pallet \
    --chain dev \
    --pallet pallet_proofofface \
    --extrinsic "*" \
    --steps 50 \
    --repeat 20 \
    --output pallets/proofofface/src/weights.rs
```

## Common Issues and Solutions

### Issue: `wasm32-unknown-unknown` target not found
```bash
rustup target add wasm32-unknown-unknown
```

### Issue: Build takes too long
```bash
# Use more CPU cores
export CARGO_BUILD_JOBS=4

# Use faster linker (Linux only)
export RUSTFLAGS="-C link-arg=-fuse-ld=lld"
```

### Issue: Out of memory during build
```bash
# Limit parallel jobs
export CARGO_BUILD_JOBS=2
```

### Issue: Permission denied on binary
```bash
chmod +x target/release/proofofface-node
```

## Development Workflow

1. **Make changes** to pallets or runtime
2. **Build**: `cargo build --release`
3. **Test**: `cargo test`
4. **Run**: `./target/release/proofofface-node --dev --tmp`
5. **Purge** (if needed): `./target/release/proofofface-node purge-chain --dev -y`

## Production Deployment

For production deployment, always use:
```bash
cargo build --release
```

And run with appropriate flags:
```bash
./target/release/proofofface-node \
    --chain local \
    --validator \
    --name "ProofOfFace-Node-1" \
    --port 30333 \
    --ws-port 9944 \
    --rpc-port 9933
```