import sys
import os

# Vai nella directory del progetto
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("="*70)
print("  AVVIO DIRETTO OFFERMANAGER CRM")
print("="*70)
print()
print("Directory:", os.getcwd())
print()
print("Avvio app su http://localhost:5000")
print("Login: marco / demo123")
print()
print("="*70)
print()

# Apri browser
import threading
import time
def open_browser():
    time.sleep(3)
    try:
        import webbrowser
        webbrowser.open('http://localhost:5000')
    except:
        pass
threading.Thread(target=open_browser, daemon=True).start()

# Avvia
try:
    import crm_app
    crm_app.app.run(host='0.0.0.0', port=5000, debug=False)
except Exception as e:
    print("\nERRORE:")
    print(f"{type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    input("\nPremi INVIO...")



















