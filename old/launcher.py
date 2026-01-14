#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Launcher OfferManager CRM - Con diagnostica completa
"""
import sys
import os
import subprocess
import time

print("\n" + "="*70)
print("  LAUNCHER OFFERMANAGER CRM - DIAGNOSTICA E AVVIO")
print("="*70 + "\n")

# [1] Vai nella directory corretta
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
print(f"[1/6] Directory: {os.getcwd()}")
print(f"      OK\n")
sys.stdout.flush()

# [2] Verifica file
print("[2/6] Verifica file...")
sys.stdout.flush()
files_needed = ['crm_app.py', 'templates/dashboard_completa.html']
missing = []
for f in files_needed:
    if os.path.exists(f):
        print(f"      OK {f}")
    else:
        print(f"      MANCA {f}")
        missing.append(f)
    sys.stdout.flush()

if missing:
    print(f"\nERRORE: File mancanti: {missing}")
    input("\nPremi INVIO per uscire...")
    sys.exit(1)
print()
sys.stdout.flush()

# [3] Verifica Python
print(f"[3/6] Python: {sys.version.split()[0]}")
print(f"      OK\n")
sys.stdout.flush()

# [4] Verifica moduli
print("[4/6] Verifica moduli...")
sys.stdout.flush()

print("      Controllo Flask...")
sys.stdout.flush()
try:
    import flask
    print("      OK Flask installato")
    sys.stdout.flush()
    flask_ok = True
except ImportError:
    print("      MANCA Flask")
    sys.stdout.flush()
    flask_ok = False

print("      Controllo Flask-SQLAlchemy...")
sys.stdout.flush()
try:
    import flask_sqlalchemy
    print("      OK Flask-SQLAlchemy installato")
    sys.stdout.flush()
    sqlalchemy_ok = True
except ImportError as e:
    print(f"      MANCA Flask-SQLAlchemy: {e}")
    sys.stdout.flush()
    sqlalchemy_ok = False
except Exception as e:
    print(f"      ERRORE import Flask-SQLAlchemy: {e}")
    sys.stdout.flush()
    sqlalchemy_ok = False

if not flask_ok or not sqlalchemy_ok:
    print("\n      >>> INSTALLAZIONE IN CORSO <<<")
    print("      Questo puo richiedere 1-2 minuti...")
    print("      Attendere...\n")
    sys.stdout.flush()
    
    # Mostra output di pip
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "flask", "flask-sqlalchemy"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    print(result.stdout)
    sys.stdout.flush()
    
    if result.returncode == 0:
        print("\n      OK Moduli installati!\n")
    else:
        print("\n      ERRORE installazione!")
        input("\nPremi INVIO per uscire...")
        sys.exit(1)
else:
    print("      Tutto installato!\n")

sys.stdout.flush()

# [5] Test import crm_app
print("[5/6] Test caricamento crm_app.py...")
sys.stdout.flush()
try:
    # Test compilazione
    with open('crm_app.py', 'r', encoding='utf-8') as f:
        compile(f.read(), 'crm_app.py', 'exec')
    print("      OK Sintassi corretta\n")
    sys.stdout.flush()
except SyntaxError as e:
    print(f"      ERRORE SINTASSI: {e}")
    input("\nPremi INVIO per uscire...")
    sys.exit(1)
except Exception as e:
    print(f"      ERRORE: {e}")
    input("\nPremi INVIO per uscire...")
    sys.exit(1)

# [6] Avvio app
print("[6/6] Avvio applicazione...")
print("="*70)
print()
print("  App in avvio su: http://localhost:5000")
print()
print("  Login:")
print("     Username: marco")
print("     Password: demo123")
print()
print("="*70)
print()
print("  Per fermare l'app: premi Ctrl+C o chiudi questa finestra")
print()
print("-"*70)
print()
sys.stdout.flush()

# Apri browser dopo 3 secondi
import threading
def open_browser():
    time.sleep(3)
    try:
        import webbrowser
        webbrowser.open('http://localhost:5000')
    except:
        pass

threading.Thread(target=open_browser, daemon=True).start()

# Avvia app
try:
    import crm_app
    print(">>> APP IN AVVIO <<<\n")
    sys.stdout.flush()
    crm_app.app.run(host='0.0.0.0', port=5000, debug=False)
except KeyboardInterrupt:
    print("\n\nApp fermata dall'utente")
except Exception as e:
    print(f"\n\nERRORE DURANTE AVVIO:")
    print(f"{type(e).__name__}: {e}")
    print("\nDettagli completi:")
    import traceback
    traceback.print_exc()
    print()
    input("\nPremi INVIO per uscire...")
    sys.exit(1)
