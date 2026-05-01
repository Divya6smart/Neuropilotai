"""JWT authentication + rate limiting middleware."""
import time
import logging
import jwt
from collections import defaultdict
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)
security_scheme = HTTPBearer(auto_error=False)


class AuthManager:
    """JWT-based auth with rate limiting and brute-force lockout."""

    def __init__(self, secret: str, algorithm: str = "HS256",
                 expiry_minutes: int = 30, max_attempts: int = 5,
                 lockout_seconds: int = 300):
        self.secret = secret
        self.algorithm = algorithm
        self.expiry_minutes = expiry_minutes
        self.max_attempts = max_attempts
        self.lockout_seconds = lockout_seconds
        self._failed_attempts: dict[str, list[float]] = defaultdict(list)
        self._lockouts: dict[str, float] = {}

    def create_token(self, user_id: str, auth_methods: list,
                     risk_level: str = "low") -> str:
        now = time.time()
        payload = {
            "sub": user_id,
            "iat": now,
            "exp": now + (self.expiry_minutes * 60),
            "auth_methods": auth_methods,
            "risk_level": risk_level,
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def verify_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, self.secret, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            raise HTTPException(401, "Token expired — re-authenticate")
        except jwt.InvalidTokenError:
            raise HTTPException(401, "Invalid token")

    def check_rate_limit(self, client_ip: str):
        if client_ip in self._lockouts:
            if time.time() < self._lockouts[client_ip]:
                remaining = int(self._lockouts[client_ip] - time.time())
                raise HTTPException(429, f"Locked out. Retry in {remaining}s.")
            del self._lockouts[client_ip]
            self._failed_attempts[client_ip] = []

    def record_failed_attempt(self, client_ip: str):
        now = time.time()
        attempts = self._failed_attempts[client_ip]
        attempts.append(now)
        self._failed_attempts[client_ip] = [
            t for t in attempts if now - t < self.lockout_seconds
        ]
        if len(self._failed_attempts[client_ip]) >= self.max_attempts:
            self._lockouts[client_ip] = now + self.lockout_seconds
            logger.warning(f"Locked out {client_ip} after {self.max_attempts} failures")
            raise HTTPException(429, f"Too many failures. Locked {self.lockout_seconds}s.")

    def clear_failed_attempts(self, client_ip: str):
        self._failed_attempts.pop(client_ip, None)
        self._lockouts.pop(client_ip, None)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
):
    """FastAPI dependency — extracts & validates JWT from Authorization header."""
    auth_manager: AuthManager = request.app.state.auth_manager
    if not credentials:
        raise HTTPException(401, "Authentication required")
    return auth_manager.verify_token(credentials.credentials)
