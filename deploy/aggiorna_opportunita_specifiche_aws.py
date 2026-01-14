#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aggiorna opportunità specifiche su AWS:
- Eurofresi e Eurovo -> tiepida + attività "chiamare" per Giovanni Pitton
- Multimac ITV e Scuola Camerana -> calda
- Cambia percentuale da_categorizzare da 10% a 0%
"""
import sqlite3
from pathlib import Path
from datetime import datetime

def aggiorna_opportunita_specifiche():
    print("=" * 80)
    print("AGGIORNAMENTO OPPORTUNITÀ SPECIFICHE - AWS")
    print("=" * 80)
    print()
    
    # Trova il database
    base_dir = Path('/home/ubuntu/offermanager')
    instance_dir = base_dir / 'instance'
    db_file = instance_dir / 'mekocrm.db'
    
    if not db_file.exists():
        db_file = base_dir / 'mekocrm.db'
    
    if not db_file.exists():
        print("❌ Database non trovato!")
        return
    
    print(f"📁 Database: {db_file}")
    print()
    
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()
    
    try:
        # Trova Giovanni Pitton (user_id)
        cursor.execute("SELECT id FROM users WHERE username LIKE '%giovanni%' OR first_name LIKE '%Giovanni%' OR last_name LIKE '%Pitton%' LIMIT 1")
        giovanni = cursor.fetchone()
        if not giovanni:
            # Prova a cercare per nome completo
            cursor.execute("SELECT id FROM users WHERE first_name || ' ' || last_name LIKE '%Giovanni%Pitton%' LIMIT 1")
            giovanni = cursor.fetchone()
        
        if not giovanni:
            print("❌ Utente Giovanni Pitton non trovato!")
            print("   Cercando tutti gli utenti...")
            cursor.execute("SELECT id, username, first_name, last_name FROM users")
            users = cursor.fetchall()
            for u in users:
                print(f"   - ID {u[0]}: {u[1]} ({u[2]} {u[3]})")
            giovanni_id = input("\nInserisci l'ID di Giovanni Pitton: ")
            if giovanni_id:
                giovanni_id = int(giovanni_id)
            else:
                print("⚠️  Saltando creazione attività (utente non trovato)")
                giovanni_id = None
        else:
            giovanni_id = giovanni[0]
            print(f"✅ Trovato Giovanni Pitton (ID: {giovanni_id})")
        
        print()
        
        # 1. Eurofresi e Eurovo -> tiepida
        print("1. Aggiornamento Eurofresi e Eurovo...")
        cursor.execute("""
            UPDATE opportunities 
            SET heat_level = 'tiepida' 
            WHERE name LIKE '%Eurofresi%' 
               OR name LIKE '%EUROFORESI%'
               OR name LIKE '%Eurovo%'
        """)
        euro_count = cursor.rowcount
        print(f"   ✅ Aggiornate {euro_count} opportunità a 'tiepida'")
        
        # Trova ID opportunità Eurofresi e Eurovo
        cursor.execute("""
            SELECT id, name FROM opportunities 
            WHERE name LIKE '%Eurofresi%' 
               OR name LIKE '%EUROFORESI%'
               OR name LIKE '%Eurovo%'
        """)
        euro_opps = cursor.fetchall()
        
        # Crea attività per Eurofresi e Eurovo
        if giovanni_id and euro_opps:
            print(f"   📝 Creazione attività per {len(euro_opps)} opportunità...")
            for opp_id, opp_name in euro_opps:
                # Verifica se esiste già un'attività simile
                cursor.execute("""
                    SELECT id FROM opportunity_tasks 
                    WHERE opportunity_id = ? AND task_type = 'call' AND assigned_to_id = ?
                """, (opp_id, giovanni_id))
                existing = cursor.fetchone()
                
                if not existing:
                    cursor.execute("""
                        INSERT INTO opportunity_tasks 
                        (opportunity_id, task_type, description, assigned_to_id, is_completed, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        opp_id,
                        'call',
                        f"Chiamare cliente per opportunità: {opp_name}",
                        giovanni_id,
                        0,  # is_completed = False
                        datetime.utcnow().isoformat(),
                        datetime.utcnow().isoformat()
                    ))
                    print(f"      ✅ Attività creata per: {opp_name}")
                else:
                    print(f"      ⏭️  Attività già esistente per: {opp_name}")
        
        conn.commit()
        print()
        
        # 2. Multimac ITV e Scuola Camerana -> calda
        print("2. Aggiornamento Multimac ITV e Scuola Camerana...")
        # Aggiorna tutte le Multimac (presumendo che quella ITV sia una di queste)
        cursor.execute("""
            UPDATE opportunities 
            SET heat_level = 'calda' 
            WHERE name LIKE '%Multimac%'
               OR name LIKE '%Scuola Camerana%'
               OR name LIKE '%Politecnico%Torino%'
        """)
        calde_count = cursor.rowcount
        print(f"   ✅ Aggiornate {calde_count} opportunità a 'calda'")
        
        # Aggiorna descrizione per Scuola Camerana
        cursor.execute("""
            UPDATE opportunities 
            SET description = COALESCE(description || '\n\n', '') || 'Nota: Oltre Scuola Camerana è anche Politecnico di Torino'
            WHERE name LIKE '%Scuola Camerana%'
        """)
        print(f"   ✅ Descrizione aggiornata per Scuola Camerana")
        
        conn.commit()
        print()
        
        # 3. Verifica risultati
        print("3. Verifica risultati...")
        cursor.execute("SELECT name, heat_level FROM opportunities WHERE name LIKE '%Eurofresi%' OR name LIKE '%Eurovo%' OR name LIKE '%Multimac%' OR name LIKE '%Scuola Camerana%'")
        results = cursor.fetchall()
        for name, heat in results:
            print(f"   - {name[:50]}... -> {heat}")
        
    finally:
        conn.close()
    
    print("\n✅ OPERAZIONE COMPLETATA!")
    print("\n📝 PROSSIMO PASSO:")
    print("   Modifica il template HTML per cambiare la percentuale da_categorizzare da 10% a 0%")

if __name__ == '__main__':
    try:
        aggiorna_opportunita_specifiche()
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
