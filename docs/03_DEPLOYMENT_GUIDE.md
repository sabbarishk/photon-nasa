# Deployment Guide

## Photon-NASA Installation, Setup, and Production Deployment

---

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Docker Deployment](#docker-deployment)
3. [AWS Deployment](#aws-deployment)
4. [Environment Variables](#environment-variables)
5. [Security Configuration](#security-configuration)
6. [Production Checklist](#production-checklist)
7. [Monitoring & Maintenance](#monitoring--maintenance)

---

## 1. LOCAL DEVELOPMENT SETUP

### Prerequisites

- **Python:** 3.10 or higher
- **Node.js:** 18 or higher
- **npm:** 9 or higher
- **Git:** For cloning repository
- **Redis (optional):** For rate limiting

### Backend Setup

#### Clone Repository
```bash
git clone https://github.com/sabbarishk/photon-nasa.git
cd photon-nasa/photon
```

#### Create Virtual Environment
```powershell
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

#### Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Download Embedding Model (Optional)
```bash
# Pre-download model to avoid startup delay
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

#### Create Environment File
```bash
# Create .env file
cp .env.example .env

# Edit .env (optional)
# HF_TOKEN=your_token_here  # Fallback embedding API
# VECTOR_STORE_BACKEND=file  # or 'chroma'
```

#### Ingest Sample Data
```bash
# Ingest 34 verified datasets
python -m scripts.bulk_ingest --clear

# Or ingest from NASA CMR
python -m scripts.ingest_sample --keyword MODIS --limit 20
python -m scripts.ingest_sample --keyword GISS --limit 20
```

#### Start Backend
```bash
# Option 1: Using PowerShell script (recommended)
.\scripts\run_server.ps1 -SkipAuth

# Option 2: Direct uvicorn
uvicorn app.main:app --reload --port 8000

# Option 3: With authentication
.\scripts\run_server.ps1
```

**Verify Backend:**
```bash
curl http://localhost:8000/health
# Should return: {"status":"ok"}
```

---

### Frontend Setup

#### Navigate to Frontend
```bash
cd ../frontend
```

#### Install Dependencies
```bash
npm install
```

#### Create Environment File
```bash
# Create .env
echo "VITE_API_URL=http://localhost:8000" > .env
```

#### Start Development Server
```bash
npm run dev
```

**Access Application:**
```
Open browser: http://localhost:5173
```

---

### Full System Test

#### Backend Health Check
```bash
curl http://localhost:8000/health
```

#### Search Test
```bash
curl -X POST http://localhost:8000/query/ \
  -H "Content-Type: application/json" \
  -d '{"query":"MODIS temperature","top_k":3}'
```

#### Workflow Generation Test
```bash
curl -X POST http://localhost:8000/workflow/generate \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_url": "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv",
    "dataset_format": "csv",
    "variable": "J-D",
    "title": "Test Notebook"
  }'
```

#### Frontend Test
1. Open http://localhost:5173
2. Enter query: "MODIS temperature"
3. Click Search
4. Verify results appear
5. Click "Generate Workflow"
6. Verify notebook generates

---

## 2. DOCKER DEPLOYMENT

### Backend Dockerfile

```dockerfile
# photon/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download embedding model (saves startup time)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Build & Run Backend
```bash
# Build image
docker build -t photon-backend:latest -f photon/Dockerfile photon/

# Run container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/photon/data:/app/data \
  -e PHOTON_SKIP_AUTH=1 \
  --name photon-backend \
  photon-backend:latest
```

---

### Frontend Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production image with Nginx
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### Nginx Configuration
```nginx
# frontend/nginx.conf
server {
    listen 80;
    server_name _;
    
    root /usr/share/nginx/html;
    index index.html;
    
    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Gzip compression
    gzip on;
    gzip_types text/css application/javascript application/json;
    gzip_min_length 1000;
}
```

#### Build & Run Frontend
```bash
# Build image
docker build -t photon-frontend:latest -f frontend/Dockerfile frontend/

# Run container
docker run -d \
  -p 80:80 \
  --name photon-frontend \
  photon-frontend:latest
```

---

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./photon
    ports:
      - "8000:8000"
    volumes:
      - ./photon/data:/app/data
    environment:
      - PHOTON_SKIP_AUTH=1
      - REDIS_URL=redis://redis:6379
      - VECTOR_STORE_BACKEND=file
    depends_on:
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
  
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    environment:
      - VITE_API_URL=http://localhost:8000
    restart: unless-stopped
    depends_on:
      - backend
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

**Usage:**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

---

## 3. AWS DEPLOYMENT

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                          AWS Cloud                          │
│                                                             │
│  ┌───────────────┐         ┌──────────────────────────┐   │
│  │  CloudFront   │         │   Application Load       │   │
│  │  (CDN)        │         │   Balancer (ALB)         │   │
│  │  Static Files │         └──────────┬───────────────┘   │
│  └───────────────┘                    │                    │
│                           ┌───────────┴──────────┐         │
│                           │                      │         │
│                    ┌──────▼──────┐        ┌─────▼──────┐  │
│                    │  Backend    │        │  Backend   │  │
│                    │  Instance   │        │  Instance  │  │
│                    │  (EC2/ECS)  │        │  (EC2/ECS) │  │
│                    └──────┬──────┘        └─────┬──────┘  │
│                           │                      │         │
│                           └───────────┬──────────┘         │
│                                       │                    │
│                             ┌─────────▼──────────┐         │
│                             │  ElastiCache       │         │
│                             │  (Redis)           │         │
│                             └────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### Option 1: Elastic Beanstalk (Easiest)

#### Install EB CLI
```bash
pip install awsebcli
```

#### Initialize Backend
```bash
cd photon

# Initialize EB application
eb init -p python-3.10 photon-backend

# Create environment
eb create photon-backend-prod

# Deploy
eb deploy

# View status
eb status

# View logs
eb logs

# Open in browser
eb open
```

#### Configure Environment Variables
```bash
eb setenv PHOTON_SKIP_AUTH=0 REDIS_URL=redis://your-elasticache-endpoint:6379
```

---

### Option 2: EC2 Manual Deployment

#### Launch EC2 Instance
1. Launch Ubuntu 22.04 t3.medium instance
2. Configure security group (ports 22, 80, 8000)
3. SSH into instance

#### Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.10 python3-pip python3-venv -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Install Nginx
sudo apt install nginx -y

# Install Docker (optional)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

#### Deploy Backend
```bash
# Clone repository
git clone https://github.com/sabbarishk/photon-nasa.git
cd photon-nasa/photon

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Ingest data
python -m scripts.bulk_ingest --clear

# Create systemd service
sudo nano /etc/systemd/system/photon-backend.service
```

**Systemd Service File:**
```ini
[Unit]
Description=Photon Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/photon-nasa/photon
Environment="PATH=/home/ubuntu/photon-nasa/photon/.venv/bin"
ExecStart=/home/ubuntu/photon-nasa/photon/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl daemon-reload
sudo systemctl enable photon-backend
sudo systemctl start photon-backend
sudo systemctl status photon-backend
```

#### Deploy Frontend
```bash
# Build frontend
cd ../frontend
npm install
npm run build

# Copy to Nginx
sudo cp -r dist/* /var/www/html/

# Configure Nginx
sudo nano /etc/nginx/sites-available/photon
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    root /var/www/html;
    index index.html;
    
    # Frontend
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API proxy
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Gzip
    gzip on;
    gzip_types text/css application/javascript application/json;
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/photon /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

### Option 3: Frontend on S3 + CloudFront

#### Build Frontend
```bash
cd frontend
npm run build
```

#### Upload to S3
```bash
# Create S3 bucket
aws s3 mb s3://photon-frontend

# Enable static website hosting
aws s3 website s3://photon-frontend --index-document index.html --error-document index.html

# Upload files
aws s3 sync dist/ s3://photon-frontend/ --delete

# Make public
aws s3api put-bucket-policy --bucket photon-frontend --policy '{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::photon-frontend/*"
  }]
}'
```

#### Create CloudFront Distribution
```bash
# Via AWS Console or CLI
aws cloudfront create-distribution \
  --origin-domain-name photon-frontend.s3.amazonaws.com \
  --default-root-object index.html
```

#### Invalidate Cache After Updates
```bash
aws cloudfront create-invalidation \
  --distribution-id E1234567890ABC \
  --paths "/*"
```

---

## 4. ENVIRONMENT VARIABLES

### Backend (.env)

```bash
# Vector Store
VECTOR_STORE_BACKEND=file  # or 'chroma'
CHROMA_PERSIST_DIR=./data/chroma

# Embedding (optional fallback)
HF_TOKEN=hf_xxxxxxxxxxxxx

# Rate Limiting
REDIS_URL=redis://localhost:6379

# Authentication
PHOTON_SKIP_AUTH=0  # 1 to disable
SECRET_KEY=your-secret-key-here

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR

# Production
ALLOWED_HOSTS=photon-nasa.com,www.photon-nasa.com
```

### Frontend (.env)

```bash
# Development
VITE_API_URL=http://localhost:8000

# Production
# VITE_API_URL=https://api.photon-nasa.com
```

---

## 5. SECURITY CONFIGURATION

### API Key Authentication

**Generate API Key:**
```bash
python scripts/create_api_key.py
# Output: photon_abc123def456...
```

**Store in data/api_keys.json:**
```json
{
  "keys": [
    {
      "key": "photon_abc123def456...",
      "created": "2026-01-19T10:30:00Z",
      "rate_limit": 120,
      "description": "Research team API key"
    }
  ]
}
```

### Rate Limiting Setup

**Install Redis:**
```bash
# Docker
docker run -d -p 6379:6379 redis:7-alpine

# Ubuntu
sudo apt install redis-server
sudo systemctl start redis
```

**Configure in .env:**
```bash
REDIS_URL=redis://localhost:6379
```

### CORS Configuration

**Development:**
```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Production:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://photon-nasa.com",
        "https://www.photon-nasa.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
)
```

### HTTPS/TLS Setup

**Using Let's Encrypt with Certbot:**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d photon-nasa.com -d www.photon-nasa.com

# Auto-renewal (already configured)
sudo systemctl status certbot.timer
```

**Nginx HTTPS Configuration:**
```nginx
server {
    listen 443 ssl http2;
    server_name photon-nasa.com;
    
    ssl_certificate /etc/letsencrypt/live/photon-nasa.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/photon-nasa.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # ... rest of configuration
}
```

---

## 6. PRODUCTION CHECKLIST

### Pre-Deployment

- [ ] All tests passing (`pytest tests/`)
- [ ] Frontend builds without errors (`npm run build`)
- [ ] Environment variables configured
- [ ] API keys generated and stored securely
- [ ] Redis configured for rate limiting
- [ ] Database backups configured (if using ChromaDB)
- [ ] HTTPS/TLS certificates obtained
- [ ] CORS configured for production domains
- [ ] Monitoring and logging configured

### Security Hardening

- [ ] Disable `PHOTON_SKIP_AUTH` (set to 0)
- [ ] API key authentication enabled
- [ ] Rate limiting active
- [ ] Execution sandboxing (Docker containers)
- [ ] Network isolation for execution service
- [ ] Regular dependency updates (`pip-audit`, `npm audit`)
- [ ] Security headers configured (CSP, HSTS, etc.)

### Performance

- [ ] Embedding model pre-loaded on startup
- [ ] Vector store cached in memory
- [ ] Gzip compression enabled
- [ ] CDN configured for static assets
- [ ] Database connection pooling
- [ ] Load balancer configured (if multiple instances)

### Monitoring

- [ ] Application logs configured
- [ ] Error tracking (e.g., Sentry)
- [ ] Performance monitoring (e.g., Prometheus + Grafana)
- [ ] Uptime monitoring (e.g., UptimeRobot)
- [ ] Alert notifications configured

---

## 7. MONITORING & MAINTENANCE

### Logging Setup

**Python Logging:**
```python
# app/main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('/var/log/photon/app.log'),
        logging.StreamHandler()
    ]
)
```

**Nginx Access Logs:**
```nginx
access_log /var/log/nginx/photon-access.log;
error_log /var/log/nginx/photon-error.log;
```

### Health Checks

**Backend Health:**
```bash
curl http://localhost:8000/health
```

**Systemd Service:**
```bash
sudo systemctl status photon-backend
```

**Docker:**
```bash
docker ps
docker logs photon-backend
```

### Backup & Recovery

**Backup Vector Store:**
```bash
# File backend
cp photon/data/vectors.json photon/data/vectors.json.backup

# Automated daily backup
crontab -e
# Add: 0 2 * * * cp /home/ubuntu/photon-nasa/photon/data/vectors.json /backups/vectors-$(date +\%Y\%m\%d).json
```

**Backup Database (ChromaDB):**
```bash
# Backup ChromaDB directory
tar -czf chroma-backup-$(date +%Y%m%d).tar.gz photon/data/chroma/
```

### Updates & Maintenance

**Update Application:**
```bash
cd photon-nasa
git pull origin main

# Backend
cd photon
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart photon-backend

# Frontend
cd ../frontend
npm install
npm run build
sudo cp -r dist/* /var/www/html/
sudo systemctl reload nginx
```

**Update Dependencies:**
```bash
# Backend
pip install --upgrade pip
pip list --outdated
pip install --upgrade <package>

# Frontend
npm outdated
npm update
```

---

*For architecture details, see [Technical Architecture Guide](01_TECHNICAL_ARCHITECTURE.md)*  
*For API documentation, see [API Reference](02_API_REFERENCE.md)*
