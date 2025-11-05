#!/usr/bin/env python3
"""
Mock Face Processing Module for ProofOfFace AI Service
Provides mock implementations for testing without face_recognition dependencies
"""

import numpy as np
from PIL import Image, ImageOps
import io
import hashlib
import tempfile
import os
from typing import List, Optional, Tuple, Dict, Any, Union
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FaceProcessingResult:
    """Result of face processing operations"""
    success: bool
    face_encodings: Optional[List[np.ndarray]] = None
    face_locations: Optional[List[Tuple[int, int, int, int]]] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    image_quality_score: Optional[float] = None


class MockFaceProcessor:
    """
    Mock Face processing class for testing without dependencies
    
    Provides the same interface as FaceProcessor but with mock implementations
    """
    
    def __init__(self, 
                 tolerance: float = 0.6,
                 model: str = 'large',
                 max_image_size: int = 5 * 1024 * 1024):
        """
        Initialize MockFaceProcessor
        
        Args:
            tolerance: Face matching tolerance (0.0-1.0, lower = stricter)
            model: Face recognition model ('small' or 'large')
            max_image_size: Maximum image size in bytes
        """
        self.tolerance = tolerance
        self.model = model
        self.max_image_size = max_image_size
        
        # Supported image formats
        self.supported_formats = {'JPEG', 'PNG', 'BMP', 'TIFF'}
        
        logger.info(f"MockFaceProcessor initialized with tolerance={tolerance}, model={model}")
    
    def preprocess_image(self, image_data: bytes) -> Optional[np.ndarray]:
        """
        Mock preprocess image for face recognition
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            np.ndarray: Processed image array or None if processing fails
        """
        try:
            # Check image size
            if len(image_data) > self.max_image_size:
                logger.warning(f"Image size {len(image_data)} exceeds maximum {self.max_image_size}")
                return None
            
            # Load image using PIL
            if isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
            else:
                image = Image.open(image_data)
            
            # Validate image format
            if image.format not in self.supported_formats:
                logger.warning(f"Unsupported image format: {image.format}")
                return None
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Auto-orient image based on EXIF data
            image = ImageOps.exif_transpose(image)
            
            # Resize if image is too large (maintain aspect ratio)
            max_dimension = 1920
            if max(image.size) > max_dimension:
                image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
            
            # Convert PIL image to numpy array
            image_array = np.array(image)
            
            logger.debug(f"Image preprocessed: shape={image_array.shape}, format={image.format}")
            return image_array
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {str(e)}")
            return None
    
    def assess_image_quality(self, image_array: np.ndarray) -> float:
        """
        Mock assess image quality for face recognition
        
        Args:
            image_array: Image as numpy array
            
        Returns:
            float: Quality score (0.0-1.0, higher = better quality)
        """
        try:
            # Mock quality assessment based on image properties
            height, width = image_array.shape[:2]
            
            # Size score (larger images generally better)
            size_score = min((width * height) / (640 * 480), 1.0)
            
            # Brightness score (mock calculation)
            brightness = np.mean(image_array) / 255.0
            brightness_score = 1.0 - abs(brightness - 0.5) * 2
            
            # Variance score (mock contrast)
            variance = np.var(image_array) / (255.0 ** 2)
            variance_score = min(variance * 4, 1.0)
            
            # Combined quality score
            quality_score = (size_score * 0.4 + brightness_score * 0.3 + variance_score * 0.3)
            
            logger.debug(f"Mock image quality: size={size_score:.3f}, "
                        f"brightness={brightness_score:.3f}, variance={variance_score:.3f}, "
                        f"overall={quality_score:.3f}")
            
            return quality_score
            
        except Exception as e:
            logger.error(f"Image quality assessment failed: {str(e)}")
            return 0.0
    
    def detect_faces(self, image_array: np.ndarray) -> FaceProcessingResult:
        """
        Mock detect faces in image and extract encodings
        
        Args:
            image_array: Image as numpy array
            
        Returns:
            FaceProcessingResult: Processing result with face data
        """
        import time
        start_time = time.time()
        
        try:
            # Assess image quality
            quality_score = self.assess_image_quality(image_array)
            
            if quality_score < 0.3:
                return FaceProcessingResult(
                    success=False,
                    error_message=f"Image quality too low: {quality_score:.3f}",
                    processing_time=time.time() - start_time,
                    image_quality_score=quality_score
                )
            
            # Mock face detection based on image content
            height, width = image_array.shape[:2]
            
            # Simple heuristic: if image has reasonable size and quality, assume face present
            if width > 100 and height > 100 and quality_score > 0.2:
                # Mock face location (center of image)
                face_top = height // 4
                face_bottom = 3 * height // 4
                face_left = width // 4
                face_right = 3 * width // 4
                
                face_locations = [(face_top, face_right, face_bottom, face_left)]
                
                # Mock face encoding (128-dimensional)
                mock_encoding = np.random.randn(128).astype(np.float64)
                face_encodings = [mock_encoding]
                
                processing_time = time.time() - start_time
                
                logger.info(f"Mock face detection successful: 1 encoding extracted "
                           f"in {processing_time:.3f}s, quality={quality_score:.3f}")
                
                return FaceProcessingResult(
                    success=True,
                    face_encodings=face_encodings,
                    face_locations=face_locations,
                    processing_time=processing_time,
                    image_quality_score=quality_score
                )
            else:
                return FaceProcessingResult(
                    success=False,
                    error_message="No faces detected in image (mock)",
                    processing_time=time.time() - start_time,
                    image_quality_score=quality_score
                )
            
        except Exception as e:
            logger.error(f"Mock face detection failed: {str(e)}")
            return FaceProcessingResult(
                success=False,
                error_message=f"Face detection error: {str(e)}",
                processing_time=time.time() - start_time
            )
    
    def process_image(self, image_data: bytes) -> FaceProcessingResult:
        """
        Complete mock image processing pipeline
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            FaceProcessingResult: Complete processing result
        """
        # Preprocess image
        image_array = self.preprocess_image(image_data)
        if image_array is None:
            return FaceProcessingResult(
                success=False,
                error_message="Image preprocessing failed"
            )
        
        # Detect faces and extract encodings
        return self.detect_faces(image_array)
    
    def compare_faces(self, 
                     known_encoding: np.ndarray, 
                     candidate_encoding: np.ndarray) -> Dict[str, Any]:
        """
        Mock compare two face encodings
        
        Args:
            known_encoding: Reference face encoding
            candidate_encoding: Candidate face encoding to compare
            
        Returns:
            Dict: Comparison result with match status and distance
        """
        try:
            # Mock face distance calculation using cosine similarity
            dot_product = np.dot(known_encoding, candidate_encoding)
            norm_a = np.linalg.norm(known_encoding)
            norm_b = np.linalg.norm(candidate_encoding)
            
            if norm_a == 0 or norm_b == 0:
                distance = 1.0
            else:
                cosine_similarity = dot_product / (norm_a * norm_b)
                distance = 1.0 - cosine_similarity
            
            # Determine match based on tolerance
            is_match = distance <= self.tolerance
            
            logger.debug(f"Mock face comparison: distance={distance:.4f}, "
                        f"match={is_match}, tolerance={self.tolerance}")
            
            return {
                "match": is_match,
                "distance": float(distance),
                "similarity": float(1.0 - distance)
            }
            
        except Exception as e:
            logger.error(f"Mock face comparison failed: {str(e)}")
            return {
                "match": False,
                "distance": 1.0,
                "similarity": 0.0,
                "error": str(e)
            }
    
    def generate_biometric_hash(self, encoding: np.ndarray) -> str:
        """
        Generate a biometric hash from face encoding
        
        Args:
            encoding: Face encoding array
            
        Returns:
            str: SHA-256 hash of the encoding
        """
        try:
            # Convert encoding to bytes for hashing
            encoding_bytes = encoding.tobytes()
            
            # Generate SHA-256 hash
            hash_obj = hashlib.sha256(encoding_bytes)
            biometric_hash = hash_obj.hexdigest()
            
            logger.debug(f"Generated biometric hash: {biometric_hash[:16]}...")
            return biometric_hash
            
        except Exception as e:
            logger.error(f"Biometric hash generation failed: {str(e)}")
            raise
    
    def validate_face_encoding(self, encoding: np.ndarray) -> bool:
        """
        Validate face encoding format and content
        
        Args:
            encoding: Face encoding to validate
            
        Returns:
            bool: True if encoding is valid
        """
        try:
            # Check if it's a numpy array
            if not isinstance(encoding, np.ndarray):
                return False
            
            # Check dimensions (face_recognition produces 128-dimensional encodings)
            if encoding.shape != (128,):
                return False
            
            # Check for NaN or infinite values
            if np.any(np.isnan(encoding)) or np.any(np.isinf(encoding)):
                return False
            
            # Check if encoding has reasonable magnitude
            magnitude = np.linalg.norm(encoding)
            if magnitude < 0.01 or magnitude > 100.0:  # More lenient bounds for mock
                return False
            
            return True
            
        except Exception:
            return False
    
    def extract_embeddings(self, image_file: Union[str, bytes, io.BytesIO]) -> Dict[str, Any]:
        """
        Mock extract face embeddings from image file
        
        Args:
            image_file: Image file path, bytes, or BytesIO object
        
        Returns:
            Dict containing mock embedding results
        """
        import time
        start_time = time.time()
        
        try:
            # Process input file
            if isinstance(image_file, str):
                if not os.path.exists(image_file):
                    return {
                        "success": False,
                        "error": f"File not found: {image_file}",
                        "processing_time": time.time() - start_time
                    }
                with open(image_file, 'rb') as f:
                    image_data = f.read()
            elif isinstance(image_file, bytes):
                image_data = image_file
            elif isinstance(image_file, io.BytesIO):
                image_data = image_file.getvalue()
            else:
                return {
                    "success": False,
                    "error": f"Unsupported file type: {type(image_file)}",
                    "processing_time": time.time() - start_time
                }
            
            # Process image
            result = self.process_image(image_data)
            
            if result.success:
                # Convert to expected format
                embedding = result.face_encodings[0].tolist()
                face_location = result.face_locations[0]
                
                return {
                    "success": True,
                    "embeddings": embedding,
                    "confidence": result.image_quality_score,
                    "face_locations": [[face_location[0], face_location[1], 
                                      face_location[2], face_location[3]]],
                    "processing_time": result.processing_time
                }
            else:
                return {
                    "success": False,
                    "error": result.error_message,
                    "processing_time": result.processing_time
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Processing error: {str(e)}",
                "processing_time": time.time() - start_time
            }
    
    def compare_embeddings(self, 
                          embedding1: Union[List[float], np.ndarray], 
                          embedding2: Union[List[float], np.ndarray], 
                          threshold: float = 0.6) -> Dict[str, Any]:
        """
        Mock compare two face embeddings
        
        Args:
            embedding1: First face embedding
            embedding2: Second face embedding
            threshold: Similarity threshold
        
        Returns:
            Dict containing comparison results
        """
        try:
            # Convert to numpy arrays if needed
            if isinstance(embedding1, list):
                embedding1 = np.array(embedding1)
            if isinstance(embedding2, list):
                embedding2 = np.array(embedding2)
            
            # Validate embeddings
            if not self.validate_face_encoding(embedding1):
                return {
                    "match": False,
                    "similarity": 0.0,
                    "distance": 1.0,
                    "error": "Invalid first embedding"
                }
            
            if not self.validate_face_encoding(embedding2):
                return {
                    "match": False,
                    "similarity": 0.0,
                    "distance": 1.0,
                    "error": "Invalid second embedding"
                }
            
            # Use the compare_faces method
            return self.compare_faces(embedding1, embedding2)
            
        except Exception as e:
            return {
                "match": False,
                "similarity": 0.0,
                "distance": 1.0,
                "error": str(e)
            }


def create_mock_face_processor(tolerance: float = 0.6, 
                              model: str = 'large',
                              max_image_size: int = 5 * 1024 * 1024) -> MockFaceProcessor:
    """
    Factory function to create MockFaceProcessor instance
    
    Args:
        tolerance: Face matching tolerance (0.0-1.0, lower = stricter)
        model: Face recognition model ('small' or 'large')
        max_image_size: Maximum image size in bytes
        
    Returns:
        MockFaceProcessor: Configured processor instance
    """
    return MockFaceProcessor(
        tolerance=tolerance,
        model=model,
        max_image_size=max_image_size
    )