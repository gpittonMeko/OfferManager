#!/usr/bin/env python3
"""
Script per verificare che il file DNS corretto sia completo e senza errori
"""
import csv

def verifica_file_csv(file_path):
    """Verifica il file CSV DNS"""
    print(f"🔍 Verifica file: {file_path}\n")
    
    records = []
    errors = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            nome = row['NOME'].strip()
            tipo = row['TIPO'].strip()
            valore = row['VALORE'].strip()
            
            records.append({
                'nome': nome,
                'tipo': tipo,
                'valore': valore
            })
            
            # Verifica errori
            if tipo == 'TXT':
                # Controlla che non ci siano virgolette nei valori TXT
                if '"' in valore and not valore.startswith('"') and not valore.endswith('"'):
                    errors.append(f"❌ Record TXT {nome}: contiene virgolette nel valore")
                if valore.startswith('""') or valore.endswith('""'):
                    errors.append(f"❌ Record TXT {nome}: ha doppie virgolette")
            
            if tipo in ['A', 'MX', 'CNAME']:
                # Controlla punti finali
                if valore.endswith('"') and not valore.startswith('"'):
                    errors.append(f"⚠️ Record {tipo} {nome}: possibile virgoletta finale errata")
    
    print(f"📊 Totale record trovati: {len(records)}\n")
    
    # Verifica record Mailgun richiesti
    print("🔍 Verifica record Mailgun:\n")
    
    mx_records = [r for r in records if r['tipo'] == 'MX' and 'mailgun' in r['valore'].lower()]
    print(f"✅ Record MX Mailgun trovati: {len(mx_records)}")
    for mx in mx_records:
        if '.eu.' in mx['valore']:
            print(f"   ✅ {mx['nome']} → {mx['valore']}")
        else:
            print(f"   ⚠️ {mx['nome']} → {mx['valore']} (manca .eu)")
    
    cname_tracking = [r for r in records if r['nome'] == 'email.infomekosrl.it.']
    if cname_tracking:
        if 'eu.mailgun.org' in cname_tracking[0]['valore']:
            print(f"   ✅ CNAME tracking corretto: {cname_tracking[0]['valore']}")
        else:
            print(f"   ⚠️ CNAME tracking: {cname_tracking[0]['valore']} (dovrebbe essere eu.mailgun.org.)")
    
    dkim_records = [r for r in records if 's1._domainkey' in r['nome']]
    if dkim_records:
        print(f"   ✅ Record DKIM s1._domainkey presente")
    else:
        print(f"   ❌ Record DKIM s1._domainkey MANCANTE")
    
    # Verifica record rimossi
    mx_register = [r for r in records if 'mail.register.it' in r['valore']]
    if mx_register:
        print(f"   ⚠️ ATTENZIONE: Record MX mail.register.it ancora presente - dovrebbe essere rimosso")
    else:
        print(f"   ✅ Record MX mail.register.it rimosso correttamente")
    
    print(f"\n📋 Errori trovati: {len(errors)}")
    if errors:
        print("\n⚠️ Errori:")
        for error in errors:
            print(f"   {error}")
    else:
        print("   ✅ Nessun errore trovato!")
    
    return len(errors) == 0, records

if __name__ == "__main__":
    import sys
    file_path = sys.argv[1] if len(sys.argv) > 1 else "Elenco_record_dns_infomekosrl.it_FINALE.csv"
    
    try:
        is_valid, records = verifica_file_csv(file_path)
        if is_valid:
            print("\n✅ File DNS corretto e valido!")
        else:
            print("\n⚠️ File DNS contiene errori da correggere")
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()







