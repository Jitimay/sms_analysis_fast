#!/usr/bin/env python3
"""
Unit tests for enhanced face processor embedding functionality
"""

import unittest
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.face_processor_mock import create_mock_face_processor

class TestFaceProcessorEmbeddings(unittest.TestCase):
    """Test enhanced face processor functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = create_mock_face_processor(tolerance=0.6, model='small')
    
    def test_processor_creation(self):
        """Test processor can be created"""
        self.assertIsNotNone(self.processor)
        self.assertEqual(self.processor.tolerance, 0.6)
        self.assertEqual(self.processor.model, 'small')
    
    def test_validate_face_encoding(self):
        """Test face encoding validation"""
        # Valid encoding
        valid_encoding = np.random.randn(128).astype(np.float64)
        # Ensure it has reasonable magnitude
        valid_encoding = valid_encoding / np.linalg.norm(valid_encoding) * 2.0
        
        self.assertTrue(self.processor.validate_face_encoding(valid_encoding))
        
        # Invalid encodings
        self.assertFalse(self.processor.validate_face_encoding(np.array([1, 2, 3])))  # Wrong size
        self.assertFalse(self.processor.validate_face_encoding([1, 2, 3]))  # Not numpy array
        self.assertFalse(self.processor.validate_face_encoding(np.array([np.nan] * 128)))  # NaN values
        self.assertFalse(self.processor.validate_face_encoding(np.array([np.inf] * 128)))  # Inf values
    
    def test_generate_biometric_hash(self):
        """Test biometric hash generation"""
        encoding = np.random.randn(128).astype(np.float64)
        
        hash1 = self.processor.generate_biometric_hash(encoding)
        hash2 = self.processor.generate_biometric_hash(encoding)
        
        # Same encoding should produce same hash
        self.assertEqual(hash1, hash2)
        
        # Different encoding should produce different hash
        different_encoding = np.random.randn(128).astype(np.float64)
        hash3 = self.processor.generate_biometric_hash(different_encoding)
        self.assertNotEqual(hash1, hash3)
        
        # Hash should be hex string
        self.assertIsInstance(hash1, str)
        self.assertEqual(len(hash1), 64)  # SHA-256 produces 64 character hex string
    
    def test_compare_embeddings_with_arrays(self):
        """Test embedding comparison with numpy arrays"""
        # Create two similar embeddings
        embedding1 = np.random.randn(128).astype(np.float64)
        embedding1 = embedding1 / np.linalg.norm(embedding1) * 2.0  # Normalize
        
        # Create similar embedding (same + small noise)
        embedding2 = embedding1 + np.random.randn(128) * 0.01
        
        result = self.processor.compare_embeddings(embedding1, embedding2, threshold=0.6)
        
        self.assertIn('match', result)
        self.assertIn('similarity', result)
        self.assertIn('distance', result)
        self.assertIn(result['match'], [True, False])  # Check it's a boolean value
        self.assertIsInstance(result['similarity'], (float, int))
        self.assertIsInstance(result['distance'], (float, int))
    
    def test_compare_embeddings_with_lists(self):
        """Test embedding comparison with lists"""
        # Create embeddings as lists
        embedding1 = np.random.randn(128).astype(np.float64)
        embedding1 = embedding1 / np.linalg.norm(embedding1) * 2.0
        embedding1_list = embedding1.tolist()
        
        embedding2 = np.random.randn(128).astype(np.float64)
        embedding2 = embedding2 / np.linalg.norm(embedding2) * 2.0
        embedding2_list = embedding2.tolist()
        
        result = self.processor.compare_embeddings(embedding1_list, embedding2_list)
        
        self.assertIn('match', result)
        self.assertIn('similarity', result)
        self.assertIn('distance', result)
    
    def test_compare_embeddings_invalid_input(self):
        """Test embedding comparison with invalid input"""
        valid_embedding = np.random.randn(128).astype(np.float64)
        valid_embedding = valid_embedding / np.linalg.norm(valid_embedding) * 2.0
        
        invalid_embedding = np.random.randn(64)  # Wrong size
        
        result = self.processor.compare_embeddings(valid_embedding, invalid_embedding)
        
        self.assertFalse(result['match'])
        self.assertEqual(result['similarity'], 0.0)
        self.assertEqual(result['distance'], 1.0)
        self.assertIn('error', result)
    
    def test_compare_embeddings_threshold_validation(self):
        """Test embedding comparison threshold validation"""
        embedding1 = np.random.randn(128).astype(np.float64)
        embedding1 = embedding1 / np.linalg.norm(embedding1) * 2.0
        
        embedding2 = np.random.randn(128).astype(np.float64)
        embedding2 = embedding2 / np.linalg.norm(embedding2) * 2.0
        
        # Valid thresholds should work
        result = self.processor.compare_embeddings(embedding1, embedding2, threshold=0.5)
        self.assertNotIn('error', result)
        
        result = self.processor.compare_embeddings(embedding1, embedding2, threshold=0.0)
        self.assertNotIn('error', result)
        
        result = self.processor.compare_embeddings(embedding1, embedding2, threshold=1.0)
        self.assertNotIn('error', result)
    
    def test_extract_embeddings_invalid_input(self):
        """Test extract_embeddings with invalid input"""
        # Test with invalid bytes
        result = self.processor.extract_embeddings(b"not an image")
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        
        # Test with non-existent file
        result = self.processor.extract_embeddings("/non/existent/file.jpg")
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        
        # Test with unsupported type
        result = self.processor.extract_embeddings(12345)
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_assess_image_quality(self):
        """Test image quality assessment"""
        # Create a test image array
        test_image = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
        
        quality = self.processor.assess_image_quality(test_image)
        
        self.assertIsInstance(quality, float)
        self.assertGreaterEqual(quality, 0.0)
        self.assertLessEqual(quality, 1.0)
    
    def test_compare_faces_method(self):
        """Test the compare_faces method directly"""
        embedding1 = np.random.randn(128).astype(np.float64)
        embedding1 = embedding1 / np.linalg.norm(embedding1) * 2.0
        
        embedding2 = np.random.randn(128).astype(np.float64)
        embedding2 = embedding2 / np.linalg.norm(embedding2) * 2.0
        
        result = self.processor.compare_faces(embedding1, embedding2)
        
        self.assertIn('match', result)
        self.assertIn('distance', result)
        self.assertIn('similarity', result)
        self.assertIn(result['match'], [True, False])  # Check it's a boolean value
        self.assertIsInstance(result['distance'], (float, int))
        self.assertIsInstance(result['similarity'], (float, int))


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)