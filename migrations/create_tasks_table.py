#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Crea tabella opportunity_tasks"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')

from crm_app_completo import db, app
from sqlalchemy import text

with app.app_context():
    try:
        # Crea tabella opportunity_tasks
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS opportunity_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                opportunity_id INTEGER NOT NULL,
                task_type VARCHAR(50) NOT NULL,
                description TEXT,
                assigned_to_id INTEGER,
                due_date DATE,
                is_completed BOOLEAN DEFAULT 0,
                completed_at DATETIME,
                completed_by_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (opportunity_id) REFERENCES opportunities(id),
                FOREIGN KEY (assigned_to_id) REFERENCES users(id),
                FOREIGN KEY (completed_by_id) REFERENCES users(id)
            )
        """))
        db.session.commit()
        print("✅ Tabella opportunity_tasks creata")
    except Exception as e:
        db.session.rollback()
        if "already exists" in str(e).lower():
            print("ℹ️  Tabella opportunity_tasks già esistente")
        else:
            print(f"⚠️  Errore: {e}")




