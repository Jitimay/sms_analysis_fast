# ProofOfFace Smart Contracts

Ink! smart contracts for identity verification and NFT management.

## Contracts

### 1. IdentityRegistry.rs
- Register new identities
- Store IPFS hashes of face embeddings
- Manage identity metadata

### 2. FaceProofNFT.rs
- Mint unique identity NFTs
- Transfer and ownership management
- Metadata and provenance tracking

### 3. VerificationOracle.rs
- Interface with AI service
- Store verification results
- Manage verification history

### 4. DisputeManager.rs
- Handle dispute submissions
- Voting mechanism
- Resolution and penalties

## Development

```bash
# Install cargo-contract
cargo install --force --locked cargo-contract

# Build contracts
cargo contract build

# Deploy to local node
cargo contract instantiate --constructor new --args "initial_params"
```