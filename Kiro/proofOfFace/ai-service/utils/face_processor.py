"""
Face Processing Module for ProofOfFace AI Service
Handles face detection, encoding extraction, and comparison operations
"""

# Try to import face_recognition, fall back to mock if not available
try:
    import face_recognition
    import cv2
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    # Will use mock processor as fallback

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


class FaceProcessor:
    """
    Face processing class for ProofOfFace identity verification
    
    Handles:
    - Face detection in images
    - Face encoding extraction
    - Face comparison and matching
    - Image quality assessment
    """
    
    def __init__(self, 
                 tolerance: float = 0.6,
                 model: str = 'large',
                 max_image_size: int = 5 * 1024 * 1024):
        """
        Initialize FaceProcessor
        
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
        
        logger.info(f"FaceProcessor initialized with tolerance={tolerance}, model={model}")
    
    def preprocess_image(self, image_data: bytes) -> Optional[np.ndarray]:
        """
        Preprocess image for face recognition
        
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
            image = Image.open(io.BytesIO(image_data))
            
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
        Assess image quality for face recognition
        
        Args:
            image_array: Image as numpy array
            
        Returns:
            float: Quality score (0.0-1.0, higher = better quality)
        """
        try:
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            
            # Calculate sharpness using Laplacian variance
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(laplacian_var / 1000.0, 1.0)  # Normalize
            
            # Calculate brightness
            brightness = np.mean(gray) / 255.0
            brightness_score = 1.0 - abs(brightness - 0.5) * 2  # Optimal around 0.5
            
            # Calculate contrast
            contrast = np.std(gray) / 255.0
            contrast_score = min(contrast * 4, 1.0)  # Normalize
            
            # Combined quality score
            quality_score = (sharpness_score * 0.5 + brightness_score * 0.3 + contrast_score * 0.2)
            
            logger.debug(f"Image quality: sharpness={sharpness_score:.3f}, "
                        f"brightness={brightness_score:.3f}, contrast={contrast_score:.3f}, "
                        f"overall={quality_score:.3f}")
            
            return quality_score
            
        except Exception as e:
            logger.error(f"Image quality assessment failed: {str(e)}")
            return 0.0
    
    def detect_faces(self, image_array: np.ndarray) -> FaceProcessingResult:
        """
        Detect faces in image and extract encodings
        
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
            
            # Detect face locations
            face_locations = face_recognition.face_locations(
                image_array, 
                model='hog' if self.model == 'small' else 'cnn'
            )
            
            if not face_locations:
                return FaceProcessingResult(
                    success=False,
                    error_message="No faces detected in image",
                    processing_time=time.time() - start_time,
                    image_quality_score=quality_score
                )
            
            if len(face_locations) > 1:
                logger.warning(f"Multiple faces detected: {len(face_locations)}. Using the largest face.")
                # Sort by face area (largest first)
                face_locations = sorted(face_locations, 
                                      key=lambda loc: (loc[2] - loc[0]) * (loc[1] - loc[3]), 
                                      reverse=True)
                face_locations = [face_locations[0]]  # Keep only the largest face
            
            # Extract face encodings
            face_encodings = face_recognition.face_encodings(
                image_array, 
                face_locations,
                model=self.model
            )
            
            if not face_encodings:
                return FaceProcessingResult(
                    success=False,
                    error_message="Failed to extract face encodings",
                    processing_time=time.time() - start_time,
                    image_quality_score=quality_score
                )
            
            processing_time = time.time() - start_time
            
            logger.info(f"Face detection successful: {len(face_encodings)} encoding(s) extracted "
                       f"in {processing_time:.3f}s, quality={quality_score:.3f}")
            
            return FaceProcessingResult(
                success=True,
                face_encodings=face_encodings,
                face_locations=face_locations,
                processing_time=processing_time,
                image_quality_score=quality_score
            )
            
        except Exception as e:
            logger.error(f"Face detection failed: {str(e)}")
            return FaceProcessingResult(
                success=False,
                error_message=f"Face detection error: {str(e)}",
                processing_time=time.time() - start_time
            )
    
    def process_image(self, image_data: bytes) -> FaceProcessingResult:
        """
        Complete image processing pipeline
        
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
        Compare two face encodings
        
        Args:
            known_encoding: Reference face encoding
            candidate_encoding: Candidate face encoding to compare
            
        Returns:
            Dict: Comparison result with match status and distance
        """
        try:
            # Calculate face distance
            distance = face_recognition.face_distance([known_encoding], candidate_encoding)[0]
            
            # Determine if faces match
            is_match = distance <= self.tolerance
            
            # Calculate confidence score (inverse of distance, normalized)
            confidence = max(0.0, 1.0 - (distance / 1.0))
            
            result = {
                'is_match': is_match,
                'distance': float(distance),
                'confidence': float(confidence),
                'tolerance': self.tolerance
            }
            
            logger.debug(f"Face comparison: distance={distance:.4f}, "
                        f"match={is_match}, confidence={confidence:.4f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Face comparison failed: {str(e)}")
            return {
                'is_match': False,
                'distance': 1.0,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def generate_biometric_hash(self, face_encoding: np.ndarray) -> str:
        """
        Generate a deterministic hash from face encoding
        
        Args:
            face_encoding: Face encoding array
            
        Returns:
            str: SHA-256 hash of the face encoding
        """
        try:
            # Normalize encoding to ensure consistency
            normalized_encoding = face_encoding / np.linalg.norm(face_encoding)
            
            # Round to reduce floating point precision issues
            rounded_encoding = np.round(normalized_encoding, decimals=6)
            
            # Convert to bytes and hash
            encoding_bytes = rounded_encoding.tobytes()
            hash_object = hashlib.sha256(encoding_bytes)
            biometric_hash = hash_object.hexdigest()
            
            logger.debug(f"Generated biometric hash: {biometric_hash[:16]}...")
            return biometric_hash
            
        except Exception as e:
            logger.error(f"Biometric hash generation failed: {str(e)}")
            raise ValueError(f"Failed to generate biometric hash: {str(e)}")
    
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
            if magnitude < 0.1 or magnitude > 10.0:
                return False
            
            return True
            
        except Exception:
            return False
    
    def extract_embeddings(self, image_file: Union[str, bytes, io.BytesIO]) -> Dict[str, Any]:
        """
        Extract face embeddings from image or video file
        
        Args:
            image_file: Image file path, bytes, or BytesIO object
                       Supports JPEG/PNG images and MP4 videos
        
        Returns:
            Dict containing:
            - success: bool
            - embeddings: List[float] (128-dimensional)
            - confidence: float (0-1)
            - face_locations: List[List[int]] [[top, right, bottom, left]]
            - error: str (if failed)
        """
        import time
        start_time = time.time()
        
        try:
            # Input validation and file type detection
            file_data, file_type = self._process_input_file(image_file)
            if file_data is None:
                return {
                    "success": False,
                    "error": "Invalid file format or corrupted file",
                    "processing_time": time.time() - start_time
                }
            
            # Process based on file type
            if file_type == 'video':
                image_array = self._extract_frame_from_video(file_data)
                if image_array is None:
                    return {
                        "success": False,
                        "error": "Failed to extract clear frame from video",
                        "processing_time": time.time() - start_time
                    }
            else:
                # Process as image
                image_array = self.preprocess_image(file_data)
                if image_array is None:
                    return {
                        "success": False,
                        "error": "Failed to process image",
                        "processing_time": time.time() - start_time
                    }
            
            # Assess image quality
            quality_score = self.assess_image_quality(image_array)
            if quality_score < 0.3:
                return {
                    "success": False,
                    "error": f"Image quality too low: {quality_score:.3f}",
                    "confidence": quality_score,
                    "processing_time": time.time() - start_time
                }
            
            # Detect faces
            face_locations = face_recognition.face_locations(
                image_array,
                model='hog' if self.model == 'small' else 'cnn'
            )
            
            if not face_locations:
                return {
                    "success": False,
                    "error": "No faces detected in image",
                    "confidence": quality_score,
                    "processing_time": time.time() - start_time
                }
            
            if len(face_locations) > 1:
                return {
                    "success": False,
                    "error": f"Multiple faces detected ({len(face_locations)}). Please use image with single face.",
                    "confidence": quality_score,
                    "face_locations": [[loc[0], loc[1], loc[2], loc[3]] for loc in face_locations],
                    "processing_time": time.time() - start_time
                }
            
            # Extract face encodings
            face_encodings = face_recognition.face_encodings(
                image_array,
                face_locations,
                model=self.model
            )
            
            if not face_encodings:
                return {
                    "success": False,
                    "error": "Failed to extract face encodings",
                    "confidence": quality_score,
                    "processing_time": time.time() - start_time
                }
            
            # Convert numpy array to list for JSON serialization
            embedding = face_encodings[0].tolist()
            
            # Calculate confidence based on quality and face detection certainty
            confidence = min(quality_score + 0.1, 1.0)  # Boost confidence slightly
            
            processing_time = time.time() - start_time
            
            logger.info(f"Face embedding extracted successfully in {processing_time:.3f}s, "
                       f"confidence={confidence:.3f}")
            
            return {
                "success": True,
                "embeddings": embedding,
                "confidence": confidence,
                "face_locations": [[face_locations[0][0], face_locations[0][1], 
                                   face_locations[0][2], face_locations[0][3]]],
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"Face embedding extraction failed: {str(e)}")
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
        Compare two face embeddings
        
        Args:
            embedding1: First face embedding (128-dimensional)
            embedding2: Second face embedding (128-dimensional)
            threshold: Similarity threshold (0.0-1.0, default 0.6)
        
        Returns:
            Dict containing:
            - match: bool
            - similarity: float (0-1 scale)
            - distance: float
        """
        try:
            # Input validation
            if threshold < 0.0 or threshold > 1.0:
                raise ValueError("Threshold must be between 0.0 and 1.0")
            
            # Convert to numpy arrays if needed
            if isinstance(embedding1, list):
                embedding1 = np.array(embedding1)
            if isinstance(embedding2, list):
                embedding2 = np.array(embedding2)
            
            # Validate embeddings
            if not self.validate_face_encoding(embedding1):
                raise ValueError("Invalid first embedding")
            if not self.validate_face_encoding(embedding2):
                raise ValueError("Invalid second embedding")
            
            # Calculate face distance using face_recognition library
            distance = face_recognition.face_distance([embedding1], embedding2)[0]
            
            # Determine match using face_recognition's compare_faces
            matches = face_recognition.compare_faces([embedding1], embedding2, tolerance=threshold)
            is_match = matches[0]
            
            # Calculate similarity score (inverse of distance, normalized)
            # Distance typically ranges from 0 (identical) to 1+ (very different)
            similarity = max(0.0, 1.0 - distance)
            
            logger.debug(f"Face comparison: distance={distance:.4f}, "
                        f"similarity={similarity:.4f}, match={is_match}, threshold={threshold}")
            
            return {
                "match": is_match,
                "similarity": float(similarity),
                "distance": float(distance)
            }
            
        except Exception as e:
            logger.error(f"Face comparison failed: {str(e)}")
            return {
                "match": False,
                "similarity": 0.0,
                "distance": 1.0,
                "error": str(e)
            }
    
    def _process_input_file(self, image_file: Union[str, bytes, io.BytesIO]) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Process input file and determine type
        
        Args:
            image_file: File path, bytes, or BytesIO object
            
        Returns:
            Tuple of (file_data, file_type) or (None, None) if invalid
        """
        try:
            # Handle different input types
            if isinstance(image_file, str):
                # File path
                if not os.path.exists(image_file):
                    logger.error(f"File not found: {image_file}")
                    return None, None
                
                with open(image_file, 'rb') as f:
                    file_data = f.read()
                    
            elif isinstance(image_file, bytes):
                file_data = image_file
                
            elif isinstance(image_file, io.BytesIO):
                file_data = image_file.getvalue()
                
            else:
                logger.error(f"Unsupported file type: {type(image_file)}")
                return None, None
            
            # Validate file size
            if len(file_data) > self.max_image_size:
                logger.error(f"File size {len(file_data)} exceeds maximum {self.max_image_size}")
                return None, None
            
            if len(file_data) < 100:  # Minimum reasonable file size
                logger.error("File too small to be valid")
                return None, None
            
            # Determine file type by magic bytes
            file_type = self._detect_file_type(file_data)
            if file_type is None:
                logger.error("Unsupported file format")
                return None, None
            
            return file_data, file_type
            
        except Exception as e:
            logger.error(f"File processing error: {str(e)}")
            return None, None
    
    def _detect_file_type(self, file_data: bytes) -> Optional[str]:
        """
        Detect file type from magic bytes
        
        Args:
            file_data: Raw file bytes
            
        Returns:
            'image' or 'video' or None if unsupported
        """
        # Check magic bytes for common formats
        if file_data.startswith(b'\xff\xd8\xff'):  # JPEG
            return 'image'
        elif file_data.startswith(b'\x89PNG\r\n\x1a\n'):  # PNG
            return 'image'
        elif file_data.startswith(b'BM'):  # BMP
            return 'image'
        elif file_data.startswith(b'GIF87a') or file_data.startswith(b'GIF89a'):  # GIF
            return 'image'
        elif (file_data[4:8] == b'ftyp' and 
              (b'mp4' in file_data[8:20] or b'isom' in file_data[8:20])):  # MP4
            return 'video'
        elif file_data.startswith(b'\x1a\x45\xdf\xa3'):  # WebM/MKV
            return 'video'
        elif file_data.startswith(b'RIFF') and b'AVI ' in file_data[8:12]:  # AVI
            return 'video'
        
        return None
    
    def _extract_frame_from_video(self, video_data: bytes) -> Optional[np.ndarray]:
        """
        Extract the first clear frame with a face from video
        
        Args:
            video_data: Raw video bytes
            
        Returns:
            Image array or None if no suitable frame found
        """
        temp_file = None
        try:
            # Save video data to temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                temp_file.write(video_data)
                temp_file_path = temp_file.name
            
            # Open video with OpenCV
            cap = cv2.VideoCapture(temp_file_path)
            
            if not cap.isOpened():
                logger.error("Failed to open video file")
                return None
            
            frame_count = 0
            max_frames_to_check = 30  # Check first 30 frames (1 second at 30fps)
            
            while frame_count < max_frames_to_check:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                frame_count += 1
                
                # Convert BGR to RGB (OpenCV uses BGR, face_recognition expects RGB)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Check if frame has good quality
                quality_score = self.assess_image_quality(rgb_frame)
                
                if quality_score < 0.4:
                    continue
                
                # Check if frame contains a face
                face_locations = face_recognition.face_locations(rgb_frame, model='hog')
                
                if len(face_locations) == 1:  # Exactly one face found
                    logger.info(f"Found suitable frame at position {frame_count} "
                               f"with quality {quality_score:.3f}")
                    cap.release()
                    return rgb_frame
                
                elif len(face_locations) > 1:
                    logger.debug(f"Frame {frame_count} has multiple faces, skipping")
                    continue
            
            cap.release()
            logger.warning(f"No suitable frame found in first {max_frames_to_check} frames")
            return None
            
        except Exception as e:
            logger.error(f"Video frame extraction failed: {str(e)}")
            return None
            
        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temporary file: {str(e)}")


# Utility functions for common operations
def create_face_processor(tolerance: float = 0.6, 
                         model: str = 'large',
                         max_image_size: int = 5 * 1024 * 1024,
                         force_mock: bool = False):
    """
    Factory function to create FaceProcessor instance
    Automatically chooses between real and mock processor based on dependencies
    
    Args:
        tolerance: Face matching tolerance (0.0-1.0, lower = stricter)
        model: Face recognition model ('small' or 'large')
        max_image_size: Maximum image size in bytes
        force_mock: Force use of mock processor for testing
        
    Returns:
        FaceProcessor or MockFaceProcessor: Configured processor instance
    """
    if FACE_RECOGNITION_AVAILABLE and not force_mock:
        logger.info("Using real FaceProcessor with face_recognition library")
        return FaceProcessor(
            tolerance=tolerance,
            model=model,
            max_image_size=max_image_size
        )
    else:
        logger.warning("face_recognition not available, using MockFaceProcessor")
        from .face_processor_mock import MockFaceProcessor
        return MockFaceProcessor(
            tolerance=tolerance,
            model=model,
            max_image_size=max_image_size
        )


def extract_face_encoding_from_image(image_data: bytes, 
                                   tolerance: float = 0.6,
                                   model: str = 'large') -> Optional[np.ndarray]:
    """
    Convenience function to extract a single face encoding from image
    
    Args:
        image_data: Raw image bytes
        tolerance: Face matching tolerance
        model: Face recognition model
        
    Returns:
        np.ndarray: Face encoding or None if extraction fails
    """
    processor = create_face_processor(tolerance=tolerance, model=model)
    result = processor.process_image(image_data)
    
    if result.success and result.face_encodings:
        return result.face_encodings[0]
    
    return None