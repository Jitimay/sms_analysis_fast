"""
Encryption utilities for ProofOfFace AI Service
Handles encryption/decryption of sensitive data like face encodings and embeddings
"""

import base64
import json
import numpy as np
import secrets
import struct
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
from typing import Union, Dict, Any, Optional, List
import logging
import os

logger = logging.getLogger(__name__)


class EmbeddingEncryptor:
    """
    Advanced encryption class for face embeddings using AES-256-GCM
    
    Features:
    - AES-256-GCM encryption for authenticated encryption
    - PBKDF2 key derivation with configurable iterations
    - Secure salt generation and storage
    - Base64 encoding for safe transport
    - Comprehensive error handling
    """
    
    # Security constants
    SALT_SIZE = 32  # 256 bits
    NONCE_SIZE = 12  # 96 bits for GCM
    KEY_SIZE = 32   # 256 bits
    PBKDF2_ITERATIONS = 100000  # OWASP recommended minimum
    
    def __init__(self, iterations: int = PBKDF2_ITERATIONS):
        """
        Initialize the embedding encryptor
        
        Args:
            iterations: Number of PBKDF2 iterations (default: 100,000)
        """
        self.iterations = iterations
        logger.info(f"EmbeddingEncryptor initialized with {iterations} PBKDF2 iterations")
    
    def generate_key(self) -> str:
        """
        Generate a random secure encryption key
        
        Returns:
            str: 64-character hex string (256-bit key)
        """
        try:
            # Generate 256-bit (32-byte) random key
            key_bytes = secrets.token_bytes(self.KEY_SIZE)
            key_hex = key_bytes.hex()
            
            logger.info("New encryption key generated")
            return key_hex
            
        except Exception as e:
            logger.error(f"Key generation failed: {str(e)}")
            raise RuntimeError(f"Failed to generate encryption key: {str(e)}")
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """
        Derive encryption key from password using PBKDF2
        
        Args:
            password: User password
            salt: Random salt bytes
            
        Returns:
            bytes: Derived 256-bit key
        """
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=self.KEY_SIZE,
                salt=salt,
                iterations=self.iterations,
                backend=default_backend()
            )
            
            derived_key = kdf.derive(password.encode('utf-8'))
            logger.debug("Key derived successfully from password")
            return derived_key
            
        except Exception as e:
            logger.error(f"Key derivation failed: {str(e)}")
            raise ValueError(f"Failed to derive key from password: {str(e)}")
    
    def encrypt_embeddings(self, embeddings: List[float], password: str) -> str:
        """
        Encrypt face embeddings using AES-256-GCM
        
        Args:
            embeddings: List of 128 float values representing face embeddings
            password: Password for encryption
            
        Returns:
            str: Base64-encoded encrypted string containing salt, nonce, and ciphertext
            
        Raises:
            ValueError: If embeddings format is invalid
            RuntimeError: If encryption fails
        """
        try:
            # Validate embeddings
            if not isinstance(embeddings, list):
                raise ValueError("Embeddings must be a list")
            
            if len(embeddings) != 128:
                raise ValueError(f"Embeddings must contain exactly 128 values, got {len(embeddings)}")
            
            # Validate all values are numbers
            for i, value in enumerate(embeddings):
                if not isinstance(value, (int, float)):
                    raise ValueError(f"All embedding values must be numbers, found {type(value).__name__} at index {i}")
                if np.isnan(value) or np.isinf(value):
                    raise ValueError(f"Invalid embedding value (NaN or Inf) at index {i}")
            
            # Convert embeddings to bytes
            # Pack as 128 double-precision floats (8 bytes each)
            embeddings_bytes = struct.pack('128d', *embeddings)
            
            # Generate random salt and nonce
            salt = secrets.token_bytes(self.SALT_SIZE)
            nonce = secrets.token_bytes(self.NONCE_SIZE)
            
            # Derive key from password
            key = self._derive_key(password, salt)
            
            # Encrypt using AES-256-GCM
            aesgcm = AESGCM(key)
            ciphertext = aesgcm.encrypt(nonce, embeddings_bytes, None)
            
            # Combine salt + nonce + ciphertext
            encrypted_data = salt + nonce + ciphertext
            
            # Encode as base64 for safe transport
            encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
            
            logger.info("Embeddings encrypted successfully")
            return encrypted_b64
            
        except ValueError as e:
            logger.error(f"Embedding validation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise RuntimeError(f"Failed to encrypt embeddings: {str(e)}")
    
    def decrypt_embeddings(self, encrypted_str: str, password: str) -> List[float]:
        """
        Decrypt face embeddings using AES-256-GCM
        
        Args:
            encrypted_str: Base64-encoded encrypted string
            password: Password for decryption
            
        Returns:
            List[float]: List of 128 float values representing face embeddings
            
        Raises:
            ValueError: If encrypted string format is invalid or password is wrong
            RuntimeError: If decryption fails
        """
        try:
            # Validate input
            if not isinstance(encrypted_str, str):
                raise ValueError("Encrypted string must be a string")
            
            if not encrypted_str:
                raise ValueError("Encrypted string cannot be empty")
            
            # Decode base64
            try:
                encrypted_data = base64.b64decode(encrypted_str.encode('utf-8'))
            except Exception as e:
                raise ValueError(f"Invalid base64 encoding: {str(e)}")
            
            # Validate minimum size (salt + nonce + at least some ciphertext)
            min_size = self.SALT_SIZE + self.NONCE_SIZE + 16  # 16 bytes for GCM tag
            if len(encrypted_data) < min_size:
                raise ValueError(f"Encrypted data too short, expected at least {min_size} bytes")
            
            # Extract salt, nonce, and ciphertext
            salt = encrypted_data[:self.SALT_SIZE]
            nonce = encrypted_data[self.SALT_SIZE:self.SALT_SIZE + self.NONCE_SIZE]
            ciphertext = encrypted_data[self.SALT_SIZE + self.NONCE_SIZE:]
            
            # Derive key from password
            key = self._derive_key(password, salt)
            
            # Decrypt using AES-256-GCM
            aesgcm = AESGCM(key)
            try:
                embeddings_bytes = aesgcm.decrypt(nonce, ciphertext, None)
            except Exception as e:
                # This typically means wrong password or corrupted data
                raise ValueError("Decryption failed - incorrect password or corrupted data")
            
            # Validate decrypted data size
            expected_size = 128 * 8  # 128 doubles, 8 bytes each
            if len(embeddings_bytes) != expected_size:
                raise ValueError(f"Decrypted data size mismatch, expected {expected_size} bytes, got {len(embeddings_bytes)}")
            
            # Unpack embeddings from bytes
            embeddings = list(struct.unpack('128d', embeddings_bytes))
            
            # Validate unpacked embeddings
            for i, value in enumerate(embeddings):
                if np.isnan(value) or np.isinf(value):
                    raise ValueError(f"Invalid embedding value after decryption at index {i}")
            
            logger.info("Embeddings decrypted successfully")
            return embeddings
            
        except ValueError as e:
            logger.error(f"Decryption validation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise RuntimeError(f"Failed to decrypt embeddings: {str(e)}")
    
    def encrypt_embeddings_with_key(self, embeddings: List[float], key_hex: str) -> str:
        """
        Encrypt embeddings using a hex-encoded key directly (no password derivation)
        
        Args:
            embeddings: List of 128 float values
            key_hex: 64-character hex string (256-bit key)
            
        Returns:
            str: Base64-encoded encrypted string
        """
        try:
            # Validate key format
            if not isinstance(key_hex, str) or len(key_hex) != 64:
                raise ValueError("Key must be a 64-character hex string")
            
            try:
                key_bytes = bytes.fromhex(key_hex)
            except ValueError:
                raise ValueError("Key must be valid hexadecimal")
            
            if len(key_bytes) != self.KEY_SIZE:
                raise ValueError(f"Key must be {self.KEY_SIZE} bytes ({self.KEY_SIZE * 2} hex characters)")
            
            # Validate embeddings
            if not isinstance(embeddings, list) or len(embeddings) != 128:
                raise ValueError("Embeddings must be a list of 128 float values")
            
            # Convert embeddings to bytes
            embeddings_bytes = struct.pack('128d', *embeddings)
            
            # Generate random nonce
            nonce = secrets.token_bytes(self.NONCE_SIZE)
            
            # Encrypt using AES-256-GCM
            aesgcm = AESGCM(key_bytes)
            ciphertext = aesgcm.encrypt(nonce, embeddings_bytes, None)
            
            # Combine nonce + ciphertext (no salt needed since key is provided directly)
            encrypted_data = nonce + ciphertext
            
            # Encode as base64
            encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
            
            logger.info("Embeddings encrypted with direct key")
            return encrypted_b64
            
        except ValueError as e:
            logger.error(f"Direct key encryption validation failed: {str(e)}")
            raise  # Re-raise ValueError as-is
        except Exception as e:
            logger.error(f"Direct key encryption failed: {str(e)}")
            raise RuntimeError(f"Failed to encrypt embeddings with key: {str(e)}")
    
    def decrypt_embeddings_with_key(self, encrypted_str: str, key_hex: str) -> List[float]:
        """
        Decrypt embeddings using a hex-encoded key directly
        
        Args:
            encrypted_str: Base64-encoded encrypted string
            key_hex: 64-character hex string (256-bit key)
            
        Returns:
            List[float]: List of 128 float values
        """
        try:
            # Validate key format
            if not isinstance(key_hex, str) or len(key_hex) != 64:
                raise ValueError("Key must be a 64-character hex string")
            
            try:
                key_bytes = bytes.fromhex(key_hex)
            except ValueError:
                raise ValueError("Key must be valid hexadecimal")
            
            # Decode base64
            encrypted_data = base64.b64decode(encrypted_str.encode('utf-8'))
            
            # Extract nonce and ciphertext
            nonce = encrypted_data[:self.NONCE_SIZE]
            ciphertext = encrypted_data[self.NONCE_SIZE:]
            
            # Decrypt using AES-256-GCM
            aesgcm = AESGCM(key_bytes)
            embeddings_bytes = aesgcm.decrypt(nonce, ciphertext, None)
            
            # Unpack embeddings
            embeddings = list(struct.unpack('128d', embeddings_bytes))
            
            logger.info("Embeddings decrypted with direct key")
            return embeddings
            
        except Exception as e:
            logger.error(f"Direct key decryption failed: {str(e)}")
            raise RuntimeError(f"Failed to decrypt embeddings with key: {str(e)}")
    
    def change_password(self, encrypted_str: str, old_password: str, new_password: str) -> str:
        """
        Change the password for encrypted embeddings
        
        Args:
            encrypted_str: Currently encrypted embeddings
            old_password: Current password
            new_password: New password
            
        Returns:
            str: Re-encrypted embeddings with new password
        """
        try:
            # Decrypt with old password
            embeddings = self.decrypt_embeddings(encrypted_str, old_password)
            
            # Re-encrypt with new password
            new_encrypted = self.encrypt_embeddings(embeddings, new_password)
            
            logger.info("Password changed successfully for encrypted embeddings")
            return new_encrypted
            
        except Exception as e:
            logger.error(f"Password change failed: {str(e)}")
            raise RuntimeError(f"Failed to change password: {str(e)}")
    
    def verify_password(self, encrypted_str: str, password: str) -> bool:
        """
        Verify if a password can decrypt the embeddings
        
        Args:
            encrypted_str: Encrypted embeddings string
            password: Password to verify
            
        Returns:
            bool: True if password is correct, False otherwise
        """
        try:
            self.decrypt_embeddings(encrypted_str, password)
            return True
        except (ValueError, RuntimeError):
            return False


class EncryptionManager:
    """
    Manages encryption and decryption of sensitive data
    
    Features:
    - Symmetric encryption using Fernet (AES 128)
    - Key derivation from passwords
    - Secure encoding/decoding of numpy arrays
    - JSON serialization support
    """
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize encryption manager
        
        Args:
            encryption_key: Base64-encoded encryption key. If None, generates a new key.
        """
        if encryption_key:
            try:
                # Validate and use provided key
                self.key = encryption_key.encode() if isinstance(encryption_key, str) else encryption_key
                self.fernet = Fernet(self.key)
                logger.info("Encryption manager initialized with provided key")
            except Exception as e:
                logger.error(f"Invalid encryption key provided: {str(e)}")
                raise ValueError(f"Invalid encryption key: {str(e)}")
        else:
            # Generate new key
            self.key = Fernet.generate_key()
            self.fernet = Fernet(self.key)
            logger.warning("Generated new encryption key. Save this key securely!")
            logger.info(f"New encryption key: {self.key.decode()}")
    
    def get_key(self) -> str:
        """
        Get the encryption key as a string
        
        Returns:
            str: Base64-encoded encryption key
        """
        return self.key.decode()
    
    @classmethod
    def from_password(cls, password: str, salt: Optional[bytes] = None) -> 'EncryptionManager':
        """
        Create encryption manager from password using key derivation
        
        Args:
            password: Password to derive key from
            salt: Salt for key derivation. If None, generates random salt.
            
        Returns:
            EncryptionManager: Instance with derived key
        """
        if salt is None:
            salt = os.urandom(16)
        
        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        instance = cls(key.decode())
        instance.salt = salt  # Store salt for future use
        
        logger.info("Encryption manager created from password")
        return instance
    
    def encrypt_data(self, data: Union[str, bytes, Dict, np.ndarray]) -> str:
        """
        Encrypt various types of data
        
        Args:
            data: Data to encrypt (string, bytes, dict, or numpy array)
            
        Returns:
            str: Base64-encoded encrypted data
        """
        try:
            # Convert data to bytes based on type
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            elif isinstance(data, bytes):
                data_bytes = data
            elif isinstance(data, dict):
                data_bytes = json.dumps(data).encode('utf-8')
            elif isinstance(data, np.ndarray):
                # Serialize numpy array
                data_dict = {
                    'array_data': data.tolist(),
                    'dtype': str(data.dtype),
                    'shape': data.shape
                }
                data_bytes = json.dumps(data_dict).encode('utf-8')
            else:
                raise ValueError(f"Unsupported data type: {type(data)}")
            
            # Encrypt data
            encrypted_data = self.fernet.encrypt(data_bytes)
            
            # Return base64-encoded encrypted data
            return base64.b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise ValueError(f"Encryption failed: {str(e)}")
    
    def decrypt_data(self, encrypted_data: str, data_type: str = 'auto') -> Union[str, bytes, Dict, np.ndarray]:
        """
        Decrypt data and return in specified format
        
        Args:
            encrypted_data: Base64-encoded encrypted data
            data_type: Expected data type ('string', 'bytes', 'dict', 'numpy', 'auto')
            
        Returns:
            Decrypted data in specified format
        """
        try:
            # Decode base64 and decrypt
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
            
            # Convert back to original format
            if data_type == 'bytes':
                return decrypted_bytes
            elif data_type == 'string':
                return decrypted_bytes.decode('utf-8')
            elif data_type == 'dict':
                return json.loads(decrypted_bytes.decode('utf-8'))
            elif data_type == 'numpy':
                data_dict = json.loads(decrypted_bytes.decode('utf-8'))
                array_data = np.array(data_dict['array_data'], dtype=data_dict['dtype'])
                return array_data.reshape(data_dict['shape'])
            elif data_type == 'auto':
                # Try to auto-detect format
                try:
                    # Try JSON first (dict or numpy array)
                    json_data = json.loads(decrypted_bytes.decode('utf-8'))
                    if isinstance(json_data, dict) and 'array_data' in json_data:
                        # It's a numpy array
                        array_data = np.array(json_data['array_data'], dtype=json_data['dtype'])
                        return array_data.reshape(json_data['shape'])
                    else:
                        # It's a regular dict
                        return json_data
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # Try string
                    try:
                        return decrypted_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        # Return as bytes
                        return decrypted_bytes
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
                
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise ValueError(f"Decryption failed: {str(e)}")
    
    def encrypt_face_encoding(self, face_encoding: np.ndarray) -> str:
        """
        Encrypt face encoding specifically
        
        Args:
            face_encoding: Face encoding numpy array
            
        Returns:
            str: Encrypted face encoding
        """
        if not isinstance(face_encoding, np.ndarray):
            raise ValueError("Face encoding must be a numpy array")
        
        return self.encrypt_data(face_encoding)
    
    def decrypt_face_encoding(self, encrypted_encoding: str) -> np.ndarray:
        """
        Decrypt face encoding specifically
        
        Args:
            encrypted_encoding: Encrypted face encoding string
            
        Returns:
            np.ndarray: Decrypted face encoding
        """
        return self.decrypt_data(encrypted_encoding, data_type='numpy')
    
    def encrypt_json(self, data: Dict[str, Any]) -> str:
        """
        Encrypt JSON data
        
        Args:
            data: Dictionary to encrypt
            
        Returns:
            str: Encrypted JSON data
        """
        return self.encrypt_data(data)
    
    def decrypt_json(self, encrypted_data: str) -> Dict[str, Any]:
        """
        Decrypt JSON data
        
        Args:
            encrypted_data: Encrypted JSON string
            
        Returns:
            Dict: Decrypted dictionary
        """
        return self.decrypt_data(encrypted_data, data_type='dict')


class SecureStorage:
    """
    Secure storage wrapper for sensitive data
    Combines encryption with additional security measures
    """
    
    def __init__(self, encryption_manager: EncryptionManager):
        """
        Initialize secure storage
        
        Args:
            encryption_manager: Encryption manager instance
        """
        self.encryption_manager = encryption_manager
        self.storage = {}  # In-memory storage (use database in production)
        logger.info("Secure storage initialized")
    
    def store_face_encoding(self, identifier: str, face_encoding: np.ndarray, metadata: Optional[Dict] = None) -> bool:
        """
        Securely store face encoding with metadata
        
        Args:
            identifier: Unique identifier for the encoding
            face_encoding: Face encoding to store
            metadata: Optional metadata to store with encoding
            
        Returns:
            bool: True if storage successful
        """
        try:
            # Encrypt face encoding
            encrypted_encoding = self.encryption_manager.encrypt_face_encoding(face_encoding)
            
            # Prepare storage entry
            entry = {
                'encrypted_encoding': encrypted_encoding,
                'metadata': metadata or {},
                'timestamp': np.datetime64('now').isoformat()
            }
            
            # Store entry
            self.storage[identifier] = entry
            
            logger.info(f"Face encoding stored for identifier: {identifier}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store face encoding: {str(e)}")
            return False
    
    def retrieve_face_encoding(self, identifier: str) -> Optional[np.ndarray]:
        """
        Retrieve and decrypt face encoding
        
        Args:
            identifier: Unique identifier for the encoding
            
        Returns:
            np.ndarray: Decrypted face encoding or None if not found
        """
        try:
            if identifier not in self.storage:
                logger.warning(f"Face encoding not found for identifier: {identifier}")
                return None
            
            entry = self.storage[identifier]
            encrypted_encoding = entry['encrypted_encoding']
            
            # Decrypt and return face encoding
            face_encoding = self.encryption_manager.decrypt_face_encoding(encrypted_encoding)
            
            logger.debug(f"Face encoding retrieved for identifier: {identifier}")
            return face_encoding
            
        except Exception as e:
            logger.error(f"Failed to retrieve face encoding: {str(e)}")
            return None
    
    def delete_face_encoding(self, identifier: str) -> bool:
        """
        Delete stored face encoding
        
        Args:
            identifier: Unique identifier for the encoding
            
        Returns:
            bool: True if deletion successful
        """
        try:
            if identifier in self.storage:
                del self.storage[identifier]
                logger.info(f"Face encoding deleted for identifier: {identifier}")
                return True
            else:
                logger.warning(f"Face encoding not found for deletion: {identifier}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete face encoding: {str(e)}")
            return False
    
    def list_identifiers(self) -> list:
        """
        List all stored identifiers
        
        Returns:
            list: List of stored identifiers
        """
        return list(self.storage.keys())


# Utility functions
def create_encryption_manager(key: Optional[str] = None) -> EncryptionManager:
    """
    Factory function to create encryption manager
    
    Args:
        key: Optional encryption key
        
    Returns:
        EncryptionManager: Configured encryption manager
    """
    return EncryptionManager(key)


def create_embedding_encryptor(iterations: int = 100000) -> EmbeddingEncryptor:
    """
    Factory function to create embedding encryptor
    
    Args:
        iterations: Number of PBKDF2 iterations
        
    Returns:
        EmbeddingEncryptor: Configured embedding encryptor
    """
    return EmbeddingEncryptor(iterations)


def generate_encryption_key() -> str:
    """
    Generate a new encryption key (Fernet compatible)
    
    Returns:
        str: Base64-encoded encryption key
    """
    return Fernet.generate_key().decode()


def generate_embedding_key() -> str:
    """
    Generate a new encryption key for embeddings (AES-256)
    
    Returns:
        str: 64-character hex string (256-bit key)
    """
    encryptor = EmbeddingEncryptor()
    return encryptor.generate_key()


def encrypt_face_encoding(face_encoding: np.ndarray, encryption_key: str) -> str:
    """
    Convenience function to encrypt face encoding
    
    Args:
        face_encoding: Face encoding to encrypt
        encryption_key: Encryption key
        
    Returns:
        str: Encrypted face encoding
    """
    manager = EncryptionManager(encryption_key)
    return manager.encrypt_face_encoding(face_encoding)


def decrypt_face_encoding(encrypted_encoding: str, encryption_key: str) -> np.ndarray:
    """
    Convenience function to decrypt face encoding
    
    Args:
        encrypted_encoding: Encrypted face encoding
        encryption_key: Encryption key
        
    Returns:
        np.ndarray: Decrypted face encoding
    """
    manager = EncryptionManager(encryption_key)
    return manager.decrypt_face_encoding(encrypted_encoding)


def encrypt_embeddings(embeddings: List[float], password: str) -> str:
    """
    Convenience function to encrypt embeddings with password
    
    Args:
        embeddings: List of 128 float values
        password: Password for encryption
        
    Returns:
        str: Encrypted embeddings string
    """
    encryptor = EmbeddingEncryptor()
    return encryptor.encrypt_embeddings(embeddings, password)


def decrypt_embeddings(encrypted_str: str, password: str) -> List[float]:
    """
    Convenience function to decrypt embeddings with password
    
    Args:
        encrypted_str: Encrypted embeddings string
        password: Password for decryption
        
    Returns:
        List[float]: Decrypted embeddings
    """
    encryptor = EmbeddingEncryptor()
    return encryptor.decrypt_embeddings(encrypted_str, password)


def encrypt_embeddings_with_key(embeddings: List[float], key_hex: str) -> str:
    """
    Convenience function to encrypt embeddings with direct key
    
    Args:
        embeddings: List of 128 float values
        key_hex: 64-character hex string
        
    Returns:
        str: Encrypted embeddings string
    """
    encryptor = EmbeddingEncryptor()
    return encryptor.encrypt_embeddings_with_key(embeddings, key_hex)


def decrypt_embeddings_with_key(encrypted_str: str, key_hex: str) -> List[float]:
    """
    Convenience function to decrypt embeddings with direct key
    
    Args:
        encrypted_str: Encrypted embeddings string
        key_hex: 64-character hex string
        
    Returns:
        List[float]: Decrypted embeddings
    """
    encryptor = EmbeddingEncryptor()
    return encryptor.decrypt_embeddings_with_key(encrypted_str, key_hex)