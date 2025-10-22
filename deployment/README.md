# Deployment Configuration Files

This directory contains the deployment configuration files used for hosting the Startup Health Check application on an Apache web server.

## Directory Structure

```
deployment/
├── apache/
│   └── virtual-host-ssl.conf    # Apache virtual host configuration with SSL
├── systemd/
│   └── startup-health-check-backend.service  # Systemd service for backend
└── README.md                     # This file
```

## Apache Configuration

**File**: `apache/virtual-host-ssl.conf`

This is the Apache virtual host configuration file that:
- Serves the frontend static files from `/var/www/startup-health-check/frontend/dist`
- Proxies API requests (`/api/v1/*`) to the backend running on port 8001
- Includes SSL certificates from Let's Encrypt
- Handles SPA routing (all non-file requests go to index.html)
- Adds security headers

**Installation**:
```bash
# Copy to Apache sites-available
sudo cp apache/virtual-host-ssl.conf /etc/apache2/sites-available/yourdomain.com-le-ssl.conf

# Edit the file to update:
# - ServerName (your domain)
# - SSL certificate paths
# - DocumentRoot path

# Enable the site
sudo a2ensite yourdomain.com-le-ssl.conf

# Enable required Apache modules
sudo a2enmod ssl proxy proxy_http rewrite headers

# Test configuration
sudo apache2ctl configtest

# Reload Apache
sudo systemctl reload apache2
```

## Systemd Service

**File**: `systemd/startup-health-check-backend.service`

This systemd service file runs the FastAPI backend as a managed service that:
- Runs on port 8001 (configurable)
- Auto-restarts on failure
- Runs as the ubuntu user
- Uses Poetry for dependency management

**Installation**:
```bash
# Copy to systemd directory
sudo cp systemd/startup-health-check-backend.service /etc/systemd/system/

# Edit the file to update:
# - User (if not ubuntu)
# - WorkingDirectory (path to backend)
# - Port (if not 8001)

# Reload systemd
sudo systemctl daemon-reload

# Enable and start the service
sudo systemctl enable startup-health-check-backend
sudo systemctl start startup-health-check-backend

# Check status
sudo systemctl status startup-health-check-backend
```

## Environment Variables

The application requires environment variable files:

**Backend** (`backend/.env`):
```
NOTIFICATION_EMAIL=service@offrd.co
SENDER_EMAIL=noreply@offrd.co
LOG_LEVEL=INFO
LOG_FORMAT=json
ENVIRONMENT=production
```

**Frontend** (`frontend/.env`):
```
VITE_API_URL=https://yourdomain.com
```

**Important**: The frontend `VITE_API_URL` should NOT include `/api` suffix as the frontend code automatically appends `/api/v1/...` to the base URL.

## Deployment Steps

1. **Prepare the server**:
   ```bash
   # Install required software
   sudo apt update
   sudo apt install apache2 python3 python3-pip nodejs npm certbot python3-certbot-apache
   
   # Install Poetry
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Deploy application files**:
   ```bash
   # Create application directory
   sudo mkdir -p /var/www/startup-health-check
   sudo chown $USER:$USER /var/www/startup-health-check
   
   # Copy application files
   # (use git clone, scp, or rsync)
   ```

3. **Install backend dependencies**:
   ```bash
   cd /var/www/startup-health-check/backend
   poetry install --no-root
   ```

4. **Build frontend**:
   ```bash
   cd /var/www/startup-health-check/frontend
   npm install
   npx vite build
   ```

5. **Configure environment variables**:
   ```bash
   # Create backend .env file
   cp backend/.env.example backend/.env
   # Edit backend/.env with your values
   
   # Create frontend .env file
   cp frontend/.env.example frontend/.env
   # Edit frontend/.env with your domain
   ```

6. **Set up systemd service**:
   ```bash
   sudo cp deployment/systemd/startup-health-check-backend.service /etc/systemd/system/
   # Edit the file if needed
   sudo systemctl daemon-reload
   sudo systemctl enable --now startup-health-check-backend
   ```

7. **Configure Apache**:
   ```bash
   # Obtain SSL certificate
   sudo certbot --apache -d yourdomain.com
   
   # Copy and configure virtual host
   sudo cp deployment/apache/virtual-host-ssl.conf /etc/apache2/sites-available/yourdomain.com-le-ssl.conf
   # Edit the file with your domain and paths
   
   # Enable modules and site
   sudo a2enmod ssl proxy proxy_http rewrite headers
   sudo a2ensite yourdomain.com-le-ssl.conf
   sudo apache2ctl configtest
   sudo systemctl reload apache2
   ```

8. **Verify deployment**:
   ```bash
   # Check backend is running
   curl http://localhost:8001/api/v1/questions
   
   # Check frontend is accessible
   curl https://yourdomain.com
   
   # Test the complete flow in browser
   ```

## Monitoring

**Backend logs**:
```bash
# View recent logs
sudo journalctl -u startup-health-check-backend -n 50

# Follow logs in real-time
sudo journalctl -u startup-health-check-backend -f
```

**Apache logs**:
```bash
# Error logs
sudo tail -f /var/log/apache2/error.log

# Access logs
sudo tail -f /var/log/apache2/access.log
```

## Troubleshooting

See the main [HOSTING_DOCUMENTATION.md](../HOSTING_DOCUMENTATION.md) for detailed troubleshooting steps.

## Current Deployment

The application is currently deployed at:
- **Domain**: https://devin05.deploymirror.com
- **Server**: 34.211.35.174
- **Backend Port**: 8001
