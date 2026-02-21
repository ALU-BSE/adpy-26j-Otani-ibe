#!/bin/bash
# IshemaLink — Automated DB Backup Script
# Runs via cron: 0 2 * * * /app/scripts/backup.sh

set -e

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/backups"
FILENAME="ishemalink_backup_${TIMESTAMP}.sql"
RETENTION_DAYS=7

mkdir -p "$BACKUP_DIR"

echo "[$(date)] Starting backup: $FILENAME"

# Dump PostgreSQL
PGPASSWORD=ishemalink_pass pg_dump \
    -h db \
    -U ishemalink_user \
    -d ishemalink_db \
    -F c \
    -f "${BACKUP_DIR}/${FILENAME}"

# Compress
gzip "${BACKUP_DIR}/${FILENAME}"
echo "[$(date)] Backup compressed: ${FILENAME}.gz"

# Remove backups older than retention period
find "$BACKUP_DIR" -name "ishemalink_backup_*.gz" \
    -mtime +${RETENTION_DAYS} -delete
echo "[$(date)] Old backups cleaned (>${RETENTION_DAYS} days)"

echo "[$(date)] Backup complete: ${BACKUP_DIR}/${FILENAME}.gz"
