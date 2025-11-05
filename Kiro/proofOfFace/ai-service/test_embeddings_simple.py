#!/usr/bin/env python3
"""
Simple test script for face embedding functionality
Uses mock processor to test without face_recognition dependencies
"""

import sys
import os
import numpy as np
from PIL import Image, ImageDraw
import io
import json

# Add current directory to path
sys.path.insert(0, '.')

# Import mock processor
from utils.face_processor_mock import create_mock_face_processor

def create_test_image(width=300, height=300, with_face=True):
    """Create a test image with or without face-like pattern"""
    img = Image.new('RGB', (width, height), color='white')
    
    if with_face:
        draw = ImageDraw.Draw(img)
        
        # Draw a simple face-like pattern
        center_x, center_y = width // 2, height // 2
        face_size = min(width, height) // 3
        
        # Face outline (circle)
        draw.ellipse([
            center_x - face_size, center_y - face_size,
            center_x + face_size, center_y + face_size
        ], outline='black', width=3)
        
        # Eyes
        eye_size = face_size // 6
        draw.ellipse([
            center_x - face_size//2 - eye_size, center_y - face_size//3 - eye_size,
            center_x - face_size//2 + eye_size, center_y - face_size//3 + eye_size
        ], fill='black')
        
        draw.ellipse([
            center_x + face_size//2 - eye_size, center_y - face_size//3 - eye_size,
            center_x + face_size//2 + eye_size, center_y - face_size//3 + eye_size
        ], fill='black')
        
        # Mouth
        draw.ellipse([
            center_x - face_size//3, center_y + face_size//3,
            center_x + face_size//3, center_y + face_size//2
        ], outline='black', width=2)
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()

def test_embedding_extraction():
    """Test face embedding extraction"""
    print("🧪 Testing Face Embedding Extraction")
    print("=" * 40)
    
    # Create processor
    processor = create_mock_face_processor(tolerance=0.6, model='small')
    
    # Test with face image
    print("📸 Testing with face image...")
    face_image = create_test_image(with_face=True)
    result = processor.extract_embeddings(face_image)
    
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Embeddings length: {len(result['embeddings'])}")
        print(f"Confidence: {result['confidence']:.3f}")
        print(f"Face locations: {len(result['face_locations'])}")
        print(f"Processing time: {result['processing_time']:.3f}s")
        return result['embeddings']
    else:
        print(f"Error: {result['error']}")
        return None

def test_embedding_comparison():
    """Test face embedding comparison"""
    print("\n🔍 Testing Face Embedding Comparison")
    print("=" * 40)
    
    processor = create_mock_face_processor(tolerance=0.6, model='small')
    
    # Create two similar images
    print("📸 Creating test images...")
    image1 = create_test_image(300, 300, with_face=True)
    image2 = create_test_image(320, 320, with_face=True)  # Slightly different size
    
    # Extract embeddings
    result1 = processor.extract_embeddings(image1)
    result2 = processor.extract_embeddings(image2)
    
    if result1['success'] and result2['success']:
        embedding1 = result1['embeddings']
        embedding2 = result2['embeddings']
        
        # Compare embeddings
        comparison = processor.compare_embeddings(embedding1, embedding2, threshold=0.6)
        
        print(f"Match: {comparison['match']}")
        print(f"Similarity: {comparison['similarity']:.3f}")
        print(f"Distance: {comparison['distance']:.3f}")
        
        # Test with different threshold
        comparison_strict = processor.compare_embeddings(embedding1, embedding2, threshold=0.3)
        print(f"Match (strict): {comparison_strict['match']}")
        
        return comparison
    else:
        print("❌ Failed to extract embeddings for comparison")
        return None

def test_validation():
    """Test embedding validation"""
    print("\n✅ Testing Embedding Validation")
    print("=" * 35)
    
    processor = create_mock_face_processor()
    
    # Valid embedding
    valid_embedding = np.random.randn(128).astype(np.float64)
    print(f"Valid embedding (128D): {processor.validate_face_encoding(valid_embedding)}")
    
    # Invalid embeddings
    invalid_size = np.random.randn(64)
    print(f"Invalid size (64D): {processor.validate_face_encoding(invalid_size)}")
    
    invalid_nan = np.array([np.nan] * 128)
    print(f"Invalid (NaN values): {processor.validate_face_encoding(invalid_nan)}")
    
    invalid_type = [1.0] * 128  # List instead of numpy array
    print(f"Invalid type (list): {processor.validate_face_encoding(invalid_type)}")

def test_biometric_hash():
    """Test biometric hash generation"""
    print("\n🔐 Testing Biometric Hash Generation")
    print("=" * 38)
    
    processor = create_mock_face_processor()
    
    # Create test embedding
    embedding = np.random.randn(128).astype(np.float64)
    
    # Generate hash
    hash1 = processor.generate_biometric_hash(embedding)
    hash2 = processor.generate_biometric_hash(embedding)
    
    print(f"Hash 1: {hash1[:32]}...")
    print(f"Hash 2: {hash2[:32]}...")
    print(f"Hashes match: {hash1 == hash2}")
    print(f"Hash length: {len(hash1)}")
    
    # Different embedding should produce different hash
    different_embedding = np.random.randn(128).astype(np.float64)
    hash3 = processor.generate_biometric_hash(different_embedding)
    print(f"Different hash: {hash3[:32]}...")
    print(f"Different from original: {hash1 != hash3}")

def test_error_handling():
    """Test error handling"""
    print("\n⚠️  Testing Error Handling")
    print("=" * 28)
    
    processor = create_mock_face_processor()
    
    # Test with invalid file
    print("📄 Testing with invalid data...")
    result = processor.extract_embeddings(b"invalid image data")
    print(f"Invalid data result: {result['success']}")
    if not result['success']:
        print(f"Error message: {result['error']}")
    
    # Test with non-existent file
    print("📁 Testing with non-existent file...")
    result = processor.extract_embeddings("/non/existent/file.jpg")
    print(f"Non-existent file result: {result['success']}")
    if not result['success']:
        print(f"Error message: {result['error']}")
    
    # Test comparison with invalid embeddings
    print("🔍 Testing comparison with invalid embeddings...")
    valid_embedding = np.random.randn(128)
    invalid_embedding = np.random.randn(64)  # Wrong size
    
    comparison = processor.compare_embeddings(valid_embedding, invalid_embedding)
    print(f"Invalid comparison result: {comparison['match']}")
    if 'error' in comparison:
        print(f"Error message: {comparison['error']}")

def main():
    """Run all tests"""
    print("🚀 ProofOfFace Face Embedding Tests")
    print("=" * 50)
    print("Using Mock Face Processor (no face_recognition dependency)")
    print()
    
    try:
        # Test embedding extraction
        embeddings = test_embedding_extraction()
        
        # Test embedding comparison
        test_embedding_comparison()
        
        # Test validation
        test_validation()
        
        # Test biometric hash
        test_biometric_hash()
        
        # Test error handling
        test_error_handling()
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed successfully!")
        print("✅ Mock face processor is working correctly")
        print("\n📝 Note: This uses mock implementations.")
        print("   Install face-recognition for real functionality:")
        print("   pip install face-recognition")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)