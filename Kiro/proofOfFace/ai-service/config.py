"""
Configuration module for ProofOfFace AI Service
Handles environment-specific settings and security configurations
"""

import os
from typing import Optional
from dataclasses import dataclass
from cryptography.fernet import Fernet


@dataclass
class Config:
    """Base configuration class with common settings"""
    
    # Flask Configuration
    SECRET_KEY: str = os.getenv('SECRET_KEY', Fernet.generate_key().decode())
    DEBUG: bool = False
    TESTING: bool = False
    
    # Server Configuration
    HOST: str = os.getenv('HOST', '0.0.0.0')
    PORT: int = int(os.getenv('PORT', 5000))
    
    # CORS Configuration
    CORS_ORIGINS: str = os.getenv('CORS_ORIGINS', '*')
    
    # Face Recognition Configuration
    FACE_RECOGNITION_TOLERANCE: float = float(os.getenv('FACE_RECOGNITION_TOLERANCE', 0.6))
    FACE_RECOGNITION_MODEL: str = os.getenv('FACE_RECOGNITION_MODEL', 'large')  # 'small' or 'large'
    MAX_IMAGE_SIZE: int = int(os.getenv('MAX_IMAGE_SIZE', 5 * 1024 * 1024))  # 5MB
    ALLOWED_IMAGE_EXTENSIONS: set = None
    
    # Encryption Configuration
    ENCRYPTION_KEY: Optional[str] = os.getenv('ENCRYPTION_KEY')
    
    # Substrate Node Configuration
    SUBSTRATE_NODE_URL: str = os.getenv('SUBSTRATE_NODE_URL', 'ws://localhost:9944')
    SUBSTRATE_ACCOUNT_SEED: Optional[str] = os.getenv('SUBSTRATE_ACCOUNT_SEED')
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT: str = os.getenv('LOG_FORMAT', 'json')  # 'json' or 'text'
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv('RATE_LIMIT_PER_MINUTE', 60))
    
    # File Storage
    UPLOAD_FOLDER: str = os.getenv('UPLOAD_FOLDER', '/tmp/proofofface_uploads')
    
    def __post_init__(self):
        """Post-initialization validation and setup"""
        # Set default allowed extensions if not set
        if self.ALLOWED_IMAGE_EXTENSIONS is None:
            self.ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
        
        # Ensure upload folder exists
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        
        # Generate encryption key if not provided
        if not self.ENCRYPTION_KEY:
            self.ENCRYPTION_KEY = Fernet.generate_key().decode()
            print("⚠️  Generated new encryption key. Set ENCRYPTION_KEY environment variable for production!")


@dataclass
class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG: bool = True
    LOG_LEVEL: str = 'DEBUG'
    CORS_ORIGINS: str = '*'  # Allow all origins in development
    
    def __post_init__(self):
        super().__post_init__()
        print("🔧 Running in DEVELOPMENT mode")


@dataclass
class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG: bool = False
    TESTING: bool = False
    LOG_LEVEL: str = 'WARNING'
    
    # Security: Restrict CORS in production
    CORS_ORIGINS: str = os.getenv('CORS_ORIGINS', 'https://proofofface.com')
    
    # Enhanced security settings
    FACE_RECOGNITION_TOLERANCE: float = 0.5  # Stricter matching in production
    RATE_LIMIT_PER_MINUTE: int = 30  # Lower rate limit in production
    
    def __post_init__(self):
        super().__post_init__()
        
        # Validate required production environment variables
        required_vars = ['SECRET_KEY', 'ENCRYPTION_KEY', 'SUBSTRATE_ACCOUNT_SEED']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
        
        print("🚀 Running in PRODUCTION mode")


@dataclass
class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING: bool = True
    DEBUG: bool = True
    LOG_LEVEL: str = 'DEBUG'
    
    # Use in-memory or test-specific settings
    UPLOAD_FOLDER: str = '/tmp/proofofface_test_uploads'
    FACE_RECOGNITION_TOLERANCE: float = 0.8  # More lenient for testing
    
    def __post_init__(self):
        super().__post_init__()
        print("🧪 Running in TESTING mode")


def get_config() -> Config:
    """
    Factory function to get the appropriate configuration based on environment
    
    Returns:
        Config: Configuration instance based on FLASK_ENV environment variable
    """
    env = os.getenv('FLASK_ENV', 'development').lower()
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
    }
    
    config_class = config_map.get(env, DevelopmentConfig)
    return config_class()


# Global configuration instance
config = get_config()


# Configuration validation helper
def validate_config(config_instance: Config) -> bool:
    """
    Validate configuration settings
    
    Args:
        config_instance: Configuration instance to validate
        
    Returns:
        bool: True if configuration is valid
        
    Raises:
        ValueError: If configuration is invalid
    """
    # Validate face recognition tolerance
    if not 0.0 <= config_instance.FACE_RECOGNITION_TOLERANCE <= 1.0:
        raise ValueError("FACE_RECOGNITION_TOLERANCE must be between 0.0 and 1.0")
    
    # Validate face recognition model
    if config_instance.FACE_RECOGNITION_MODEL not in ['small', 'large']:
        raise ValueError("FACE_RECOGNITION_MODEL must be 'small' or 'large'")
    
    # Validate log level
    valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if config_instance.LOG_LEVEL.upper() not in valid_log_levels:
        raise ValueError(f"LOG_LEVEL must be one of: {valid_log_levels}")
    
    # Validate port range
    if not 1 <= config_instance.PORT <= 65535:
        raise ValueError("PORT must be between 1 and 65535")
    
    return True


# Validate configuration on import
validate_config(config)