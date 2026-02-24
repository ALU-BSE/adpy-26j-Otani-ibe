# IshemaLink Deployment Manual
## How to Deploy on a Clean Ubuntu 24 Server

**Version:** 1.0
**Target:** AOS / KtRN Data Center, Kigali Rwanda
**Time Required:** ~30 minutes

---

## Prerequisites

| Requirement | Version |
|---|---|
| Ubuntu Server | 24 LTS |
| RAM | 4GB minimum, 8GB recommended |
| Storage | 50GB SSD |
| Docker | 24+ |
| Docker Compose | 2.0+ |
| Domain | Pointed to server IP |

---

## Step 1: Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker --version
docker compose version
```

---

## Step 2: Clone the Repository
```bash
git clone https://github.com/ALU-BSE/adpy-26j-Otani-ibe.git
cd adpy-26j-Otani-ibe
git checkout main
```

---

## Step 3: Configure Environment
```bash
# Create .env from template
cp .env.example .env

# Edit with production values
nano .env
```

Fill in these required values:
```env
DEBUG=False
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_urlsafe(50))">
ALLOWED_HOSTS=your-domain.rw,www.your-domain.rw
DATABASE_URL=postgresql://ishemalink_user:STRONG_PASSWORD@db:5432/ishemalink_db
REDIS_URL=redis://redis:6379/0
RRA_API_KEY=<from RRA developer portal>
RURA_API_KEY=<from RURA developer portal>
MOMO_API_KEY=<from MTN Rwanda developer portal>
MOMO_WEBHOOK_SECRET=<random 32 char string>
```

---

## Step 4: SSL Certificate
```bash
# Create certs directory
mkdir -p nginx/certs

# Option A: Self-signed (staging only)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/certs/ishemalink.key \
  -out nginx/certs/ishemalink.crt

# Option B: Let's Encrypt (production)
sudo apt install certbot -y
sudo certbot certonly --standalone -d your-domain.rw
sudo cp /etc/letsencrypt/live/your-domain.rw/fullchain.pem nginx/certs/ishemalink.crt
sudo cp /etc/letsencrypt/live/your-domain.rw/privkey.pem nginx/certs/ishemalink.key
```

---

## Step 5: Build and Start
```bash
# Build containers
docker compose -f docker-compose.prod.yml build

# Start all services
docker compose -f docker-compose.prod.yml up -d

# Verify all containers running
docker compose -f docker-compose.prod.yml ps
```

Expected output:
```
NAME          STATUS    PORTS
web           Up        8000/tcp
db            Up        5432/tcp
redis         Up        6379/tcp
nginx         Up        0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
```

---

## Step 6: Initialize Database
```bash
# Run migrations
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# Create superuser
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Collect static files
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

---

## Step 7: Verify Deployment
```bash
# Health check
curl https://your-domain.rw/api/health/deep/

# Expected response:
# {
#     "status": "Healthy",
#     "services": {
#         "database": "Healthy",
#         "cache_redis": "Healthy"
#     }
# }

# Test authentication
curl -X POST https://your-domain.rw/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-password"}'
```

---

## Step 8: Setup Automated Backups
```bash
# Install backup cron job
(crontab -l 2>/dev/null; echo "0 2 * * * /bin/bash /workspaces/adpy-26j-Otani-ibe/scripts/backup.sh >> /var/log/ishemalink_backup.log 2>&1") | crontab -

# Verify cron
crontab -l
```

---

## Step 9: SSL Auto-Renewal (Production)
```bash
# Test renewal
sudo certbot renew --dry-run

# Add renewal cron
(crontab -l 2>/dev/null; echo "0 0 1 * * certbot renew --quiet && docker compose -f /path/to/docker-compose.prod.yml restart nginx") | crontab -
```

---

## Monitoring
```bash
# View live logs
docker compose -f docker-compose.prod.yml logs -f web

# View specific service
docker compose -f docker-compose.prod.yml logs -f nginx

# Check resource usage
docker stats
```

---

## Updating the Application
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker compose -f docker-compose.prod.yml build web
docker compose -f docker-compose.prod.yml up -d web

# Run new migrations if any
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| 502 Bad Gateway | `docker compose restart web` |
| Database connection failed | Check `DATABASE_URL` in `.env` |
| Static files not loading | Run `collectstatic` again |
| SSL certificate error | Check cert paths in `nginx/nginx.conf` |
| Container won't start | Check `docker compose logs web` |

---

## Support

For deployment issues contact the IshemaLink Engineering Team.
Check `/api/health/deep/` first — it tells you which service is down.
