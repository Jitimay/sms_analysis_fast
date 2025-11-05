#!/usr/bin/env python3
"""
Simple test to verify mock face processor
"""

import sys
sys.path.insert(0, '.')

from utils.face_processor_mock import create_mock_face_processor
import numpy as np

def main():
    print("Testing mock face processor...")
    
    # Create processor
    processor = create_mock_face_processor(tolerance=0.6, model='small')
    print("✅ Processor created")
    
    # Test validation
    valid_embedding = np.random.randn(128).astype(np.float64)
    is_valid = processor.validate_face_encoding(valid_embedding)
    print(f"✅ Validation test: {is_valid}")
    
    # Test hash generation
    hash_result = processor.generate_biometric_hash(valid_embedding)
    print(f"✅ Hash generated: {hash_result[:16]}...")
    
    print("🎉 Basic tests passed!")

if __name__ == '__main__':
    main()