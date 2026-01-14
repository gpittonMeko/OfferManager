#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test REALE con browser - Apre la pagina e verifica errori console"""
import sys
import os
import io
import time
from playwright.sync_api import sync_playwright

# Fix encoding per Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

URL = "http://crm.infomekosrl.it:8000"

def test_browser():
    print("=" * 70)
    print("TEST BROWSER REALE - Verifica errori console")
    print("=" * 70)
    
    errors = []
    console_errors = []
    
    with sync_playwright() as p:
        # Avvia browser
        print("\n1. Avvio browser...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # Intercetta errori console
        def handle_console(msg):
            if msg.type == 'error':
                console_errors.append({
                    'type': 'console',
                    'text': msg.text,
                    'location': msg.location
                })
                print(f"  [ERROR] Console Error: {msg.text}")
        
        page.on("console", handle_console)
        
        # Traccia tutte le richieste HTTP
        failed_requests = []
        
        def handle_response(response):
            if response.status >= 400:
                failed_requests.append({
                    'url': response.url,
                    'status': response.status
                })
                print(f"  [ERROR] HTTP Error {response.status}: {response.url}")
        
        page.on("response", handle_response)
        
        # Naviga alla pagina
        print("\n2. Navigazione alla pagina...")
        try:
            page.goto(URL, wait_until='networkidle', timeout=30000)
            print(f"  [OK] Pagina caricata: {page.url}")
        except Exception as e:
            errors.append({'type': 'navigation', 'error': str(e)})
            print(f"  [ERROR] Errore navigazione: {e}")
            browser.close()
            return
        
        # Attendi caricamento completo
        print("\n3. Attendo caricamento completo...")
        time.sleep(3)
        
        # Verifica login (se necessario)
        print("\n4. Verifica login...")
        try:
            # Cerca campo username o link login
            current_url = page.url
            if '/login' in current_url.lower():
                print("  [INFO] Pagina di login rilevata - inserisco credenziali")
                
                # Prova diversi selettori per username
                username_selectors = [
                    'input[name="username"]',
                    'input[type="text"]',
                    'input[id*="username"]',
                    'input[id*="user"]'
                ]
                username_input = None
                for selector in username_selectors:
                    if page.locator(selector).count() > 0:
                        username_input = page.locator(selector).first
                        break
                
                # Prova diversi selettori per password
                password_selectors = [
                    'input[name="password"]',
                    'input[type="password"]',
                    'input[id*="password"]'
                ]
                password_input = None
                for selector in password_selectors:
                    if page.locator(selector).count() > 0:
                        password_input = page.locator(selector).first
                        break
                
                # Prova diversi selettori per submit
                submit_selectors = [
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("Login")',
                    'button:has-text("Accedi")',
                    'form button',
                    'form input[type="submit"]'
                ]
                submit_button = None
                for selector in submit_selectors:
                    if page.locator(selector).count() > 0:
                        submit_button = page.locator(selector).first
                        break
                
                if username_input:
                    username_input.fill('admin')
                    print("  [INFO] Username inserito: 'admin'")
                if password_input:
                    password_input.fill('admin')
                    print("  [INFO] Password inserita: 'admin'")
                
                # Prova a fare login usando fetch POST (come fa il frontend)
                print("  [INFO] Provo login con fetch POST...")
                try:
                    login_result = page.evaluate("""
                        async () => {
                            try {
                                const response = await fetch('/login', {
                                    method: 'POST',
                                    headers: {'Content-Type': 'application/json'},
                                    body: JSON.stringify({username: 'admin', password: 'admin'})
                                });
                                const data = await response.json();
                                return {status: response.status, data: data};
                            } catch (e) {
                                return {error: e.toString()};
                            }
                        }
                    """)
                    
                    if login_result.get('status') == 200 and login_result.get('data', {}).get('success'):
                        print("  [OK] Login riuscito!")
                        # Naviga alla dashboard
                        page.goto(f"{URL}/", wait_until='networkidle', timeout=15000)
                        time.sleep(5)
                        print(f"  [OK] Dashboard caricata - URL: {page.url}")
                    else:
                        print(f"  [WARN] Login fallito: {login_result}")
                        print("  [INFO] Continuo comunque per verificare errori sulla pagina di login...")
                        # Non fare nulla, continua il test
                except Exception as e:
                    print(f"  [WARN] Errore login fetch: {e}")
                    # Fallback: prova a cliccare sul submit
                    if submit_button:
                        submit_button.click()
                        page.wait_for_load_state('networkidle', timeout=10000)
                        time.sleep(2)
                else:
                    print("  [WARN] Pulsante submit non trovato")
            else:
                print("  [INFO] Non sulla pagina di login - potrebbe essere già loggato")
        except Exception as e:
            print(f"  [WARN] Errore login: {e}")
            import traceback
            traceback.print_exc()
        
        # Attendi caricamento dashboard (o pagina corrente)
        print("\n5. Attendo caricamento completo...")
        try:
            # Attendi che la pagina sia completamente caricata
            page.wait_for_load_state('networkidle', timeout=15000)
            time.sleep(3)
            current_url = page.url
            print(f"  [OK] Pagina caricata - URL: {current_url}")
            
            # Se siamo sulla dashboard, verifica che non ci siano errori
            if '/login' not in current_url.lower():
                print("  [INFO] Sulla dashboard - verifico errori...")
                # Attendi che tutte le chiamate API vengano completate
                time.sleep(5)
        except Exception as e:
            print(f"  [WARN] Timeout caricamento: {e}")
        
        # Verifica errori JavaScript nella console (già intercettati da handle_console)
        print("\n6. Verifica errori console JavaScript...")
        
        # Controlla errori nella pagina
        try:
            page_errors = page.evaluate("""
                () => {
                    const errors = [];
                    // Controlla se ci sono errori globali
                    if (window.errors) {
                        errors.push(...window.errors);
                    }
                    // Controlla se ci sono errori in console.error
                    if (window.console && window.console._errors) {
                        errors.push(...window.console._errors);
                    }
                    return errors;
                }
            """)
            if page_errors:
                console_errors.extend([{'type': 'page', 'text': str(e)} for e in page_errors])
        except Exception as e:
            print(f"  [WARN] Errore verifica errori pagina: {e}")
        
        # Verifica chiamate API fallite (già tracciate in handle_response)
        print("\n7. Verifica chiamate API...")
        
        # Riepilogo
        print("\n" + "=" * 70)
        print("RIEPILOGO ERRORI")
        print("=" * 70)
        
        if console_errors:
            print(f"\n❌ Errori Console: {len(console_errors)}")
            for err in console_errors[:10]:  # Mostra primi 10
                print(f"  - {err['text']}")
        else:
            print("\n✓ Nessun errore console")
        
        if errors:
            print(f"\n❌ Errori HTTP: {len(errors)}")
            for err in errors[:10]:
                print(f"  - {err.get('url', err.get('error', 'Unknown'))}: {err.get('status', 'N/A')}")
        else:
            print("\n✓ Nessun errore HTTP")
        
        if failed_requests:
            print(f"\n❌ Richieste fallite: {len(failed_requests)}")
            for req in failed_requests[:10]:
                print(f"  - {req['url']}: {req['status']}")
        else:
            print("\n✓ Nessuna richiesta fallita")
        
        # Screenshot finale
        print("\n8. Salvataggio screenshot...")
        try:
            screenshot_path = '/tmp/test_browser_screenshot.png'
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"  [OK] Screenshot salvato: {screenshot_path}")
        except Exception as e:
            print(f"  [WARN] Errore screenshot: {e}")
        
        browser.close()
        
        # Filtra errori 401 di login (normali se credenziali sbagliate)
        real_errors = [e for e in console_errors if '401' not in e.get('text', '') or '/login' not in e.get('text', '')]
        real_failed = [r for r in failed_requests if r['status'] != 401 or '/login' not in r['url']]
        
        # Risultato finale
        total_errors = len(real_errors) + len(errors) + len(real_failed)
        if total_errors > 0:
            print("\n" + "=" * 70)
            print(f"[ERROR] TROVATI {total_errors} ERRORI REALI!")
            print("=" * 70)
            if real_errors:
                print("\nErrori console (esclusi login 401):")
                for err in real_errors[:10]:
                    print(f"  - {err['text']}")
            if real_failed:
                print("\nRichieste fallite (esclusi login 401):")
                for req in real_failed[:10]:
                    print(f"  - {req['url']}: {req['status']}")
            sys.exit(1)
        else:
            print("\n" + "=" * 70)
            print("[OK] NESSUN ERRORE REALE TROVATO!")
            print("(Errori 401 login sono normali se credenziali non corrette)")
            print("=" * 70)
            sys.exit(0)

if __name__ == '__main__':
    test_browser()
