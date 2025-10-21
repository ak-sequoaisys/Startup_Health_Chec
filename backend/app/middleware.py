from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        response.headers["X-Frame-Options"] = "DENY"
        
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://challenges.cloudflare.com; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://www.google-analytics.com; "
            "frame-src https://challenges.cloudflare.com;"
        )
        
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response
