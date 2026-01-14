#!/bin/bash
# Script per configurare la sincronizzazione giornaliera automatica

SCRIPT_DIR="/home/ubuntu/offermanager"
SYNC_SCRIPT="$SCRIPT_DIR/scripts/sync_all_portals.py"
LOG_FILE="$SCRIPT_DIR/logs/daily_sync.log"
CRON_JOB="0 2 * * * cd $SCRIPT_DIR && source venv/bin/activate && python3 $SYNC_SCRIPT >> $LOG_FILE 2>&1"

# Crea directory logs se non esiste
mkdir -p "$SCRIPT_DIR/logs"

# Aggiungi cron job (esegue ogni giorno alle 2:00 AM)
(crontab -l 2>/dev/null | grep -v "$SYNC_SCRIPT"; echo "$CRON_JOB") | crontab -

echo "✅ Sincronizzazione giornaliera configurata!"
echo "   Esecuzione: ogni giorno alle 2:00 AM"
echo "   Script: $SYNC_SCRIPT"
echo "   Log: $LOG_FILE"
echo ""
echo "Per verificare: crontab -l"
echo "Per testare manualmente: python3 $SYNC_SCRIPT"
