//! ProofOfFace Substrate Node
//! 
//! A decentralized identity verification system built on Substrate.

use proofofface_node::command;

fn main() -> sc_cli::Result<()> {
	command::run()
}