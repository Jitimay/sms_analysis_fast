#!/usr/bin/env python3
"""
Unit tests for EmbeddingEncryptor class
Tests AES-256-GCM encryption of face embeddings
"""

import unittest
import numpy as np
import sys
import os
import secrets
import base64

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.encryption import (
    EmbeddingEncryptor, 
    create_embedding_encryptor,
    generate_embedding_key,
    encrypt_embeddings,
    decrypt_embeddings,
    encrypt_embeddings_with_key,
    decrypt_embeddings_with_key
)


class TestEmbeddingEncryptor(unittest.TestCase):
    """Test cases for EmbeddingEncryptor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.encryptor = EmbeddingEncryptor()
        self.test_password = "test_password_123"
        self.test_embeddings = [float(i) for i in range(128)]  # Simple test embeddings
        self.random_embeddings = np.random.randn(128).tolist()  # Random embeddings
    
    def test_encryptor_initialization(self):
        """Test encryptor initialization"""
        # Default initialization
        encryptor1 = EmbeddingEncryptor()
        self.assertEqual(encryptor1.iterations, 100000)
        
        # Custom iterations
        encryptor2 = EmbeddingEncryptor(iterations=50000)
        self.assertEqual(encryptor2.iterations, 50000)
    
    def test_generate_key(self):
        """Test encryption key generation"""
        key1 = self.encryptor.generate_key()
        key2 = self.encryptor.generate_key()
        
        # Keys should be different
        self.assertNotEqual(key1, key2)
        
        # Keys should be 64-character hex strings
        self.assertEqual(len(key1), 64)
        self.assertEqual(len(key2), 64)
        
        # Keys should be valid hex
        try:
            bytes.fromhex(key1)
            bytes.fromhex(key2)
        except ValueError:
            self.fail("Generated keys are not valid hex strings")
    
    def test_encrypt_decrypt_embeddings_basic(self):
        """Test basic encryption and decryption"""
        encrypted = self.encryptor.encrypt_embeddings(self.test_embeddings, self.test_password)
        decrypted = self.encryptor.decrypt_embeddings(encrypted, self.test_password)
        
        # Should decrypt to original embeddings
        self.assertEqual(len(decrypted), 128)
        for i in range(128):
            self.assertAlmostEqual(decrypted[i], self.test_embeddings[i], places=10)
    
    def test_encrypt_decrypt_random_embeddings(self):
        """Test encryption/decryption with random embeddings"""
        encrypted = self.encryptor.encrypt_embeddings(self.random_embeddings, self.test_password)
        decrypted = self.encryptor.decrypt_embeddings(encrypted, self.test_password)
        
        # Should decrypt to original embeddings
        self.assertEqual(len(decrypted), 128)
        for i in range(128):
            self.assertAlmostEqual(decrypted[i], self.random_embeddings[i], places=10)
    
    def test_different_passwords_produce_different_ciphertext(self):
        """Test that different passwords produce different encrypted results"""
        encrypted1 = self.encryptor.encrypt_embeddings(self.test_embeddings, "password1")
        encrypted2 = self.encryptor.encrypt_embeddings(self.test_embeddings, "password2")
        
        # Different passwords should produce different ciphertext
        self.assertNotEqual(encrypted1, encrypted2)
    
    def test_same_password_different_salt(self):
        """Test that same password produces different ciphertext due to random salt"""
        encrypted1 = self.encryptor.encrypt_embeddings(self.test_embeddings, self.test_password)
        encrypted2 = self.encryptor.encrypt_embeddings(self.test_embeddings, self.test_password)
        
        # Should be different due to random salt and nonce
        self.assertNotEqual(encrypted1, encrypted2)
        
        # But both should decrypt to same result
        decrypted1 = self.encryptor.decrypt_embeddings(encrypted1, self.test_password)
        decrypted2 = self.encryptor.decrypt_embeddings(encrypted2, self.test_password)
        
        for i in range(128):
            self.assertAlmostEqual(decrypted1[i], decrypted2[i], places=10)
    
    def test_wrong_password_fails(self):
        """Test that wrong password fails to decrypt"""
        encrypted = self.encryptor.encrypt_embeddings(self.test_embeddings, "correct_password")
        
        with self.assertRaises(ValueError):
            self.encryptor.decrypt_embeddings(encrypted, "wrong_password")
    
    def test_encrypt_with_direct_key(self):
        """Test encryption/decryption with direct key"""
        key = self.encryptor.generate_key()
        
        encrypted = self.encryptor.encrypt_embeddings_with_key(self.test_embeddings, key)
        decrypted = self.encryptor.decrypt_embeddings_with_key(encrypted, key)
        
        # Should decrypt to original embeddings
        self.assertEqual(len(decrypted), 128)
        for i in range(128):
            self.assertAlmostEqual(decrypted[i], self.test_embeddings[i], places=10)
    
    def test_invalid_embeddings_validation(self):
        """Test validation of invalid embeddings"""
        # Not a list
        with self.assertRaises(ValueError):
            self.encryptor.encrypt_embeddings("not a list", self.test_password)
        
        # Wrong length
        with self.assertRaises(ValueError):
            self.encryptor.encrypt_embeddings([1.0] * 64, self.test_password)
        
        # Non-numeric values
        invalid_embeddings = [1.0] * 127 + ["not a number"]
        with self.assertRaises(ValueError):
            self.encryptor.encrypt_embeddings(invalid_embeddings, self.test_password)
        
        # NaN values
        nan_embeddings = [1.0] * 127 + [float('nan')]
        with self.assertRaises(ValueError):
            self.encryptor.encrypt_embeddings(nan_embeddings, self.test_password)
        
        # Infinite values
        inf_embeddings = [1.0] * 127 + [float('inf')]
        with self.assertRaises(ValueError):
            self.encryptor.encrypt_embeddings(inf_embeddings, self.test_password)
    
    def test_invalid_encrypted_string(self):
        """Test handling of invalid encrypted strings"""
        # Empty string
        with self.assertRaises(ValueError):
            self.encryptor.decrypt_embeddings("", self.test_password)
        
        # Invalid base64
        with self.assertRaises(ValueError):
            self.encryptor.decrypt_embeddings("invalid_base64!", self.test_password)
        
        # Too short data
        short_data = base64.b64encode(b"too_short").decode()
        with self.assertRaises(ValueError):
            self.encryptor.decrypt_embeddings(short_data, self.test_password)
    
    def test_invalid_key_format(self):
        """Test handling of invalid key formats"""
        # Wrong length
        with self.assertRaises(ValueError):
            self.encryptor.encrypt_embeddings_with_key(self.test_embeddings, "short_key")
        
        # Invalid hex
        with self.assertRaises(ValueError):
            self.encryptor.encrypt_embeddings_with_key(self.test_embeddings, "g" * 64)
        
        # Not a string
        with self.assertRaises(ValueError):
            self.encryptor.encrypt_embeddings_with_key(self.test_embeddings, 12345)
    
    def test_password_change(self):
        """Test changing password for encrypted embeddings"""
        old_password = "old_password"
        new_password = "new_password"
        
        # Encrypt with old password
        encrypted_old = self.encryptor.encrypt_embeddings(self.test_embeddings, old_password)
        
        # Change password
        encrypted_new = self.encryptor.change_password(encrypted_old, old_password, new_password)
        
        # Should not be able to decrypt with old password
        with self.assertRaises(ValueError):
            self.encryptor.decrypt_embeddings(encrypted_new, old_password)
        
        # Should be able to decrypt with new password
        decrypted = self.encryptor.decrypt_embeddings(encrypted_new, new_password)
        
        for i in range(128):
            self.assertAlmostEqual(decrypted[i], self.test_embeddings[i], places=10)
    
    def test_password_verification(self):
        """Test password verification"""
        correct_password = "correct_password"
        wrong_password = "wrong_password"
        
        encrypted = self.encryptor.encrypt_embeddings(self.test_embeddings, correct_password)
        
        # Correct password should verify
        self.assertTrue(self.encryptor.verify_password(encrypted, correct_password))
        
        # Wrong password should not verify
        self.assertFalse(self.encryptor.verify_password(encrypted, wrong_password))
    
    def test_base64_output_format(self):
        """Test that output is valid base64"""
        encrypted = self.encryptor.encrypt_embeddings(self.test_embeddings, self.test_password)
        
        # Should be valid base64
        try:
            decoded = base64.b64decode(encrypted)
            self.assertIsInstance(decoded, bytes)
        except Exception:
            self.fail("Encrypted output is not valid base64")
    
    def test_encryption_determinism(self):
        """Test that encryption is non-deterministic (due to random salt/nonce)"""
        results = []
        for _ in range(5):
            encrypted = self.encryptor.encrypt_embeddings(self.test_embeddings, self.test_password)
            results.append(encrypted)
        
        # All results should be different
        for i in range(len(results)):
            for j in range(i + 1, len(results)):
                self.assertNotEqual(results[i], results[j])
    
    def test_large_embeddings_values(self):
        """Test encryption with large embedding values"""
        large_embeddings = [1000000.0 + i for i in range(128)]
        
        encrypted = self.encryptor.encrypt_embeddings(large_embeddings, self.test_password)
        decrypted = self.encryptor.decrypt_embeddings(encrypted, self.test_password)
        
        for i in range(128):
            self.assertAlmostEqual(decrypted[i], large_embeddings[i], places=10)
    
    def test_negative_embeddings_values(self):
        """Test encryption with negative embedding values"""
        negative_embeddings = [-float(i) for i in range(128)]
        
        encrypted = self.encryptor.encrypt_embeddings(negative_embeddings, self.test_password)
        decrypted = self.encryptor.decrypt_embeddings(encrypted, self.test_password)
        
        for i in range(128):
            self.assertAlmostEqual(decrypted[i], negative_embeddings[i], places=10)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_embeddings = [float(i) for i in range(128)]
        self.test_password = "test_password"
    
    def test_create_embedding_encryptor(self):
        """Test factory function"""
        encryptor = create_embedding_encryptor()
        self.assertIsInstance(encryptor, EmbeddingEncryptor)
        self.assertEqual(encryptor.iterations, 100000)
        
        encryptor_custom = create_embedding_encryptor(iterations=50000)
        self.assertEqual(encryptor_custom.iterations, 50000)
    
    def test_generate_embedding_key(self):
        """Test key generation utility"""
        key = generate_embedding_key()
        self.assertEqual(len(key), 64)
        
        # Should be valid hex
        try:
            bytes.fromhex(key)
        except ValueError:
            self.fail("Generated key is not valid hex")
    
    def test_convenience_functions(self):
        """Test convenience functions"""
        # Test password-based functions
        encrypted = encrypt_embeddings(self.test_embeddings, self.test_password)
        decrypted = decrypt_embeddings(encrypted, self.test_password)
        
        self.assertEqual(len(decrypted), 128)
        for i in range(128):
            self.assertAlmostEqual(decrypted[i], self.test_embeddings[i], places=10)
        
        # Test key-based functions
        key = generate_embedding_key()
        encrypted_key = encrypt_embeddings_with_key(self.test_embeddings, key)
        decrypted_key = decrypt_embeddings_with_key(encrypted_key, key)
        
        self.assertEqual(len(decrypted_key), 128)
        for i in range(128):
            self.assertAlmostEqual(decrypted_key[i], self.test_embeddings[i], places=10)


class TestSecurityProperties(unittest.TestCase):
    """Test security properties of the encryption"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.encryptor = EmbeddingEncryptor()
        self.test_embeddings = [float(i) for i in range(128)]
    
    def test_salt_uniqueness(self):
        """Test that each encryption uses a unique salt"""
        password = "test_password"
        encrypted_results = []
        
        for _ in range(10):
            encrypted = self.encryptor.encrypt_embeddings(self.test_embeddings, password)
            encrypted_data = base64.b64decode(encrypted)
            salt = encrypted_data[:32]  # First 32 bytes are salt
            encrypted_results.append(salt)
        
        # All salts should be unique
        unique_salts = set(encrypted_results)
        self.assertEqual(len(unique_salts), 10)
    
    def test_nonce_uniqueness(self):
        """Test that each encryption uses a unique nonce"""
        password = "test_password"
        nonces = []
        
        for _ in range(10):
            encrypted = self.encryptor.encrypt_embeddings(self.test_embeddings, password)
            encrypted_data = base64.b64decode(encrypted)
            nonce = encrypted_data[32:44]  # Bytes 32-44 are nonce
            nonces.append(nonce)
        
        # All nonces should be unique
        unique_nonces = set(nonces)
        self.assertEqual(len(unique_nonces), 10)
    
    def test_ciphertext_appears_random(self):
        """Test that ciphertext appears random"""
        encrypted = self.encryptor.encrypt_embeddings(self.test_embeddings, "password")
        encrypted_data = base64.b64decode(encrypted)
        ciphertext = encrypted_data[44:]  # Skip salt and nonce
        
        # Basic randomness test - no byte should appear too frequently
        byte_counts = {}
        for byte in ciphertext:
            byte_counts[byte] = byte_counts.get(byte, 0) + 1
        
        # No single byte should appear more than 10% of the time in random data
        max_expected_frequency = len(ciphertext) * 0.1
        for count in byte_counts.values():
            self.assertLess(count, max_expected_frequency)
    
    def test_avalanche_effect(self):
        """Test avalanche effect - small input change causes large output change"""
        password = "password"
        embeddings1 = [1.0] * 128
        embeddings2 = embeddings1.copy()
        embeddings2[0] = 1.0000001  # Tiny change
        
        encrypted1 = self.encryptor.encrypt_embeddings(embeddings1, password)
        encrypted2 = self.encryptor.encrypt_embeddings(embeddings2, password)
        
        # Encrypted results should be completely different
        self.assertNotEqual(encrypted1, encrypted2)
        
        # Hamming distance should be high
        data1 = base64.b64decode(encrypted1)
        data2 = base64.b64decode(encrypted2)
        
        # Skip salt comparison since they're random
        ciphertext1 = data1[44:]
        ciphertext2 = data2[44:]
        
        if len(ciphertext1) == len(ciphertext2):
            different_bytes = sum(b1 != b2 for b1, b2 in zip(ciphertext1, ciphertext2))
            difference_ratio = different_bytes / len(ciphertext1)
            
            # Should be significantly different (> 40%)
            self.assertGreater(difference_ratio, 0.4)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)