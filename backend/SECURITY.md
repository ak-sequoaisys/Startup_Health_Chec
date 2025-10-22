# Security Features

This document outlines the security measures implemented in the Startup Compliance Health Check API.

## Transport Security

### HTTPS + HSTS
- **Strict-Transport-Security** header enforces HTTPS for 1 year including subdomains
- Must be deployed behind HTTPS proxy/load balancer in production

## API Security

### Rate Limiting
- **60 requests per minute per IP** on public endpoints:
  - `/api/v1/assessments/start`
  - `/api/v1/reports/generate`
- **10 requests per hour per IP** on privacy endpoints:
  - `/api/v1/privacy/delete-my-data`
- Implemented using `slowapi` library
- Returns 429 status code when limit exceeded

### Input Sanitization
- All user inputs are sanitized using `bleach` library
- Removes HTML tags and dangerous characters
- Applied to:
  - Company names
  - Contact information
  - Industry fields
  - All text inputs

### CSRF Protection
- Security headers configured to prevent CSRF attacks
- X-Frame-Options: DENY
- Content-Security-Policy configured

## Bot Protection

### CAPTCHA Integration
- Supports both **Cloudflare Turnstile** and **Google reCAPTCHA v3**
- CAPTCHA verification on:
  - Assessment start form
  - PDF report generation
- Pass token via `X-Captcha-Token` header
- Falls back gracefully if CAPTCHA not configured (development mode)

### Configuration
Set environment variables:
```bash
# For Turnstile
TURNSTILE_SECRET_KEY=your_secret_key

# For reCAPTCHA
RECAPTCHA_SECRET_KEY=your_secret_key

# Disable CAPTCHA in development
DISABLE_CAPTCHA=true
```

## Data Privacy

### Email Encryption
- Email addresses can be encrypted for storage
- Uses HMAC-SHA256 encryption
- Configure with `EMAIL_ENCRYPTION_KEY` environment variable

### Delete My Data Endpoint
- **POST /api/v1/privacy/delete-my-data**
- Allows users to request deletion of all their data
- Deletes:
  - Lead records
  - Assessment results
  - Audit logs
- Rate limited to 10 requests per hour
- Returns count of deleted records

Example request:
```json
{
  "email": "user@example.com"
}
```

## Security Headers

The following security headers are automatically added to all responses:

- **Strict-Transport-Security**: Force HTTPS
- **X-Frame-Options**: Prevent clickjacking
- **X-Content-Type-Options**: Prevent MIME sniffing
- **X-XSS-Protection**: Enable XSS filtering
- **Content-Security-Policy**: Restrict resource loading
- **Referrer-Policy**: Control referrer information
- **Permissions-Policy**: Disable unnecessary browser features

## Authentication

### Admin Endpoints
- Protected with JWT/Okta SSO authentication
- Endpoints requiring auth:
  - `/api/v1/admin/trials`
  - `/api/v1/admin/trials/export`

### Configuration
```bash
OKTA_DOMAIN=your-domain.okta.com
OKTA_AUDIENCE=api://default
OKTA_ISSUER=https://your-domain.okta.com/oauth2/default

# Disable auth in development
DISABLE_AUTH=true
```

## Best Practices

### Production Deployment
1. Always deploy behind HTTPS
2. Configure CAPTCHA keys
3. Set strong `EMAIL_ENCRYPTION_KEY`
4. Configure Okta for admin access
5. Use PostgreSQL instead of in-memory database
6. Set up proper CORS origins (not wildcard)
7. Enable all security headers
8. Monitor rate limit violations
9. Regularly review audit logs

### Environment Variables
```bash
# Security
EMAIL_ENCRYPTION_KEY=strong-random-key-here
TURNSTILE_SECRET_KEY=your-turnstile-key
RECAPTCHA_SECRET_KEY=your-recaptcha-key

# Auth
OKTA_DOMAIN=your-domain.okta.com
OKTA_AUDIENCE=api://default
OKTA_ISSUER=https://your-domain.okta.com/oauth2/default

# Email
NOTIFICATION_EMAIL=service@offrd.co
SENDER_EMAIL=noreply@offrd.co
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_REGION=us-east-1

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

## Security Audit

Last updated: 2025-10-21

### Implemented
- ✅ HTTPS/HSTS headers
- ✅ Rate limiting (60/min/IP)
- ✅ Input sanitization
- ✅ CAPTCHA support (Turnstile/reCAPTCHA)
- ✅ Email encryption capability
- ✅ Delete-my-data endpoint
- ✅ Security headers (CSP, X-Frame-Options, etc.)
- ✅ JWT/SSO authentication for admin
- ✅ Audit logging

### Recommendations
- Configure CAPTCHA keys before production
- Set up proper CORS origins
- Enable PostgreSQL for production
- Regular security audits
- Monitor rate limit violations
- Review and rotate encryption keys
