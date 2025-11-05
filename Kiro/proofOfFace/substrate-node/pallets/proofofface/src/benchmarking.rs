//! Benchmarking setup for pallet-proofofface

use super::*;

#[allow(unused)]
use crate::Pallet as ProofOfFace;
use frame_benchmarking::{benchmarks, whitelisted_caller};
use frame_system::RawOrigin;
use sp_std::vec;

benchmarks! {
	register_identity {
		let caller: T::AccountId = whitelisted_caller();
		let ipfs_hash = vec![1u8; 32];
	}: _(RawOrigin::Signed(caller.clone()), ipfs_hash.clone())
	verify {
		assert!(Identities::<T>::contains_key(&caller));
	}

	verify_identity {
		let caller: T::AccountId = whitelisted_caller();
		let identity: T::AccountId = whitelisted_caller();
		let ipfs_hash = vec![1u8; 32];
		
		// Setup: register identity first
		let _ = ProofOfFace::<T>::register_identity(
			RawOrigin::Signed(identity.clone()).into(),
			ipfs_hash
		);
	}: _(RawOrigin::Signed(caller.clone()), identity.clone(), 9500u32, true, None)
	verify {
		assert!(Verifications::<T>::contains_key(&identity, 0));
	}

	raise_dispute {
		let caller: T::AccountId = whitelisted_caller();
		let identity: T::AccountId = whitelisted_caller();
		let ipfs_hash = vec![1u8; 32];
		let reason = vec![1u8; 100];
		
		// Setup: register identity first
		let _ = ProofOfFace::<T>::register_identity(
			RawOrigin::Signed(identity.clone()).into(),
			ipfs_hash
		);
	}: _(RawOrigin::Signed(caller), identity, reason)
	verify {
		assert!(Disputes::<T>::contains_key(0));
	}

	vote_dispute {
		let caller: T::AccountId = whitelisted_caller();
		let identity: T::AccountId = whitelisted_caller();
		let reporter: T::AccountId = whitelisted_caller();
		let ipfs_hash = vec![1u8; 32];
		let reason = vec![1u8; 100];
		
		// Setup: register identity and raise dispute
		let _ = ProofOfFace::<T>::register_identity(
			RawOrigin::Signed(identity.clone()).into(),
			ipfs_hash
		);
		let _ = ProofOfFace::<T>::raise_dispute(
			RawOrigin::Signed(reporter).into(),
			identity,
			reason
		);
	}: _(RawOrigin::Signed(caller), 0u32, true)
	verify {
		let dispute = Disputes::<T>::get(0).unwrap();
		assert_eq!(dispute.votes_for, 1);
	}

	impl_benchmark_test_suite!(ProofOfFace, crate::mock::new_test_ext(), crate::mock::Test);
}