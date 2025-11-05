"""
Encryption utilities for ProofOfFace AI Service
Handles encryption/decryption of sensitive data like face encodings
"""

import base64
import json
import numpy as np
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Union, Dict, Any, Optional
import logging
import os

logger = logging.getLogger(__name__)


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


def generate_encryption_key() -> str:
    """
    Generate a new encryption key
    
    Returns:
        str: Base64-encoded encryption key
    """
    return Fernet.generate_key().decode()


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