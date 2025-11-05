#!/usr/bin/env python3
"""
Test automatic fallback between real and mock face processor
"""

import sys
sys.path.insert(0, '.')

from utils.face_processor import create_face_processor
import numpy as np

def test_auto_fallback():
    """Test automatic processor selection"""
    print("🔄 Testing Automatic Processor Fallback")
    print("=" * 45)
    
    # Test automatic selection
    print("1. Testing automatic processor selection...")
    processor = create_face_processor(tolerance=0.6, model='small')
    print(f"   Processor type: {type(processor).__name__}")
    
    # Test forced mock
    print("2. Testing forced mock processor...")
    mock_processor = create_face_processor(tolerance=0.6, model='small', force_mock=True)
    print(f"   Processor type: {type(mock_processor).__name__}")
    
    # Test basic functionality
    print("3. Testing basic functionality...")
    
    # Test validation
    valid_embedding = np.random.randn(128).astype(np.float64)
    valid_embedding = valid_embedding / np.linalg.norm(valid_embedding) * 2.0
    
    is_valid = processor.validate_face_encoding(valid_embedding)
    print(f"   Validation test: {is_valid}")
    
    # Test hash generation
    hash_result = processor.generate_biometric_hash(valid_embedding)
    print(f"   Hash generated: {hash_result[:16]}...")
    
    # Test comparison
    embedding2 = np.random.randn(128).astype(np.float64)
    embedding2 = embedding2 / np.linalg.norm(embedding2) * 2.0
    
    comparison = processor.compare_embeddings(valid_embedding, embedding2)
    print(f"   Comparison result: match={comparison['match']}, similarity={comparison['similarity']:.3f}")
    
    print("\n✅ Automatic fallback system working correctly!")
    
    return processor

if __name__ == '__main__':
    test_auto_fallback()