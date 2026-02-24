# IshemaLink Disaster Recovery Plan

**Version:** 1.0  
**Date:** 2026-02-21  
**Owner:** IshemaLink Engineering Team  
**Data Center:** AOS / KtRN (Kigali, Rwanda)  
**Compliance:** MINICOM, RURA, RRA Data Sovereignty Requirements

---

## 1. Recovery Objectives

| Metric | Target | Rationale |
|---|---|---|
| RTO (Recovery Time Objective) | 2 hours | RURA requires max 2hr system downtime |
| RPO (Recovery Point Objective) | 24 hours | Daily backups at 02:00 CAT |
| Backup Retention | 30 days | RRA audit requirement |
| Backup Location | MinIO (local) + S3 (offsite) | Data sovereignty — Rwanda-hosted primary |

---

## 2. System Architecture (Recovery Context)
```
Internet → Nginx (SSL) → Gunicorn (Django) → PostgreSQL
                                           → Redis (Cache)
                                           → MinIO (Backups)
```

All components run as Docker containers managed by Docker Compose.
Data persists in named volumes: `postgres_data`, `static_volume`.

---

## 3. Backup Strategy

### Automated Daily Backup (02:00 CAT)
```bash
# Cron entry on production server
0 2 * * * /app/scripts/backup.sh >> /var/log/ishemalink_backup.log 2>&1
```

### What Gets Backed Up
| Data | Method | Destination |
|---|---|---|
| PostgreSQL DB | `pg_dump -F c` (compressed) | MinIO + S3 |
| Static files | Volume snapshot | MinIO |
| Environment config | Manual — stored in vault | HashiCorp Vault |

### Backup Verification (Weekly)
```bash
# Test restore to staging environment every Sunday
pg_restore -h staging-db -U ishemalink_user -d ishemalink_db_test backup.dump
```

---

## 4. Failure Scenarios & Recovery Steps

### Scenario A: Web Container Crash
**Symptoms:** API returns 502 Bad Gateway  
**Auto-recovery:** Docker `restart: always` restarts container automatically  
**Manual check:**
```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs web --tail=50
docker compose -f docker-compose.prod.yml restart web
```
**Expected RTO:** 2 minutes (auto) / 10 minutes (manual)

---

### Scenario B: PostgreSQL Data Corruption
**Symptoms:** 500 errors, `/api/health/deep/` reports database unhealthy  
**Steps:**
```bash
# 1. Stop web service
docker compose -f docker-compose.prod.yml stop web

# 2. Identify latest clean backup
ls -la /backups/*.dump.gz

# 3. Restore database
docker compose -f docker-compose.prod.yml exec db psql -U ishemalink_user -c "DROP DATABASE ishemalink_db;"
docker compose -f docker-compose.prod.yml exec db psql -U ishemalink_user -c "CREATE DATABASE ishemalink_db;"
pg_restore -h localhost -U ishemalink_user -d ishemalink_db /backups/ishemalink_db_LATEST.dump

# 4. Run migrations
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# 5. Restart
docker compose -f docker-compose.prod.yml start web
```
**Expected RTO:** 45 minutes

---

### Scenario C: Full Server Loss (AOS Data Center Failure)
**Symptoms:** Complete system unavailable  
**Steps:**
```bash
# 1. Provision new Ubuntu 24 server at KtRN (backup DC)

# 2. Install Docker
curl -fsSL https://get.docker.com | sh

# 3. Clone repository
git clone https://github.com/your-org/adpy-26j-Otani-ibe.git
cd adpy-26j-Otani-ibe

# 4. Restore environment
cp .env.example .env
# Fill in production values from HashiCorp Vault

# 5. Pull latest backup from MinIO
aws s3 cp s3://ishemalink-backups/db/LATEST/ ./backups/ --recursive

# 6. Start all services
docker compose -f docker-compose.prod.yml up -d

# 7. Restore database
pg_restore -h localhost -U ishemalink_user -d ishemalink_db ./backups/LATEST.dump

# 8. Run migrations + collect static
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# 9. Verify health
curl https://your-domain.rw/api/health/deep/
```
**Expected RTO:** 2 hours

---

### Scenario D: Rwanda Network Outage (Nyamagabe Scenario)
**Symptoms:** Mobile agents cannot sync — offline mode activates  
**System behaviour:**
- Mobile apps queue transactions locally (offline-first design)
- Sync resumes automatically when connectivity returns
- No data loss — atomic transactions ensure partial writes are rolled back
- Redis cache serves static data (tariffs, routes) during outage

**No manual intervention required.**

---

### Scenario E: Redis Cache Failure
**Symptoms:** Slow API responses, `/api/health/deep/` reports cache unhealthy  
```bash
# Restart Redis
docker compose -f docker-compose.prod.yml restart redis

# Verify
curl https://your-domain.rw/api/health/deep/
```
**Expected RTO:** 5 minutes  
**Data loss:** None — Redis is cache only, not primary storage

---

## 5. Health Monitoring

### Deep Health Check Endpoint
```bash
GET /api/health/deep/

# Expected response:
{
    "status": "Healthy",
    "timestamp": "2026-02-21T21:35:50.145754",
    "services": {
        "database": "Healthy",
        "cache_redis": "Healthy"
    }
}
```

### Recommended Monitoring Schedule
| Check | Frequency | Tool |
|---|---|---|
| `/api/health/deep/` | Every 60 seconds | Prometheus + Grafana |
| Backup verification | Weekly (Sunday 03:00) | Cron job |
| SSL certificate expiry | Monthly | certbot auto-renew |
| Docker container status | Every 30 seconds | Docker health checks |

---

## 6. Emergency Contacts

| Role | Responsibility |
|---|---|
| Lead Engineer | System architecture, code fixes |
| DevOps | Docker, server, network issues |
| MINICOM Liaison | Regulatory notifications |
| AOS Data Center | Hardware, power, cooling |
| KtRN Data Center | Failover site activation |

---

## 7. Post-Recovery Checklist

After any recovery event:

- [ ] Verify `/api/health/deep/` returns all services healthy
- [ ] Test `POST /api/shipments/create/` end-to-end
- [ ] Test `POST /api/payments/webhook/` with SUCCESS callback
- [ ] Confirm EBM signatures are being generated (RRA compliance)
- [ ] Confirm RURA license checks are passing
- [ ] Notify MINICOM of incident and resolution time
- [ ] Update incident log with RTO achieved vs target
- [ ] Run `pytest` suite to confirm no regressions
- [ ] Verify backup ran successfully after recovery

---

## 8. Data Sovereignty Compliance

All primary data remains within Rwanda at all times:
- **Primary:** AOS Data Center, Kigali
- **Failover:** KtRN Data Center, Kigali  
- **Backup storage:** MinIO instance hosted at AOS
- **Offsite backup:** Rwanda-based S3-compatible provider only

No personal or financial data is stored outside Rwanda borders,
in compliance with Rwanda's Data Protection Law and MINICOM directives.
