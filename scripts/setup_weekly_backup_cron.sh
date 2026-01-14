#!/bin/bash
# Script per configurare il cron job per backup settimanale
# Esegue il backup ogni domenica alle 2:00 AM

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_SCRIPT="$SCRIPT_DIR/weekly_backup.py"
PYTHON_PATH=$(which python3)

if [ -z "$PYTHON_PATH" ]; then
    PYTHON_PATH=$(which python)
fi

if [ -z "$PYTHON_PATH" ]; then
    echo "❌ Python non trovato!"
    exit 1
fi

# Crea il cron job (ogni domenica alle 2:00 AM)
CRON_JOB="0 2 * * 0 $PYTHON_PATH $BACKUP_SCRIPT >> /var/log/mekocrm_backup.log 2>&1"

# Verifica se il cron job esiste già
if crontab -l 2>/dev/null | grep -q "$BACKUP_SCRIPT"; then
    echo "⚠️  Cron job già configurato"
    crontab -l | grep "$BACKUP_SCRIPT"
else
    # Aggiungi il cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ Cron job configurato con successo!"
    echo "   📅 Esecuzione: Ogni domenica alle 2:00 AM"
    echo "   📝 Log: /var/log/mekocrm_backup.log"
    echo ""
    echo "Cron job attivo:"
    crontab -l | grep "$BACKUP_SCRIPT"
fi
