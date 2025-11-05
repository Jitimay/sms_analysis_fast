#!/usr/bin/env python3
"""
Simplified Face Processing Module for ProofOfFace AI Service
Uses mock processor to avoid dependency issues during development
"""

import logging
from .face_processor_mock import MockFaceProcessor

logger = logging.getLogger(__name__)


def create_face_processor(tolerance: float = 0.6, 
                         model: str = 'large',
                         max_image_size: int = 5 * 1024 * 1024,
                         force_mock: bool = False):
    """
    Factory function to create FaceProcessor instance
    Currently uses MockFaceProcessor to avoid dependency issues
    
    Args:
        tolerance: Face matching tolerance (0.0-1.0, lower = stricter)
        model: Face recognition model ('small' or 'large')
        max_image_size: Maximum image size in bytes
        force_mock: Force use of mock processor for testing (ignored for now)
        
    Returns:
        MockFaceProcessor: Configured processor instance
    """
    logger.info("Using MockFaceProcessor for development")
    return MockFaceProcessor(
        tolerance=tolerance,
        model=model,
        max_image_size=max_image_size
    )


# For backward compatibility, export the main classes
FaceProcessor = MockFaceProcessor