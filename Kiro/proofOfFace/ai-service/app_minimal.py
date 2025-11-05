#!/usr/bin/env python3
"""
Minimal Flask app for testing enhanced face processing functionality
"""

import os
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Flask, request, jsonify, g
from flask_cors import CORS
import numpy as np

# Import local modules
from config import config
from utils.face_processor_simple import create_face_processor
from utils.encryption import create_encryption_manager

def create_app() -> Flask:
    """Create minimal Flask app for testing"""
    app = Flask(__name__)
    
    # Basic configuration
    app.config['DEBUG'] = config.DEBUG
    
    # Setup CORS
    CORS(app)
    
    # Initialize services
    app.face_processor = create_face_processor(
        tolerance=config.FACE_RECOGNITION_TOLERANCE,
        model=config.FACE_RECOGNITION_MODEL,
        max_image_size=config.MAX_IMAGE_SIZE
    )
    
    app.encryption_manager = create_encryption_manager(config.ENCRYPTION_KEY)
    
    # Routes
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'proofofface-ai-minimal',
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat(),
            'processor_type': type(app.face_processor).__name__
        })
    
    @app.route('/extract-embeddings', methods=['POST'])
    def extract_embeddings():
        """Extract face embeddings from uploaded image"""
        try:
            # Validate request
            if 'file' not in request.files:
                return jsonify({
                    'success': False,
                    'error': 'No file provided'
                }), 400
            
            uploaded_file = request.files['file']
            
            if uploaded_file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'No file selected'
                }), 400
            
            # Read file data
            file_data = uploaded_file.read()
            
            # Extract embeddings
            result = app.face_processor.extract_embeddings(file_data)
            
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 400
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Processing failed: {str(e)}'
            }), 500
    
    @app.route('/compare-faces', methods=['POST'])
    def compare_faces():
        """Compare two face embeddings"""
        try:
            data = request.get_json()
            
            if not data or 'embedding1' not in data or 'embedding2' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Missing embeddings'
                }), 400
            
            embedding1 = data['embedding1']
            embedding2 = data['embedding2']
            threshold = data.get('threshold', 0.6)
            
            # Validate embeddings
            if len(embedding1) != 128 or len(embedding2) != 128:
                return jsonify({
                    'success': False,
                    'error': 'Embeddings must contain exactly 128 values'
                }), 400
            
            # Compare embeddings
            result = app.face_processor.compare_embeddings(
                embedding1, embedding2, threshold=threshold
            )
            
            if 'error' in result:
                return jsonify({
                    'success': False,
                    'error': result['error']
                }), 400
            
            return jsonify({
                'success': True,
                'match': result['match'],
                'similarity': result['similarity'],
                'distance': result['distance'],
                'threshold': threshold
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Processing failed: {str(e)}'
            }), 500
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    print(f"Starting minimal ProofOfFace AI Service on {config.HOST}:{config.PORT}")
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
        threaded=True
    )