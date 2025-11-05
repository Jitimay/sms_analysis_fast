#!/usr/bin/env python3
"""
Basic test for Flask app functionality
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, '.')

def test_imports():
    """Test basic imports"""
    print("📦 Testing Imports")
    print("-" * 18)
    
    try:
        # Test config import
        from config import config
        print("✅ Config imported")
        
        # Test face processor import
        from utils.face_processor import create_face_processor
        print("✅ Face processor imported")
        
        # Test encryption import
        from utils.encryption import create_encryption_manager
        print("✅ Encryption manager imported")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        return False

def test_services():
    """Test service creation"""
    print("\n⚙️  Testing Service Creation")
    print("-" * 28)
    
    try:
        from config import config
        from utils.face_processor import create_face_processor
        from utils.encryption import create_encryption_manager
        
        # Create face processor
        processor = create_face_processor(
            tolerance=config.FACE_RECOGNITION_TOLERANCE,
            model=config.FACE_RECOGNITION_MODEL,
            max_image_size=config.MAX_IMAGE_SIZE
        )
        print(f"✅ Face processor created: {type(processor).__name__}")
        
        # Create encryption manager
        encryption_manager = create_encryption_manager(config.ENCRYPTION_KEY)
        print("✅ Encryption manager created")
        
        # Test basic functionality
        import numpy as np
        test_embedding = np.random.randn(128).astype(np.float64)
        test_embedding = test_embedding / np.linalg.norm(test_embedding) * 2.0
        
        is_valid = processor.validate_face_encoding(test_embedding)
        print(f"✅ Embedding validation: {is_valid}")
        
        hash_result = processor.generate_biometric_hash(test_embedding)
        print(f"✅ Hash generation: {hash_result[:16]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Service creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_flask_app_creation():
    """Test Flask app creation without running server"""
    print("\n🌐 Testing Flask App Creation")
    print("-" * 32)
    
    try:
        # Import Flask app creation function
        from app import create_app
        
        # Create app instance
        flask_app = create_app()
        print("✅ Flask app created")
        print(f"✅ App name: {flask_app.name}")
        
        # Check if services are attached
        if hasattr(flask_app, 'face_processor'):
            processor_type = type(flask_app.face_processor).__name__
            print(f"✅ Face processor attached: {processor_type}")
        else:
            print("❌ Face processor not attached")
            return False
        
        if hasattr(flask_app, 'encryption_manager'):
            print("✅ Encryption manager attached")
        else:
            print("❌ Encryption manager not attached")
            return False
        
        # Test routes are registered
        routes = [rule.endpoint for rule in flask_app.url_map.iter_rules()]
        expected_routes = ['health_check', 'extract_embeddings', 'compare_faces']
        
        for route in expected_routes:
            if route in routes:
                print(f"✅ Route registered: {route}")
            else:
                print(f"❌ Route missing: {route}")
                return False
        
        print(f"✅ Total routes: {len(routes)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask app creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_app_context():
    """Test app context functionality"""
    print("\n🔧 Testing App Context")
    print("-" * 22)
    
    try:
        from app import create_app
        
        flask_app = create_app()
        
        # Test app context
        with flask_app.app_context():
            print("✅ App context created")
            
            # Test that services are accessible
            processor = flask_app.face_processor
            print(f"✅ Processor accessible: {type(processor).__name__}")
            
            # Test basic processor functionality in context
            import numpy as np
            test_embedding = np.random.randn(128).astype(np.float64)
            test_embedding = test_embedding / np.linalg.norm(test_embedding) * 2.0
            
            is_valid = processor.validate_face_encoding(test_embedding)
            print(f"✅ Processor working in context: {is_valid}")
        
        print("✅ App context closed successfully")
        return True
        
    except Exception as e:
        print(f"❌ App context test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run basic app tests"""
    print("🚀 ProofOfFace Flask App Basic Test")
    print("=" * 40)
    
    tests = [
        ("Imports", test_imports),
        ("Services", test_services), 
        ("Flask App Creation", test_flask_app_creation),
        ("App Context", test_app_context)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results Summary")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests passed!")
        print("📝 Flask app is ready for startup")
        return True
    else:
        print("⚠️  Some tests failed")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)