# Security & Privacy Hardening

This document describes the security and privacy features implemented in the Startup Compliance Health Check Tool.

## Security Features

### 1. Transport Security

#### HTTPS & HSTS
- **Strict-Transport-Security** header enforces HTTPS connections for 1 year
- **X-Content-Type-Options** prevents MIME-type sniffing
- **X-Frame-Options** prevents clickjacking attacks
- **X-XSS-Protection** enables browser XSS filtering
- **Referrer-Policy** controls referrer information
- **Permissions-Policy** restricts access to sensitive browser features

### 2. API Security

#### Rate Limiting
- Implemented using SlowAPI
- **60 requests per minute per IP** for most endpoints
- **10 requests per hour per IP** for data deletion endpoint
- Prevents brute force attacks and API abuse

#### Input Sanitization
- All user inputs are sanitized using bleach library
- HTML tags are stripped from text inputs
- Email addresses are normalized and sanitized
- Prevents XSS and injection attacks

#### CSRF Protection
- Rate limiting acts as CSRF mitigation
- Security headers prevent cross-origin attacks
- Turnstile verification adds additional layer

### 3. Bot Protection

#### Cloudflare Turnstile
- Integrated on critical user actions:
  - Starting an assessment (contact form submission)
  - Downloading PDF reports
- Uses test site key `1x00000000000000000000AA` by default
- Configure production site key via `VITE_TURNSTILE_SITE_KEY` environment variable
- Get your site key from: https://dash.cloudflare.com/

### 4. Data Privacy

#### Email Encryption
- All email addresses are encrypted at rest using Fernet symmetric encryption
- Encryption key is configurable via `ENCRYPTION_KEY` environment variable
- If no key is provided, a temporary key is generated (not recommended for production)
- Generate a secure key using:
  ```bash
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  ```

#### Delete My Data Endpoint
- **Endpoint**: `POST /api/v1/privacy/delete-my-data`
- **Rate Limit**: 10 requests per hour per IP
- **Parameters**: `email` (string)
- Searches for and deletes all data associated with an email address
- Handles both encrypted and unencrypted email formats
- Returns count of deleted records

Example usage:
```bash
curl -X POST "http://localhost:8000/api/v1/privacy/delete-my-data?email=user@example.com"
```

Response:
```json
{
  "status": "success",
  "message": "Data deletion request processed. 2 records found and marked for deletion.",
  "email": "user@example.com"
}
```

## Configuration

### Backend Environment Variables

```bash
# Security Configuration
ENCRYPTION_KEY=your-encryption-key-here
```

### Frontend Environment Variables

```bash
# Cloudflare Turnstile
VITE_TURNSTILE_SITE_KEY=your-turnstile-site-key
```

## Production Deployment Checklist

- [ ] Set a strong `ENCRYPTION_KEY` in production environment
- [ ] Configure production Cloudflare Turnstile site key
- [ ] Enable HTTPS/TLS on your web server
- [ ] Configure CORS to allow only trusted origins (update `allow_origins` in `main.py`)
- [ ] Review and adjust rate limits based on your traffic patterns
- [ ] Set up monitoring for rate limit violations
- [ ] Implement backup and recovery procedures for encrypted data
- [ ] Document encryption key management procedures
- [ ] Set up regular security audits
- [ ] Configure logging for security events

## Security Best Practices

1. **Never commit secrets**: Keep `.env` files out of version control
2. **Rotate encryption keys**: Implement a key rotation strategy for production
3. **Monitor rate limits**: Set up alerts for unusual API usage patterns
4. **Regular updates**: Keep dependencies up to date for security patches
5. **Audit logs**: Review audit logs regularly for suspicious activity
6. **Backup encrypted data**: Ensure you can recover encrypted data if needed
7. **Test security features**: Regularly test rate limiting, input sanitization, and bot protection

## Compliance

This implementation helps meet the following security requirements:

- **Transport Security**: HTTPS + HSTS headers
- **API Security**: CSRF protection, input sanitization, rate limiting (60/min/IP)
- **Bot Protection**: Turnstile/reCAPTCHA on Start Assessment and Report Download
- **Data Privacy**: Email encryption at rest, delete-my-data endpoint

## Support

For security concerns or to report vulnerabilities, please contact the development team.
