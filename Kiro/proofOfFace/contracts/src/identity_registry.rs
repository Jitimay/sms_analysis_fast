#![cfg_attr(not(feature = "std"), no_std)]

#[ink::contract]
pub mod identity_registry {
    use ink::prelude::string::String;
    use ink::storage::Mapping;

    #[derive(Debug, PartialEq, Eq, Clone)]
    #[ink::scale_derive(Encode, Decode, TypeInfo)]
    #[cfg_attr(feature = "std", derive(ink::storage::traits::StorageLayout))]
    pub struct IdentityData {
        pub ipfs_hash: String,
        pub timestamp: u64,
        pub verified: bool,
        pub reputation_score: u32,
    }

    #[ink(storage)]
    pub struct IdentityRegistry {
        identities: Mapping<AccountId, IdentityData>,
        total_identities: u64,
    }

    impl IdentityRegistry {
        #[ink(constructor)]
        pub fn new() -> Self {
            Self {
                identities: Mapping::default(),
                total_identities: 0,
            }
        }

        #[ink(message)]
        pub fn register_identity(&mut self, ipfs_hash: String) {
            let caller = self.env().caller();
            let identity_data = IdentityData {
                ipfs_hash,
                timestamp: self.env().block_timestamp(),
                verified: false,
                reputation_score: 100,
            };
            self.identities.insert(&caller, &identity_data);
            self.total_identities += 1;
        }

        #[ink(message)]
        pub fn get_total_identities(&self) -> u64 {
            self.total_identities
        }
    }
}