"""Centralized configuration management. Zero hardcoded secrets."""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class Config:
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    SCREENSHOTS_DIR = DATA_DIR / "screenshots"
    SECURE_DIR = DATA_DIR / "secure"
    MEMORY_FILE = DATA_DIR / "memory.json"

    # Security — loaded from env, never hardcoded
    JWT_SECRET = os.getenv("JWT_SECRET", "")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRY_MINUTES = int(os.getenv("JWT_EXPIRY_MINUTES", "30"))
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "")

    # API
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    API_HOST = os.getenv("API_HOST", "127.0.0.1")
    API_PORT = int(os.getenv("API_PORT", "8000"))

    # Auth thresholds
    FACE_CONFIDENCE_THRESHOLD = float(os.getenv("FACE_CONFIDENCE_THRESHOLD", "0.6"))
    CONTINUOUS_AUTH_THRESHOLD = float(os.getenv("CONTINUOUS_AUTH_THRESHOLD", "0.5"))
    MAX_AUTH_ATTEMPTS = int(os.getenv("MAX_AUTH_ATTEMPTS", "5"))
    AUTH_LOCKOUT_SECONDS = int(os.getenv("AUTH_LOCKOUT_SECONDS", "300"))

    @classmethod
    def ensure_directories(cls):
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.SECURE_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def validate(cls):
        """Generate missing secrets at runtime with warnings."""
        warnings = []
        if not cls.JWT_SECRET:
            cls.JWT_SECRET = os.urandom(32).hex()
            warnings.append("JWT_SECRET not set — using ephemeral key")
        if not cls.ENCRYPTION_KEY:
            from cryptography.fernet import Fernet
            cls.ENCRYPTION_KEY = Fernet.generate_key().decode()
            warnings.append("ENCRYPTION_KEY not set — using ephemeral key")
        return warnings


config = Config()
config.ensure_directories()
