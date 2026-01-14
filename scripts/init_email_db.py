#!/usr/bin/env python3
# Script per inizializzare tabelle email marketing
from crm_app_completo import db, app

with app.app_context():
    db.create_all()
    print("✓ Tabelle database create/aggiornate")







