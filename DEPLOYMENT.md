# Production Deployment Documentation

## Overview

This document provides comprehensive instructions for deploying the Startup Compliance Health Check application to production on AWS EC2 with Apache, Docker, and SSL certificates.

## Deployment Architecture

The application uses a Docker Compose setup with three services:

1. **PostgreSQL Database** (postgres:16-alpine) - Stores assessment and lead data
2. **FastAPI Backend** (Python 3.12) - REST API service
3. **Nginx Frontend** (React 18 + TypeScript) - Single-page application

All services run in Docker containers on port 8080, with Apache acting as a reverse proxy on ports 80/443 with SSL termination.

## Server Requirements

- **OS**: Ubuntu 24.04 LTS or later
- **RAM**: Minimum 2GB
- **Disk**: Minimum 20GB
- **Software**: Docker 28.4.0+, Docker Compose v2.39.2+, Apache 2.4.58+

## Initial Server Setup

### 1. Install Required Software

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Install Apache
sudo apt install apache2 -y

# Install Certbot for SSL
sudo apt install certbot python3-certbot-apache -y
```

### 2. Clone Repository

```bash
# Clone to deployment directory
sudo mkdir -p /var/www
cd /var/www
sudo git clone https://github.com/ak-sequoaisys/Startup_Health_Chec.git devin05.deploymirror.com
cd devin05.deploymirror.com

# Checkout production branch
sudo git checkout devin/1761072881-remove-australia-redeploy
```

## Configuration

### 1. Environment Variables

Create a `.env` file in the project root:

```bash
cd /var/www/devin05.deploymirror.com
sudo nano .env
```

Add the following content:

```env
# PostgreSQL Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=YOUR_SECURE_PASSWORD_HERE
POSTGRES_DB=startup_health_check

# Backend Configuration
DATABASE_URL=postgresql://postgres:YOUR_SECURE_PASSWORD_HERE@postgres:5432/startup_health_check

# Frontend Configuration
VITE_API_URL=
```

**Important**: 
- Replace `YOUR_SECURE_PASSWORD_HERE` with a strong password
- Leave `VITE_API_URL` empty (nginx handles API routing)

### 2. Backend Environment

Update the backend `.env` file:

```bash
cd /var/www/devin05.deploymirror.com/backend
sudo nano .env
```

Add:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:YOUR_SECURE_PASSWORD_HERE@postgres:5432/startup_health_check

# Admin Authentication
ADMIN_USERNAME=admin
ADMIN_PASSWORD=YOUR_ADMIN_PASSWORD_HERE

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## Docker Deployment

### 1. Build Docker Images

```bash
cd /var/www/devin05.deploymirror.com

# Build all services
sudo docker-compose -f docker-compose.prod.yml build --no-cache

# Start services
sudo docker-compose -f docker-compose.prod.yml up -d
```

### 2. Verify Containers

```bash
# Check running containers
sudo docker ps

# Expected output:
# - startup_health_check_frontend_prod (port 8080)
# - startup_health_check_backend_prod (internal port 8000)
# - startup_health_check_db_prod (internal port 5432)

# Check logs
sudo docker logs startup_health_check_backend_prod
sudo docker logs startup_health_check_frontend_prod
```

## Apache Configuration

### 1. Create Virtual Host

Create Apache virtual host configuration:

```bash
sudo nano /etc/apache2/sites-available/devin05.deploymirror.com.conf
```

Add:

```apache
<VirtualHost *:80>
    ServerName devin05.deploymirror.com
    ServerAdmin admin@deploymirror.com

    # Proxy all requests to Docker container on port 8080
    ProxyPreserveHost On
    ProxyPass / http://localhost:8080/
    ProxyPassReverse / http://localhost:8080/

    # Security headers
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-XSS-Protection "1; mode=block"

    # Logs
    ErrorLog ${APACHE_LOG_DIR}/devin05-error.log
    CustomLog ${APACHE_LOG_DIR}/devin05-access.log combined
</VirtualHost>
```

### 2. Enable Required Modules

```bash
# Enable Apache modules
sudo a2enmod proxy proxy_http headers ssl rewrite

# Enable site
sudo a2ensite devin05.deploymirror.com.conf

# Test configuration
sudo apache2ctl configtest

# Reload Apache
sudo systemctl reload apache2
```

## SSL Certificate Setup

### 1. Obtain Let's Encrypt Certificate

```bash
# Run Certbot
sudo certbot --apache -d devin05.deploymirror.com --non-interactive --agree-tos --email admin@deploymirror.com --redirect
```

This will:
- Obtain an SSL certificate from Let's Encrypt
- Create an SSL virtual host configuration
- Set up automatic HTTP to HTTPS redirect
- Configure automatic certificate renewal

### 2. Verify SSL Configuration

The SSL virtual host will be created at:
```
/etc/apache2/sites-enabled/devin05.deploymirror.com-le-ssl.conf
```

It should contain:

```apache
<IfModule mod_ssl.c>
<VirtualHost *:443>
    ServerName devin05.deploymirror.com
    ServerAdmin admin@deploymirror.com

    # Proxy all requests to Docker container on port 8080
    ProxyPreserveHost On
    ProxyPass / http://localhost:8080/
    ProxyPassReverse / http://localhost:8080/

    # Security headers
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-XSS-Protection "1; mode=block"

    # Logs
    ErrorLog ${APACHE_LOG_DIR}/devin05-error.log
    CustomLog ${APACHE_LOG_DIR}/devin05-access.log combined

Include /etc/letsencrypt/options-ssl-apache.conf
SSLCertificateFile /etc/letsencrypt/live/devin05.deploymirror.com/fullchain.pem
SSLCertificateKeyFile /etc/letsencrypt/live/devin05.deploymirror.com/privkey.pem
</VirtualHost>
</IfModule>
```

## Verification

### 1. Test Application

```bash
# Test API endpoint
curl https://devin05.deploymirror.com/api/questions

# Test health check
curl https://devin05.deploymirror.com/api/healthz
```

### 2. Browser Testing

1. Open https://devin05.deploymirror.com in a browser
2. Click "Start Assessment"
3. Fill out the contact form (verify NO Australian state fields)
4. Complete the assessment
5. Verify results are displayed correctly

## Maintenance

### Update Application

```bash
cd /var/www/devin05.deploymirror.com

# Pull latest changes
sudo git pull origin devin/1761072881-remove-australia-redeploy

# Rebuild and restart containers
sudo docker-compose -f docker-compose.prod.yml down
sudo docker-compose -f docker-compose.prod.yml build --no-cache
sudo docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
sudo docker ps
```

### View Logs

```bash
# Docker container logs
sudo docker logs -f startup_health_check_backend_prod
sudo docker logs -f startup_health_check_frontend_prod
sudo docker logs -f startup_health_check_db_prod

# Apache logs
sudo tail -f /var/log/apache2/devin05-error.log
sudo tail -f /var/log/apache2/devin05-access.log
```

### Backup Database

```bash
# Create backup
sudo docker exec startup_health_check_db_prod pg_dump -U postgres startup_health_check > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
sudo docker exec -i startup_health_check_db_prod psql -U postgres startup_health_check < backup_20250101_120000.sql
```

### SSL Certificate Renewal

Certbot automatically renews certificates. To test renewal:

```bash
# Test renewal
sudo certbot renew --dry-run

# Force renewal (if needed)
sudo certbot renew --force-renewal
```

## Troubleshooting

### Container Issues

```bash
# Check container status
sudo docker ps -a

# Restart specific container
sudo docker-compose -f docker-compose.prod.yml restart backend

# View detailed logs
sudo docker logs --tail 100 startup_health_check_backend_prod

# Rebuild specific service
sudo docker-compose -f docker-compose.prod.yml build --no-cache backend
sudo docker-compose -f docker-compose.prod.yml up -d backend
```

### Database Connection Issues

1. Check PostgreSQL container is running:
   ```bash
   sudo docker ps | grep postgres
   ```

2. Verify database credentials in `.env` file

3. Check backend logs for connection errors:
   ```bash
   sudo docker logs startup_health_check_backend_prod | grep -i "database\|postgres"
   ```

4. Test database connection:
   ```bash
   sudo docker exec -it startup_health_check_db_prod psql -U postgres -d startup_health_check
   ```

### API 502 Errors

1. Check backend container is running:
   ```bash
   sudo docker ps | grep backend
   ```

2. Verify backend logs:
   ```bash
   sudo docker logs startup_health_check_backend_prod
   ```

3. Test backend directly:
   ```bash
   curl http://localhost:8080/api/questions
   ```

4. Restart backend if needed:
   ```bash
   sudo docker-compose -f docker-compose.prod.yml restart backend
   ```

### Apache Issues

```bash
# Check Apache status
sudo systemctl status apache2

# Test configuration
sudo apache2ctl configtest

# Restart Apache
sudo systemctl restart apache2

# Check Apache error logs
sudo tail -f /var/log/apache2/error.log
```

### Browser Cache Issues

If users see old content after deployment:

1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh (Ctrl+Shift+R)
3. Open in incognito/private mode
4. Add cache-busting headers in nginx.conf:

```nginx
location / {
    try_files $uri $uri/ /index.html;
    add_header Cache-Control "no-cache, no-store, must-revalidate";
}
```

## Security Considerations

1. **Firewall**: Ensure only ports 80, 443, and 22 are open
2. **SSH**: Use key-based authentication, disable password login
3. **Database**: Use strong passwords, never expose port 5432 externally
4. **Secrets**: Never commit `.env` files to version control
5. **Updates**: Regularly update system packages and Docker images
6. **Backups**: Implement regular database backups
7. **Monitoring**: Set up application and server monitoring

## Performance Optimization

1. **Docker Resources**: Allocate appropriate CPU/memory limits
2. **Database**: Configure PostgreSQL connection pooling
3. **Caching**: Implement Redis for session/API caching
4. **CDN**: Use CloudFront or similar for static assets
5. **Compression**: Enable gzip compression in nginx

## Support

For issues or questions:
- GitHub Repository: https://github.com/ak-sequoaisys/Startup_Health_Chec
- Pull Request: https://github.com/ak-sequoaisys/Startup_Health_Chec/pull/39

## Deployment Checklist

- [ ] Server provisioned with required software
- [ ] Repository cloned to `/var/www/devin05.deploymirror.com`
- [ ] Environment variables configured in `.env` files
- [ ] Docker images built successfully
- [ ] All containers running (postgres, backend, frontend)
- [ ] Apache virtual host configured
- [ ] SSL certificate obtained and configured
- [ ] Application accessible at https://devin05.deploymirror.com
- [ ] API endpoints responding correctly
- [ ] No Australian state references in contact form
- [ ] Assessment flow working end-to-end
- [ ] Database backups configured
- [ ] Monitoring and logging set up
