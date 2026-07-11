#!/bin/bash
# Fynlo Database Backup Script
# Usage: ./backup.sh
# Requires: DATABASE_URL environment variable

set -e

BACKUP_DIR="${BACKUP_DIR:-./backups}"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_URL=${DATABASE_URL:-"sqlite:///dev.db"}

echo "[$(date)] Starting backup process..."

if [[ "$DB_URL" == sqlite* ]]; then
    # SQLite Backup
    DB_PATH=$(echo "$DB_URL" | sed 's|^sqlite:///||')
    if [ ! -f "$DB_PATH" ]; then
        echo "Error: SQLite database file $DB_PATH not found."
        exit 1
    fi
    BACKUP_FILE="$BACKUP_DIR/fynlo_sqlite_$TIMESTAMP.db"
    
    # Use SQLite safe backup command if available, otherwise just copy
    if command -v sqlite3 &> /dev/null; then
        sqlite3 "$DB_PATH" ".backup '$BACKUP_FILE'"
    else
        cp "$DB_PATH" "$BACKUP_FILE"
    fi
    
    echo "SQLite backup completed: $BACKUP_FILE"

elif [[ "$DB_URL" == postgres* ]]; then
    # PostgreSQL Backup
    # Replace postgres:// with postgresql:// if needed for pg_dump
    export PGDATABASE="$DB_URL"
    BACKUP_FILE="$BACKUP_DIR/fynlo_pg_$TIMESTAMP.dump"
    
    if ! command -v pg_dump &> /dev/null; then
        echo "Error: pg_dump is not installed."
        exit 1
    fi
    
    pg_dump -Fc --no-owner --dbname="$DB_URL" -f "$BACKUP_FILE"
    
    echo "PostgreSQL backup completed: $BACKUP_FILE"
else
    echo "Unsupported DATABASE_URL scheme."
    exit 1
fi

# Optional: Rotate backups (keep last 7 days)
# find "$BACKUP_DIR" -type f -mtime +7 -name "fynlo_*.dump" -exec rm {} \;
# find "$BACKUP_DIR" -type f -mtime +7 -name "fynlo_*.db" -exec rm {} \;

echo "[$(date)] Backup process finished successfully."
