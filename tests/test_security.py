"""Tests for security modules: encryption, auth, biometrics, continuous auth."""
import os
import sys
import time
import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
config.validate()

from security.encryption import EncryptionManager
from security.auth_middleware import AuthManager
from security.continuous_auth import ContinuousAuthenticator, BehaviorProfile


class TestEncryption:
    def setup_method(self):
        self.enc = EncryptionManager(config.ENCRYPTION_KEY)

    def test_encrypt_decrypt_roundtrip(self):
        plaintext = "sensitive biometric data"
        encrypted = self.enc.encrypt(plaintext)
        assert encrypted != plaintext
        assert self.enc.decrypt(encrypted) == plaintext

    def test_encrypt_embedding_roundtrip(self):
        embedding = [0.123, 0.456, 0.789, -0.321]
        encrypted = self.enc.encrypt_embedding(embedding)
        decrypted = self.enc.decrypt_embedding(encrypted)
        assert decrypted == pytest.approx(embedding)

    def test_hash_deterministic(self):
        h1 = EncryptionManager.hash_data("test")
        h2 = EncryptionManager.hash_data("test")
        assert h1 == h2

    def test_hash_different_inputs(self):
        h1 = EncryptionManager.hash_data("test1")
        h2 = EncryptionManager.hash_data("test2")
        assert h1 != h2

    def test_decrypt_invalid_data_raises(self):
        with pytest.raises(ValueError):
            self.enc.decrypt("not_valid_encrypted_data")

    def test_no_key_passthrough(self):
        enc = EncryptionManager(None)
        assert enc.encrypt("hello") == "hello"
        assert enc.decrypt("hello") == "hello"


class TestAuthManager:
    def setup_method(self):
        self.auth = AuthManager(secret="test_secret_key_123",
                                expiry_minutes=1, max_attempts=3,
                                lockout_seconds=10)

    def test_create_and_verify_token(self):
        token = self.auth.create_token("user1", ["face"], "low")
        payload = self.auth.verify_token(token)
        assert payload["sub"] == "user1"
        assert "face" in payload["auth_methods"]

    def test_expired_token_raises(self):
        from fastapi import HTTPException
        auth = AuthManager(secret="key", expiry_minutes=0)
        token = auth.create_token("user1", ["face"])
        time.sleep(1)
        with pytest.raises(HTTPException) as exc_info:
            auth.verify_token(token)
        assert exc_info.value.status_code == 401

    def test_invalid_token_raises(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException):
            self.auth.verify_token("invalid.token.here")

    def test_rate_limit_lockout(self):
        from fastapi import HTTPException
        ip = "192.168.1.100"
        for _ in range(2):
            self.auth.record_failed_attempt(ip)
        with pytest.raises(HTTPException) as exc_info:
            self.auth.record_failed_attempt(ip)
        assert exc_info.value.status_code == 429

    def test_clear_failed_attempts(self):
        ip = "10.0.0.1"
        self.auth.record_failed_attempt(ip)
        self.auth.clear_failed_attempts(ip)
        # Should not raise
        self.auth.check_rate_limit(ip)


class TestContinuousAuth:
    def setup_method(self):
        self.cont = ContinuousAuthenticator(threshold=0.5)

    def test_register_user(self):
        self.cont.register_user("user1")
        assert "user1" in self.cont.profiles

    def test_initial_confidence_is_high(self):
        self.cont.register_user("user1")
        assert self.cont.calculate_confidence("user1") == 1.0

    def test_risk_score_inverse_of_confidence(self):
        self.cont.register_user("user1")
        assert self.cont.get_risk_score("user1") == 0.0

    def test_unknown_user_confidence_zero(self):
        assert self.cont.calculate_confidence("unknown") == 0.0

    def test_record_activity(self):
        self.cont.record_activity("user1", "keystroke", {"timestamp": time.time()})
        assert "user1" in self.cont.profiles


class TestBehaviorProfile:
    def test_record_keystroke(self):
        p = BehaviorProfile()
        t = time.time()
        p.record_keystroke(t)
        p.record_keystroke(t + 0.2)
        assert len(p.typing_intervals) == 1

    def test_set_baseline(self):
        p = BehaviorProfile()
        t = time.time()
        for i in range(15):
            p.record_keystroke(t + i * 0.15)
        p.set_baseline()
        assert p._baseline_typing is not None
        assert "mean" in p._baseline_typing


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
