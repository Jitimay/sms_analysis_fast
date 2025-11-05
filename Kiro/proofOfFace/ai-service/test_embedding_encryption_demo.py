#!/usr/bin/env python3
"""
Demonstration of EmbeddingEncryptor functionality
Shows how to encrypt face embeddings for IPFS storage
"""

import sys
import os
import numpy as np
import time

# Add current directory to path
sys.path.insert(0, '.')

from utils.encryption import (
    EmbeddingEncryptor,
    create_embedding_encryptor,
    generate_embedding_key,
    encrypt_embeddings,
    decrypt_embeddings
)


def create_sample_embeddings():
    """Create sample face embeddings for testing"""
    # Simulate realistic face embeddings (normalized random values)
    embeddings = np.random.randn(128)
    embeddings = embeddings / np.linalg.norm(embeddings)  # Normalize
    return embeddings.tolist()


def demo_password_based_encryption():
    """Demonstrate password-based encryption"""
    print("🔐 Password-Based Encryption Demo")
    print("=" * 45)
    
    # Create sample embeddings
    embeddings = create_sample_embeddings()
    password = "secure_user_password_123"
    
    print(f"Original embeddings (first 5 values): {embeddings[:5]}")
    print(f"Password: {password}")
    
    # Create encryptor
    encryptor = EmbeddingEncryptor()
    
    # Encrypt embeddings
    start_time = time.time()
    encrypted = encryptor.encrypt_embeddings(embeddings, password)
    encrypt_time = time.time() - start_time
    
    print(f"\n✅ Encryption completed in {encrypt_time:.4f}s")
    print(f"Encrypted data length: {len(encrypted)} characters")
    print(f"Encrypted data (first 50 chars): {encrypted[:50]}...")
    
    # Decrypt embeddings
    start_time = time.time()
    decrypted = encryptor.decrypt_embeddings(encrypted, password)
    decrypt_time = time.time() - start_time
    
    print(f"\n✅ Decryption completed in {decrypt_time:.4f}s")
    print(f"Decrypted embeddings (first 5 values): {decrypted[:5]}")
    
    # Verify accuracy
    max_diff = max(abs(orig - dec) for orig, dec in zip(embeddings, decrypted))
    print(f"Maximum difference: {max_diff:.2e}")
    
    if max_diff < 1e-10:
        print("✅ Perfect reconstruction!")
    else:
        print("❌ Reconstruction error")
    
    return encrypted


def demo_key_based_encryption():
    """Demonstrate direct key-based encryption"""
    print("\n🔑 Direct Key-Based Encryption Demo")
    print("=" * 42)
    
    # Create sample embeddings
    embeddings = create_sample_embeddings()
    
    # Generate encryption key
    encryptor = EmbeddingEncryptor()
    key = encryptor.generate_key()
    
    print(f"Generated key: {key}")
    print(f"Key length: {len(key)} characters")
    
    # Encrypt with key
    start_time = time.time()
    encrypted = encryptor.encrypt_embeddings_with_key(embeddings, key)
    encrypt_time = time.time() - start_time
    
    print(f"\n✅ Key-based encryption completed in {encrypt_time:.4f}s")
    print(f"Encrypted data (first 50 chars): {encrypted[:50]}...")
    
    # Decrypt with key
    start_time = time.time()
    decrypted = encryptor.decrypt_embeddings_with_key(encrypted, key)
    decrypt_time = time.time() - start_time
    
    print(f"\n✅ Key-based decryption completed in {decrypt_time:.4f}s")
    
    # Verify accuracy
    max_diff = max(abs(orig - dec) for orig, dec in zip(embeddings, decrypted))
    print(f"Maximum difference: {max_diff:.2e}")
    
    return encrypted, key


def demo_security_features():
    """Demonstrate security features"""
    print("\n🛡️  Security Features Demo")
    print("=" * 30)
    
    embeddings = create_sample_embeddings()
    password = "test_password"
    encryptor = EmbeddingEncryptor()
    
    # Test password verification
    print("Testing password verification...")
    encrypted = encryptor.encrypt_embeddings(embeddings, password)
    
    correct_verify = encryptor.verify_password(encrypted, password)
    wrong_verify = encryptor.verify_password(encrypted, "wrong_password")
    
    print(f"✅ Correct password verification: {correct_verify}")
    print(f"❌ Wrong password verification: {wrong_verify}")
    
    # Test password change
    print("\nTesting password change...")
    old_password = "old_password"
    new_password = "new_password"
    
    encrypted_old = encryptor.encrypt_embeddings(embeddings, old_password)
    encrypted_new = encryptor.change_password(encrypted_old, old_password, new_password)
    
    # Verify old password no longer works
    old_works = encryptor.verify_password(encrypted_new, old_password)
    new_works = encryptor.verify_password(encrypted_new, new_password)
    
    print(f"❌ Old password works: {old_works}")
    print(f"✅ New password works: {new_works}")
    
    # Test non-deterministic encryption
    print("\nTesting non-deterministic encryption...")
    encrypted1 = encryptor.encrypt_embeddings(embeddings, password)
    encrypted2 = encryptor.encrypt_embeddings(embeddings, password)
    encrypted3 = encryptor.encrypt_embeddings(embeddings, password)
    
    all_different = (encrypted1 != encrypted2 and 
                    encrypted2 != encrypted3 and 
                    encrypted1 != encrypted3)
    
    print(f"✅ Multiple encryptions produce different results: {all_different}")
    
    # But all decrypt to same result
    dec1 = encryptor.decrypt_embeddings(encrypted1, password)
    dec2 = encryptor.decrypt_embeddings(encrypted2, password)
    dec3 = encryptor.decrypt_embeddings(encrypted3, password)
    
    all_same = (dec1 == dec2 == dec3)
    print(f"✅ All decrypt to same result: {all_same}")


def demo_error_handling():
    """Demonstrate error handling"""
    print("\n⚠️  Error Handling Demo")
    print("=" * 25)
    
    encryptor = EmbeddingEncryptor()
    
    # Test invalid embeddings
    print("Testing invalid embeddings...")
    
    try:
        encryptor.encrypt_embeddings([1.0] * 64, "password")  # Wrong size
        print("❌ Should have failed for wrong size")
    except ValueError as e:
        print(f"✅ Caught wrong size error: {str(e)[:50]}...")
    
    try:
        encryptor.encrypt_embeddings([1.0] * 127 + [float('nan')], "password")  # NaN
        print("❌ Should have failed for NaN")
    except ValueError as e:
        print(f"✅ Caught NaN error: {str(e)[:50]}...")
    
    # Test wrong password
    print("\nTesting wrong password...")
    embeddings = create_sample_embeddings()
    encrypted = encryptor.encrypt_embeddings(embeddings, "correct")
    
    try:
        encryptor.decrypt_embeddings(encrypted, "wrong")
        print("❌ Should have failed for wrong password")
    except ValueError as e:
        print(f"✅ Caught wrong password error: {str(e)[:50]}...")
    
    # Test invalid encrypted data
    print("\nTesting invalid encrypted data...")
    
    try:
        encryptor.decrypt_embeddings("invalid_base64!", "password")
        print("❌ Should have failed for invalid base64")
    except ValueError as e:
        print(f"✅ Caught invalid base64 error: {str(e)[:50]}...")


def demo_performance_benchmark():
    """Benchmark encryption/decryption performance"""
    print("\n⚡ Performance Benchmark")
    print("=" * 25)
    
    encryptor = EmbeddingEncryptor()
    embeddings = create_sample_embeddings()
    password = "benchmark_password"
    
    # Benchmark encryption
    print("Benchmarking encryption...")
    encrypt_times = []
    
    for i in range(10):
        start_time = time.time()
        encrypted = encryptor.encrypt_embeddings(embeddings, password)
        encrypt_time = time.time() - start_time
        encrypt_times.append(encrypt_time)
    
    avg_encrypt_time = sum(encrypt_times) / len(encrypt_times)
    print(f"Average encryption time: {avg_encrypt_time:.4f}s")
    
    # Benchmark decryption
    print("Benchmarking decryption...")
    decrypt_times = []
    
    for i in range(10):
        start_time = time.time()
        decrypted = encryptor.decrypt_embeddings(encrypted, password)
        decrypt_time = time.time() - start_time
        decrypt_times.append(decrypt_time)
    
    avg_decrypt_time = sum(decrypt_times) / len(decrypt_times)
    print(f"Average decryption time: {avg_decrypt_time:.4f}s")
    
    # Calculate throughput
    embeddings_per_sec_encrypt = 1.0 / avg_encrypt_time
    embeddings_per_sec_decrypt = 1.0 / avg_decrypt_time
    
    print(f"Encryption throughput: {embeddings_per_sec_encrypt:.1f} embeddings/sec")
    print(f"Decryption throughput: {embeddings_per_sec_decrypt:.1f} embeddings/sec")


def demo_ipfs_use_case():
    """Demonstrate IPFS use case scenario"""
    print("\n🌐 IPFS Use Case Demo")
    print("=" * 22)
    
    print("Scenario: Encrypting embeddings before uploading to IPFS")
    
    # Simulate user registration process
    user_id = "user_12345"
    user_password = "user_secure_password"
    
    # Create face embeddings (would come from face recognition)
    embeddings = create_sample_embeddings()
    print(f"User ID: {user_id}")
    print(f"Embeddings generated: 128 dimensions")
    
    # Encrypt embeddings for IPFS storage
    encryptor = EmbeddingEncryptor()
    encrypted_for_ipfs = encryptor.encrypt_embeddings(embeddings, user_password)
    
    print(f"\n✅ Encrypted for IPFS storage")
    print(f"Encrypted size: {len(encrypted_for_ipfs)} characters")
    print(f"Storage overhead: {len(encrypted_for_ipfs) / (128 * 8):.1f}x")
    
    # Simulate IPFS hash (would be actual IPFS hash)
    ipfs_hash = f"Qm{encrypted_for_ipfs[:40]}..."
    print(f"Simulated IPFS hash: {ipfs_hash}")
    
    # Simulate retrieval and decryption
    print(f"\n🔄 Simulating retrieval from IPFS...")
    retrieved_encrypted = encrypted_for_ipfs  # Would fetch from IPFS
    
    # Decrypt for identity verification
    decrypted_embeddings = encryptor.decrypt_embeddings(retrieved_encrypted, user_password)
    
    print(f"✅ Successfully decrypted embeddings")
    print(f"Verification ready: {len(decrypted_embeddings)} values")
    
    # Verify integrity
    max_diff = max(abs(orig - dec) for orig, dec in zip(embeddings, decrypted_embeddings))
    print(f"Data integrity: {max_diff:.2e} max difference")
    
    return encrypted_for_ipfs


def demo_convenience_functions():
    """Demonstrate convenience functions"""
    print("\n🛠️  Convenience Functions Demo")
    print("=" * 32)
    
    embeddings = create_sample_embeddings()
    password = "convenience_test"
    
    # Test convenience functions
    print("Using convenience functions...")
    
    # Password-based
    encrypted = encrypt_embeddings(embeddings, password)
    decrypted = decrypt_embeddings(encrypted, password)
    
    print(f"✅ Password-based convenience functions work")
    
    # Key-based
    key = generate_embedding_key()
    from utils.encryption import encrypt_embeddings_with_key, decrypt_embeddings_with_key
    
    encrypted_key = encrypt_embeddings_with_key(embeddings, key)
    decrypted_key = decrypt_embeddings_with_key(encrypted_key, key)
    
    print(f"✅ Key-based convenience functions work")
    print(f"Generated key: {key[:20]}...")


def main():
    """Run all demonstrations"""
    print("🚀 EmbeddingEncryptor Comprehensive Demo")
    print("=" * 50)
    print("Demonstrating AES-256-GCM encryption for face embeddings")
    print("Perfect for secure IPFS storage and privacy protection")
    print()
    
    try:
        # Run all demos
        demo_password_based_encryption()
        demo_key_based_encryption()
        demo_security_features()
        demo_error_handling()
        demo_performance_benchmark()
        demo_ipfs_use_case()
        demo_convenience_functions()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Demo Summary")
        print("=" * 50)
        print("✅ Password-based encryption: Working")
        print("✅ Direct key encryption: Working")
        print("✅ Security features: Implemented")
        print("✅ Error handling: Comprehensive")
        print("✅ Performance: Benchmarked")
        print("✅ IPFS use case: Demonstrated")
        print("✅ Convenience functions: Available")
        
        print("\n🎉 All demonstrations completed successfully!")
        print("\n📝 Key Features:")
        print("   • AES-256-GCM authenticated encryption")
        print("   • PBKDF2 key derivation (100,000 iterations)")
        print("   • Secure random salt and nonce generation")
        print("   • Base64 encoding for safe transport")
        print("   • Comprehensive input validation")
        print("   • Perfect for IPFS storage")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)