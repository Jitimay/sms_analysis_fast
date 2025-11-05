use crate::{mock::*, Error, Event};
use frame_support::{assert_noop, assert_ok, BoundedVec};
use sp_core::H256;
use sp_runtime::traits::{BlakeTwo256, Hash};

/// Helper function to create a test biometric hash
fn test_biometric_hash(seed: u8) -> H256 {
	BlakeTwo256::hash(&[seed; 32])
}

/// Helper function to create a test IPFS CID
fn test_ipfs_cid(content: &str) -> BoundedVec<u8, frame_support::traits::ConstU32<100>> {
	BoundedVec::try_from(content.as_bytes().to_vec()).unwrap()
}

#[test]
fn register_identity_works() {
	new_test_ext().execute_with(|| {
		// Go past genesis block so events get deposited
		System::set_block_number(1);

		let account_id = 1u64;
		let biometric_hash = test_biometric_hash(1);
		let ipfs_cid = test_ipfs_cid("QmTestHash123456789abcdef");

		// Register identity should work
		assert_ok!(ProofOfFaceModule::register_identity(
			RuntimeOrigin::signed(account_id),
			biometric_hash,
			ipfs_cid.clone()
		));

		// Check that identity proof was stored correctly
		let stored_proof = ProofOfFaceModule::identity_proofs(account_id).unwrap();
		assert_eq!(stored_proof.owner, account_id);
		assert_eq!(stored_proof.biometric_hash, biometric_hash);
		assert_eq!(stored_proof.ipfs_cid, ipfs_cid);
		assert_eq!(stored_proof.timestamp, 1); // Current block number
		assert_eq!(stored_proof.is_active, true);

		// Check that reverse lookup was stored
		let owner = ProofOfFaceModule::biometric_hash_to_owner(biometric_hash).unwrap();
		assert_eq!(owner, account_id);

		// Check that event was emitted
		System::assert_last_event(
			Event::IdentityRegistered(account_id, biometric_hash).into(),
		);
	});
}

#[test]
fn register_identity_fails_when_already_exists() {
	new_test_ext().execute_with(|| {
		let account_id = 1u64;
		let biometric_hash = test_biometric_hash(1);
		let ipfs_cid = test_ipfs_cid("QmTestHash123456789abcdef");

		// Register identity first time
		assert_ok!(ProofOfFaceModule::register_identity(
			RuntimeOrigin::signed(account_id),
			biometric_hash,
			ipfs_cid.clone()
		));

		// Try to register again with same account - should fail
		let new_biometric_hash = test_biometric_hash(2);
		let new_ipfs_cid = test_ipfs_cid("QmNewTestHash987654321");
		
		assert_noop!(
			ProofOfFaceModule::register_identity(
				RuntimeOrigin::signed(account_id),
				new_biometric_hash,
				new_ipfs_cid
			),
			Error::<Test>::IdentityAlreadyExists
		);
	});
}

#[test]
fn register_identity_fails_with_duplicate_biometric_hash() {
	new_test_ext().execute_with(|| {
		let account_id_1 = 1u64;
		let account_id_2 = 2u64;
		let biometric_hash = test_biometric_hash(1); // Same hash for both
		let ipfs_cid_1 = test_ipfs_cid("QmTestHash123456789abcdef");
		let ipfs_cid_2 = test_ipfs_cid("QmTestHash987654321fedcba");

		// Register identity with first account
		assert_ok!(ProofOfFaceModule::register_identity(
			RuntimeOrigin::signed(account_id_1),
			biometric_hash,
			ipfs_cid_1
		));

		// Try to register with second account using same biometric hash - should fail
		assert_noop!(
			ProofOfFaceModule::register_identity(
				RuntimeOrigin::signed(account_id_2),
				biometric_hash, // Same hash as first registration
				ipfs_cid_2
			),
			Error::<Test>::InvalidBiometricHash
		);
	});
}

#[test]
fn register_identity_fails_with_empty_ipfs_cid() {
	new_test_ext().execute_with(|| {
		let account_id = 1u64;
		let biometric_hash = test_biometric_hash(1);
		let empty_ipfs_cid = BoundedVec::try_from(Vec::<u8>::new()).unwrap();

		// Try to register with empty IPFS CID - should fail
		assert_noop!(
			ProofOfFaceModule::register_identity(
				RuntimeOrigin::signed(account_id),
				biometric_hash,
				empty_ipfs_cid
			),
			Error::<Test>::InvalidIpfsCid
		);
	});
}

#[test]
fn register_identity_fails_with_unsigned_origin() {
	new_test_ext().execute_with(|| {
		let biometric_hash = test_biometric_hash(1);
		let ipfs_cid = test_ipfs_cid("QmTestHash123456789abcdef");

		// Try to register without signed origin - should fail
		assert_noop!(
			ProofOfFaceModule::register_identity(
				RuntimeOrigin::none(),
				biometric_hash,
				ipfs_cid
			),
			sp_runtime::DispatchError::BadOrigin
		);
	});
}

#[test]
fn register_identity_stores_correct_timestamp() {
	new_test_ext().execute_with(|| {
		let account_id = 1u64;
		let biometric_hash = test_biometric_hash(1);
		let ipfs_cid = test_ipfs_cid("QmTestHash123456789abcdef");

		// Set specific block number
		System::set_block_number(42);

		// Register identity
		assert_ok!(ProofOfFaceModule::register_identity(
			RuntimeOrigin::signed(account_id),
			biometric_hash,
			ipfs_cid
		));

		// Check that timestamp matches current block number
		let stored_proof = ProofOfFaceModule::identity_proofs(account_id).unwrap();
		assert_eq!(stored_proof.timestamp, 42);
	});
}

#[test]
fn register_identity_creates_active_proof() {
	new_test_ext().execute_with(|| {
		let account_id = 1u64;
		let biometric_hash = test_biometric_hash(1);
		let ipfs_cid = test_ipfs_cid("QmTestHash123456789abcdef");

		// Register identity
		assert_ok!(ProofOfFaceModule::register_identity(
			RuntimeOrigin::signed(account_id),
			biometric_hash,
			ipfs_cid
		));

		// Check that proof is active by default
		let stored_proof = ProofOfFaceModule::identity_proofs(account_id).unwrap();
		assert_eq!(stored_proof.is_active, true);

		// Check helper function
		assert_eq!(ProofOfFaceModule::is_identity_active(&account_id), true);
	});
}

#[test]
fn multiple_users_can_register_different_identities() {
	new_test_ext().execute_with(|| {
		let account_id_1 = 1u64;
		let account_id_2 = 2u64;
		let account_id_3 = 3u64;
		
		let biometric_hash_1 = test_biometric_hash(1);
		let biometric_hash_2 = test_biometric_hash(2);
		let biometric_hash_3 = test_biometric_hash(3);
		
		let ipfs_cid_1 = test_ipfs_cid("QmTestHash1");
		let ipfs_cid_2 = test_ipfs_cid("QmTestHash2");
		let ipfs_cid_3 = test_ipfs_cid("QmTestHash3");

		// Register multiple different identities
		assert_ok!(ProofOfFaceModule::register_identity(
			RuntimeOrigin::signed(account_id_1),
			biometric_hash_1,
			ipfs_cid_1
		));

		assert_ok!(ProofOfFaceModule::register_identity(
			RuntimeOrigin::signed(account_id_2),
			biometric_hash_2,
			ipfs_cid_2
		));

		assert_ok!(ProofOfFaceModule::register_identity(
			RuntimeOrigin::signed(account_id_3),
			biometric_hash_3,
			ipfs_cid_3
		));

		// Verify all identities are stored correctly
		assert!(ProofOfFaceModule::identity_proofs(account_id_1).is_some());
		assert!(ProofOfFaceModule::identity_proofs(account_id_2).is_some());
		assert!(ProofOfFaceModule::identity_proofs(account_id_3).is_some());

		// Verify reverse lookups work
		assert_eq!(ProofOfFaceModule::biometric_hash_to_owner(biometric_hash_1).unwrap(), account_id_1);
		assert_eq!(ProofOfFaceModule::biometric_hash_to_owner(biometric_hash_2).unwrap(), account_id_2);
		assert_eq!(ProofOfFaceModule::biometric_hash_to_owner(biometric_hash_3).unwrap(), account_id_3);
	});
}

// ================================
// VERIFY IDENTITY TESTS
// ================================

#[test]
fn verify_identity_works_for_existing_identity() {
	new_test_ext().execute_with(|| {
		// Set up initial state
		System::set_block_number(1);

		let identity_owner = 1u64;
		let verifier = 2u64;
		let biometric_hash = test_biometric_hash(1);
		let ipfs_cid = test_ipfs_cid("QmTestHash123456789abcdef");

		// Step 1: Register an identity first
		assert_ok!(ProofOfFaceModule::register_identity(
			RuntimeOrigin::signed(identity_owner),
			biometric_hash,
			ipfs_cid
		));

		// Step 2: Verify the registered identity
		assert_ok!(ProofOfFaceModule::verify_identity(
			RuntimeOrigin::signed(verifier),
			biometric_hash
		));

		// Step 3: Check that the correct event was emitted
		// The event should indicate successful verification (true)
		System::assert_last_event(
			Event::VerificationPerformed(biometric_hash, true).into(),
		);
	});
}

#[test]
fn verify_identity_works_for_non_existent_identity() {
	new_test_ext().execute_with(|| {
		// Set up initial state
		System::set_block_number(1);

		let verifier = 1u64;
		let non_existent_hash = test_biometric_hash(99); // Hash that was never registered

		// Verify a non-existent identity
		// This should succeed (not return an error) but emit a "false" event
		assert_ok!(ProofOfFaceModule::verify_identity(
			RuntimeOrigin::signed(verifier),
			non_existent_hash
		));

		// Check that the correct event was emitted
		// The event should indicate failed verification (false)
		System::assert_last_event(
			Event::VerificationPerformed(non_existent_hash, false).into(),
		);
	});
}

#[test]
fn verify_identity_creates_audit_trail() {
	new_test_ext().execute_with(|| {
		// This test demonstrates the audit trail concept
		// Multiple verification attempts should create multiple events
		
		System::set_block_number(1);

		let identity_owner = 1u64;
		let verifier_1 = 2u64;
		let verifier_2 = 3u64;
		let biometric_hash = test_biometric_hash(1);
		let ipfs_cid = test_ipfs_cid("QmTestHash123456789abcdef");

		// Register an identity
		assert_ok!(ProofOfFaceModule::register_identity(
			RuntimeOrigin::signed(identity_owner),
			biometric_hash,
			ipfs_cid
		));

		// Multiple verifiers can verify the same identity
		// Each creates an audit event
		assert_ok!(ProofOfFaceModule::verify_identity(
			RuntimeOrigin::signed(verifier_1),
			biometric_hash
		));

		assert_ok!(ProofOfFaceModule::verify_identity(
			RuntimeOrigin::signed(verifier_2),
			biometric_hash
		));

		// Both verifications should have succeeded
		// The events create an immutable audit trail of who verified when
		let events = System::events();
		
		// Should have 3 events: 1 registration + 2 verifications
		assert_eq!(events.len(), 3);
		
		// Check the verification events
		assert!(matches!(
			events[1].event,
			RuntimeEvent::ProofOfFaceModule(Event::VerificationPerformed(_, true))
		));
		assert!(matches!(
			events[2].event,
			RuntimeEvent::ProofOfFaceModule(Event::VerificationPerformed(_, true))
		));
	});
}

#[test]
fn verify_identity_fails_with_unsigned_origin() {
	new_test_ext().execute_with(|| {
		let biometric_hash = test_biometric_hash(1);

		// Try to verify without signed origin - should fail
		assert_noop!(
			ProofOfFaceModule::verify_identity(
				RuntimeOrigin::none(),
				biometric_hash
			),
			sp_runtime::DispatchError::BadOrigin
		);
	});
}

#[test]
fn verify_identity_works_after_identity_deactivation() {
	new_test_ext().execute_with(|| {
		// This test shows that verification still works even if identity is deactivated
		// The biometric hash remains in storage, only the is_active flag changes
		
		System::set_block_number(1);

		let identity_owner = 1u64;
		let verifier = 2u64;
		let biometric_hash = test_biometric_hash(1);
		let ipfs_cid = test_ipfs_cid("QmTestHash123456789abcdef");

		// Register identity
		assert_ok!(ProofOfFaceModule::register_identity(
			RuntimeOrigin::signed(identity_owner),
			biometric_hash,
			ipfs_cid
		));

		// Deactivate the identity
		assert_ok!(ProofOfFaceModule::deactivate_identity(
			RuntimeOrigin::signed(identity_owner)
		));

		// Verification should still work (hash still exists in BiometricHashToOwner)
		assert_ok!(ProofOfFaceModule::verify_identity(
			RuntimeOrigin::signed(verifier),
			biometric_hash
		));

		// Should emit successful verification event
		System::assert_last_event(
			Event::VerificationPerformed(biometric_hash, true).into(),
		);
	});
}

#[test]
fn verify_identity_multiple_hashes_same_session() {
	new_test_ext().execute_with(|| {
		// Test verifying multiple different hashes in the same session
		// This simulates batch verification scenarios
		
		System::set_block_number(1);

		let identity_owner_1 = 1u64;
		let identity_owner_2 = 2u64;
		let verifier = 3u64;
		
		let biometric_hash_1 = test_biometric_hash(1);
		let biometric_hash_2 = test_biometric_hash(2);
		let non_existent_hash = test_biometric_hash(99);
		
		let ipfs_cid_1 = test_ipfs_cid("QmTestHash1");
		let ipfs_cid_2 = test_ipfs_cid("QmTestHash2");

		// Register two identities
		assert_ok!(ProofOfFaceModule::register_identity(
			RuntimeOrigin::signed(identity_owner_1),
			biometric_hash_1,
			ipfs_cid_1
		));

		assert_ok!(ProofOfFaceModule::register_identity(
			RuntimeOrigin::signed(identity_owner_2),
			biometric_hash_2,
			ipfs_cid_2
		));

		// Verify all three hashes (2 existing, 1 non-existent)
		assert_ok!(ProofOfFaceModule::verify_identity(
			RuntimeOrigin::signed(verifier),
			biometric_hash_1
		));

		assert_ok!(ProofOfFaceModule::verify_identity(
			RuntimeOrigin::signed(verifier),
			biometric_hash_2
		));

		assert_ok!(ProofOfFaceModule::verify_identity(
			RuntimeOrigin::signed(verifier),
			non_existent_hash
		));

		// Check events - should have 2 registrations + 3 verifications = 5 events
		let events = System::events();
		assert_eq!(events.len(), 5);

		// Check verification results
		assert!(matches!(
			events[2].event,
			RuntimeEvent::ProofOfFaceModule(Event::VerificationPerformed(_, true))
		));
		assert!(matches!(
			events[3].event,
			RuntimeEvent::ProofOfFaceModule(Event::VerificationPerformed(_, true))
		));
		assert!(matches!(
			events[4].event,
			RuntimeEvent::ProofOfFaceModule(Event::VerificationPerformed(_, false))
		));
	});
}
