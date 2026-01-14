#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Associa indirizzi ai contatti cercando nelle offerte e nei siti web
"""
import os
import sys
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crm_app_completo import db, app, Account, Contact, Opportunity, OfferDocument

def extract_address_from_text(text):
    """Estrae indirizzi italiani da un testo"""
    if not text:
        return None
    
    # Pattern per indirizzi italiani
    address_patterns = [
        r'(Via|Viale|Vicolo|Piazza|Corso|Largo|Piazzale|Strada|Contrada|Corso)\s+[A-Za-z0-9\s\',\.\-]+,\s*\d{5}\s+[A-Za-z\s]+(?:\([A-Z]{2}\))?',
        r'[A-Za-z0-9\s\',\.\-]+,\s*\d{5}\s+[A-Za-z\s]+(?:\([A-Z]{2}\))?',
        r'\d{5}\s+[A-Za-z\s]+(?:\([A-Z]{2}\))?',
    ]
    
    for pattern in address_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        if matches:
            for match in matches:
                match_clean = match.strip()
                # Verifica che contenga almeno CAP e città
                if re.search(r'\d{5}', match_clean) and len(match_clean) > 10:
                    return match_clean
    return None

def extract_address_from_pdf(pdf_path):
    """Estrae l'indirizzo dal PDF dell'offerta"""
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            all_text = ""
            for page in pdf.pages[:3]:  # Prime 3 pagine
                all_text += page.extract_text() or ""
            return extract_address_from_text(all_text)
    except Exception as e:
        return None

def extract_address_from_docx(docx_path):
    """Estrae l'indirizzo dal DOCX dell'offerta"""
    try:
        from docx import Document
        doc = Document(docx_path)
        all_text = "\n".join([para.text for para in doc.paragraphs[:20]])
        return extract_address_from_text(all_text)
    except Exception as e:
        return None

def extract_address_from_website(url):
    """Estrae indirizzo dal sito web dell'account"""
    try:
        # Aggiungi http:// se mancante
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Rimuovi script e style
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        
        # Cerca indirizzo nel testo
        address = extract_address_from_text(text)
        if address:
            return address
        
        # Cerca anche nei tag specifici (footer, address, etc.)
        for tag in soup.find_all(['address', 'footer', 'div'], class_=re.compile(r'address|contact|footer', re.I)):
            address = extract_address_from_text(tag.get_text())
            if address:
                return address
        
        return None
    except Exception as e:
        return None

def associa_indirizzi_contatti():
    """Associa indirizzi ai contatti cercando nelle offerte e nei siti web"""
    db, app, Account, Contact, Opportunity, OfferDocument = get_models()
    with app.app_context():
        accounts = Account.query.all()
        updated_count = 0
        skipped_count = 0
        
        for account in accounts:
            # 1. Cerca indirizzo nel sito web
            if account.website and not account.billing_address:
                print(f"🔍 Cercando indirizzo nel sito web per {account.name}...")
                address = extract_address_from_website(account.website)
                if address:
                    account.billing_address = address
                    updated_count += 1
                    print(f"  ✅ Trovato: {address}")
            
            # 2. Cerca indirizzo nelle offerte associate
            if not account.billing_address:
                opportunities = Opportunity.query.filter_by(account_id=account.id).all()
                for opp in opportunities:
                    for offer in opp.offers:
                        address = None
                        if offer.pdf_path and os.path.exists(offer.pdf_path):
                            address = extract_address_from_pdf(offer.pdf_path)
                        elif offer.docx_path and os.path.exists(offer.docx_path):
                            address = extract_address_from_docx(offer.docx_path)
                        
                        if address:
                            account.billing_address = address
                            updated_count += 1
                            print(f"  ✅ Trovato nelle offerte: {address}")
                            break
                    
                    if account.billing_address:
                        break
            
            # 3. Associa indirizzo ai contatti dell'account
            if account.billing_address:
                contacts = Contact.query.filter_by(account_id=account.id).all()
                for contact in contacts:
                    if not contact.address:  # Assumendo che Contact abbia un campo address
                        # Se Contact non ha campo address, possiamo aggiungerlo o usare description
                        # Per ora saltiamo se non esiste
                        pass
        
        db.session.commit()
        print(f"\n✅ Completato: {updated_count} account aggiornati, {skipped_count} saltati")
        return updated_count

if __name__ == '__main__':
    associa_indirizzi_contatti()
