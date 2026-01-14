#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test frontend gestione link SMB"""
import os
import re

template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'app_mekocrm_completo.html')

if not os.path.exists(template_path):
    print("ERRORE: Template HTML non trovato")
    exit(1)

with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 70)
print("TEST FRONTEND - GESTIONE LINK SMB")
print("=" * 70)

errors = []

# 1. Verifica funzione downloadOpportunityFile
if 'downloadOpportunityFile' not in content:
    errors.append("Funzione downloadOpportunityFile non trovata")
else:
    print("OK 1. Funzione downloadOpportunityFile trovata")
    
    # Estrai la funzione
    func_match = re.search(r'function downloadOpportunityFile\([^)]+\)\s*\{[^}]*\}', content, re.DOTALL)
    if not func_match:
        errors.append("Corpo funzione downloadOpportunityFile non trovato")
    else:
        func_body = func_match.group(0)
        
        # Verifica gestione smbPath
        if 'smbPath' not in func_body:
            errors.append("downloadOpportunityFile non gestisce smbPath")
        else:
            print("OK 2. downloadOpportunityFile gestisce smbPath")
        
        # Verifica apertura link SMB
        if 'file:///' not in func_body and 'window.open' not in func_body and 'window.location.href' not in func_body:
            errors.append("downloadOpportunityFile non apre link SMB")
        else:
            print("OK 3. downloadOpportunityFile apre link SMB")

# 2. Verifica che i file nella lista HTML passino smbPath
file_map_match = re.search(r'data\.files\.map\(file =>', content)
if not file_map_match:
    errors.append("Mappatura file non trovata")
else:
    print("OK 4. Mappatura file trovata")
    
    # Verifica che smb_path venga passato
    if 'smb_path' not in content[content.find('data.files.map'):content.find('data.files.map')+2000]:
        errors.append("smb_path non viene passato nella mappatura file")
    else:
        print("OK 5. smb_path viene passato nella mappatura file")

# 3. Verifica onclick con smbPath
if 'onclick=' not in content or 'downloadOpportunityFile' not in content:
    errors.append("onclick con downloadOpportunityFile non trovato")
else:
    # Cerca pattern onclick con smbPath
    onclick_pattern = r'onclick=["\']downloadOpportunityFile\([^)]+smbPath[^)]*\)'
    if not re.search(onclick_pattern, content):
        # Verifica pattern alternativo con smb_path
        if 'smb_path' in content and 'downloadOpportunityFile' in content:
            # Verifica che venga costruito correttamente
            if 'smbPath' in content.split('downloadOpportunityFile')[1][:1000]:
                print("OK 6. onclick passa smbPath correttamente")
            else:
                errors.append("onclick non passa smbPath correttamente")
        else:
            errors.append("onclick non passa smbPath")
    else:
        print("OK 6. onclick passa smbPath correttamente")

if errors:
    print("\nERRORE: Problemi trovati nel frontend:")
    for e in errors:
        print(f"  - {e}")
    exit(1)
else:
    print("\n" + "=" * 70)
    print("✅ FRONTEND: TUTTO CORRETTO!")
    print("=" * 70)
    exit(0)
