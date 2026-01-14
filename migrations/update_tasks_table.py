#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aggiorna la tabella opportunity_tasks per permettere opportunity_id NULL"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crm_app_completo import app, db
from sqlalchemy import text

if __name__ == '__main__':
    with app.app_context():
        try:
            # Modifica la colonna opportunity_id per permettere NULL
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS opportunity_tasks_new (
                    id INTEGER PRIMARY KEY,
                    opportunity_id INTEGER,
                    task_type VARCHAR(50) NOT NULL,
                    description TEXT,
                    assigned_to_id INTEGER,
                    due_date DATE,
                    is_completed BOOLEAN DEFAULT 0,
                    completed_at DATETIME,
                    completed_by_id INTEGER,
                    created_at DATETIME,
                    updated_at DATETIME,
                    FOREIGN KEY(opportunity_id) REFERENCES opportunities(id),
                    FOREIGN KEY(assigned_to_id) REFERENCES users(id),
                    FOREIGN KEY(completed_by_id) REFERENCES users(id)
                )
            """))
            
            # Copia dati esistenti
            db.session.execute(text("""
                INSERT INTO opportunity_tasks_new 
                SELECT * FROM opportunity_tasks
            """))
            
            # Elimina vecchia tabella
            db.session.execute(text("DROP TABLE opportunity_tasks"))
            
            # Rinomina nuova tabella
            db.session.execute(text("ALTER TABLE opportunity_tasks_new RENAME TO opportunity_tasks"))
            
            db.session.commit()
            print("✅ Tabella opportunity_tasks aggiornata con successo")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️  Errore: {e}")
            print("💡 La tabella potrebbe essere già aggiornata o non esistere")




