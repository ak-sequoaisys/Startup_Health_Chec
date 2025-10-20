from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import os
import jwt
from jwt import PyJWKClient


security = HTTPBearer()


OKTA_DOMAIN = os.getenv("OKTA_DOMAIN", "")
OKTA_AUDIENCE = os.getenv("OKTA_AUDIENCE", "api://default")
OKTA_ISSUER = os.getenv("OKTA_ISSUER", f"https://{OKTA_DOMAIN}/oauth2/default")


def verify_token(token: str) -> dict:
    if not OKTA_DOMAIN:
        if os.getenv("DISABLE_AUTH") == "true":
            return {"sub": "admin", "email": "admin@example.com"}
        raise HTTPException(status_code=500, detail="OKTA_DOMAIN not configured")
    
    try:
        jwks_url = f"{OKTA_ISSUER}/v1/keys"
        jwks_client = PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=OKTA_AUDIENCE,
            issuer=OKTA_ISSUER,
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    token = credentials.credentials
    return verify_token(token)
