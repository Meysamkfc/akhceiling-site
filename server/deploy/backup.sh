#!/usr/bin/env bash
# Daily backup of the CRM database + customer files.   crontab -e  ->  30 2 * * *  /srv/akh/server/deploy/backup.sh
set -euo pipefail
SRC=/srv/akh/server/instance
DST=/srv/akh-backup
KEEP_DAYS=30
mkdir -p "$DST"
STAMP=$(date +%Y%m%d-%H%M)
# consistent SQLite copy while the site is running
sqlite3 "$SRC/akh.db" ".backup '$DST/akh-$STAMP.db'"
tar -czf "$DST/uploads-$STAMP.tar.gz" -C "$SRC" uploads
find "$DST" -type f -mtime +$KEEP_DAYS -delete
echo "backup ok: $STAMP"
# tip: also copy $DST to another machine / cloud storage (rclone, rsync) -- a backup on the same disk is not enough.
