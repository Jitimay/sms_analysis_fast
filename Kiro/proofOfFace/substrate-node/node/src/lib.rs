//! ProofOfFace Substrate Node Library
//! 
//! This library provides the core functionality for the ProofOfFace blockchain node.

pub mod chain_spec;
pub mod cli;
pub mod command;
pub mod rpc;
pub mod service;

pub use sc_cli::{Error, Result};