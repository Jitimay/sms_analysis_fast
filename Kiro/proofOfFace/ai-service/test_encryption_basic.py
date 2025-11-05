#!/usr/bin/env python3
"""
Basic test of EmbeddingEncryptor functionality
"""

import sys
sys.path.insert(0, '.')

def test_basic_encryption():
    """Test basic encryption functionality"""
    print("🔐 Testing EmbeddingEncryptor Basic Functionality")
    print("=" * 50)
    
    try:
        from utils.encryption import EmbeddingEncryptor
        print("✅ EmbeddingEncryptor imported successfully")
        
        # Create encryptor
        encryptor = EmbeddingEncryptor()
        print("✅ EmbeddingEncryptor created")
        
        # Test key generation
        key = encryptor.generate_key()
        print(f"✅ Key generated: {key[:20]}...")
        
        # Test embeddings
        test_embeddings = [float(i) for i in range(128)]
        password = "test_password"
        
        # Test encryption
        encrypted = encryptor.encrypt_embeddings(test_embeddings, password)
        print(f"✅ Embeddings encrypted: {len(encrypted)} chars")
        
        # Test decryption
        decrypted = encryptor.decrypt_embeddings(encrypted, password)
        print(f"✅ Embeddings decrypted: {len(decrypted)} values")
        
        # Verify accuracy
        max_diff = max(abs(orig - dec) for orig, dec in zip(test_embeddings, decrypted))
        print(f"✅ Max difference: {max_diff:.2e}")
        
        if max_diff < 1e-10:
            print("🎉 Perfect reconstruction!")
            return True
        else:
            print("❌ Reconstruction error")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_basic_encryption()
    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
    sys.exit(0 if success else 1)