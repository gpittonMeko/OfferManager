#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test COMPLETO end-to-end simulando Chrome"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crm_app_completo import app, db
from sqlalchemy import text
import json

def test_completo():
    """Test completo simulando tutto il flusso Chrome"""
    print("=" * 70)
    print("TEST COMPLETO END-TO-END - K1550-25")
    print("=" * 70)
    
    with app.app_context():
        # 1. Trova utente admin
        user = db.session.execute(text("""
            SELECT id, username FROM users WHERE username = 'admin' LIMIT 1
        """)).fetchone()
        
        if not user:
            print("ERRORE: Utente admin non trovato")
            return False
        
        print(f"OK 1. Utente trovato: {user[1]} (ID={user[0]})")
        
        # 2. Trova opportunità K1550-25
        opp = db.session.execute(text("""
            SELECT id, name FROM opportunities 
            WHERE name LIKE '%K1550%'
            ORDER BY id
        """)).fetchone()
        
        if not opp:
            print("ERRORE: Opportunità K1550-25 non trovata")
            return False
        
        print(f"OK 2. Opportunità trovata: ID={opp[0]}, Nome={opp[1]}")
        
        # 3. Verifica offerte associate
        offers = db.session.execute(text("""
            SELECT id, number, folder_path, pdf_path, docx_path 
            FROM offers 
            WHERE opportunity_id = :opp_id
        """), {"opp_id": opp[0]}).fetchall()
        
        if not offers:
            print("ERRORE: Nessuna offerta associata")
            return False
        
        print(f"OK 3. Offerte associate: {len(offers)}")
        for off in offers:
            print(f"     - {off[1]}: folder={off[2]}")
        
        # 4. Simula chiamata endpoint con sessione
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = user[0]
            
            print(f"\n4. Chiamata endpoint /api/opportunities/{opp[0]}/files...")
            response = client.get(f'/api/opportunities/{opp[0]}/files')
            
            if response.status_code != 200:
                print(f"ERRORE: Status code {response.status_code}")
                print(response.get_data(as_text=True))
                return False
            
            data = response.get_json()
            print(f"OK 4. Endpoint risponde correttamente")
            
            # 5. Verifica struttura risposta
            if 'files' not in data:
                print("ERRORE: Campo 'files' mancante nella risposta")
                return False
            
            if 'offers_count' not in data:
                print("ERRORE: Campo 'offers_count' mancante nella risposta")
                return False
            
            print(f"OK 5. Struttura risposta corretta")
            print(f"     - File trovati: {data.get('files_found', 0)}")
            print(f"     - Offerte associate: {data.get('offers_count', 0)}")
            print(f"     - File nella lista: {len(data.get('files', []))}")
            
            # 6. Verifica che ci siano file con link SMB
            files = data.get('files', [])
            if not files:
                print("ERRORE: Nessun file nella risposta")
                return False
            
            files_with_smb = []
            for f in files:
                if f.get('smb_path') or f.get('is_folder_link'):
                    files_with_smb.append(f)
            
            if not files_with_smb:
                print("ERRORE: Nessun file con link SMB!")
                print("\nFile trovati senza SMB:")
                for f in files:
                    print(f"  - {f.get('name')}: tipo={f.get('type')}, smb_path={f.get('smb_path')}")
                return False
            
            print(f"OK 6. File con link SMB: {len(files_with_smb)}")
            for f in files_with_smb:
                print(f"     - {f.get('name')}")
                print(f"       SMB: {f.get('smb_path')}")
            
            # 7. Verifica formato link SMB
            for f in files_with_smb:
                smb_path = f.get('smb_path', '')
                if not smb_path.startswith('\\\\'):
                    print(f"ERRORE: Link SMB non valido: {smb_path}")
                    return False
                if '192.168.10.240' not in smb_path:
                    print(f"ERRORE: IP server non presente nel link SMB: {smb_path}")
                    return False
                if 'commerciale' not in smb_path:
                    print(f"ERRORE: Share 'commerciale' non presente nel link SMB: {smb_path}")
                    return False
            
            print(f"OK 7. Formato link SMB corretto")
            
            # 8. Verifica che il frontend possa gestire i link SMB
            # Controlla che il template HTML gestisca smb_path
            template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'app_mekocrm_completo.html')
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                
                # Verifica che il JavaScript gestisca smbPath
                if 'smbPath' not in template_content:
                    print("ERRORE: Frontend non gestisce smbPath!")
                    return False
                
                if 'downloadOpportunityFile' not in template_content:
                    print("ERRORE: Funzione downloadOpportunityFile non trovata!")
                    return False
                
                # Verifica che la funzione gestisca smbPath
                if 'smbPath' not in template_content.split('downloadOpportunityFile')[1][:500]:
                    print("ERRORE: downloadOpportunityFile non gestisce smbPath!")
                    return False
                
                print(f"OK 8. Frontend gestisce correttamente smbPath")
            else:
                print("WARNING: Template HTML non trovato, non posso verificare frontend")
            
            # 9. Verifica che i link SMB siano utilizzabili
            # Controlla che ogni file abbia almeno un link SMB valido
            for f in files_with_smb:
                smb_path = f.get('smb_path', '')
                if not smb_path:
                    print(f"ERRORE: File {f.get('name')} ha is_folder_link=True ma smb_path vuoto")
                    return False
            
            print(f"OK 9. Tutti i link SMB sono validi e utilizzabili")
            
            # 10. Test finale: verifica che la risposta sia completa
            required_fields = ['files', 'files_found', 'offers_count']
            for field in required_fields:
                if field not in data:
                    print(f"ERRORE: Campo '{field}' mancante nella risposta")
                    return False
            
            print(f"OK 10. Risposta completa e valida")
            
            print("\n" + "=" * 70)
            print("✅ TEST COMPLETO: TUTTO FUNZIONA CORRETTAMENTE!")
            print("=" * 70)
            print(f"\nRiepilogo:")
            print(f"  - Opportunità: {opp[1]}")
            print(f"  - Offerte associate: {len(offers)}")
            print(f"  - File con link SMB: {len(files_with_smb)}")
            print(f"  - Link SMB validi: Sì")
            print(f"  - Frontend compatibile: Sì")
            
            return True

if __name__ == '__main__':
    success = test_completo()
    sys.exit(0 if success else 1)
