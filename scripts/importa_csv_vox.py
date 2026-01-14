#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Importa contatti dal CSV VOX Mail come Lead
"""
import sys
import csv
import os
from datetime import datetime
sys.path.insert(0, '/home/ubuntu/offermanager')
from crm_app_completo import app, db
from sqlalchemy import text

def import_vox_csv(csv_path):
    """Importa contatti dal CSV VOX come Lead"""
    with app.app_context():
        # Ottieni admin user
        admin_user = db.session.execute(text("SELECT id FROM users WHERE username='admin' LIMIT 1")).fetchone()
        if not admin_user:
            print("❌ Utente admin non trovato!")
            return
        
        user_id = admin_user[0]
        
        print("=" * 70)
        print("📥 IMPORTazione CSV VOX Mail")
        print("=" * 70)
        print()
        
        imported = 0
        updated = 0
        skipped = 0
        errors = 0
        
        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter=';')
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        email = row.get('Email', '').strip()
                        if not email:
                            skipped += 1
                            continue
                        
                        # Estrai dati
                        company_name = row.get('AZIENDA', '').strip() or 'Azienda non specificata'
                        nome = row.get('Nome', '').strip()
                        cognome = row.get('Cognome', '').strip()
                        gruppo = row.get('Gruppi', '').strip() or 'MIR'
                        stato = row.get('Stato complessivo', '').strip()
                        iscritto = row.get('Iscritto', '').strip()
                        
                        # Determina source e interest basato sul gruppo
                        source = 'VOX Mail'
                        interest = gruppo  # MIR, UR, Unitree, ecc.
                        
                        # Determina rating basato sullo stato
                        rating = 'Cold'
                        if 'aperto' in stato.lower() or 'cliccato' in stato.lower():
                            rating = 'Warm'
                        elif 'interagito' in stato.lower():
                            rating = 'Hot'
                        
                        # Verifica se esiste già un Lead con questa email
                        existing = db.session.execute(text("""
                            SELECT id FROM leads WHERE email = :email LIMIT 1
                        """), {"email": email}).fetchone()
                        
                        if existing:
                            # Aggiorna Lead esistente
                            db.session.execute(text("""
                                UPDATE leads 
                                SET company_name = :company_name,
                                    contact_first_name = :first_name,
                                    contact_last_name = :last_name,
                                    source = :source,
                                    interest = :interest,
                                    rating = :rating,
                                    notes = :notes,
                                    updated_at = :updated_at
                                WHERE id = :lead_id
                            """), {
                                "company_name": company_name[:200],
                                "first_name": nome[:100],
                                "last_name": cognome[:100],
                                "source": source[:50],
                                "interest": interest[:50],
                                "rating": rating[:20],
                                "notes": f"Importato da VOX Mail - Gruppo: {gruppo}, Stato: {stato}",
                                "updated_at": datetime.utcnow(),
                                "lead_id": existing[0]
                            })
                            updated += 1
                        else:
                            # Crea nuovo Lead
                            db.session.execute(text("""
                                INSERT INTO leads 
                                (company_name, contact_first_name, contact_last_name, email,
                                 source, interest, rating, status, notes, owner_id, created_at, updated_at)
                                VALUES (:company_name, :first_name, :last_name, :email,
                                        :source, :interest, :rating, :status, :notes, :owner_id, :created_at, :updated_at)
                            """), {
                                "company_name": company_name[:200],
                                "first_name": nome[:100],
                                "last_name": cognome[:100],
                                "email": email[:100],
                                "source": source[:50],
                                "interest": interest[:50],
                                "rating": rating[:20],
                                "status": "New",
                                "notes": f"Importato da VOX Mail - Gruppo: {gruppo}, Stato: {stato}, Iscritto: {iscritto}",
                                "owner_id": user_id,
                                "created_at": datetime.utcnow(),
                                "updated_at": datetime.utcnow()
                            })
                            imported += 1
                        
                        if row_num % 100 == 0:
                            db.session.commit()
                            print(f"  Processati {row_num} contatti...")
                    
                    except Exception as e:
                        errors += 1
                        print(f"  ❌ Errore riga {row_num}: {str(e)}")
                        continue
                
                db.session.commit()
        
        except Exception as e:
            print(f"❌ Errore lettura file: {str(e)}")
            return
        
        print()
        print("=" * 70)
        print("📊 Riepilogo:")
        print(f"  ✅ Importati: {imported}")
        print(f"  🔄 Aggiornati: {updated}")
        print(f"  ⚠️  Saltati: {skipped}")
        print(f"  ❌ Errori: {errors}")
        print("=" * 70)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Utilizzo: python importa_csv_vox.py <percorso_file.csv>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    if not os.path.exists(csv_path):
        print(f"❌ File non trovato: {csv_path}")
        sys.exit(1)
    
    import_vox_csv(csv_path)
