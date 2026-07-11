#!/bin/bash
# Fynlo Database Restore Script
# Usage: ./db_restore.sh <path_to_backup_file>
# Requires: DATABASE_URL environment variable

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <path_to_backup_file>"
    exit 1
fi

BACKUP_FILE="$1"
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file $BACKUP_FILE not found."
    exit 1
fi

DB_URL=${DATABASE_URL:-"sqlite:///dev.db"}

echo "[$(date)] Starting restore process from $BACKUP_FILE..."

if [[ "$DB_URL" == sqlite* ]]; then
    DB_PATH=$(echo "$DB_URL" | sed 's|^sqlite:///||')
    echo "Restoring SQLite database to $DB_PATH..."
    
    # Backup current DB just in case before restore
    if [ -f "$DB_PATH" ]; then
        cp "$DB_PATH" "${DB_PATH}.pre_restore.bak"
        echo "Created pre-restore backup at ${DB_PATH}.pre_restore.bak"
    fi
    
    # Overwrite the db with the backup
    cp "$BACKUP_FILE" "$DB_PATH"
    
    echo "SQLite restore completed successfully."

elif [[ "$DB_URL" == postgres* ]]; then
    if ! command -v pg_restore &> /dev/null; then
        echo "Error: pg_restore is not installed."
        exit 1
    fi
    
    echo "Restoring PostgreSQL database..."
    
    # Clean the database before restoring, and use single transaction if possible
    pg_restore --clean --if-exists --no-owner --dbname="$DB_URL" "$BACKUP_FILE"
    
    echo "PostgreSQL restore completed successfully."
else
    echo "Unsupported DATABASE_URL scheme."
    exit 1
fi

echo "[$(date)] Restore process finished successfully."
