#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aggiunge colonna product_category alla tabella tickets se mancante
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from crm_app_completo import app, db
from sqlalchemy import inspect

def fix_ticket_table():
    with app.app_context():
        # Verifica se la colonna esiste
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('tickets')]
        
        print(f"Colonne attuali: {columns}")
        
        if 'product_category' not in columns:
            print("Aggiungo colonna product_category...")
            try:
                db.engine.execute("ALTER TABLE tickets ADD COLUMN product_category VARCHAR(100)")
                print("✅ Colonna product_category aggiunta")
            except Exception as e:
                print(f"⚠️  Errore aggiunta colonna: {e}")
                # Prova con SQLAlchemy
                try:
                    from sqlalchemy import text
                    with db.engine.connect() as conn:
                        conn.execute(text("ALTER TABLE tickets ADD COLUMN product_category VARCHAR(100)"))
                        conn.commit()
                    print("✅ Colonna product_category aggiunta (metodo 2)")
                except Exception as e2:
                    print(f"❌ Errore metodo 2: {e2}")
        else:
            print("✅ Colonna product_category già presente")
        
        # Verifica anche TicketAttachment
        try:
            inspector.get_columns('ticket_attachments')
            print("✅ Tabella ticket_attachments esiste")
        except:
            print("⚠️  Tabella ticket_attachments non esiste, verrà creata...")
            db.create_all()
            print("✅ Tabelle create")

if __name__ == "__main__":
    fix_ticket_table()
