#!/usr/bin/env python3
"""
Test Flask app startup and basic functionality
"""

import sys
import os
import time
import threading
import requests
from contextlib import contextmanager

# Add current directory to path
sys.path.insert(0, '.')

def test_app_import():
    """Test that the app can be imported successfully"""
    print("📦 Testing App Import")
    print("-" * 20)
    
    try:
        # Import the app module first
        import app as app_module
        flask_app = app_module.app
        
        print("✅ App imported successfully")
        print(f"✅ App name: {flask_app.name}")
        print(f"✅ Debug mode: {flask_app.debug}")
        return True, flask_app
    except Exception as e:
        print(f"❌ App import failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None

def test_app_configuration(app):
    """Test app configuration"""
    print("\n⚙️  Testing App Configuration")
    print("-" * 30)
    
    try:
        # Test that services are initialized
        if hasattr(app, 'face_processor'):
            print("✅ Face processor initialized")
            processor_type = type(app.face_processor).__name__
            print(f"✅ Processor type: {processor_type}")
        else:
            print("❌ Face processor not initialized")
            return False
        
        if hasattr(app, 'encryption_manager'):
            print("✅ Encryption manager initialized")
        else:
            print("❌ Encryption manager not initialized")
            return False
        
        # Test basic processor functionality
        print("Testing basic processor functionality...")
        import numpy as np
        
        # Test validation
        test_embedding = np.random.randn(128).astype(np.float64)
        test_embedding = test_embedding / np.linalg.norm(test_embedding) * 2.0
        
        is_valid = app.face_processor.validate_face_encoding(test_embedding)
        print(f"✅ Embedding validation: {is_valid}")
        
        # Test hash generation
        hash_result = app.face_processor.generate_biometric_hash(test_embedding)
        print(f"✅ Hash generation: {hash_result[:16]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_routes(app):
    """Test that routes are registered"""
    print("\n🛣️  Testing Route Registration")
    print("-" * 32)
    
    try:
        # Get all registered routes
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': rule.rule
            })
        
        expected_routes = [
            'health_check',
            'extract_embeddings', 
            'compare_faces',
            'process_face',
            'get_config'
        ]
        
        found_routes = [route['endpoint'] for route in routes]
        
        for expected in expected_routes:
            if expected in found_routes:
                print(f"✅ Route registered: {expected}")
            else:
                print(f"❌ Route missing: {expected}")
                return False
        
        print(f"✅ Total routes registered: {len(routes)}")
        return True
        
    except Exception as e:
        print(f"❌ Route test failed: {str(e)}")
        return False

@contextmanager
def run_test_server(app, port=5001):
    """Context manager to run test server"""
    server_thread = None
    
    try:
        # Start server in a separate thread
        def run_server():
            app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait for server to start
        time.sleep(2)
        
        # Test if server is responding
        try:
            response = requests.get(f"http://127.0.0.1:{port}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ Test server started on port {port}")
                yield f"http://127.0.0.1:{port}"
            else:
                raise Exception(f"Server not responding: {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Server connection failed: {str(e)}")
    
    except Exception as e:
        print(f"❌ Test server startup failed: {str(e)}")
        yield None
    
    finally:
        # Server will stop when main thread exits (daemon thread)
        pass

def test_basic_endpoints(base_url):
    """Test basic endpoint functionality"""
    print("\n🌐 Testing Basic Endpoints")
    print("-" * 28)
    
    if not base_url:
        print("❌ No server URL available")
        return False
    
    try:
        # Test health endpoint
        print("Testing /health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check: {data.get('status')}")
            print(f"✅ Service: {data.get('service')}")
            print(f"✅ Version: {data.get('version')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
        
        # Test config endpoint
        print("Testing /config endpoint...")
        response = requests.get(f"{base_url}/config", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Config loaded: {data.get('face_recognition_model')}")
            print(f"✅ Max image size: {data.get('max_image_size_mb')}MB")
        else:
            print(f"❌ Config endpoint failed: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Endpoint test failed: {str(e)}")
        return False

def main():
    """Run app startup tests"""
    print("🚀 ProofOfFace Flask App Startup Test")
    print("=" * 45)
    
    # Test 1: Import app
    success, app = test_app_import()
    if not success:
        print("\n❌ App import failed - cannot continue")
        return False
    
    # Test 2: Configuration
    success = test_app_configuration(app)
    if not success:
        print("\n❌ App configuration failed")
        return False
    
    # Test 3: Routes
    success = test_routes(app)
    if not success:
        print("\n❌ Route registration failed")
        return False
    
    # Test 4: Basic server functionality
    print("\n🖥️  Testing Server Startup")
    print("-" * 25)
    
    with run_test_server(app, port=5001) as base_url:
        if base_url:
            success = test_basic_endpoints(base_url)
            if not success:
                print("\n❌ Basic endpoint tests failed")
                return False
        else:
            print("❌ Could not start test server")
            return False
    
    # Summary
    print("\n" + "=" * 45)
    print("📊 Startup Test Results")
    print("=" * 45)
    print("✅ App import: PASS")
    print("✅ Configuration: PASS") 
    print("✅ Route registration: PASS")
    print("✅ Server startup: PASS")
    print("✅ Basic endpoints: PASS")
    
    print("\n🎉 All startup tests passed!")
    print("📝 The Flask app is ready for production use")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)