import bleach
from typing import Any, Dict
from fastapi import Request, HTTPException
import hashlib
import hmac
import os


def sanitize_string(value: str) -> str:
    """Sanitize string input to prevent XSS attacks."""
    return bleach.clean(value, tags=[], strip=True)


def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively sanitize dictionary values."""
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_string(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_string(item) if isinstance(item, str)
                else sanitize_dict(item) if isinstance(item, dict)
                else item
                for item in value
            ]
        else:
            sanitized[key] = value
    return sanitized


def encrypt_email(email: str) -> str:
    """Encrypt email address for storage."""
    secret_key = os.getenv("EMAIL_ENCRYPTION_KEY", "default-secret-key-change-in-production")
    return hmac.new(
        secret_key.encode(),
        email.encode(),
        hashlib.sha256
    ).hexdigest()


def verify_csrf_token(request: Request, token: str) -> bool:
    """Verify CSRF token (placeholder for future implementation)."""
    expected_token = request.headers.get("X-CSRF-Token")
    return token == expected_token if expected_token else True


async def verify_turnstile_token(token: str) -> bool:
    """Verify Cloudflare Turnstile token."""
    import httpx
    
    secret_key = os.getenv("TURNSTILE_SECRET_KEY")
    if not secret_key:
        if os.getenv("DISABLE_CAPTCHA") == "true":
            return True
        return False
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                json={
                    "secret": secret_key,
                    "response": token
                }
            )
            result = response.json()
            return result.get("success", False)
        except Exception:
            return False


async def verify_recaptcha_token(token: str) -> bool:
    """Verify Google reCAPTCHA token."""
    import httpx
    
    secret_key = os.getenv("RECAPTCHA_SECRET_KEY")
    if not secret_key:
        if os.getenv("DISABLE_CAPTCHA") == "true":
            return True
        return False
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data={
                    "secret": secret_key,
                    "response": token
                }
            )
            result = response.json()
            return result.get("success", False) and result.get("score", 0) >= 0.5
        except Exception:
            return False
