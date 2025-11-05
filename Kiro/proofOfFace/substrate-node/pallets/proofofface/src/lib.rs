#![cfg_attr(not(feature = "std"), no_std)]

/// ProofOfFace Identity Verification Pallet
///
/// This pallet provides functionality for:
/// - Registering biometric proofs (face identities) on-chain
/// - Verifying face matches against registered identities
/// - Managing disputes and resolution
/// - Reverse lookup capabilities for biometric hashes

pub use pallet::*;

#[cfg(test)]
mod mock;

#[cfg(test)]
mod tests;

#[cfg(feature = "runtime-benchmarks")]
mod benchmarking;

pub mod weights;
pub use weights::*;

#[frame_support::pallet]
pub mod pallet {
	use super::*;
	use frame_support::{
		dispatch::DispatchResultWithPostInfo,
		pallet_prelude::*,
		traits::{Get, Randomness},
	};
	use frame_system::pallet_prelude::*;
	
	

	#[pallet::pallet]
	pub struct Pallet<T>(_);

	/// Configure the pallet by specifying the parameters and types on which it depends.
	#[pallet::config]
	pub trait Config: frame_system::Config {
		/// Because this pallet emits events, it depends on the runtime's definition of an event.
		type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;

		/// Type representing the weight of this pallet
		type WeightInfo: WeightInfo;

		/// The maximum length of an IPFS CID
		#[pallet::constant]
		type MaxIpfsCidLength: Get<u32>;

		/// The maximum length of evidence URL
		#[pallet::constant]
		type MaxEvidenceUrlLength: Get<u32>;

		/// Randomness source for generating unique IDs
		type Randomness: Randomness<Self::Hash, BlockNumberFor<Self>>;
	}

	/// Biometric proof structure containing face identity data
	#[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
	pub struct BiometricProof<AccountId, Hash, BlockNumber> {
		/// Owner of the biometric proof
		pub owner: AccountId,
		/// SHA-256 hash of face embeddings
		pub biometric_hash: Hash,
		/// IPFS content identifier for stored face data
		pub ipfs_cid: BoundedVec<u8, ConstU32<100>>,
		/// Block number when proof was created
		pub timestamp: BlockNumber,
		/// Whether the proof is currently active
		pub is_active: bool,
	}

	/// Dispute structure for challenging biometric proofs
	#[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
	pub struct Dispute<AccountId, Hash, BlockNumber> {
		/// Unique dispute identifier
		pub dispute_id: u64,
		/// Hash of the face proof being disputed
		pub face_proof_id: Hash,
		/// Account that created the dispute
		pub creator: AccountId,
		/// URL to evidence supporting the dispute
		pub evidence_url: BoundedVec<u8, ConstU32<256>>,
		/// Number of votes supporting the dispute
		pub votes_for: u32,
		/// Number of votes against the dispute
		pub votes_against: u32,
		/// Current status of the dispute
		pub status: DisputeStatus,
		/// Block number when dispute was created
		pub created_at: BlockNumber,
	}

	/// Dispute status enumeration
	#[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
	pub enum DisputeStatus {
		/// Dispute is pending resolution
		Pending,
		/// Dispute has been resolved (accepted)
		Resolved,
		/// Dispute has been rejected
		Rejected,
	}

	// Storage for identity proofs mapped by account ID
	#[pallet::storage]
	#[pallet::getter(fn identity_proofs)]
	pub type IdentityProofs<T: Config> = StorageMap<
		_,
		Blake2_128Concat,
		T::AccountId,
		BiometricProof<T::AccountId, T::Hash, BlockNumberFor<T>>,
		OptionQuery,
	>;

	/// Reverse lookup: biometric hash to owner account
	#[pallet::storage]
	#[pallet::getter(fn biometric_hash_to_owner)]
	pub type BiometricHashToOwner<T: Config> = StorageMap<
		_,
		Blake2_128Concat,
		T::Hash,
		T::AccountId,
		OptionQuery,
	>;

	/// Storage for disputes mapped by dispute ID
	#[pallet::storage]
	#[pallet::getter(fn disputes)]
	pub type Disputes<T: Config> = StorageMap<
		_,
		Blake2_128Concat,
		u64,
		Dispute<T::AccountId, T::Hash, BlockNumberFor<T>>,
		OptionQuery,
	>;

	/// Counter for generating unique dispute IDs
	#[pallet::storage]
	#[pallet::getter(fn next_dispute_id)]
	pub type NextDisputeId<T: Config> = StorageValue<_, u64, ValueQuery>;

	/// Tracking votes per dispute per account to prevent double voting
	#[pallet::storage]
	#[pallet::getter(fn dispute_votes)]
	pub type DisputeVotes<T: Config> = StorageDoubleMap<
		_,
		Blake2_128Concat,
		u64, // Dispute ID
		Blake2_128Concat,
		T::AccountId, // Voter
		bool, // Vote (true = for, false = against)
		OptionQuery,
	>;

	// Pallets use events to inform users when important changes are made.
	#[pallet::event]
	#[pallet::generate_deposit(pub(super) fn deposit_event)]
	pub enum Event<T: Config> {
		/// Identity registered successfully
		/// [account_id, biometric_hash]
		IdentityRegistered(T::AccountId, T::Hash),
		
		/// Verification performed against a biometric hash
		/// [biometric_hash, verification_result]
		VerificationPerformed(T::Hash, bool),
		
		/// Dispute created against an identity
		/// [dispute_id, creator_account]
		DisputeCreated(u64, T::AccountId),
		
		/// Vote cast on a dispute
		/// [dispute_id, voter_account, vote_for]
		DisputeVoted(u64, T::AccountId, bool),
		
		/// Dispute resolved with final status
		/// [dispute_id, final_status]
		DisputeResolved(u64, DisputeStatus),
	}

	// Errors inform users that something went wrong.
	#[pallet::error]
	pub enum Error<T> {
		/// Identity already exists for this account
		IdentityAlreadyExists,
		/// Identity not found
		IdentityNotFound,
		/// Invalid biometric hash format or content (hash already registered to another account)
		InvalidBiometricHash,
		/// Dispute not found
		DisputeNotFound,
		/// Not authorized to perform this action
		NotAuthorized,
		/// Dispute has already been resolved
		DisputeAlreadyResolved,
		/// Account has already voted on this dispute
		AlreadyVoted,
		/// Cannot dispute your own identity
		CannotDisputeOwnIdentity,
		/// Invalid IPFS CID format or empty CID
		InvalidIpfsCid,
		/// Invalid evidence URL format
		InvalidEvidenceUrl,
	}
	
	// Dispatchable functions allow users to interact with the pallet and invoke state changes.
	#[pallet::call]
	impl<T: Config> Pallet<T> {
		/// Register a new biometric proof (face identity)
		///
		/// This function allows users to register their face identity on-chain by providing
		/// a biometric hash (SHA-256 of face embeddings) and an IPFS CID pointing to
		/// the encrypted face data stored off-chain.
		///
		/// # Parameters
		/// - `origin`: The account registering the identity (must be signed)
		/// - `biometric_hash`: SHA-256 hash of the face embeddings
		/// - `ipfs_cid`: IPFS Content Identifier for the stored face data
		///
		/// # Errors
		/// - `IdentityAlreadyExists`: If the account already has a registered identity
		/// - `InvalidBiometricHash`: If the biometric hash is already registered to another account
		/// - `InvalidIpfsCid`: If the IPFS CID is empty or invalid format
		#[pallet::call_index(0)]
		#[pallet::weight(10_000)]
		pub fn register_identity(
			origin: OriginFor<T>,
			biometric_hash: T::Hash,
			ipfs_cid: BoundedVec<u8, ConstU32<100>>,
		) -> DispatchResult {
			// Step 1: Ensure the origin is signed and get the AccountId
			let who = ensure_signed(origin)?;

			// Step 2: Check if user already has a registered identity
			// This prevents users from registering multiple identities with the same account
			ensure!(
				!IdentityProofs::<T>::contains_key(&who),
				Error::<T>::IdentityAlreadyExists
			);

			// Step 3: Check if biometric_hash already exists in the system
			// This prevents duplicate registrations of the same biometric data
			ensure!(
				!BiometricHashToOwner::<T>::contains_key(&biometric_hash),
				Error::<T>::InvalidBiometricHash
			);

			// Step 4: Validate that ipfs_cid is not empty
			// An empty IPFS CID would indicate no actual face data is stored
			ensure!(!ipfs_cid.is_empty(), Error::<T>::InvalidIpfsCid);

			// Step 5: Get current block number for timestamp
			// This provides an immutable record of when the identity was registered
			let current_block = <frame_system::Pallet<T>>::block_number();

			// Step 6: Create BiometricProof struct with all required data
			let biometric_proof = BiometricProof {
				owner: who.clone(),
				biometric_hash,
				ipfs_cid,
				timestamp: current_block,
				is_active: true, // New identities are active by default
			};

			// Step 7: Store the proof in IdentityProofs storage
			// This creates the primary mapping from AccountId to BiometricProof
			IdentityProofs::<T>::insert(&who, &biometric_proof);

			// Step 8: Store reverse mapping in BiometricHashToOwner
			// This enables efficient lookup of identity owner by biometric hash
			BiometricHashToOwner::<T>::insert(&biometric_hash, &who);

			// Step 9: Emit IdentityRegistered event
			// This notifies external systems (frontend, indexers) of the registration
			Self::deposit_event(Event::IdentityRegistered(who, biometric_hash));

			// Step 10: Return success
			Ok(())
		}

		/// Perform verification against a registered biometric hash
		///
		/// This function checks if a given biometric hash exists in the system and emits
		/// an audit event with the verification result. This is primarily used by the AI
		/// service to verify face matches against registered identities.
		///
		/// # Audit Trail Concept
		/// Even though this is essentially a read operation, we emit events to create
		/// an immutable audit trail of all verification attempts. This serves multiple purposes:
		/// - Compliance: Regulatory requirements for identity verification logging
		/// - Security: Detection of potential brute force or enumeration attacks
		/// - Analytics: Understanding verification patterns and system usage
		/// - Transparency: Users can see when their identity was used for verification
		///
		/// # Parameters
		/// - `origin`: The account performing the verification (must be signed)
		/// - `biometric_hash`: The biometric hash to verify against registered identities
		///
		/// # Returns
		/// Always returns `Ok(())` - verification failure is not an error, just no match
		///
		/// # Events
		/// - `VerificationPerformed(biometric_hash, true)`: If hash exists in system
		/// - `VerificationPerformed(biometric_hash, false)`: If hash not found
		#[pallet::call_index(1)]
		#[pallet::weight(10_000)]
		pub fn verify_identity(
			origin: OriginFor<T>,
			biometric_hash: T::Hash,
		) -> DispatchResult {
			// Step 1: Ensure origin is signed
			// We require a signed transaction to create accountability for verification attempts
			let _who = ensure_signed(origin)?;

			// Step 2: Check if biometric_hash exists in BiometricHashToOwner storage
			// This is the core verification logic - does this biometric hash belong to any registered identity?
			let verification_result = BiometricHashToOwner::<T>::contains_key(&biometric_hash);

			// Step 3 & 4: Emit audit event based on verification result
			// This creates an immutable record of the verification attempt on the blockchain
			// The event includes both the hash being verified and whether it was found
			if verification_result {
				// Hash found - successful verification
				Self::deposit_event(Event::VerificationPerformed(biometric_hash, true));
			} else {
				// Hash not found - no matching identity
				Self::deposit_event(Event::VerificationPerformed(biometric_hash, false));
			}

			// Always return Ok(()) - verification failure is not an error condition
			// The caller can determine success/failure from the emitted event
			Ok(())
		}

		/// Create a dispute against a biometric proof
		#[pallet::call_index(2)]
		#[pallet::weight(10_000)]
		pub fn create_dispute(
			origin: OriginFor<T>,
			face_proof_id: T::Hash,
			evidence_url: BoundedVec<u8, ConstU32<256>>,
		) -> DispatchResult {
			// 1. Ensure origin is signed
			let who = ensure_signed(origin)?;

			// 2. Verify the face_proof_id exists (caller must own it)
			let _owner = BiometricHashToOwner::<T>::get(&face_proof_id)
				.ok_or(Error::<T>::IdentityNotFound)?;

			// 3. Get next dispute ID from NextDisputeId storage
			let dispute_id = NextDisputeId::<T>::get();

			// 4. Create Dispute struct with status: Pending
			let dispute = Dispute {
				dispute_id,
				face_proof_id,
				creator: who.clone(),
				evidence_url,
				votes_for: 0,
				votes_against: 0,
				status: DisputeStatus::Pending,
				created_at: <frame_system::Pallet<T>>::block_number(),
			};

			// 5. Store in Disputes storage
			Disputes::<T>::insert(dispute_id, &dispute);

			// 6. Increment NextDisputeId
			NextDisputeId::<T>::put(dispute_id + 1);

			// 7. Emit DisputeCreated event
			Self::deposit_event(Event::DisputeCreated(dispute_id, who));

			Ok(())
		}

		/// Vote on an open dispute
		#[pallet::call_index(3)]
		#[pallet::weight(10_000)]
		pub fn vote_on_dispute(
			origin: OriginFor<T>,
			dispute_id: u64,
			vote: bool, // true = agree it's unauthorized, false = disagree
		) -> DispatchResultWithPostInfo {
			let who = ensure_signed(origin)?;

			// Get dispute info
			let mut dispute = Disputes::<T>::get(dispute_id)
				.ok_or(Error::<T>::DisputeNotFound)?;

			// Ensure dispute is still pending
			ensure!(
				matches!(dispute.status, DisputeStatus::Pending),
				Error::<T>::DisputeAlreadyResolved
			);

			// Ensure hasn't already voted
			ensure!(
				!DisputeVotes::<T>::contains_key(dispute_id, &who),
				Error::<T>::AlreadyVoted
			);

			// Record the vote
			DisputeVotes::<T>::insert(dispute_id, &who, vote);

			// Update vote counts
			if vote {
				dispute.votes_for = dispute.votes_for.saturating_add(1);
			} else {
				dispute.votes_against = dispute.votes_against.saturating_add(1);
			}

			// Check if dispute should be resolved (simple majority with minimum 10 votes)
			let total_votes = dispute.votes_for + dispute.votes_against;
			if total_votes >= 10u32 {
				if dispute.votes_for > dispute.votes_against {
					dispute.status = DisputeStatus::Resolved;
					
					// Deactivate the disputed biometric proof
					if let Some(owner) = BiometricHashToOwner::<T>::get(&dispute.face_proof_id) {
						if let Some(mut proof) = IdentityProofs::<T>::get(&owner) {
							proof.is_active = false;
							IdentityProofs::<T>::insert(&owner, &proof);
						}
					}
				} else {
					dispute.status = DisputeStatus::Rejected;
				}
				
				Self::deposit_event(Event::DisputeResolved(dispute_id, dispute.status.clone()));
			}

			// Store updated dispute
			Disputes::<T>::insert(dispute_id, &dispute);

			// Emit vote event
			Self::deposit_event(Event::DisputeVoted(dispute_id, who, vote));

			Ok(().into())
		}
	
		/// Deactivate a biometric proof (only by owner)
		#[pallet::call_index(4)]
		#[pallet::weight(T::WeightInfo::register_identity())]
		pub fn deactivate_identity(
			origin: OriginFor<T>,
		) -> DispatchResultWithPostInfo {
			let who = ensure_signed(origin)?;

			// Get the identity proof
			let mut proof = IdentityProofs::<T>::get(&who)
				.ok_or(Error::<T>::IdentityNotFound)?;

			// Deactivate the proof
			proof.is_active = false;
			IdentityProofs::<T>::insert(&who, &proof);

			Ok(().into())
		}

		/// Reactivate a biometric proof (only by owner)
		#[pallet::call_index(5)]
		#[pallet::weight(T::WeightInfo::register_identity())]
		pub fn reactivate_identity(
			origin: OriginFor<T>,
		) -> DispatchResultWithPostInfo {
			let who = ensure_signed(origin)?;

			// Get the identity proof
			let mut proof = IdentityProofs::<T>::get(&who)
				.ok_or(Error::<T>::IdentityNotFound)?;

			// Reactivate the proof
			proof.is_active = true;
			IdentityProofs::<T>::insert(&who, &proof);



			Ok(().into())
		}
	}

	// Helper functions for querying
	impl<T: Config> Pallet<T> {
		/// Get biometric proof by account ID
		pub fn get_identity_proof(account: &T::AccountId) -> Option<BiometricProof<T::AccountId, T::Hash, BlockNumberFor<T>>> {
			IdentityProofs::<T>::get(account)
		}

		/// Get owner by biometric hash
		pub fn get_owner_by_hash(hash: &T::Hash) -> Option<T::AccountId> {
			BiometricHashToOwner::<T>::get(hash)
		}

		/// Check if identity is active
		pub fn is_identity_active(account: &T::AccountId) -> bool {
			if let Some(proof) = IdentityProofs::<T>::get(account) {
				proof.is_active
			} else {
				false
			}
		}

		/// Get dispute by ID
		pub fn get_dispute(dispute_id: u64) -> Option<Dispute<T::AccountId, T::Hash, BlockNumberFor<T>>> {
			Disputes::<T>::get(dispute_id)
		}

		/// Check if account has voted on dispute
		pub fn has_voted(dispute_id: u64, account: &T::AccountId) -> bool {
			DisputeVotes::<T>::contains_key(dispute_id, account)
		}
	}
}
