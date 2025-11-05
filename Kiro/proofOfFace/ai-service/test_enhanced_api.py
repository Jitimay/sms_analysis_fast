#!/usr/bin/env python3
"""
Test enhanced Flask API endpoints with face processing functionality
"""

import sys
import os
import json
import time
import requests
from PIL import Image, ImageDraw
import io
import numpy as np

# Add current directory to path
sys.path.insert(0, '.')

def create_test_image(width=300, height=300, face_id=1):
    """Create a test image with face-like pattern"""
    img = Image.new('RGB', (width, height), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Face parameters based on face_id for uniqueness
    center_x, center_y = width // 2, height // 2
    face_size = min(width, height) // 3 + (face_id * 5)
    
    # Face outline
    draw.ellipse([
        center_x - face_size, center_y - face_size,
        center_x + face_size, center_y + face_size
    ], outline='black', fill='peachpuff', width=2)
    
    # Eyes
    eye_size = face_size // 6
    eye_offset = face_size // 2
    
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
    
    # Mouth
    mouth_width = face_size // 3
    draw.ellipse([
        center_x - mouth_width, center_y + face_size//3,
        center_x + mouth_width, center_y + face_size//2
    ], outline='red', width=3)
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def test_health_endpoint(base_url):
    """Test health check endpoint"""
    print("🏥 Testing Health Endpoint")
    print("-" * 30)
    
    try:
        response = requests.get(f"{base_url}/health")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Service Status: {data.get('status')}")
            print(f"✅ Service Name: {data.get('service')}")
            print(f"✅ Version: {data.get('version')}")
            print(f"✅ Environment: {data.get('environment')}")
            print(f"✅ Available Endpoints: {len(data.get('endpoints', []))}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_extract_embeddings_endpoint(base_url):
    """Test extract embeddings endpoint"""
    print("\n📸 Testing Extract Embeddings Endpoint")
    print("-" * 40)
    
    try:
        # Create test image
        test_image = create_test_image(face_id=1)
        
        # Prepare request
        files = {'file': ('test_face.png', test_image, 'image/png')}
        
        # Make request
        response = requests.post(f"{base_url}/extract-embeddings", files=files)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                embeddings = data.get('embeddings', [])
                confidence = data.get('confidence', 0)
                face_locations = data.get('face_locations', [])
                processing_time = data.get('processing_time', 0)
                
                print(f"✅ Success: {data['success']}")
                print(f"✅ Embeddings Length: {len(embeddings)}")
                print(f"✅ Confidence: {confidence:.3f}")
                print(f"✅ Face Locations: {len(face_locations)}")
                print(f"✅ Processing Time: {processing_time:.3f}s")
                
                # Validate embedding format
                if len(embeddings) == 128:
                    print("✅ Embedding format valid (128 dimensions)")
                else:
                    print(f"❌ Invalid embedding format: {len(embeddings)} dimensions")
                    return False, None
                
                return True, embeddings
            else:
                print(f"❌ Extraction failed: {data.get('error')}")
                return False, None
        else:
            print(f"❌ Request failed: {response.status_code}")
            if response.headers.get('content-type', '').startswith('application/json'):
                error_data = response.json()
                print(f"   Error: {error_data.get('error')}")
            return False, None
            
    except Exception as e:
        print(f"❌ Extract embeddings error: {str(e)}")
        return False, None

def test_compare_faces_endpoint(base_url, embedding1=None, embedding2=None):
    """Test compare faces endpoint"""
    print("\n🔍 Testing Compare Faces Endpoint")
    print("-" * 35)
    
    try:
        # Use provided embeddings or create mock ones
        if embedding1 is None:
            embedding1 = np.random.randn(128).tolist()
        if embedding2 is None:
            # Create similar embedding for testing
            embedding2 = np.array(embedding1) + np.random.randn(128) * 0.1
            embedding2 = embedding2.tolist()
        
        # Test data
        test_data = {
            'embedding1': embedding1,
            'embedding2': embedding2,
            'threshold': 0.6
        }
        
        # Make request
        response = requests.post(
            f"{base_url}/compare-faces",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                match = data.get('match')
                similarity = data.get('similarity', 0)
                distance = data.get('distance', 0)
                threshold = data.get('threshold', 0)
                processing_time = data.get('processing_time', 0)
                
                print(f"✅ Success: {data['success']}")
                print(f"✅ Match: {match}")
                print(f"✅ Similarity: {similarity:.3f}")
                print(f"✅ Distance: {distance:.3f}")
                print(f"✅ Threshold: {threshold}")
                print(f"✅ Processing Time: {processing_time:.6f}s")
                
                return True
            else:
                print(f"❌ Comparison failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            if response.headers.get('content-type', '').startswith('application/json'):
                error_data = response.json()
                print(f"   Error: {error_data.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Compare faces error: {str(e)}")
        return False

def test_config_endpoint(base_url):
    """Test config endpoint"""
    print("\n⚙️  Testing Config Endpoint")
    print("-" * 27)
    
    try:
        response = requests.get(f"{base_url}/config")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Face Recognition Model: {data.get('face_recognition_model')}")
            print(f"✅ Face Recognition Tolerance: {data.get('face_recognition_tolerance')}")
            print(f"✅ Max Image Size: {data.get('max_image_size_mb')}MB")
            print(f"✅ Allowed Extensions: {data.get('allowed_extensions')}")
            print(f"✅ Rate Limit: {data.get('rate_limit_per_minute')}/min")
            print(f"✅ Environment: {data.get('environment')}")
            
            return True
        else:
            print(f"❌ Config request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Config endpoint error: {str(e)}")
        return False

def test_error_handling(base_url):
    """Test error handling scenarios"""
    print("\n⚠️  Testing Error Handling")
    print("-" * 26)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Extract embeddings without file
    total_tests += 1
    try:
        response = requests.post(f"{base_url}/extract-embeddings")
        if response.status_code == 400:
            data = response.json()
            if not data.get('success') and 'file' in data.get('error', '').lower():
                print("✅ Test 1: No file error handled correctly")
                tests_passed += 1
            else:
                print("❌ Test 1: Incorrect error response")
        else:
            print(f"❌ Test 1: Expected 400, got {response.status_code}")
    except Exception as e:
        print(f"❌ Test 1 error: {str(e)}")
    
    # Test 2: Compare faces with invalid JSON
    total_tests += 1
    try:
        response = requests.post(
            f"{base_url}/compare-faces",
            data="invalid json",
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 400:
            print("✅ Test 2: Invalid JSON handled correctly")
            tests_passed += 1
        else:
            print(f"❌ Test 2: Expected 400, got {response.status_code}")
    except Exception as e:
        print(f"❌ Test 2 error: {str(e)}")
    
    # Test 3: Compare faces with missing embeddings
    total_tests += 1
    try:
        response = requests.post(
            f"{base_url}/compare-faces",
            json={'embedding1': [0.1] * 128},  # Missing embedding2
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 400:
            data = response.json()
            if 'embedding' in data.get('error', '').lower():
                print("✅ Test 3: Missing embedding handled correctly")
                tests_passed += 1
            else:
                print("❌ Test 3: Incorrect error message")
        else:
            print(f"❌ Test 3: Expected 400, got {response.status_code}")
    except Exception as e:
        print(f"❌ Test 3 error: {str(e)}")
    
    # Test 4: Compare faces with wrong embedding size
    total_tests += 1
    try:
        response = requests.post(
            f"{base_url}/compare-faces",
            json={
                'embedding1': [0.1] * 64,  # Wrong size
                'embedding2': [0.1] * 128
            },
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 400:
            data = response.json()
            if 'size' in data.get('error', '').lower():
                print("✅ Test 4: Wrong embedding size handled correctly")
                tests_passed += 1
            else:
                print("❌ Test 4: Incorrect error message")
        else:
            print(f"❌ Test 4: Expected 400, got {response.status_code}")
    except Exception as e:
        print(f"❌ Test 4 error: {str(e)}")
    
    print(f"\nError Handling Results: {tests_passed}/{total_tests} tests passed")
    return tests_passed == total_tests

def test_performance(base_url):
    """Test API performance"""
    print("\n⚡ Testing API Performance")
    print("-" * 26)
    
    try:
        # Test multiple embedding extractions
        print("Testing embedding extraction performance...")
        
        extraction_times = []
        for i in range(3):
            test_image = create_test_image(face_id=i+1)
            files = {'file': (f'test_face_{i}.png', test_image, 'image/png')}
            
            start_time = time.time()
            response = requests.post(f"{base_url}/extract-embeddings", files=files)
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    extraction_times.append(end_time - start_time)
        
        if extraction_times:
            avg_extraction_time = sum(extraction_times) / len(extraction_times)
            print(f"✅ Average extraction time: {avg_extraction_time:.3f}s")
            print(f"✅ Extractions completed: {len(extraction_times)}/3")
        else:
            print("❌ No successful extractions for performance test")
        
        # Test comparison performance
        print("Testing comparison performance...")
        
        # Create test embeddings
        embedding1 = np.random.randn(128).tolist()
        embedding2 = np.random.randn(128).tolist()
        
        comparison_times = []
        for i in range(5):
            test_data = {
                'embedding1': embedding1,
                'embedding2': embedding2,
                'threshold': 0.6
            }
            
            start_time = time.time()
            response = requests.post(
                f"{base_url}/compare-faces",
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    comparison_times.append(end_time - start_time)
        
        if comparison_times:
            avg_comparison_time = sum(comparison_times) / len(comparison_times)
            print(f"✅ Average comparison time: {avg_comparison_time:.3f}s")
            print(f"✅ Comparisons completed: {len(comparison_times)}/5")
        else:
            print("❌ No successful comparisons for performance test")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test error: {str(e)}")
        return False

def main():
    """Run comprehensive API tests"""
    print("🚀 ProofOfFace Enhanced API Test Suite")
    print("=" * 50)
    
    # Configuration
    base_url = "http://localhost:5000"
    
    print(f"Testing API at: {base_url}")
    print()
    
    # Test results tracking
    test_results = {}
    
    try:
        # Test 1: Health Check
        test_results['health'] = test_health_endpoint(base_url)
        
        # Test 2: Extract Embeddings
        success, embeddings = test_extract_embeddings_endpoint(base_url)
        test_results['extract_embeddings'] = success
        
        # Test 3: Compare Faces (use extracted embeddings if available)
        if embeddings:
            # Create a second set of embeddings for comparison
            test_image2 = create_test_image(face_id=2)
            files = {'file': ('test_face2.png', test_image2, 'image/png')}
            response = requests.post(f"{base_url}/extract-embeddings", files=files)
            
            embeddings2 = None
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    embeddings2 = data.get('embeddings')
            
            test_results['compare_faces'] = test_compare_faces_endpoint(
                base_url, embeddings, embeddings2
            )
        else:
            test_results['compare_faces'] = test_compare_faces_endpoint(base_url)
        
        # Test 4: Config Endpoint
        test_results['config'] = test_config_endpoint(base_url)
        
        # Test 5: Error Handling
        test_results['error_handling'] = test_error_handling(base_url)
        
        # Test 6: Performance
        test_results['performance'] = test_performance(base_url)
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Test Results Summary")
        print("=" * 50)
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
            if result:
                passed_tests += 1
        
        print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! Enhanced API is working correctly.")
            return True
        else:
            print("⚠️  Some tests failed. Check the API implementation.")
            return False
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Test suite error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("📝 Note: Make sure the Flask API server is running on localhost:5000")
    print("   Start it with: python3 app.py")
    print()
    
    success = main()
    sys.exit(0 if success else 1)