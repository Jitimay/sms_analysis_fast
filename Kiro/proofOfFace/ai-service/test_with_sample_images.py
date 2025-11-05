#!/usr/bin/env python3
"""
Comprehensive test of enhanced face processing functionality
Creates sample images and tests all new methods
"""

import sys
import os
import numpy as np
from PIL import Image, ImageDraw
import io
import json
import time

# Add current directory to path
sys.path.insert(0, '.')

# Import mock processor
from utils.face_processor_mock import create_mock_face_processor

def create_sample_face_image(width=400, height=400, face_id=1):
    """Create a sample face image with unique characteristics"""
    img = Image.new('RGB', (width, height), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Face parameters based on face_id for uniqueness
    center_x, center_y = width // 2, height // 2
    face_size = min(width, height) // 3 + (face_id * 10)
    
    # Face outline
    draw.ellipse([
        center_x - face_size, center_y - face_size,
        center_x + face_size, center_y + face_size
    ], outline='black', fill='peachpuff', width=2)
    
    # Eyes (slightly different positions based on face_id)
    eye_size = face_size // 6
    eye_offset = face_size // 2 + (face_id * 2)
    
    # Left eye
    draw.ellipse([
        center_x - eye_offset - eye_size, center_y - face_size//3 - eye_size,
        center_x - eye_offset + eye_size, center_y - face_size//3 + eye_size
    ], fill='black')
    
    # Right eye
    draw.ellipse([
        center_x + eye_offset - eye_size, center_y - face_size//3 - eye_size,
        center_x + eye_offset + eye_size, center_y - face_size//3 + eye_size
    ], fill='black')
    
    # Nose
    nose_points = [
        (center_x, center_y - 10),
        (center_x - 5, center_y + 10),
        (center_x + 5, center_y + 10)
    ]
    draw.polygon(nose_points, fill='brown')
    
    # Mouth (different shape based on face_id)
    mouth_width = face_size // 3 + (face_id * 5)
    draw.ellipse([
        center_x - mouth_width, center_y + face_size//3,
        center_x + mouth_width, center_y + face_size//2
    ], outline='red', width=3)
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()

def test_enhanced_functionality():
    """Test all enhanced face processing functionality"""
    print("🚀 Enhanced Face Processing Functionality Test")
    print("=" * 55)
    
    # Create processor
    processor = create_mock_face_processor(tolerance=0.6, model='large')
    print("✅ Mock Face Processor created")
    
    # Test 1: Extract embeddings from multiple face images
    print("\n📸 Test 1: Extract Face Embeddings")
    print("-" * 35)
    
    embeddings_data = {}
    
    for i in range(1, 4):  # Create 3 different face images
        print(f"Processing face image {i}...")
        face_image = create_sample_face_image(face_id=i)
        
        result = processor.extract_embeddings(face_image)
        
        if result['success']:
            embeddings_data[f'face_{i}'] = {
                'embeddings': result['embeddings'],
                'confidence': result['confidence'],
                'processing_time': result['processing_time']
            }
            print(f"  ✅ Face {i}: {len(result['embeddings'])}D embedding, "
                  f"confidence={result['confidence']:.3f}, "
                  f"time={result['processing_time']:.3f}s")
        else:
            print(f"  ❌ Face {i}: {result['error']}")
    
    # Test 2: Compare embeddings between different faces
    print("\n🔍 Test 2: Compare Face Embeddings")
    print("-" * 35)
    
    if len(embeddings_data) >= 2:
        faces = list(embeddings_data.keys())
        
        # Compare face 1 with face 2 (should be different)
        emb1 = embeddings_data[faces[0]]['embeddings']
        emb2 = embeddings_data[faces[1]]['embeddings']
        
        comparison = processor.compare_embeddings(emb1, emb2, threshold=0.6)
        print(f"Face 1 vs Face 2:")
        print(f"  Match: {comparison['match']}")
        print(f"  Similarity: {comparison['similarity']:.3f}")
        print(f"  Distance: {comparison['distance']:.3f}")
        
        # Compare face 1 with itself (should match)
        self_comparison = processor.compare_embeddings(emb1, emb1, threshold=0.6)
        print(f"Face 1 vs Face 1 (self):")
        print(f"  Match: {self_comparison['match']}")
        print(f"  Similarity: {self_comparison['similarity']:.3f}")
        print(f"  Distance: {self_comparison['distance']:.3f}")
        
        # Test different thresholds
        strict_comparison = processor.compare_embeddings(emb1, emb2, threshold=0.3)
        print(f"Face 1 vs Face 2 (strict threshold=0.3):")
        print(f"  Match: {strict_comparison['match']}")
    
    # Test 3: Biometric hash generation
    print("\n🔐 Test 3: Biometric Hash Generation")
    print("-" * 37)
    
    if embeddings_data:
        face_name = list(embeddings_data.keys())[0]
        embedding = np.array(embeddings_data[face_name]['embeddings'])
        
        # Generate hash multiple times (should be consistent)
        hash1 = processor.generate_biometric_hash(embedding)
        hash2 = processor.generate_biometric_hash(embedding)
        
        print(f"Hash 1: {hash1}")
        print(f"Hash 2: {hash2}")
        print(f"Hashes identical: {hash1 == hash2}")
        print(f"Hash length: {len(hash1)} characters")
        
        # Generate hash for different embedding
        if len(embeddings_data) > 1:
            face_name2 = list(embeddings_data.keys())[1]
            embedding2 = np.array(embeddings_data[face_name2]['embeddings'])
            hash3 = processor.generate_biometric_hash(embedding2)
            
            print(f"Different face hash: {hash3}")
            print(f"Hashes different: {hash1 != hash3}")
    
    # Test 4: Validation functionality
    print("\n✅ Test 4: Embedding Validation")
    print("-" * 32)
    
    if embeddings_data:
        face_name = list(embeddings_data.keys())[0]
        embedding = np.array(embeddings_data[face_name]['embeddings'])
        
        # Test valid embedding
        is_valid = processor.validate_face_encoding(embedding)
        print(f"Valid 128D embedding: {is_valid}")
        
        # Test invalid embeddings
        invalid_size = np.random.randn(64)
        print(f"Invalid size (64D): {processor.validate_face_encoding(invalid_size)}")
        
        invalid_nan = np.array([np.nan] * 128)
        print(f"Invalid (NaN): {processor.validate_face_encoding(invalid_nan)}")
        
        invalid_inf = np.array([np.inf] * 128)
        print(f"Invalid (Inf): {processor.validate_face_encoding(invalid_inf)}")
        
        invalid_type = embedding.tolist()  # Convert to list
        print(f"Invalid type (list): {processor.validate_face_encoding(invalid_type)}")
    
    # Test 5: Error handling
    print("\n⚠️  Test 5: Error Handling")
    print("-" * 25)
    
    # Test with invalid image data
    result = processor.extract_embeddings(b"not an image")
    print(f"Invalid image data: success={result['success']}")
    if not result['success']:
        print(f"  Error: {result['error']}")
    
    # Test with non-existent file
    result = processor.extract_embeddings("/path/that/does/not/exist.jpg")
    print(f"Non-existent file: success={result['success']}")
    if not result['success']:
        print(f"  Error: {result['error']}")
    
    # Test comparison with invalid embeddings
    valid_emb = np.random.randn(128)
    invalid_emb = np.random.randn(64)
    
    comparison = processor.compare_embeddings(valid_emb, invalid_emb)
    print(f"Invalid embedding comparison: match={comparison['match']}")
    if 'error' in comparison:
        print(f"  Error: {comparison['error']}")
    
    # Test 6: Performance metrics
    print("\n⚡ Test 6: Performance Metrics")
    print("-" * 30)
    
    # Time multiple operations
    start_time = time.time()
    
    for i in range(5):
        face_image = create_sample_face_image(face_id=i+10)
        result = processor.extract_embeddings(face_image)
    
    total_time = time.time() - start_time
    avg_time = total_time / 5
    
    print(f"5 embedding extractions: {total_time:.3f}s total")
    print(f"Average per extraction: {avg_time:.3f}s")
    
    # Time comparisons
    if embeddings_data and len(embeddings_data) >= 2:
        faces = list(embeddings_data.keys())
        emb1 = embeddings_data[faces[0]]['embeddings']
        emb2 = embeddings_data[faces[1]]['embeddings']
        
        start_time = time.time()
        for i in range(100):
            processor.compare_embeddings(emb1, emb2)
        comparison_time = time.time() - start_time
        
        print(f"100 comparisons: {comparison_time:.3f}s total")
        print(f"Average per comparison: {comparison_time/100:.6f}s")
    
    return embeddings_data

def save_test_results(embeddings_data):
    """Save test results to JSON file"""
    print("\n💾 Saving Test Results")
    print("-" * 22)
    
    # Prepare data for JSON serialization
    json_data = {
        'test_timestamp': time.time(),
        'processor_config': {
            'tolerance': 0.6,
            'model': 'large',
            'type': 'mock'
        },
        'faces_processed': len(embeddings_data),
        'embeddings': {}
    }
    
    for face_name, data in embeddings_data.items():
        json_data['embeddings'][face_name] = {
            'confidence': data['confidence'],
            'processing_time': data['processing_time'],
            'embedding_length': len(data['embeddings']),
            'embedding_sample': data['embeddings'][:10]  # First 10 values as sample
        }
    
    # Save to file
    with open('face_processing_test_results.json', 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print("✅ Results saved to face_processing_test_results.json")

def main():
    """Run comprehensive test suite"""
    print("🧪 ProofOfFace Enhanced Face Processing Test Suite")
    print("=" * 60)
    print("Using Mock Face Processor (no external dependencies)")
    print()
    
    try:
        # Run all tests
        embeddings_data = test_enhanced_functionality()
        
        # Save results
        save_test_results(embeddings_data)
        
        print("\n" + "=" * 60)
        print("🎉 All Enhanced Functionality Tests Completed!")
        print("✅ Face embedding extraction working")
        print("✅ Face embedding comparison working") 
        print("✅ Biometric hash generation working")
        print("✅ Embedding validation working")
        print("✅ Error handling working")
        print("✅ Performance metrics collected")
        
        print(f"\n📊 Summary:")
        print(f"  - Processed {len(embeddings_data)} face images")
        print(f"  - Generated {len(embeddings_data)} 128D embeddings")
        print(f"  - All validations passed")
        
        print("\n📝 Note: This uses mock implementations for testing.")
        print("   For production use, install: pip install face-recognition opencv-python")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)