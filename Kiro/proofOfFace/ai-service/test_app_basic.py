#!/usr/bin/env python3
"""
Basic test version of ProofOfFace AI Service
Tests Flask app startup without face_recognition dependencies
"""

import os
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Flask, request, jsonify, g
from flask_cors import CORS

# Mock the face processor and encryption for testing
class MockFaceProcessor:
    def __init__(self, tolerance=0.6, model='large', max_image_size=5*1024*1024):
        self.tolerance = tolerance
        self.model = model
        self.max_image_size = max_image_size
    
    def process_image(self, image_data):
        # Mock processing result
        class MockResult:
            def __init__(self):
                self.success = True
                self.face_encodings = [b'mock_encoding']
                self.face_locations = [(50, 150, 200, 100)]
                self.processing_time = 0.5
                self.image_quality_score = 0.85
                self.error_message = None
        
        return MockResult()
    
    def generate_biometric_hash(self, face_encoding):
        return "mock_biometric_hash_" + str(hash(str(face_encoding)))[:16]

class MockEncryptionManager:
    def __init__(self, key=None):
        self.key = key or "mock_encryption_key"
    
    def encrypt_face_encoding(self, face_encoding):
        return "mock_encrypted_" + str(hash(str(face_encoding)))[:32]

def create_app():
    """Create Flask app for testing"""
    app = Flask(__name__)
    
    # Setup CORS
    CORS(app, origins='*')
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)
    
    # Initialize mock services
    app.face_processor = MockFaceProcessor()
    app.encryption_manager = MockEncryptionManager()
    
    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.request_id = f"{int(time.time())}-{os.getpid()}"
    
    @app.after_request
    def after_request(response):
        duration = time.time() - g.start_time
        response.headers['X-Request-ID'] = g.request_id
        response.headers['X-Response-Time'] = f"{duration:.3f}s"
        return response
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'proofofface-ai-test',
            'version': '1.0.0-test',
            'timestamp': datetime.utcnow().isoformat(),
            'environment': 'testing',
            'face_recognition_model': 'mock',
            'face_recognition_tolerance': 0.6,
            'note': 'This is a test version without face_recognition dependencies'
        })
    
    @app.route('/process-face', methods=['POST'])
    def process_face():
        """Mock face processing endpoint"""
        try:
            if 'image' not in request.files:
                return jsonify({
                    'success': False,
                    'error': 'No image file provided',
                    'message': 'Please provide an image file in the "image" field'
                }), 400
            
            image_file = request.files['image']
            
            if image_file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'No image file selected',
                    'message': 'Please select an image file'
                }), 400
            
            # Read image data
            image_data = image_file.read()
            
            # Mock processing
            result = app.face_processor.process_image(image_data)
            face_encoding = result.face_encodings[0]
            biometric_hash = app.face_processor.generate_biometric_hash(face_encoding)
            encrypted_encoding = app.encryption_manager.encrypt_face_encoding(face_encoding)
            
            return jsonify({
                'success': True,
                'biometric_hash': biometric_hash,
                'encrypted_face_encoding': encrypted_encoding,
                'quality_score': result.image_quality_score,
                'processing_time': result.processing_time,
                'face_location': result.face_locations[0],
                'note': 'This is a mock response for testing'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Processing failed',
                'message': str(e)
            }), 500
    
    @app.route('/config', methods=['GET'])
    def get_config():
        """Get configuration"""
        return jsonify({
            'face_recognition_model': 'mock',
            'face_recognition_tolerance': 0.6,
            'max_image_size': 5242880,
            'allowed_extensions': ['png', 'jpg', 'jpeg', 'gif', 'bmp'],
            'rate_limit_per_minute': 60,
            'environment': 'testing',
            'note': 'Mock configuration for testing'
        })
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("🚀 Starting ProofOfFace AI Service (Test Mode)")
    print("=" * 50)
    print("📝 Note: This is a test version without face_recognition dependencies")
    print("🔧 All endpoints return mock data for testing purposes")
    print("🌐 Server will be available at: http://localhost:5000")
    print("=" * 50)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )