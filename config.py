"""
Configuration module for Audio Extractor
"""
import os
from pathlib import Path
from typing import Dict, List


class Config:
    """Configuration class for the audio extractor application"""
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8001"))
    
    # File Processing
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "524288000"))  # 500MB
    TEMP_DIR: Path = Path(os.getenv("TEMP_DIR", "temp_files"))
    
    # FFmpeg Configuration
    FFMPEG_TIMEOUT: int = int(os.getenv("FFMPEG_TIMEOUT", "300"))  # 5 minutes
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/audio_extractor.log")
    
    # Security
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8001"
    ]
    
    # Supported formats and codecs
    SUPPORTED_FORMATS: Dict[str, str] = {
        "mp3": "libmp3lame",
        "wav": "pcm_s16le",
        "ogg": "libvorbis",
        "aac": "aac",
        "flac": "flac"
    }
    
    # File type validation
    ALLOWED_VIDEO_TYPES: List[str] = [
        "video/mp4",
        "video/avi",
        "video/mov",
        "video/wmv",
        "video/flv",
        "video/webm",
        "video/mkv"
    ]
    
    @classmethod
    def create_directories(cls) -> None:
        """Create necessary directories"""
        cls.TEMP_DIR.mkdir(exist_ok=True)
        
        # Create logs directory if specified
        if cls.LOG_FILE:
            log_dir = Path(cls.LOG_FILE).parent
            log_dir.mkdir(exist_ok=True)
    
    @classmethod
    def validate_config(cls) -> None:
        """Validate configuration settings"""
        if cls.MAX_FILE_SIZE <= 0:
            raise ValueError("MAX_FILE_SIZE must be positive")
        
        if cls.FFMPEG_TIMEOUT <= 0:
            raise ValueError("FFMPEG_TIMEOUT must be positive")
        
        if cls.PORT <= 0 or cls.PORT > 65535:
            raise ValueError("PORT must be between 1 and 65535")


# Initialize configuration
config = Config()
config.create_directories()
config.validate_config()