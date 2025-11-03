#![cfg_attr(not(feature = "std"), no_std)]

// ProofOfFace Smart Contracts
// Main library file for Ink! contracts

pub mod identity_registry;
// pub mod face_proof_nft;
// pub mod verification_oracle;
// pub mod dispute_manager;

// Re-export main contracts
pub use identity_registry::identity_registry::IdentityRegistry;
// pub use face_proof_nft::FaceProofNFT;
// pub use verification_oracle::VerificationOracle;
// pub use dispute_manager::DisputeManager;