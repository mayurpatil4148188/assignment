# Production Deployment Guide - Student Platform API

This guide provides step-by-step instructions to deploy the Student Platform API on an Ubuntu live server using Docker.

## 📋 Prerequisites

- Ubuntu server with Docker and Docker Compose installed
- Git installed on the server
- Domain name (optional, for production)
- SSL certificate (optional, for HTTPS)

## 🚀 Deployment Steps

### Step 1: Connect to Your Ubuntu Server

```bash
# SSH into your Ubuntu server
ssh username@your-server-ip

# Update system packages
sudo apt update && sudo apt upgrade -y
```

### Step 2: Install Required Dependencies

```bash
# Install Git (if not already installed)
sudo apt install git -y

# Install Docker (if not already installed)
sudo apt install docker.io docker-compose -y

# Start and enable Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (optional, to run docker without sudo)
sudo usermod -aG docker $USER
# Log out and log back in for group changes to take effect
```

### Step 3: Clone the Project

```bash
# Navigate to your desired directory
cd /opt  # or /home/username

# Clone your GitHub repository
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

# Verify the project structure
ls -la
```

### Step 4: Configure Environment Variables

```bash
# Create production environment file
cp .env.example .env  # if you have an example file
# OR create a new .env file
nano .env
```

**Add the following environment variables to `.env`:**

```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here

# Database Configuration
DATABASE_URL=postgresql://postgres:your-secure-password@db:5432/student_platform_db
# OR use individual variables:
DB_HOST=db
DB_PORT=5432
DB_NAME=student_platform_db
DB_USER=postgres
DB_PASSWORD=your-secure-password

# Application Configuration
API_HOST=0.0.0.0
API_PORT=5000
```

**Important Security Notes:**
- Generate a strong `SECRET_KEY` using: `python -c "import secrets; print(secrets.token_hex(32))"`
- Use a strong database password
- Never commit `.env` file to version control

### Step 5: Configure Docker Compose for Production

```bash
# Review and modify docker-compose.yml if needed
nano docker-compose.yml
```

**Ensure your `docker-compose.yml` has production-ready settings:**

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: student_platform_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  web:
    build: .
    ports:
      - "80:5000"  # Map to port 80 for production
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@db:5432/student_platform_db
    depends_on:
      - db
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs  # For application logs

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"  # For HTTPS
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl  # For SSL certificates
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
```

### Step 6: Build and Start the Application

```bash
# Build the Docker images
docker-compose build

# Start the services
docker-compose up -d

# Check if all services are running
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 7: Initialize the Database

```bash
# Wait for database to be ready (about 30 seconds)
sleep 30

# Run database migrations
docker-compose exec web flask db upgrade

# Create initial database tables
docker-compose exec web python database_utils.py tables

# Verify tables were created
docker-compose exec web python database_utils.py show
```

### Step 8: Test the Application

```bash
# Test if the API is responding
curl http://localhost/api/health

# Test from external access (replace with your server IP)
curl http://your-server-ip/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "message": "Student Platform API is running",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 🔧 Production Optimizations

### 1. Configure Nginx for Production

```bash
# Edit nginx configuration
nano nginx.conf
```

**Production nginx.conf:**

```nginx
events {
    worker_connections 1024;
}

http {
    upstream app {
        server web:5000;
    }

    server {
        listen 80;
        server_name your-domain.com;  # Replace with your domain

        # Redirect HTTP to HTTPS (optional)
        # return 301 https://$server_name$request_uri;

        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Static files caching
        location /static/ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # HTTPS configuration (optional)
    # server {
    #     listen 443 ssl;
    #     server_name your-domain.com;
    #     
    #     ssl_certificate /etc/nginx/ssl/cert.pem;
    #     ssl_certificate_key /etc/nginx/ssl/key.pem;
    #     
    #     location / {
    #         proxy_pass http://app;
    #         proxy_set_header Host $host;
    #         proxy_set_header X-Real-IP $remote_addr;
    #         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    #         proxy_set_header X-Forwarded-Proto $scheme;
    #     }
    # }
}
```

### 2. Set Up SSL Certificate (Optional)

```bash
# Install Certbot for Let's Encrypt
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add this line:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. Configure Firewall

```bash
# Install UFW (if not already installed)
sudo apt install ufw -y

# Configure firewall rules
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# Check status
sudo ufw status
```

## 📊 Monitoring and Maintenance

### 1. View Application Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f nginx

# View logs with timestamps
docker-compose logs -f -t
```

### 2. Monitor System Resources

```bash
# Check Docker container stats
docker stats

# Check disk usage
df -h

# Check memory usage
free -h

# Check running processes
htop
```

### 3. Backup Database

```bash
# Create backup script
nano backup_db.sh
```

**backup_db.sh:**
```bash
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="student_platform_backup_$DATE.sql"

mkdir -p $BACKUP_DIR

docker-compose exec -T db pg_dump -U postgres student_platform_db > $BACKUP_DIR/$BACKUP_FILE

# Keep only last 7 days of backups
find $BACKUP_DIR -name "student_platform_backup_*.sql" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"
```

```bash
# Make script executable
chmod +x backup_db.sh

# Run backup
./backup_db.sh

# Set up automated backups (daily at 2 AM)
crontab -e
# Add this line:
# 0 2 * * * /opt/your-repo-name/backup_db.sh
```

## 🔄 Updates and Maintenance

### 1. Update Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart services
docker-compose down
docker-compose build
docker-compose up -d

# Run database migrations if needed
docker-compose exec web flask db upgrade
```

### 2. Scale Application (Optional)

```bash
# Scale web service to multiple instances
docker-compose up -d --scale web=3

# Check scaled services
docker-compose ps
```

### 3. Health Checks

```bash
# Create health check script
nano health_check.sh
```

**health_check.sh:**
```bash
#!/bin/bash
HEALTH_URL="http://localhost/api/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -eq 200 ]; then
    echo "✅ Application is healthy"
    exit 0
else
    echo "❌ Application is unhealthy (HTTP $RESPONSE)"
    exit 1
fi
```

```bash
# Make executable and test
chmod +x health_check.sh
./health_check.sh
```

## 🚨 Troubleshooting

### Common Issues and Solutions

#### 1. Database Connection Issues
```bash
# Check if database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Test database connection
docker-compose exec web python -c "from app import create_app; from database import db; app = create_app(); app.app_context().push(); print('DB connected:', db.engine.execute('SELECT 1').scalar())"
```

#### 2. Application Not Starting
```bash
# Check application logs
docker-compose logs web

# Check if all dependencies are installed
docker-compose exec web pip list

# Restart services
docker-compose restart
```

#### 3. Port Conflicts
```bash
# Check what's using port 80
sudo netstat -tlnp | grep :80

# Kill process if needed
sudo kill -9 <PID>

# Or change port in docker-compose.yml
```

#### 4. Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER /opt/your-repo-name
chmod -R 755 /opt/your-repo-name
```

## 📈 Performance Optimization

### 1. Database Optimization

```bash
# Connect to database
docker-compose exec db psql -U postgres -d student_platform_db

# Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_students_email ON students(email);
CREATE INDEX IF NOT EXISTS idx_applications_student_id ON applications(student_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);

# Exit database
\q
```

### 2. Application Optimization

```bash
# Edit docker-compose.yml to add resource limits
nano docker-compose.yml
```

**Add resource limits:**
```yaml
services:
  web:
    # ... existing configuration
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
```

## 🔐 Security Checklist

- [ ] Strong database password set
- [ ] SECRET_KEY is secure and unique
- [ ] Firewall configured (UFW)
- [ ] SSL certificate installed (optional)
- [ ] Regular backups scheduled
- [ ] Application logs monitored
- [ ] System packages updated
- [ ] Docker images regularly updated
- [ ] Environment variables secured
- [ ] Database access restricted

## 📞 Support

If you encounter issues:

1. Check application logs: `docker-compose logs -f`
2. Verify environment variables: `cat .env`
3. Test database connection: `docker-compose exec web python database_utils.py show`
4. Check service status: `docker-compose ps`
5. Review this documentation for troubleshooting steps

## 🎉 Success!

Your Student Platform API should now be running in production on your Ubuntu server! 

**Access your API at:**
- HTTP: `http://your-server-ip/api/health`
- HTTPS: `https://your-domain.com/api/health` (if SSL configured)

**API Endpoints:**
- Health Check: `GET /api/health`
- Students: `GET /api/students/`, `POST /api/students/`
- Applications: `GET /api/applications/`, `POST /api/applications/`

Remember to monitor your application regularly and keep it updated for security and performance!
