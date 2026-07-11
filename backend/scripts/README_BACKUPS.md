# Database Backup and Recovery Guide

Fynlo relies heavily on ensuring user financial data is never lost. This directory contains scripts for automated snapshot backups, and this guide outlines how to configure Point-in-Time Recovery (PITR) for production.

## 1. Snapshot Backups

The `db_backup.sh` and `db_restore.sh` scripts automatically detect whether you are running `sqlite` or `postgres` via your `DATABASE_URL` environment variable.

### Automated Cron Job Setup (Daily Backups)
To schedule a daily backup at 2:00 AM, add the following to your server's crontab (`crontab -e`):

```bash
# Run Fynlo DB Backup daily at 02:00 AM
0 2 * * * cd /path/to/Fynlo/backend && DATABASE_URL="postgresql://user:pass@localhost/db" ./scripts/db_backup.sh >> /var/log/fynlo_backup.log 2>&1
```

### Manual Restore
To restore a backup, ensure no active connections are modifying the DB, then run:
```bash
./scripts/db_restore.sh ./backups/fynlo_pg_20260712_020000.dump
```

## 2. Point-in-Time Recovery (PITR) for Production

While snapshot backups are good for daily recovery, production financial systems require **Point-in-Time Recovery (PITR)**. This allows you to restore the database to *any exact second* (e.g., right before a mistaken data deletion).

If you are using **PostgreSQL** in production, you must enable WAL (Write-Ahead Log) Archiving. 

### Enabling PITR on Postgres
1. Open your `postgresql.conf`.
2. Configure the following parameters:
   ```ini
   wal_level = replica
   archive_mode = on
   archive_command = 'cp %p /path/to/wal_archive/%f' # Or send to S3/GCS using pgbackrest
   ```
3. Restart PostgreSQL.

### Restoring to a Point-in-Time
If a catastrophic error happens at `14:35:00`, you can recover using your base backup + WAL logs:
1. Stop the database.
2. Restore the most recent base backup into the data directory.
3. Add a `recovery.signal` file to the data directory.
4. Add to `postgresql.conf`:
   ```ini
   restore_command = 'cp /path/to/wal_archive/%f %p'
   recovery_target_time = '2026-07-12 14:34:59'
   ```
5. Start the database. Postgres will replay transactions exactly up to that second.

*Note: For modern cloud setups (AWS RDS, GCP Cloud SQL), PITR is a 1-click toggle in the console. Simply enable "Automated Backups" and you will be able to restore to any second within your retention window.*
