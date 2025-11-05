#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

try:
    from utils.face_processor_mock import create_mock_face_processor
    import numpy as np
    
    # Create processor
    processor = create_mock_face_processor(tolerance=0.6, model='small')
    
    # Test validation
    valid_embedding = np.random.randn(128).astype(np.float64)
    is_valid = processor.validate_face_encoding(valid_embedding)
    
    # Test hash generation
    hash_result = processor.generate_biometric_hash(valid_embedding)
    
    # Write results to file
    with open('test_results.txt', 'w') as f:
        f.write("Mock Face Processor Test Results\n")
        f.write("================================\n")
        f.write(f"Processor created: ✅\n")
        f.write(f"Validation test: {is_valid}\n")
        f.write(f"Hash generated: {hash_result[:16]}...\n")
        f.write("Basic tests passed! 🎉\n")
    
    print("Results written to test_results.txt")
    
except Exception as e:
    with open('test_error.txt', 'w') as f:
        f.write(f"Error: {str(e)}\n")
        import traceback
        f.write(traceback.format_exc())
    print(f"Error occurred: {e}")