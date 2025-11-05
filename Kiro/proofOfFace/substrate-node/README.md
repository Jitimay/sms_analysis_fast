# ProofOfFace Substrate Node

A Substrate-based blockchain node for decentralized identity verification and deepfake prevention.

## Overview

The ProofOfFace Substrate node implements a custom blockchain runtime with the `pallet-proofofface` pallet, providing:

- **Identity Registration**: Register face identities on-chain with IPFS storage
- **Verification System**: Verify face matches against registered identities  
- **Reputation Management**: Track and update identity reputation scores
- **Dispute Resolution**: Community-driven dispute handling mechanism

## Architecture

```
substrate-node/
├── node/                    # Node implementation
│   ├── src/
│   │   ├── chain_spec.rs   # Chain specification
│   │   ├── cli.rs          # Command line interface
│   │   ├── command.rs      # Command handling
│   │   ├── rpc.rs          # RPC extensions
│   │   └── service.rs      # Node service
│   └── bin/main.rs         # Entry point
├── pallets/
│   └── proofofface/        # Custom pallet
│       └── src/
│           ├── lib.rs      # Main pallet logic
│           ├── weights.rs  # Weight calculations
│           ├── tests.rs    # Unit tests
│           └── mock.rs     # Test utilities
├── runtime/                # Runtime configuration
│   └── src/lib.rs         # Runtime assembly
└── Cargo.toml             # Workspace configuration
```

## Quick Start

### Prerequisites

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Add WebAssembly target
rustup target add wasm32-unknown-unknown

# Install cargo-contract (optional, for benchmarking)
cargo install --force --locked cargo-contract
```

### Build & Run

```bash
# Build the node (takes 15-30 minutes first time)
cargo build --release

# Run local development chain
./target/release/proofofface-node --dev --tmp

# Or with external access
./target/release/proofofface-node --dev --tmp --ws-external --rpc-external --rpc-cors all
```

### Access Points

- **WebSocket RPC**: `ws://localhost:9944`
- **HTTP RPC**: `http://localhost:9933`
- **P2P**: `30333`

## Pallet Functions

### Identity Registration
```rust
// Register a new identity with IPFS hash
register_identity(origin, ipfs_hash: Vec<u8>)
```

### Identity Verification  
```rust
// Verify an identity against submitted proof
verify_identity(
    origin, 
    identity: AccountId, 
    confidence: u32,
    success: bool, 
    proof_hash: Option<Vec<u8>>
)
```

### Dispute Management
```rust
// Raise a dispute against an identity
raise_dispute(origin, identity: AccountId, reason: Vec<u8>)

// Vote on an open dispute
vote_dispute(origin, dispute_id: u32, vote_for: bool)
```

## Development Commands

### Building
```bash
# Full build
cargo build --release

# Development build (faster)
cargo build

# Build specific components
cd pallets/proofofface && cargo build
cd runtime && cargo build
cd node && cargo build
```

### Testing
```bash
# Run all tests
cargo test

# Test specific pallet
cd pallets/proofofface && cargo test

# Test with output
cargo test -- --nocapture
```

### Code Quality
```bash
# Format code
cargo fmt

# Run linter
cargo clippy

# Check without building
cargo check
```

### Chain Management
```bash
# Purge chain data (fresh start)
./target/release/proofofface-node purge-chain --dev -y

# Export chain state
./target/release/proofofface-node export-state --chain dev > state.json

# Import blocks
./target/release/proofofface-node import-blocks --chain dev blocks.bin
```

## Configuration

### Development Chain Spec
- **Chain ID**: `proofofface_dev`
- **Consensus**: Aura (Authority Round) + GRANDPA
- **Block Time**: 6 seconds
- **Authorities**: Alice (development)

### Local Testnet
- **Chain ID**: `proofofface_local_testnet`  
- **Authorities**: Alice, Bob
- **Pre-funded**: Alice, Bob, Charlie, Dave, Eve, Ferdie

### Runtime Configuration
```rust
// Key parameters
pub const MILLISECS_PER_BLOCK: u64 = 6000;
pub const EXISTENTIAL_DEPOSIT: u128 = 500;

// ProofOfFace pallet config
type MaxIpfsHashLength = ConstU32<64>;
type MaxVerificationsPerIdentity = ConstU32<1000>;
```

## Integration

### Frontend Integration
```javascript
// Connect to node
const api = await ApiPromise.create({ 
  provider: new WsProvider('ws://localhost:9944') 
});

// Register identity
const tx = api.tx.proofOfFace.registerIdentity(ipfsHash);
await tx.signAndSend(account);

// Verify identity  
const tx = api.tx.proofOfFace.verifyIdentity(
  identityAccount, 
  confidence, 
  success, 
  proofHash
);
```

### AI Service Integration
The node works with the AI service to:
1. Store face encodings on IPFS
2. Record verification results on-chain
3. Manage reputation scores
4. Handle dispute resolution

## Deployment

### Local Development
```bash
./target/release/proofofface-node --dev --tmp
```

### Local Testnet
```bash
# Node 1 (Alice)
./target/release/proofofface-node \
  --chain local \
  --alice \
  --port 30333 \
  --ws-port 9944 \
  --rpc-port 9933

# Node 2 (Bob)  
./target/release/proofofface-node \
  --chain local \
  --bob \
  --port 30334 \
  --ws-port 9945 \
  --rpc-port 9934 \
  --bootnodes /ip4/127.0.0.1/tcp/30333/p2p/NODE1_PEER_ID
```

### Production Deployment
```bash
./target/release/proofofface-node \
  --chain mainnet \
  --validator \
  --name "ProofOfFace-Validator-1" \
  --port 30333 \
  --ws-port 9944 \
  --rpc-port 9933 \
  --telemetry-url "wss://telemetry.polkadot.io/submit/ 0"
```

## Monitoring

### Health Checks
```bash
# Node health
curl http://localhost:9933/health

# System info
curl -H "Content-Type: application/json" \
  -d '{"id":1, "jsonrpc":"2.0", "method": "system_health"}' \
  http://localhost:9933
```

### Metrics
- Prometheus metrics available at `/metrics` endpoint
- Grafana dashboards for monitoring
- Telemetry integration with Polkadot telemetry

## Troubleshooting

### Common Issues

**Build Errors**:
```bash
# Missing WebAssembly target
rustup target add wasm32-unknown-unknown

# Outdated dependencies  
cargo update
```

**Runtime Errors**:
```bash
# Clear chain data
./target/release/proofofface-node purge-chain --dev -y

# Check logs
RUST_LOG=debug ./target/release/proofofface-node --dev
```

**Connection Issues**:
```bash
# Check if ports are available
netstat -tulpn | grep :9944

# Allow external connections
./target/release/proofofface-node --dev --ws-external --rpc-external --rpc-cors all
```

## Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Make changes** to pallets or runtime
4. **Run tests**: `cargo test`
5. **Format code**: `cargo fmt`
6. **Submit pull request**

## License

MIT License - see LICENSE file for details.

---

**Built for Polkadot Cloud Hackathon 2024**