import hashlib
import hmac
import base64
import json
import time
import secrets
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import SECRET_KEY, TOKEN_EXPIRE_SECONDS

security = HTTPBearer(auto_error=False)

def hash_password(password: str, salt: Optional[str] = None) -> str:
    """
    Hash a password using PBKDF2-HMAC-SHA256.
    If salt is None, generates a cryptographically random 16-byte salt and returns salt$hash.
    If salt is provided (or legacy empty salt), uses that salt.
    """
    if salt is None:
        salt_bytes = secrets.token_bytes(16)
        salt_hex = salt_bytes.hex()
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt_bytes, 100000)
        return f"{salt_hex}${pwd_hash.hex()}"
    elif salt == "legacy":
        salt_bytes = b'devhub_secure_salt_2026'
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt_bytes, 100000)
        return pwd_hash.hex()
    else:
        try:
            salt_bytes = bytes.fromhex(salt)
        except Exception:
            salt_bytes = salt.encode('utf-8')
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt_bytes, 100000)
        return f"{salt}${pwd_hash.hex()}"

def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Verify password against salt$hash or legacy static salt hash using constant-time comparison."""
    if not plain_password or not stored_hash:
        return False
    if "$" in stored_hash:
        try:
            salt_hex, expected_hash = stored_hash.split("$", 1)
            salt_bytes = bytes.fromhex(salt_hex)
            computed_hash = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt_bytes, 100000).hex()
            return hmac.compare_digest(computed_hash, expected_hash)
        except Exception:
            return False
    else:
        # Legacy backward-compatibility for demo seeds
        legacy_salt = b'devhub_secure_salt_2026'
        computed = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), legacy_salt, 100000).hex()
        return hmac.compare_digest(computed, stored_hash)

def create_access_token(data: dict) -> str:
    """Create a signed JWT token containing user payload."""
    payload = data.copy()
    payload["exp"] = int(time.time()) + TOKEN_EXPIRE_SECONDS
    header = {"alg": "HS256", "typ": "JWT"}
    
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    
    signature_input = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(SECRET_KEY.encode(), signature_input, hashlib.sha256).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    
    return f"{header_b64}.{payload_b64}.{signature_b64}"

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and verify token signature and expiration."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, signature_b64 = parts
        
        signature_input = f"{header_b64}.{payload_b64}".encode()
        expected_sig = hmac.new(SECRET_KEY.encode(), signature_input, hashlib.sha256).digest()
        expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).decode().rstrip("=")
        
        if not hmac.compare_digest(signature_b64, expected_sig_b64):
            return None
            
        padding = "=" * ((4 - len(payload_b64) % 4) % 4)
        payload_bytes = base64.urlsafe_b64decode(payload_b64 + padding)
        payload = json.loads(payload_bytes.decode())
        
        if payload.get("exp", 0) < time.time():
            return None  # Token expired
            
        return payload
    except Exception:
        return None

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)) -> Dict[str, Any]:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required"
        )
    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token"
        )
    return payload

def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)) -> Optional[Dict[str, Any]]:
    if not credentials:
        return None
    return decode_token(credentials.credentials)
