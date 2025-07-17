#!/usr/bin/env bash

echo "Starting IPO database backup..."

BACKUP_ROOT="./backup"
DATE=$(date '+%Y%m%d_%H%M%S')
echo "Backup date: $DATE"

# 환경변수에서 DB 정보 읽기
MYSQL_HOST=${IPO_MYSQL_HOST}
MYSQL_PORT=${IPO_MYSQL_PORT}
MYSQL_DATABASE=${IPO_MYSQL_DATABASE}
MYSQL_USER=${IPO_MYSQL_USER}
MYSQL_PASSWORD=${IPO_MYSQL_PASSWORD}

function main() {
  mkdir -p $BACKUP_ROOT/$DATE
  echo "Backing up database: $MYSQL_DATABASE"
  
  mysqldump --column-statistics=0 \
    --databases $MYSQL_DATABASE \
    -h $MYSQL_HOST \
    -P $MYSQL_PORT \
    -u $MYSQL_USER \
    -p"$MYSQL_PASSWORD" \
    > $BACKUP_ROOT/$DATE/ipo_backup.sql
  
  if [ $? -eq 0 ]; then
    echo "Backup completed successfully: $BACKUP_ROOT/$DATE/ipo_backup.sql"
  else
    echo "Backup failed!"
    exit 1
  fi
}

main 