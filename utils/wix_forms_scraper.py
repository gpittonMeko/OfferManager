#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper per estrarre tutti i contatti dal form Wix Studio
Usa Playwright per accedere al dashboard Wix e scaricare i dati
"""
import sys
import os
import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# URL del dashboard Wix con le submissions
WIX_DASHBOARD_URL = "https://manage.wix.com/dashboard/bda1271d-bd44-4493-8680-afed13606b5a/wix-forms/form/8981b8b2-29b4-4d25-a485-ef1995026251/submissions?folder=%5B%7B%22id%22%3A%22main%22%2C%22name%22%3A%22Moduli+inviati%22%7D%5D&sort=createdDate+desc&selectedColumns=createdDate%2Cfirst_name_a6f7%2Cemail_0481%2Ctelefono_c7b7%2Cprodotto%2Clong_answer_4009"


def scrape_wix_submissions(headless=False, wait_for_manual_login=True):
    """
    Scrapa tutte le submissions dal form Wix Studio
    
    Args:
        headless: Se True, browser invisibile
        wait_for_manual_login: Se True, aspetta che l'utente faccia login manualmente
    
    Returns:
        list: Lista di dict con i dati delle submissions
    """
    submissions = []
    
    print("=" * 70)
    print("🚀 INIZIO SCRAPING WIX STUDIO FORM")
    print("=" * 70)
    print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 URL: {WIX_DASHBOARD_URL}")
    print("=" * 70)
    print()
    
    with sync_playwright() as p:
        # Avvia browser (non headless per permettere login manuale)
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        try:
            print("📥 Navigazione al dashboard Wix...")
            page.goto(WIX_DASHBOARD_URL, wait_until='networkidle', timeout=60000)
            
            if wait_for_manual_login:
                print("\n" + "=" * 70)
                print("⏳ ATTENDI LOGIN MANUALE")
                print("=" * 70)
                print("1. Fai login su Wix nel browser che si è aperto")
                print("2. Naviga alla pagina delle submissions")
                print("3. Premi INVIO qui quando sei pronto per lo scraping...")
                print("=" * 70)
                input()
            
            # Aspetta che la pagina sia caricata
            print("\n⏳ Attendo caricamento pagina...")
            time.sleep(5)
            
            # Cerca la tabella delle submissions
            print("🔍 Cerca tabella submissions...")
            
            # Prova diversi selettori per la tabella
            table_selectors = [
                'table',
                '[data-testid="submissions-table"]',
                '.submissions-table',
                'table[role="table"]',
                'div[role="table"]'
            ]
            
            table = None
            for selector in table_selectors:
                try:
                    table = page.query_selector(selector)
                    if table:
                        print(f"✅ Trovata tabella con selettore: {selector}")
                        break
                except:
                    continue
            
            if not table:
                # Prova a cercare righe della tabella direttamente
                print("🔍 Cerca righe della tabella...")
                rows = page.query_selector_all('tr, [role="row"]')
                print(f"   Trovate {len(rows)} righe potenziali")
                
                if len(rows) > 1:  # Skip header
                    # Estrai dati dalle righe
                    for i, row in enumerate(rows[1:], 1):  # Skip prima riga (header)
                        try:
                            cells = row.query_selector_all('td, [role="gridcell"]')
                            if len(cells) >= 5:
                                submission = {
                                    'created_date': cells[0].inner_text().strip() if len(cells) > 0 else '',
                                    'name': cells[1].inner_text().strip() if len(cells) > 1 else '',
                                    'email': cells[2].inner_text().strip() if len(cells) > 2 else '',
                                    'phone': cells[3].inner_text().strip() if len(cells) > 3 else '',
                                    'product': cells[4].inner_text().strip() if len(cells) > 4 else '',
                                    'message': cells[5].inner_text().strip() if len(cells) > 5 else ''
                                }
                                
                                # Valida che abbia almeno email
                                if submission['email']:
                                    submissions.append(submission)
                                    print(f"  ✅ {i}. {submission['name']} ({submission['email']})")
                        except Exception as e:
                            print(f"  ⚠️  Errore riga {i}: {str(e)}")
                            continue
            else:
                # Estrai dati dalla tabella
                rows = table.query_selector_all('tr')
                print(f"📊 Trovate {len(rows)} righe nella tabella")
                
                for i, row in enumerate(rows[1:], 1):  # Skip header
                    try:
                        cells = row.query_selector_all('td')
                        if len(cells) >= 5:
                            submission = {
                                'created_date': cells[0].inner_text().strip() if len(cells) > 0 else '',
                                'name': cells[1].inner_text().strip() if len(cells) > 1 else '',
                                'email': cells[2].inner_text().strip() if len(cells) > 2 else '',
                                'phone': cells[3].inner_text().strip() if len(cells) > 3 else '',
                                'product': cells[4].inner_text().strip() if len(cells) > 4 else '',
                                'message': cells[5].inner_text().strip() if len(cells) > 5 else ''
                            }
                            
                            if submission['email']:
                                submissions.append(submission)
                                print(f"  ✅ {i}. {submission['name']} ({submission['email']})")
                    except Exception as e:
                        print(f"  ⚠️  Errore riga {i}: {str(e)}")
                        continue
            
            # Se non abbiamo trovato dati, prova a fare screenshot per debug
            if not submissions:
                print("\n⚠️  Nessun dato trovato. Faccio screenshot per debug...")
                screenshot_path = '/tmp/wix_page_debug.png'
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"   Screenshot salvato in: {screenshot_path}")
                
                # Prova a estrarre tutto il testo della pagina
                page_text = page.inner_text('body')
                print(f"\n📄 Primi 500 caratteri della pagina:")
                print(page_text[:500])
                
                # Cerca pattern email nella pagina
                import re
                emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', page_text)
                print(f"\n📧 Email trovate nel testo: {len(emails)}")
                if emails:
                    print(f"   Prime 5: {emails[:5]}")
            
            # Se ci sono paginazione, naviga alle pagine successive
            print("\n🔍 Verifica paginazione...")
            try:
                # Cerca pulsanti "Next" o numeri di pagina
                next_button = page.query_selector('button[aria-label*="Next"], button:has-text("Next"), [aria-label*="successiva"]')
                page_num = 1
                
                while next_button and page_num < 20:  # Max 20 pagine
                    print(f"\n📄 Pagina {page_num + 1}...")
                    try:
                        next_button.click()
                        time.sleep(2)  # Attendi caricamento
                        
                        # Estrai dati da questa pagina
                        rows = page.query_selector_all('tr, [role="row"]')
                        page_submissions = []
                        
                        for row in rows[1:]:
                            cells = row.query_selector_all('td, [role="gridcell"]')
                            if len(cells) >= 5:
                                submission = {
                                    'created_date': cells[0].inner_text().strip() if len(cells) > 0 else '',
                                    'name': cells[1].inner_text().strip() if len(cells) > 1 else '',
                                    'email': cells[2].inner_text().strip() if len(cells) > 2 else '',
                                    'phone': cells[3].inner_text().strip() if len(cells) > 3 else '',
                                    'product': cells[4].inner_text().strip() if len(cells) > 4 else '',
                                    'message': cells[5].inner_text().strip() if len(cells) > 5 else ''
                                }
                                if submission['email']:
                                    page_submissions.append(submission)
                        
                        if page_submissions:
                            submissions.extend(page_submissions)
                            print(f"   ✅ Trovate {len(page_submissions)} submissions")
                        else:
                            break
                        
                        # Cerca prossimo pulsante
                        next_button = page.query_selector('button[aria-label*="Next"], button:has-text("Next"), [aria-label*="successiva"]')
                        page_num += 1
                    except Exception as e:
                        print(f"   ⚠️  Errore pagina {page_num + 1}: {str(e)}")
                        break
            except Exception as e:
                print(f"   ⚠️  Errore paginazione: {str(e)}")
            
            browser.close()
            
        except Exception as e:
            print(f"\n❌ Errore durante scraping: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Screenshot di debug
            try:
                screenshot_path = '/tmp/wix_error.png'
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"\n📸 Screenshot errore salvato in: {screenshot_path}")
            except:
                pass
            
            browser.close()
            return []
    
    print(f"\n{'='*70}")
    print(f"✅ SCRAPING COMPLETATO")
    print(f"   Trovate {len(submissions)} submissions")
    print(f"{'='*70}")
    
    return submissions


def save_submissions_to_json(submissions, output_file='wix_submissions.json'):
    """Salva le submissions in un file JSON"""
    # Normalizza le date
    for sub in submissions:
        if sub.get('created_date'):
            # Prova a convertire date in formato ISO
            try:
                # Wix potrebbe avere formato "12 gen 2026, 12:33" o simile
                date_str = sub['created_date']
                # Per ora lascia come stringa, sarà normalizzato durante import
                pass
            except:
                pass
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(submissions, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Salvate {len(submissions)} submissions in: {output_file}")
    return output_file


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrapa submissions da Wix Studio')
    parser.add_argument('--headless', action='store_true', help='Browser invisibile')
    parser.add_argument('--no-wait', action='store_true', help='Non aspettare login manuale')
    parser.add_argument('--output', default='wix_submissions.json', help='File JSON di output')
    
    args = parser.parse_args()
    
    submissions = scrape_wix_submissions(
        headless=args.headless,
        wait_for_manual_login=not args.no_wait
    )
    
    if submissions:
        save_submissions_to_json(submissions, args.output)
        print(f"\n✅ Completato! Ora puoi importare con:")
        print(f"   python3 utils/wix_forms_import.py {args.output}")
    else:
        print("\n❌ Nessuna submission trovata. Verifica:")
        print("   1. Hai fatto login su Wix?")
        print("   2. Sei sulla pagina corretta delle submissions?")
        print("   3. La struttura della pagina è cambiata?")
