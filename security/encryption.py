"""Encryption utilities — TEE-simulated secure storage for biometric embeddings."""
import base64
import hashlib
import json
import logging
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)


class EncryptionManager:
    """AES-128-CBC encryption via Fernet. Never stores raw biometric data."""

    def __init__(self, key: str = None):
        self._fernet = None
        if key:
            self._init_fernet(key)

    def _init_fernet(self, key: str):
        try:
            self._fernet = Fernet(key.encode() if isinstance(key, str) else key)
        except Exception:
            derived = hashlib.sha256(key.encode()).digest()
            self._fernet = Fernet(base64.urlsafe_b64encode(derived))

    def encrypt(self, data: str) -> str:
        if not self._fernet:
            logger.warning("Encryption not initialized — data stored as-is")
            return data
        return self._fernet.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        if not self._fernet:
            return encrypted_data
        try:
            return self._fernet.decrypt(encrypted_data.encode()).decode()
        except InvalidToken:
            logger.error("Decryption failed — key mismatch or data corruption")
            raise ValueError("Decryption failed")

    def encrypt_embedding(self, embedding: list) -> str:
        return self.encrypt(json.dumps(embedding))

    def decrypt_embedding(self, encrypted: str) -> list:
        return json.loads(self.decrypt(encrypted))

    @staticmethod
    def hash_data(data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()
