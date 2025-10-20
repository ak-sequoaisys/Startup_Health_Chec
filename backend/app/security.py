import os
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import bleach
from typing import Optional


class EncryptionService:
    def __init__(self):
        encryption_key = os.getenv("ENCRYPTION_KEY")
        if not encryption_key:
            encryption_key = Fernet.generate_key().decode()
            print(f"WARNING: No ENCRYPTION_KEY found in environment. Generated temporary key: {encryption_key}")
            print("Please set ENCRYPTION_KEY in your environment for production use.")
        
        if isinstance(encryption_key, str):
            encryption_key = encryption_key.encode()
        
        if len(encryption_key) != 44:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'startup_health_check_salt',
                iterations=100000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(encryption_key))
            self.cipher = Fernet(key)
        else:
            self.cipher = Fernet(encryption_key)
    
    def encrypt(self, data: str) -> str:
        if not data:
            return data
        encrypted = self.cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        if not encrypted_data:
            return encrypted_data
        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception:
            return encrypted_data


encryption_service = EncryptionService()


def sanitize_input(text: str, allowed_tags: Optional[list] = None) -> str:
    if allowed_tags is None:
        allowed_tags = []
    
    return bleach.clean(
        text,
        tags=allowed_tags,
        strip=True
    )


def sanitize_email(email: str) -> str:
    email = bleach.clean(email, tags=[], strip=True)
    email = email.lower().strip()
    return email


def hash_ip(ip: str) -> str:
    return hashlib.sha256(ip.encode()).hexdigest()
