#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Crea tabella assistant_logs"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from crm_app_completo import app, db, AssistantLog

with app.app_context():
    db.create_all()
    print("✅ Tabelle create/aggiornate")
