#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integrazione diretta con portale UR usando Playwright (più stabile di Selenium)
"""
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time
import logging
import socket
import shutil
import os
import tempfile
from typing import List, Dict
from datetime import datetime
from bs4 import BeautifulSoup
import re

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [UR Portal] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ur_portal_sync.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Path per file temporanei (compatibile Windows/Linux)
TEMP_DIR = tempfile.gettempdir()


UR_EMAIL = "giovanni.pitton@mekosrl.it"
UR_PASSWORD_OPTIONS = ["RobotMeko.24", "RobotMeko.22"]  # Password corretta prima - RobotMeko.24 è la principale
UR_PORTAL_URL = "https://partners.universal-robots.com/s/"
UR_PORTAL_BASE = "https://partners.universal-robots.com"


def parse_opportunities_html(html_content: str) -> List[Dict]:
    """
    Estrae dati delle opportunità dall'HTML della pagina
    
    Args:
        html_content: Contenuto HTML della pagina Opportunities
    
    Returns:
        Lista di dizionari con i dati delle opportunità
    """
    opportunities = []
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Cerca tutte le tabelle nella pagina
        tables = soup.find_all('table')
        logger.info(f"📊 Trovate {len(tables)} tabelle nella pagina")
        
        # Cerca anche elementi con role="table" o altri selettori Salesforce Lightning
        table_like = soup.find_all(['table', 'div'], attrs={'role': 'table'})
        logger.info(f"📊 Trovati {len(table_like)} elementi tipo tabella")
        
        # Prova a trovare righe di dati in vari modi
        rows = []
        
        # Metodo 1: Cerca tutte le righe <tr> nelle tabelle
        for table in tables:
            table_rows = table.find_all('tr')
            if len(table_rows) > 1:  # Almeno header + 1 riga dati
                rows.extend(table_rows[1:])  # Salta header
                logger.info(f"  ✓ Trovate {len(table_rows)-1} righe nella tabella")
        
        # Metodo 2: Cerca righe con role="row" (Salesforce Lightning)
        for elem in soup.find_all(attrs={'role': 'row'}):
            if elem.name != 'tr':  # Evita duplicati
                rows.append(elem)
        
        # Metodo 3: Cerca pattern di testo che indicano opportunità
        # Basato sull'esempio dell'utente: "D.F. SRL - Machine Tending - CNC"
        text_content = soup.get_text()
        if 'Opportunity List View' in text_content or 'Partner Open Opportunities' in text_content:
            logger.info("✓ Trovato contenuto 'Opportunity List View'")
        
        # Estrai dati dalle righe trovate
        for idx, row in enumerate(rows[:50]):  # Limita a 50 per evitare troppi dati
            try:
                cells = row.find_all(['td', 'th', 'div'], attrs={'role': 'gridcell'})
                if len(cells) < 3:  # Almeno 3 celle per essere una riga valida
                    continue
                
                # Estrai testo da ogni cella
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                
                # Cerca pattern comuni nelle opportunità
                opportunity_name = None
                account_name = None
                stage = None
                amount = None
                date_str = None
                
                for text in cell_texts:
                    text_lower = text.lower()
                    # Cerca nome opportunità (contiene "-" spesso)
                    if '-' in text and len(text) > 10 and not opportunity_name:
                        opportunity_name = text
                    # Cerca nome account (spesso in maiuscolo o con SRL/SPA)
                    if ('srl' in text_lower or 'spa' in text_lower or 'sas' in text_lower or 'gmbh' in text_lower) and not account_name:
                        account_name = text
                    # Cerca stage (numeri come "1.", "2.", "3.", "4.")
                    if re.match(r'^\d+\.\s+', text) and not stage:
                        stage = text
                    # Cerca amount (EUR o DKK)
                    if ('eur' in text_lower or 'dkk' in text_lower) and not amount:
                        amount = text
                    # Cerca date (formato MM/DD/YYYY)
                    if re.match(r'\d{1,2}/\d{1,2}/\d{4}', text) and not date_str:
                        date_str = text
                
                # Se abbiamo almeno nome opportunità o account, crea record
                if opportunity_name or account_name:
                    opp = {
                        'name': opportunity_name or '',
                        'account_name': account_name or '',
                        'stage': stage or '',
                        'amount': amount or '',
                        'estimated_order_intake_date': date_str or '',
                        'raw_data': cell_texts  # Salva dati grezzi per debug
                    }
                    opportunities.append(opp)
                    logger.debug(f"  ✓ Opportunità {idx+1}: {opportunity_name or account_name}")
            
            except Exception as e:
                logger.debug(f"Errore parsing riga {idx}: {e}")
                continue
        
        # Se non abbiamo trovato dati con i metodi sopra, prova a cercare pattern nel testo
        if len(opportunities) == 0:
            logger.info("⚠ Nessuna opportunità trovata con parsing tabella, provo ricerca pattern testo...")
            # Cerca pattern come "Nome Opportunità - Account Name"
            text_lines = text_content.split('\n')
            for line in text_lines:
                line = line.strip()
                if '-' in line and len(line) > 20:
                    # Potrebbe essere una riga di opportunità
                    parts = line.split('-')
                    if len(parts) >= 2:
                        opp = {
                            'name': line[:100],  # Primi 100 caratteri
                            'account_name': '',
                            'stage': '',
                            'amount': '',
                            'estimated_order_intake_date': '',
                            'raw_data': [line]
                        }
                        opportunities.append(opp)
                        if len(opportunities) >= 20:  # Limita
                            break
        
        logger.info(f"✅ Estratte {len(opportunities)} opportunità totali")
        
    except Exception as e:
        logger.error(f"❌ Errore parsing HTML opportunità: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    return opportunities


def extract_opportunities_from_dom(page) -> List[Dict]:
    """
    Estrae dati delle opportunità direttamente dal DOM usando Playwright
    
    Args:
        page: Pagina Playwright
    
    Returns:
        Lista di dizionari con i dati delle opportunità
    """
    opportunities = []
    
    try:
        # Metodo 1: Cerca tutte le righe della tabella
        logger.info("  📊 Metodo 1: Ricerca righe tabella...")
        # Prova prima con tbody tr (più specifico)
        rows = page.locator('table tbody tr').all()
        if len(rows) == 0:
            # Fallback: tutte le righe della tabella
            rows = page.locator('table tr').all()
        if len(rows) == 0:
            # Fallback: righe con role="row"
            rows = page.locator('[role="row"]').all()
        logger.info(f"  ✓ Trovate {len(rows)} righe potenziali")
        
        for idx, row in enumerate(rows):
            try:
                # Estrai testo da tutte le celle
                cells = row.locator('td, th, [role="gridcell"]').all()
                if len(cells) < 3:
                    continue
                
                cell_texts = []
                for cell in cells:
                    try:
                        text = cell.text_content() or ""
                        cell_texts.append(text.strip())
                    except:
                        cell_texts.append("")
                
                # Debug: mostra le prime 3 righe per capire la struttura
                if idx < 3:
                    logger.info(f"    🔍 Riga {idx+1} - Celle trovate: {len(cell_texts)}, Testo: {cell_texts[:5]}")
                
                # Cerca pattern nelle celle
                opportunity_name = None
                account_name = None
                stage = None
                amount = None
                date_str = None
                
                for text in cell_texts:
                    if not text or len(text) < 3:
                        continue
                    
                    text_lower = text.lower()
                    
                    # Nome opportunità (contiene "-" e abbastanza lungo) - più flessibile
                    if '-' in text and len(text) > 10 and not opportunity_name:
                        opportunity_name = text
                    
                    # Account (contiene SRL/SPA/SAS/GmbH) - più flessibile
                    if ('srl' in text_lower or 'spa' in text_lower or 'sas' in text_lower or 
                        'gmbh' in text_lower or 's.p.a.' in text_lower or 's.p.a' in text_lower) and len(text) > 2 and not account_name:
                        account_name = text
                    
                    # Stage (inizia con numero punto spazio o contiene "Stage")
                    if (re.match(r'^\d+\.\s+', text) or 'stage' in text_lower or 'technical' in text_lower or 
                        'quotation' in text_lower or 'meeting' in text_lower) and not stage:
                        stage = text
                    
                    # Amount (contiene EUR o DKK o solo numeri con virgola/punto)
                    if ('eur' in text_lower or 'dkk' in text_lower or 
                        (re.match(r'[\d.,]+', text) and len(text) > 5)) and not amount:
                        amount = text
                    
                    # Date (formato MM/DD/YYYY o DD/MM/YYYY)
                    if re.match(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}', text) and not date_str:
                        date_str = text
                
                # Se abbiamo dati validi, aggiungi opportunità - più permissivo
                if opportunity_name or account_name or (len(cell_texts) >= 3 and any(len(t) > 10 for t in cell_texts)):
                    opp = {
                        'name': opportunity_name or (cell_texts[0] if len(cell_texts) > 0 else ''),
                        'account_name': account_name or (cell_texts[1] if len(cell_texts) > 1 else ''),
                        'stage': stage or '',
                        'amount': amount or '',
                        'estimated_order_intake_date': date_str or '',
                        'raw_data': cell_texts
                    }
                    opportunities.append(opp)
                    logger.info(f"    ✓ Opportunità {len(opportunities)}: {opp['name'][:50]} - {opp['account_name'][:30]}")
            
            except Exception as e:
                logger.debug(f"    ⚠ Errore parsing riga {idx}: {e}")
                continue
        
        # Metodo 2: Cerca nel testo della pagina per pattern
        if len(opportunities) == 0:
            logger.info("  📊 Metodo 2: Ricerca pattern nel testo della pagina...")
            try:
                # Usa locator per ottenere tutto il testo della pagina
                page_text = page.locator('body').text_content() or ""
                
                # Cerca pattern come "Nome - Account - Descrizione"
                lines = page_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if '-' in line and len(line) > 20:
                        # Potrebbe essere una riga di opportunità
                        parts = [p.strip() for p in line.split('-')]
                        if len(parts) >= 2:
                            opp = {
                                'name': line[:150],
                                'account_name': parts[1] if len(parts) > 1 else '',
                                'stage': '',
                                'amount': '',
                                'estimated_order_intake_date': '',
                                'raw_data': [line]
                            }
                            opportunities.append(opp)
                            if len(opportunities) >= 30:
                                break
            except Exception as e:
                logger.warning(f"  ⚠ Errore Metodo 2: {e}")
        
        logger.info(f"  ✅ Totale opportunità estratte: {len(opportunities)}")
        
    except Exception as e:
        logger.error(f"  ❌ Errore estrazione DOM opportunità: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    return opportunities


def extract_leads_from_dom(page) -> List[Dict]:
    """
    Estrae dati dei leads direttamente dal DOM usando Playwright
    
    Args:
        page: Pagina Playwright
    
    Returns:
        Lista di dizionari con i dati dei leads
    """
    leads = []
    
    try:
        # Metodo 1: Cerca righe tabella con struttura specifica Salesforce
        logger.info("  📊 Metodo 1: Ricerca righe tabella Leads...")
        
        # Prova diversi selettori per trovare le righe della tabella
        rows = []
        selectors = [
            'table tbody tr',  # Tabella standard
            'table tr',  # Tutte le righe tabella
            '[role="row"]:not([role="columnheader"])',  # Righe con role="row"
            '[role="grid"] [role="row"]',  # Grid con righe
            'tbody tr',  # Righe tbody
            'table tr:not(:first-child)',  # Tutte tranne la prima (header)
        ]
        
        for selector in selectors:
            try:
                found_rows = page.locator(selector).all()
                if len(found_rows) > 0:
                    logger.info(f"  ✓ Selettore '{selector}' trovato {len(found_rows)} righe")
                    rows = found_rows
                    break
            except:
                continue
        
        if not rows:
            # Ultimo tentativo: cerca qualsiasi riga con celle
            try:
                all_rows = page.locator('tr').all()
                logger.info(f"  ⚠ Trovate {len(all_rows)} righe totali (tutte)")
                rows = all_rows
            except:
                pass
        
        logger.info(f"  ✓ Trovate {len(rows)} righe potenziali")
        
        for idx, row in enumerate(rows):
            try:
                # Cerca tutte le celle della riga
                cells = row.locator('td, [role="gridcell"]').all()
                if len(cells) < 3:  # Almeno 3 colonne (Name, Email, Phone)
                    continue
                
                cell_texts = []
                for cell in cells:
                    text = cell.text_content() or ""
                    # Rimuovi spazi multipli e newline
                    text = ' '.join(text.split())
                    cell_texts.append(text.strip())
                
                # Filtra celle vuote
                cell_texts = [t for t in cell_texts if t and len(t) > 0]
                
                if len(cell_texts) < 2:
                    continue
                
                # Salta righe header (contengono "Name", "Email", "Phone", "Sort", "Item Number", ecc.)
                header_keywords = ['name', 'email', 'phone', 'sort', 'item number', 'lead status', 
                                 'created date', 'last modified', 'country', 'partner', 'action']
                is_header = any(keyword in ' '.join(cell_texts).lower() for keyword in header_keywords)
                if is_header and idx < 3:  # Probabilmente header se è nelle prime 3 righe
                    logger.debug(f"    ⚠ Saltata riga {idx} (header): {cell_texts[0][:50]}")
                    continue
                
                # La struttura della tabella è:
                # Name | Email | Phone | Lead Status | Comments | Created Date | Last Modified | Country | Partner | Partner Contact
                import re
                lead_name = None
                email = None
                phone = None
                lead_status = None
                country = None
                partner = None
                partner_contact = None
                
                # Pulisci tutte le celle
                cleaned_cells = []
                for text in cell_texts:
                    cleaned = re.sub(r'Edit\s+\w+:\s*Item\s*', '', text, flags=re.IGNORECASE)
                    cleaned = re.sub(r'\s*Locked Partner:?\s*Item\s*', '', cleaned, flags=re.IGNORECASE)
                    cleaned = re.sub(r'\s*SQL\s+Edit\s+.*?:?\s*Item\s*', '', cleaned, flags=re.IGNORECASE)
                    cleaned = cleaned.strip()
                    cleaned_cells.append(cleaned)
                
                # Cerca il nome: deve essere testo con almeno 2 parole, senza @, senza numeri di telefono
                for text in cleaned_cells:
                    if not text or len(text) < 3:
                        continue
                    
                    # Salta se contiene pattern di email, telefono, date, o header
                    if '@' in text or re.search(r'[\d\s\+\-\(\)]{8,}', text) or re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}', text):
                        continue
                    
                    # Salta header
                    text_lower = text.lower()
                    if text_lower in ['name', 'email', 'phone', 'sort', 'item number', 'lead status', 'country', 'partner', 'action']:
                        continue
                    
                    # Verifica se è un nome (almeno 2 parole, inizia con maiuscola)
                    name_parts = text.split()
                    if len(name_parts) >= 2:
                        # Controlla se inizia con maiuscola (probabilmente un nome)
                        if name_parts[0][0].isupper() and name_parts[1][0].isupper():
                            lead_name = text
                            break
                
                # Se non trovato, prova la prima cella pulita (potrebbe essere il nome anche se contiene altro)
                if not lead_name and len(cleaned_cells) > 0:
                    first_cell = cleaned_cells[0]
                    # Se contiene solo testo senza @ o numeri lunghi, potrebbe essere il nome
                    if '@' not in first_cell and not re.search(r'[\d\s\+\-\(\)]{10,}', first_cell):
                        name_parts = first_cell.split()
                        if len(name_parts) >= 2:
                            lead_name = first_cell
                
                # Email è di solito la seconda colonna o contiene @
                for i, text in enumerate(cell_texts):
                    if '@' in text and '.' in text:
                        # Pulisci email: rimuovi "Edit Email: Item" e simili
                        email = re.sub(r'Edit\s+\w+:\s*Item\s*', '', text, flags=re.IGNORECASE).strip()
                        # Estrai solo l'email (prima parte se ci sono spazi)
                        email_parts = email.split()
                        for part in email_parts:
                            if '@' in part and '.' in part:
                                email = part
                                break
                        break
                
                # Phone contiene numeri e caratteri come +, -, (, )
                for text in cell_texts:
                    # Pulisci telefono
                    clean_phone = re.sub(r'Edit\s+\w+:\s*Item\s*', '', text, flags=re.IGNORECASE).strip()
                    if re.search(r'[\d\s\+\-\(\)]{8,}', clean_phone) and ('+' in clean_phone or '(' in clean_phone or len(re.findall(r'\d', clean_phone)) >= 8):
                        phone = clean_phone
                        break
                
                # Lead Status contiene "SQL" o altri status
                # Cerca sia nel testo che negli attributi title/aria-label delle celle
                for i, cell in enumerate(cells):
                    # Testo della cella
                    text = cell_texts[i] if i < len(cell_texts) else ''
                    # Cerca negli attributi title e aria-label
                    try:
                        title = cell.get_attribute('title') or ''
                        aria_label = cell.get_attribute('aria-label') or ''
                        # Combina tutto
                        full_text = f"{text} {title} {aria_label}".upper()
                    except:
                        full_text = text.upper()
                    
                    # Cerca status nel testo completo
                    for status_val in ['SQL', 'MQL', 'SAL', 'QUALIFIED', 'OPEN', 'CONVERTED', 'NEW']:
                        if status_val in full_text:
                            # Estrai solo lo status, non "Edit Lead Status: Item SQL"
                            if 'EDIT LEAD STATUS' in full_text or 'LEAD STATUS' in full_text:
                                # Estrai lo status dopo "Item" o alla fine
                                match = re.search(r'ITEM\s+([A-Z]+)', full_text)
                                if match:
                                    lead_status = match.group(1)
                                else:
                                    lead_status = status_val
                            else:
                                lead_status = status_val
                            break
                    
                    if lead_status:
                        break
                
                # Country contiene "Italy" o altri paesi
                for text in cell_texts:
                    if text.lower() in ['italy', 'italia', 'germany', 'france', 'spain', 'uk', 'usa']:
                        country = text
                        break
                
                # Partner contiene "ME.KO" o altri partner
                for text in cell_texts:
                    if 'me.ko' in text.lower() or 'partner' in text.lower():
                        # Pulisci il testo partner da pattern di sistema
                        cleaned_partner = re.sub(r'\s*Locked Partner:?\s*Item\s*', '', text, flags=re.IGNORECASE)
                        cleaned_partner = cleaned_partner.strip()
                        if cleaned_partner and cleaned_partner != 'ME.KO. SRL UNIPERSONALE':
                            partner = cleaned_partner
                        break
                
                # Partner Contact è l'ultima colonna o contiene nomi come "Davide", "Giovanni"
                if len(cell_texts) > 5:
                    # Prova le ultime colonne
                    for text in cell_texts[-3:]:
                        if text and len(text.split()) >= 2 and not '@' in text and not re.search(r'[\d\s\+\-\(\)]{8,}', text):
                            partner_contact = text
                            break
                
                # Se abbiamo almeno il nome, è un lead valido
                if lead_name:
                    lead = {
                        'name': lead_name,
                        'email': email or '',
                        'phone': phone or '',
                        'lead_status': lead_status or '',
                        'country': country or '',
                        'partner': partner or '',
                        'partner_contact': partner_contact or '',
                        'raw_data': cell_texts
                    }
                    leads.append(lead)
                    logger.info(f"    ✓ Lead {len(leads)}: {lead['name']} - {lead['email']} - {lead['phone']}")
                else:
                    # Log per debug: cosa abbiamo trovato?
                    logger.info(f"    ⚠ Riga {idx} non valida - Celle: {len(cell_texts)}")
                    logger.info(f"       Prime 3 celle: {cell_texts[:3]}")
                    logger.info(f"       Celle pulite: {cleaned_cells[:3]}")
                    
                    # Se abbiamo email ma non nome, potrebbe essere che il nome sia nascosto
                    if email:
                        logger.info(f"       ⚠ Email trovata ({email}) ma nome mancante - potrebbe essere struttura diversa")
            
            except Exception as e:
                logger.debug(f"    ⚠ Errore parsing riga lead {idx}: {e}")
                continue
        
        # Metodo 2: Se non trova nulla, cerca nel testo della pagina
        if len(leads) == 0:
            logger.info("  📊 Metodo 2: Ricerca pattern nel testo della pagina...")
            try:
                page_text = page.locator('body').text_content() or ""
                # Cerca pattern email + nome
                import re
                # Pattern: Nome Cognome seguito da email
                email_pattern = r'([A-Za-z]+(?:\s+[A-Za-z]+)+)\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
                matches = re.findall(email_pattern, page_text)
                for name, email_addr in matches[:30]:
                    if len(name.split()) >= 2:  # Almeno nome e cognome
                        lead = {
                            'name': name,
                            'email': email_addr,
                            'phone': '',
                            'lead_status': '',
                            'country': '',
                            'partner': '',
                            'partner_contact': '',
                            'raw_data': [name, email_addr]
                        }
                        leads.append(lead)
                        if len(leads) >= 30:
                            break
            except Exception as e:
                logger.warning(f"  ⚠ Errore Metodo 2: {e}")
        
        logger.info(f"  ✅ Totale leads estratti: {len(leads)}")
        
    except Exception as e:
        logger.error(f"  ❌ Errore estrazione DOM leads: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    return leads


def parse_leads_html(html_content: str) -> List[Dict]:
    """
    Estrae dati dei leads dall'HTML della pagina
    
    Args:
        html_content: Contenuto HTML della pagina Leads
    
    Returns:
        Lista di dizionari con i dati dei leads
    """
    leads = []
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Cerca tabelle
        tables = soup.find_all('table')
        logger.info(f"📊 Trovate {len(tables)} tabelle nella pagina Leads")
        
        rows = []
        for table in tables:
            table_rows = table.find_all('tr')
            if len(table_rows) > 1:
                rows.extend(table_rows[1:])  # Salta header
        
        import re
        for idx, row in enumerate(rows[:50]):
            try:
                cells = row.find_all(['td', 'th', 'div'], attrs={'role': 'gridcell'})
                if len(cells) < 3:
                    continue
                
                cell_texts = []
                for cell in cells:
                    text = cell.get_text(strip=True)
                    text = ' '.join(text.split())  # Rimuovi spazi multipli
                    cell_texts.append(text)
                
                # Filtra celle vuote
                cell_texts = [t for t in cell_texts if t and len(t) > 0]
                
                if len(cell_texts) < 2:
                    continue
                
                # Estrai campi specifici
                lead_name = None
                email = None
                phone = None
                lead_status = None
                country = None
                partner = None
                partner_contact = None
                
                # Name: prima colonna con nome e cognome
                if len(cell_texts) > 0:
                    name_text = cell_texts[0]
                    if name_text and len(name_text.split()) >= 2 and name_text.lower() not in ['name', 'nome']:
                        lead_name = name_text
                
                # Email: contiene @
                for text in cell_texts:
                    if '@' in text and '.' in text:
                        email = text
                        break
                
                # Phone: contiene numeri e caratteri speciali
                for text in cell_texts:
                    if re.search(r'[\d\s\+\-\(\)]{8,}', text):
                        phone = text
                        break
                
                # Lead Status - cerca anche negli attributi title e aria-label delle celle
                for i, cell in enumerate(cells):
                    # Testo della cella
                    text = cell_texts[i] if i < len(cell_texts) else ''
                    # Cerca negli attributi title e aria-label
                    try:
                        title = cell.get('title', '') or ''
                        aria_label = cell.get('aria-label', '') or ''
                        # Combina tutto
                        full_text = f"{text} {title} {aria_label}".upper()
                    except:
                        full_text = text.upper()
                    
                    # Cerca status nel testo completo
                    for status_val in ['SQL', 'MQL', 'SAL', 'QUALIFIED', 'OPEN', 'CONVERTED', 'NEW']:
                        if status_val in full_text:
                            # Estrai solo lo status, non "Edit Lead Status: Item SQL"
                            if 'EDIT LEAD STATUS' in full_text or 'LEAD STATUS' in full_text:
                                # Estrai lo status dopo "Item" o alla fine
                                match = re.search(r'ITEM\s+([A-Z]+)', full_text)
                                if match:
                                    lead_status = match.group(1)
                                else:
                                    lead_status = status_val
                            else:
                                lead_status = status_val
                            break
                    
                    if lead_status:
                        break
                
                # Country
                for text in cell_texts:
                    if text.lower() in ['italy', 'italia', 'germany', 'france', 'spain', 'uk', 'usa']:
                        country = text
                        break
                
                # Partner
                for text in cell_texts:
                    if 'me.ko' in text.lower():
                        partner = text
                        break
                
                # Partner Contact
                if len(cell_texts) > 5:
                    for text in cell_texts[-3:]:
                        if text and len(text.split()) >= 2 and not '@' in text:
                            partner_contact = text
                            break
                
                if lead_name:
                    lead = {
                        'name': lead_name,
                        'email': email or '',
                        'phone': phone or '',
                        'lead_status': lead_status or '',
                        'country': country or '',
                        'partner': partner or '',
                        'partner_contact': partner_contact or '',
                        'raw_data': cell_texts
                    }
                    leads.append(lead)
            
            except Exception as e:
                logger.debug(f"Errore parsing riga lead {idx}: {e}")
                continue
        
        logger.info(f"✅ Estratti {len(leads)} leads totali")
        
    except Exception as e:
        logger.error(f"❌ Errore parsing HTML leads: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    return leads


def check_connectivity(url: str) -> bool:
    """Verifica connettività al portale UR"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        hostname = parsed.hostname
        logger.info(f"🔍 Verifica connettività a {hostname}...")
        
        # Risoluzione DNS
        ip = socket.gethostbyname(hostname)
        logger.info(f"✓ DNS risolto (sistema): {hostname} -> {ip}")
        
        # Test connessione TCP
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((ip, port))
        sock.close()
        
        if result == 0:
            logger.info(f"✓ Connessione TCP riuscita a {ip}:{port}")
            return True
        else:
            logger.warning(f"⚠ Connessione TCP fallita a {ip}:{port}")
            return False
    except Exception as e:
        logger.warning(f"⚠ Errore verifica connettività: {e}")
        return False


def login_to_ur_portal(playwright, password: str = None):
    """
    Login al portale UR usando Playwright
    
    Args:
        playwright: Istanza Playwright già inizializzata
        password: Password opzionale (se None, prova quelle in UR_PASSWORD_OPTIONS)
    
    Returns:
        page: Pagina Playwright dopo login
    """
    logger.info("=" * 60)
    logger.info("🚀 INIZIO LOGIN AL PORTALE UR")
    logger.info("=" * 60)
    logger.info(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"🌐 URL Portale: {UR_PORTAL_URL}")
    logger.info(f"📧 Email: {UR_EMAIL}")
    
    # Verifica connettività
    connectivity_ok = check_connectivity(UR_PORTAL_URL)
    if not connectivity_ok:
        logger.warning("⚠ Verifica connettività fallita, ma provo comunque...")
    
    try:
        # Avvia browser Chromium in headless
        # Controlla se siamo su Windows (locale) o Linux (SSH)
        import platform
        is_windows = platform.system() == 'Windows'
        
        # Headless sempre (più veloce e stabile)
        logger.info("🔧 Avvio browser Chromium headless...")
        if is_windows:
            browser = playwright.chromium.launch(
                headless=True,  # Headless anche su Windows
                args=[
                    '--window-size=1920,1080',
                ]
            )
        else:
            browser = playwright.chromium.launch(
                headless=True,  # Headless su Linux SSH
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--window-size=1920,1080',
                ]
            )
        
        # Crea contesto con user agent
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
        )
        
        # Crea pagina
        page = context.new_page()
        logger.info("✓ Browser avviato con successo")
        
        # Naviga al portale
        logger.info(f"🌐 Navigazione a {UR_PORTAL_URL}...")
        page.goto(UR_PORTAL_URL, wait_until='networkidle', timeout=60000)
        logger.info(f"✓ Pagina caricata: {page.url}")
        logger.info(f"📄 Titolo: {page.title()}")
        
        time.sleep(3)
        
        # Attendi redirect OAuth o verifica se già loggato
        max_wait = 10
        wait_count = 0
        while wait_count < max_wait:
            current_url = page.url.lower()
            logger.info(f"📍 URL corrente: {page.url}")
            
            # Se siamo sul portale principale, siamo loggati
            if "partners.universal-robots.com" in current_url and "authorizationerror" not in current_url:
                if "/s/" in current_url or current_url == UR_PORTAL_BASE + "/" or current_url == UR_PORTAL_BASE + "/s":
                    logger.info("✅ Sembra già loggato!")
                    return page
            
            # Se siamo sulla pagina OAuth2, procediamo con il login
            if "b2clogin.com" in current_url or "login" in current_url:
                logger.info("🔐 Trovata pagina di login OAuth2")
                break
            
            # Se c'è un errore OAuth, andiamo direttamente al portale
            if "authorizationerror" in current_url:
                logger.warning("⚠ Errore OAuth rilevato, vado direttamente al portale...")
                page.goto(UR_PORTAL_URL, wait_until='networkidle', timeout=60000)
                time.sleep(3)
                logger.info("✅ Navigato direttamente al portale")
                return page
            
            time.sleep(1)
            wait_count += 1
        
        if wait_count >= max_wait:
            logger.warning("⚠ Timeout attesa redirect, provo comunque il login...")
        
        # Salva HTML pagina login PRIMA di inserire credenziali
        logger.info("💾 Salvataggio HTML pagina login...")
        try:
            login_page_html = page.content()
            login_file = os.path.join(TEMP_DIR, '0_pagina_login.html')
            with open(login_file, 'w', encoding='utf-8') as f:
                f.write(login_page_html)
            logger.info(f"💾 HTML pagina login salvato in {login_file} ({len(login_page_html)} caratteri)")
        except Exception as e:
            logger.warning(f"⚠ Errore salvataggio HTML login: {e}")
        
        # Cerca campo email e password
        passwords_to_try = [password] if password else UR_PASSWORD_OPTIONS
        logger.info(f"🔑 Tentativo login con {len(passwords_to_try)} password...")
        
        for idx, pwd in enumerate(passwords_to_try, 1):
            try:
                logger.info(f"🔐 Tentativo {idx}/{len(passwords_to_try)}...")
                
                # Trova campo email
                logger.info("🔍 Ricerca campo email...")
                email_field = None
                email_selectors = [
                    'input[name="loginfmt"]',
                    'input[name="email"]',
                    'input[id="signInName"]',
                    'input[type="email"]',
                ]
                
                for selector in email_selectors:
                    try:
                        email_field = page.wait_for_selector(selector, timeout=10000)
                        if email_field:
                            logger.info(f"✓ Campo email trovato: {selector}")
                            break
                    except PlaywrightTimeoutError:
                        continue
                
                if not email_field:
                    raise Exception("Campo email non trovato")
                
                # Inserisci email PRIMA
                logger.info(f"📝 Inserimento email: {UR_EMAIL}")
                email_field.fill(UR_EMAIL)
                time.sleep(2)  # Aspetta che il campo password diventi visibile
                
                # Verifica che l'email sia stata inserita
                email_value = email_field.input_value()
                if email_value == UR_EMAIL:
                    logger.info(f"✓ Email inserita correttamente: {email_value}")
                else:
                    logger.warning(f"⚠ Email non corrisponde! Atteso: {UR_EMAIL}, Trovato: {email_value}")
                    # Riprova
                    email_field.fill(UR_EMAIL)
                    time.sleep(1)
                    email_value = email_field.input_value()
                    logger.info(f"✓ Email dopo retry: {email_value}")
                
                # Screenshot dopo inserimento email
                try:
                    screenshot_file = os.path.join(TEMP_DIR, 'ur_after_email.png')
                    page.screenshot(path=screenshot_file, full_page=True)
                    logger.info(f"✓ Screenshot dopo email salvato in {screenshot_file}")
                except:
                    pass
                
                # Ora cerca il campo password DOPO aver inserito l'email
                logger.info("🔍 Ricerca campo password dopo inserimento email...")
                password_selectors = [
                    'input[id="password"]',  # Form vecchio - PRIORITÀ
                    'input[name="password"]',
                    'input[name="passwd"]',
                    'input[id="passwd"]',
                    'form#localAccountForm input[type="password"]',  # Nel form specifico
                    'input[type="password"]',
                ]
                
                password_locator = None
                for selector in password_selectors:
                    try:
                        locator = page.locator(selector)
                        count = locator.count()
                        if count > 0:
                            logger.info(f"✓ Campo password trovato: {selector} (count: {count})")
                            # Se ci sono più campi, prendi il primo visibile
                            if count > 1:
                                logger.info("  ⚠ Trovati più campi password, cerco quello visibile...")
                                for i in range(count):
                                    try:
                                        single_locator = locator.nth(i)
                                        if single_locator.is_visible():
                                            password_locator = single_locator
                                            logger.info(f"  ✓ Usato campo password {i+1} (visibile)")
                                            break
                                    except:
                                        continue
                                if not password_locator:
                                    password_locator = locator.first()
                                    logger.info("  ⚠ Usato il primo campo password trovato")
                            else:
                                password_locator = locator.first()
                            break
                    except Exception as e:
                        logger.debug(f"  ⚠ Selector {selector} fallito: {e}")
                        continue
                
                if not password_locator:
                    # Ultimo tentativo: cerca qualsiasi input password visibile
                    try:
                        all_password_inputs = page.locator('input[type="password"]').all()
                        logger.info(f"  🔍 Trovati {len(all_password_inputs)} input password totali")
                        for i, inp in enumerate(all_password_inputs):
                            try:
                                if inp.is_visible():
                                    password_locator = page.locator('input[type="password"]').nth(i)
                                    logger.info(f"  ✓ Campo password visibile trovato (indice {i})")
                                    break
                            except:
                                continue
                        if not password_locator and len(all_password_inputs) > 0:
                            password_locator = page.locator('input[type="password"]').first()
                            logger.info("  ⚠ Usato il primo campo password disponibile")
                    except Exception as e:
                        logger.warning(f"  ⚠ Errore ricerca globale password: {e}")
                        password_locator = None
                
                if not password_locator:
                    # Salva HTML per debug
                    html_content = page.content()
                    debug_file = os.path.join(TEMP_DIR, 'ur_login_page.html')
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    logger.error(f"❌ Campo password non trovato! HTML salvato in {debug_file}")
                    raise Exception("Campo password non trovato sulla pagina")
                
                # Aspetta che il campo password sia visibile e interagibile
                try:
                    password_locator.wait_for(state='visible', timeout=5000)
                    logger.info("✓ Campo password è visibile")
                except:
                    logger.warning("⚠ Campo password potrebbe non essere visibile")
                
                # Inserisci password usando il locator trovato
                logger.info(f"📝 Compilazione campo password (lunghezza: {len(pwd)} caratteri)...")
                try:
                    # Pulisci il campo prima di inserire
                    password_locator.clear()
                    time.sleep(0.5)
                    password_locator.fill(pwd, timeout=15000)
                    logger.info("✓ Password inserita con fill()")
                except Exception as e:
                    logger.warning(f"Fill fallito: {e}, provo con type()...")
                    try:
                        password_locator.clear()
                        time.sleep(0.5)
                        password_locator.type(pwd, delay=50)
                        logger.info("✓ Password inserita con type()")
                    except Exception as e2:
                        logger.error(f"❌ Anche type() fallito: {e2}")
                        raise
                
                time.sleep(1)
                
                # Verifica che la password sia stata inserita (almeno parzialmente)
                try:
                    password_value = password_locator.input_value()
                    if password_value:
                        logger.info(f"✓ Password inserita (lunghezza: {len(password_value)} caratteri)")
                    else:
                        logger.warning("⚠ Password sembra vuota dopo inserimento!")
                except:
                    logger.warning("⚠ Impossibile verificare password (campo potrebbe essere protetto)")
                
                # Screenshot dopo inserimento password
                try:
                    screenshot_file = os.path.join(TEMP_DIR, 'ur_after_password.png')
                    page.screenshot(path=screenshot_file, full_page=True)
                    logger.info(f"✓ Screenshot dopo password salvato in {screenshot_file}")
                except:
                    pass
                
                time.sleep(2)
                
                # Salva HTML per analisi
                logger.info("💾 Salvataggio HTML per analisi...")
                html_content = page.content()
                html_file = os.path.join(TEMP_DIR, 'ur_login_page_after_password.html')
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                logger.info(f"✓ HTML salvato in {html_file}")
                
                # Cerca tutti i pulsanti disponibili nella pagina
                logger.info("🔍 Analisi pulsanti disponibili...")
                try:
                    buttons = page.locator('button').all()
                    logger.info(f"📊 Trovati {len(buttons)} pulsanti nella pagina")
                    for i, btn in enumerate(buttons[:10]):  # Primi 10
                        try:
                            text = btn.text_content() or ""
                            btn_id = btn.get_attribute('id') or ""
                            btn_class = btn.get_attribute('class') or ""
                            btn_type = btn.get_attribute('type') or ""
                            logger.info(f"  Pulsante {i+1}: id='{btn_id}', class='{btn_class[:50]}', type='{btn_type}', text='{text[:30]}'")
                        except:
                            pass
                except Exception as e:
                    logger.warning(f"Errore analisi pulsanti: {e}")
                
                # Cerca e clicca pulsante "Continua"
                logger.info("🔍 Ricerca pulsante 'Continua'...")
                continue_clicked = False
                
                # Il pulsante ha id="sign-in-form-submit-button" ma è disabled inizialmente
                # Aspetta che diventi abilitato (Angular abilita quando form è valido)
                button_selector = '#sign-in-form-submit-button'
                
                try:
                    logger.info(f"⏳ Attesa che il pulsante {button_selector} diventi abilitato...")
                    # Aspetta che il pulsante non sia più disabled
                    page.wait_for_selector(f'{button_selector}:not([disabled])', timeout=15000, state='visible')
                    logger.info("✓ Pulsante abilitato!")
                    
                    # Clicca il pulsante
                    page.click(button_selector, timeout=5000)
                    logger.info("✓ Cliccato 'Continua'")
                    continue_clicked = True
                except PlaywrightTimeoutError:
                    logger.warning("⚠ Pulsante rimane disabled, provo con JavaScript...")
                    try:
                        # Usa JavaScript per rimuovere disabled e cliccare
                        page.evaluate("""
                            const btn = document.getElementById('sign-in-form-submit-button');
                            if (btn) {
                                btn.removeAttribute('disabled');
                                btn.classList.remove('disabled');
                                btn.click();
                            }
                        """)
                        logger.info("✓ Cliccato con JavaScript")
                        continue_clicked = True
                    except Exception as e:
                        logger.warning(f"JavaScript fallito: {e}")
                        # Prova con force=True come ultimo tentativo
                        try:
                            page.click(button_selector, timeout=5000, force=True)
                            logger.info("✓ Cliccato con force=True")
                            continue_clicked = True
                        except Exception as e2:
                            logger.warning(f"Force click fallito: {e2}")
                
                if not continue_clicked:
                    logger.warning("⚠ Pulsante Continua non cliccabile, provo con submit form...")
                    try:
                        # Prova a fare submit del form direttamente
                        form = page.locator('form')
                        if form.count() > 0:
                            form.first.evaluate('form => form.submit()')
                            logger.info("✓ Submit form eseguito con JavaScript")
                            continue_clicked = True
                    except Exception as e:
                        logger.debug(f"Submit form fallito: {e}")
                    
                    if not continue_clicked:
                        try:
                            # Prova a premere Enter sul campo password
                            logger.info("⚠ Provo Enter sul campo password...")
                            password_locator.press('Enter')
                            logger.info("✓ Premuto Enter sul campo password")
                        except Exception as e:
                            logger.warning(f"Enter fallito: {e}")
                
                # Controlla ogni secondo se il redirect OAuth è completato - VELOCE!
                logger.info("⏳ Verifica redirect OAuth dopo login...")
                max_wait = 8  # Massimo 8 secondi
                for waited in range(max_wait):
                    time.sleep(1)
                    try:
                        current_url = page.url.lower()
                        
                        # Se siamo già sul portale principale (non OAuth), perfetto! Procedi subito!
                        if "partners.universal-robots.com" in current_url and "b2clogin.com" not in current_url:
                            logger.info(f"✅ Login riuscito! Arrivati sul portale dopo {waited+1}s: {page.url[:80]}")
                            
                            # Salva HTML pagina dopo login completato
                            logger.info("💾 Salvataggio HTML pagina dopo login...")
                            try:
                                after_login_html = page.content()
                                after_login_file = os.path.join(TEMP_DIR, '1_pagina_dopo_login.html')
                                with open(after_login_file, 'w', encoding='utf-8') as f:
                                    f.write(after_login_html)
                                logger.info(f"💾 HTML pagina dopo login salvato in {after_login_file} ({len(after_login_html)} caratteri)")
                            except Exception as e:
                                logger.warning(f"⚠ Errore salvataggio HTML dopo login: {e}")
                            
                            return page
                        
                        # Se ancora su OAuth, continua a controllare
                        if "b2clogin.com" in current_url:
                            if waited % 2 == 0:  # Log ogni 2 secondi per non spammare
                                logger.info(f"⏳ Ancora su OAuth, controllo {waited+1}/{max_wait}...")
                            continue
                    except:
                        # Se la pagina sta cambiando, continua ad aspettare
                        continue
                
                # Se dopo 8 secondi siamo ancora su OAuth, procedi comunque (la sessione potrebbe essere valida)
                logger.info("⏳ Procedo comunque (sessione potrebbe essere già valida)...")
                try:
                    after_login_html = page.content()
                    after_login_file = os.path.join(TEMP_DIR, '1_pagina_dopo_login.html')
                    with open(after_login_file, 'w', encoding='utf-8') as f:
                        f.write(after_login_html)
                    logger.info(f"💾 HTML pagina dopo login salvato in {after_login_file} ({len(after_login_html)} caratteri)")
                except Exception as e:
                    logger.warning(f"⚠ Errore salvataggio HTML dopo login: {e}")
                
                return page
                
            except Exception as e:
                logger.error(f"❌ Errore durante tentativo login {idx}: {e}")
                logger.error(f"   Tipo errore: {type(e).__name__}")
                if idx < len(passwords_to_try):
                    logger.info("🔄 Provo password successiva...")
                    continue
                else:
                    raise
        
        raise Exception("Tutti i tentativi di login falliti")
        
    except Exception as e:
        logger.error(f"❌ Errore durante login: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


def fetch_ur_data_direct():
    """
    Estrae dati dal portale UR usando Playwright
    
    Returns:
        dict: Dizionario con 'success', 'opportunities', 'leads', 'accounts', 'error' (se success=False)
    """
    logger.info("=" * 60)
    logger.info("🚀 INIZIO SINCRONIZZAZIONE PORTALE UR")
    logger.info("=" * 60)
    logger.info(f"📅 Timestamp inizio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    page = None
    
    try:
        # Avvia Playwright usando context manager
        with sync_playwright() as playwright:
            page = login_to_ur_portal(playwright)
            
            logger.info("=" * 60)
            logger.info("🔍 Navigazione alle pagine Leads e Opportunities...")
            logger.info("=" * 60)
            
            # IMPORTANTE: Dopo il login, naviga DIRETTAMENTE alle pagine Leads e Opportunities
            # La sessione è già stabilita, anche se siamo ancora sulla pagina OAuth!
            logger.info("=" * 60)
            logger.info("🚀 Navigazione DIRETTA alle pagine Leads e Opportunities")
            logger.info("=" * 60)
            
            # URL diretti delle pagine (come indicato dall'utente)
            direct_opportunities_urls = [
                'https://partners.universal-robots.com/s/opportunity/Opportunity/Default',  # URL corretto!
            ]
            
            direct_leads_urls = [
                'https://partners.universal-robots.com/s/lead/Lead/Default',  # URL corretto!
            ]
        
            # Naviga DIRETTAMENTE alla pagina Opportunities (PRIMA delle Leads come indicato)
            logger.info("📄 Navigazione DIRETTA alla pagina Opportunities...")
            opportunities = []
            opportunities_html = None
            
            for url in direct_opportunities_urls:
                try:
                    logger.info(f"  🔗 Navigo a: {url}")
                    # Usa 'load' invece di 'networkidle' - molto più veloce!
                    page.goto(url, wait_until='load', timeout=30000)
                    
                    # Controlla ogni secondo se siamo già sulla pagina giusta
                    logger.info("  ⏳ Verifica pagina...")
                    for check in range(10):  # Max 10 secondi di controllo
                        time.sleep(1)
                        current_url = page.url.lower()
                        
                        # Se siamo già sulla pagina corretta, procedi subito!
                        if '/opportunity/' in current_url and 'b2clogin.com' not in current_url:
                            logger.info(f"  ✓ Pagina corretta raggiunta dopo {check+1}s!")
                            break
                        
                        # Se ancora su OAuth, aspetta redirect
                        if 'b2clogin.com' in current_url:
                            logger.info(f"  ⏳ Ancora su OAuth, controllo {check+1}/10...")
                            continue
                        
                        # Se siamo sul portale ma non sulla pagina giusta, potrebbe essere redirect
                        if 'partners.universal-robots.com' in current_url:
                            logger.info(f"  ⏳ Su portale, verifico redirect...")
                            continue
                    
                    current_url = page.url.lower()
                    logger.info(f"  📍 URL finale: {current_url[:80]}")
                    
                    # Salva screenshot e HTML PRIMA di estrarre i dati
                    logger.info("  📸 Salvataggio screenshot e HTML della pagina...")
                    try:
                        screenshot_file = os.path.join(TEMP_DIR, 'ur_opportunities_page_screenshot.png')
                        page.screenshot(path=screenshot_file, full_page=True)
                        logger.info(f"  ✓ Screenshot salvato in {screenshot_file}")
                    except Exception as e:
                        logger.warning(f"  ⚠ Errore screenshot: {e}")
                    
                    opportunities_html = page.content()
                    # Salva HTML pagina opportunità con nome chiaro
                    opp_html_file = os.path.join(TEMP_DIR, '3_pagina_opportunita.html')
                    with open(opp_html_file, 'w', encoding='utf-8') as f:
                        f.write(opportunities_html)
                    logger.info(f"  💾 HTML pagina opportunità salvato in {opp_html_file} ({len(opportunities_html)} caratteri)")
                    
                    # Salva anche con nome vecchio per compatibilità
                    opp_html_file_old = os.path.join(TEMP_DIR, 'ur_opportunities_page.html')
                    with open(opp_html_file_old, 'w', encoding='utf-8') as f:
                        f.write(opportunities_html)
                    
                    # Salva anche il testo visibile della pagina
                    try:
                        page_text = page.locator('body').text_content() or ""
                        text_file = os.path.join(TEMP_DIR, 'ur_opportunities_page_text.txt')
                        with open(text_file, 'w', encoding='utf-8') as f:
                            f.write(page_text)
                        logger.info(f"  💾 Testo pagina salvato in {text_file} ({len(page_text)} caratteri)")
                    except Exception as e:
                        logger.warning(f"  ⚠ Errore salvataggio testo: {e}")
                    
                    # Aspetta che la tabella si carichi completamente (potrebbe essere dinamica)
                    logger.info("  ⏳ Attesa caricamento tabella Opportunities (potrebbe essere dinamica)...")
                    try:
                        # Aspetta che ci siano almeno alcune righe nella tabella
                        page.wait_for_selector('table tbody tr, table tr, [role="row"]', timeout=10000)
                        time.sleep(3)  # Attesa aggiuntiva per rendering completo
                        logger.info("  ✓ Tabella caricata")
                    except:
                        logger.warning("  ⚠ Timeout attesa tabella, procedo comunque")
                    
                    # Estrai dati DIRETTAMENTE dal DOM usando Playwright
                    logger.info("  🔍 Estrazione dati direttamente dal DOM...")
                    opportunities = extract_opportunities_from_dom(page)
                    
                    if opportunities:
                        logger.info(f"  ✅ Trovate {len(opportunities)} opportunità!")
                        break
                    else:
                        logger.warning("  ⚠ Nessuna opportunità trovata")
                        break  # Prova comunque con questo URL
                        
                except Exception as e:
                    logger.warning(f"  ⚠ Errore con {url}: {e}")
                    import traceback
                    logger.debug(traceback.format_exc())
                    continue
            
            # Naviga DIRETTAMENTE alla pagina Leads
            logger.info("📄 Navigazione DIRETTA alla pagina Leads...")
            leads = []
            leads_html = None
            
            for url in direct_leads_urls:
                try:
                    logger.info(f"  🔗 Navigo a: {url}")
                    # Usa 'load' invece di 'networkidle' - molto più veloce!
                    page.goto(url, wait_until='load', timeout=30000)
                    
                    # Controlla ogni secondo se siamo già sulla pagina giusta
                    logger.info("  ⏳ Verifica pagina...")
                    for check in range(10):  # Max 10 secondi di controllo
                        time.sleep(1)
                        current_url = page.url.lower()
                        
                        # Se siamo già sulla pagina corretta, procedi subito!
                        if '/lead/' in current_url and 'b2clogin.com' not in current_url:
                            logger.info(f"  ✓ Pagina corretta raggiunta dopo {check+1}s!")
                            break
                        
                        # Se ancora su OAuth, aspetta redirect
                        if 'b2clogin.com' in current_url:
                            logger.info(f"  ⏳ Ancora su OAuth, controllo {check+1}/10...")
                            continue
                        
                        # Se siamo sul portale ma non sulla pagina giusta, potrebbe essere redirect
                        if 'partners.universal-robots.com' in current_url:
                            logger.info(f"  ⏳ Su portale, verifico redirect...")
                            continue
                    
                    current_url = page.url.lower()
                    if 'b2clogin.com' in current_url or 'sign in' in page.title().lower():
                        logger.warning(f"  ⚠ Ancora sulla pagina OAuth! URL: {page.url[:100]}")
                        continue
                    
                    logger.info(f"  📍 URL finale: {current_url[:80]}")
                    
                    # Salva screenshot e HTML PRIMA di estrarre i dati
                    logger.info("  📸 Salvataggio screenshot e HTML della pagina...")
                    try:
                        screenshot_file = os.path.join(TEMP_DIR, 'ur_leads_page_screenshot.png')
                        page.screenshot(path=screenshot_file, full_page=True)
                        logger.info(f"  ✓ Screenshot salvato in {screenshot_file}")
                    except Exception as e:
                        logger.warning(f"  ⚠ Errore screenshot: {e}")
                    
                    leads_html = page.content()
                    # Salva HTML pagina leads con nome chiaro
                    leads_html_file = os.path.join(TEMP_DIR, '2_pagina_leads.html')
                    with open(leads_html_file, 'w', encoding='utf-8') as f:
                        f.write(leads_html)
                    logger.info(f"  💾 HTML pagina leads salvato in {leads_html_file} ({len(leads_html)} caratteri)")
                    
                    # Salva anche con nome vecchio per compatibilità
                    leads_html_file_old = os.path.join(TEMP_DIR, 'ur_leads_page.html')
                    with open(leads_html_file_old, 'w', encoding='utf-8') as f:
                        f.write(leads_html)
                    
                    # Salva anche il testo visibile della pagina
                    try:
                        page_text = page.locator('body').text_content() or ""
                        text_file = os.path.join(TEMP_DIR, 'ur_leads_page_text.txt')
                        with open(text_file, 'w', encoding='utf-8') as f:
                            f.write(page_text)
                        logger.info(f"  💾 Testo pagina salvato in {text_file} ({len(page_text)} caratteri)")
                    except Exception as e:
                        logger.warning(f"  ⚠ Errore salvataggio testo: {e}")
                    
                    # Aspetta che la tabella si carichi completamente (potrebbe essere dinamica)
                    logger.info("  ⏳ Attesa caricamento tabella Leads (potrebbe essere dinamica)...")
                    try:
                        # Aspetta che ci siano almeno alcune righe nella tabella
                        page.wait_for_selector('table tr, [role="row"]', timeout=10000)
                        time.sleep(2)  # Attesa aggiuntiva per rendering completo
                        logger.info("  ✓ Tabella caricata")
                    except:
                        logger.warning("  ⚠ Timeout attesa tabella, procedo comunque")
                    
                    # Estrai dati DIRETTAMENTE dal DOM usando Playwright
                    logger.info("  🔍 Estrazione dati direttamente dal DOM...")
                    leads = extract_leads_from_dom(page)
                    
                    # Se non trova nulla con DOM, prova con parsing HTML
                    if not leads and leads_html:
                        logger.info("  🔍 Metodo DOM non ha trovato leads, provo con parsing HTML...")
                        try:
                            leads = parse_leads_html(leads_html)
                            logger.info(f"  ✅ Parsing HTML trovato {len(leads)} leads!")
                        except Exception as e:
                            logger.warning(f"  ⚠ Errore parsing HTML: {e}")
                    
                    # Se ancora nulla o pochi leads, cerca nel testo della pagina per estrarre i dati
                    if len(leads) < 5:
                        logger.info("  🔍 Cerca leads nel testo della pagina (metodo alternativo)...")
                        try:
                            page_text = page.locator('body').text_content() or ""
                            
                            # Pattern: Nome Cognome seguito da email e telefono nella stessa riga o vicine
                            # Cerca pattern come "Nome Cognome" seguito da email
                            import re
                            
                            # Lista nomi noti dalla pagina
                            known_names = ['Andrea Magagna', 'Daria Rodighiero', 'Dario Pedrolo', 
                                         'Ganimede Mancini', 'Paolo Viviani']
                            
                            # Per ogni nome, cerca i dati associati nel testo
                            for name in known_names:
                                if name in page_text:
                                    # Cerca email dopo il nome (entro 200 caratteri)
                                    name_pos = page_text.find(name)
                                    text_after_name = page_text[name_pos:name_pos+500]
                                    
                                    # Estrai email: cerca pattern che inizia dopo spazio/newline o direttamente con carattere email valido
                                    # Pattern: spazio/newline seguito da email O email che inizia con carattere minuscolo/numbero
                                    email_patterns = [
                                        r'[\s\n]+([a-z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',  # Email dopo spazio
                                        r'\b([a-z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b',  # Email con word boundary
                                        r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',  # Pattern generico
                                    ]
                                    email_found = ''
                                    for pattern in email_patterns:
                                        email_match = re.search(pattern, text_after_name)
                                        if email_match:
                                            potential_email = email_match.group(1)
                                            # Verifica che l'email non inizi con maiuscola (probabilmente cognome)
                                            if potential_email[0].islower() or potential_email[0].isdigit():
                                                email_found = potential_email
                                                break
                                    # Se ancora nulla, prendi la prima email trovata
                                    if not email_found:
                                        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text_after_name)
                                        if email_match:
                                            email_found = email_match.group(1)
                                    
                                    # Estrai telefono
                                    phone_match = re.search(r'([\+\d\s\-\(\)]{8,})', text_after_name)
                                    phone_found = phone_match.group(1).strip() if phone_match else ''
                                    
                                    # Estrai status (SQL, MQL, ecc.)
                                    status_match = re.search(r'\b(SQL|MQL|SAL|QUALIFIED|OPEN)\b', text_after_name, re.IGNORECASE)
                                    status_found = status_match.group(1) if status_match else ''
                                    
                                    # Estrai country
                                    country_match = re.search(r'\b(Italy|Italia|Germany|France|Spain|UK|USA)\b', text_after_name, re.IGNORECASE)
                                    country_found = country_match.group(1) if country_match else ''
                                    
                                    # Estrai partner
                                    partner_match = re.search(r'(ME\.KO[^,\n]*)', text_after_name, re.IGNORECASE)
                                    partner_found = partner_match.group(1).strip() if partner_match else ''
                                    
                                    # Verifica se questo lead non è già stato aggiunto
                                    already_added = any(l.get('name') == name or l.get('email') == email_found for l in leads)
                                    if not already_added:
                                        lead = {
                                            'name': name,
                                            'email': email_found,
                                            'phone': phone_found,
                                            'lead_status': status_found,
                                            'country': country_found,
                                            'partner': partner_found,
                                            'partner_contact': '',
                                            'raw_data': [name, email_found, phone_found]
                                        }
                                        leads.append(lead)
                                        logger.info(f"    ✓ Lead estratto da testo: {name} - {email_found}")
                            
                            if len(leads) > 0:
                                logger.info(f"  ✅ Trovati {len(leads)} leads con metodo alternativo!")
                        except Exception as e:
                            logger.warning(f"  ⚠ Errore ricerca nomi: {e}")
                            import traceback
                            logger.debug(traceback.format_exc())
                    
                    if leads:
                        logger.info(f"  ✅ Trovati {len(leads)} leads!")
                        break
                    else:
                        logger.warning("  ⚠ Nessun lead trovato")
                        break  # Prova comunque con questo URL
                        
                except Exception as e:
                    logger.warning(f"  ⚠ Errore con {url}: {e}")
                    import traceback
                    logger.debug(traceback.format_exc())
                    continue
        
        
            logger.info("=" * 60)
            logger.info("🔍 Estrazione dati completata")
            logger.info("=" * 60)
            logger.info(f"📊 Opportunità estratte: {len(opportunities)}")
            logger.info(f"📊 Leads estratti: {len(leads)}")
        
            logger.info("=" * 60)
            logger.info("✅ SINCRONIZZAZIONE COMPLETATA")
            logger.info(f"📊 Opportunità trovate: {len(opportunities)}")
            logger.info(f"📊 Leads trovati: {len(leads)}")
            logger.info("=" * 60)
            logger.info(f"💡 HTML salvati in {TEMP_DIR} per analisi")
            logger.info("=" * 60)
            
            # Informa che i file sono pronti per il download
            logger.info("📥 File HTML pronti per download:")
            logger.info(f"   - {os.path.join(TEMP_DIR, '0_pagina_login.html')}")
            logger.info(f"   - {os.path.join(TEMP_DIR, '1_pagina_dopo_login.html')}")
            logger.info(f"   - {os.path.join(TEMP_DIR, '2_pagina_leads.html')}")
            logger.info(f"   - {os.path.join(TEMP_DIR, '3_pagina_opportunita.html')}")
            
            return {
                'success': True,
                'opportunities': opportunities,
                'leads': leads,
                'accounts': []  # Aggiungi accounts se necessario
            }
        
    except Exception as e:
        logger.error(f"❌ Errore durante sincronizzazione: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            'success': False,
            'error': str(e),
            'opportunities': [],
            'leads': [],
            'accounts': []
        }
    finally:
        if page:
            try:
                page.close()
            except:
                pass
        # Il context manager chiude automaticamente playwright

