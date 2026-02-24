#!/bin/bash
# IshemaLink Automated Backup Script
# Cron: 0 2 * * * /app/scripts/backup.sh >> /var/log/ishemalink_backup.log 2>&1

set -e

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="ishemalink_db"
DB_USER="ishemalink_user"
RETENTION_DAYS=30
MINIO_BUCKET="s3://ishemalink-backups"

echo "=========================================="
echo "IshemaLink Backup Started: $DATE"
echo "=========================================="

# 1. PostgreSQL dump
echo "[1/3] Dumping PostgreSQL database..."
mkdir -p $BACKUP_DIR
PGPASSWORD=$POSTGRES_PASSWORD pg_dump \
    -h db \
    -U $DB_USER \
    -d $DB_NAME \
    -F c \
    -f "$BACKUP_DIR/ishemalink_db_$DATE.dump"
echo "✅ Database dump complete"

# 2. Compress
echo "[2/3] Compressing backup..."
gzip "$BACKUP_DIR/ishemalink_db_$DATE.dump"
echo "✅ Compression complete: ishemalink_db_$DATE.dump.gz"

# 3. Upload to MinIO/S3
echo "[3/3] Uploading to MinIO..."
if command -v aws &> /dev/null; then
    aws s3 cp \
        "$BACKUP_DIR/ishemalink_db_$DATE.dump.gz" \
        "$MINIO_BUCKET/db/$DATE/" \
        --endpoint-url $MINIO_ENDPOINT
    echo "✅ Upload complete"
else
    echo "⚠️  aws CLI not found — backup saved locally only"
fi

# 4. Clean up old local backups
echo "Cleaning backups older than $RETENTION_DAYS days..."
find $BACKUP_DIR -name "*.dump.gz" -mtime +$RETENTION_DAYS -delete
echo "✅ Cleanup complete"

echo "=========================================="
echo "Backup Finished: $(date +%Y%m%d_%H%M%S)"
echo "=========================================="
