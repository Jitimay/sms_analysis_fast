#!/usr/bin/env python3
"""
Test script for ProofOfFace AI Service
Simple tests to verify the service is working correctly
"""

import requests
import json
import time
import os
from io import BytesIO
from PIL import Image
import numpy as np


def create_test_image():
    """Create a simple test image with a face-like pattern"""
    # Create a 200x200 RGB image
    img = Image.new('RGB', (200, 200), color='white')
    pixels = img.load()
    
    # Draw a simple face-like pattern
    # Face outline (circle)
    center_x, center_y = 100, 100
    radius = 80
    
    for x in range(200):
        for y in range(200):
            distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
            
            # Face outline
            if abs(distance - radius) < 2:
                pixels[x, y] = (0, 0, 0)
            
            # Eyes
            elif ((x - 80) ** 2 + (y - 80) ** 2) < 100 or ((x - 120) ** 2 + (y - 80) ** 2) < 100:
                pixels[x, y] = (0, 0, 0)
            
            # Mouth
            elif 90 < x < 110 and 130 < y < 140:
                pixels[x, y] = (0, 0, 0)
    
    # Save to bytes
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes.getvalue()


def test_health_check(base_url):
    """Test the health check endpoint"""
    print("🔍 Testing health check endpoint...")
    
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed")
            print(f"   Service: {data.get('service')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Environment: {data.get('environment')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False


def test_config_endpoint(base_url):
    """Test the configuration endpoint"""
    print("\n🔍 Testing configuration endpoint...")
    
    try:
        response = requests.get(f"{base_url}/config", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Configuration endpoint working")
            print(f"   Face Recognition Model: {data.get('face_recognition_model')}")
            print(f"   Tolerance: {data.get('face_recognition_tolerance')}")
            print(f"   Max Image Size: {data.get('max_image_size')} bytes")
            print(f"   Allowed Extensions: {data.get('allowed_extensions')}")
            return True
        else:
            print(f"❌ Configuration endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Configuration endpoint error: {str(e)}")
        return False


def test_process_face_no_image(base_url):
    """Test process-face endpoint with no image"""
    print("\n🔍 Testing process-face endpoint (no image)...")
    
    try:
        response = requests.post(f"{base_url}/process-face", timeout=10)
        
        if response.status_code == 400:
            data = response.json()
            print(f"✅ Correctly rejected request with no image")
            print(f"   Error: {data.get('error')}")
            return True
        else:
            print(f"❌ Expected 400 error, got: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Process face (no image) error: {str(e)}")
        return False


def test_process_face_with_image(base_url):
    """Test process-face endpoint with test image"""
    print("\n🔍 Testing process-face endpoint (with test image)...")
    
    try:
        # Create test image
        test_image = create_test_image()
        
        # Send request
        files = {'image': ('test_face.png', test_image, 'image/png')}
        response = requests.post(f"{base_url}/process-face", files=files, timeout=30)
        
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Face processing successful")
            print(f"   Success: {data.get('success')}")
            print(f"   Biometric Hash: {data.get('biometric_hash', 'N/A')[:32]}...")
            print(f"   Quality Score: {data.get('quality_score')}")
            print(f"   Processing Time: {data.get('processing_time')} seconds")
            return True
        elif response.status_code == 400:
            data = response.json()
            print(f"⚠️  Face processing failed (expected for test image)")
            print(f"   Error: {data.get('error')}")
            print(f"   Message: {data.get('message')}")
            return True  # This is expected for our simple test image
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            try:
                print(f"   Response: {response.json()}")
            except:
                print(f"   Response text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Process face (with image) error: {str(e)}")
        return False


def test_invalid_endpoint(base_url):
    """Test invalid endpoint"""
    print("\n🔍 Testing invalid endpoint...")
    
    try:
        response = requests.get(f"{base_url}/invalid-endpoint", timeout=10)
        
        if response.status_code == 404:
            print(f"✅ Correctly returned 404 for invalid endpoint")
            return True
        else:
            print(f"❌ Expected 404, got: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Invalid endpoint test error: {str(e)}")
        return False


def run_all_tests(base_url="http://localhost:5000"):
    """Run all tests"""
    print(f"🚀 Starting ProofOfFace AI Service Tests")
    print(f"   Base URL: {base_url}")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Configuration", test_config_endpoint),
        ("Process Face (No Image)", test_process_face_no_image),
        ("Process Face (With Image)", test_process_face_with_image),
        ("Invalid Endpoint", test_invalid_endpoint),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func(base_url)
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Service is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the service configuration.")
        return False


if __name__ == "__main__":
    import sys
    
    # Get base URL from command line or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    # Wait a moment for service to start if needed
    print("⏳ Waiting for service to be ready...")
    time.sleep(2)
    
    # Run tests
    success = run_all_tests(base_url)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)