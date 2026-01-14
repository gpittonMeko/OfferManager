#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper per aggiungere firma email a tutti i messaggi
"""
import re


def get_email_signature_html():
    """Restituisce la firma email HTML completa"""
    return """
    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
        <p style="margin: 0 0 8px 0; color: #1e293b; font-size: 14px; line-height: 1.8;">
            <strong>Dott. Ing. Giovanni Pitton</strong><br>
            📱 Mobile: +39 389 5333407<br>
            ☎️ Office: +39 0421 336857<br>
            <br>
            <strong>ME.KO. SRL UNIPERSONALE</strong><br>
            Via Alfred Nobel, 4<br>
            30020 Noventa di Piave (VE) – Italy<br>
            P.IVA / C.F. 04393900271 - REA: VE409498
        </p>
        <p style="margin: 15px 0 0 0; color: #64748b; font-size: 11px; line-height: 1.6; text-align: justify;">
            <strong>Disclaimer GDPR:</strong> Questo messaggio e i suoi eventuali allegati sono destinati esclusivamente al destinatario indicato e possono contenere informazioni riservate e/o confidenziali. Qualora non foste il destinatario, siete pregati di non leggere, copiare, utilizzare o diffondere il contenuto a terzi. Vi invitiamo a contattare immediatamente il mittente e a cancellare il messaggio e i relativi allegati dal vostro sistema. Qualsiasi utilizzo non autorizzato del contenuto di questa e-mail è strettamente vietato e potrebbe costituire violazione di legge ai sensi del Regolamento Generale sulla Protezione dei Dati (GDPR - Regolamento UE 2016/679) e della normativa vigente applicabile.
        </p>
    </div>
    """


def get_email_signature_text():
    """Restituisce la firma email in formato testo"""
    return """
---------------------------------------------------------------------------------
Dott. Ing. Giovanni Pitton
📱 Mobile: +39 389 5333407
☎️ Office: +39 0421 336857

ME.KO. SRL UNIPERSONALE
Via Alfred Nobel, 4
30020 Noventa di Piave (VE) – Italy
P.IVA / C.F. 04393900271 - REA: VE409498

Disclaimer GDPR: Questo messaggio e i suoi eventuali allegati sono destinati esclusivamente al destinatario indicato e possono contenere informazioni riservate e/o confidenziali. Qualora non foste il destinatario, siete pregati di non leggere, copiare, utilizzare o diffondere il contenuto a terzi. Vi invitiamo a contattare immediatamente il mittente e a cancellare il messaggio e i relativi allegati dal vostro sistema. Qualsiasi utilizzo non autorizzato del contenuto di questa e-mail è strettamente vietato e potrebbe costituire violazione di legge ai sensi del Regolamento Generale sulla Protezione dei Dati (GDPR - Regolamento UE 2016/679) e della normativa vigente applicabile.
"""


def add_signature_to_html(html_content: str) -> str:
    """
    Aggiunge la firma email all'HTML se non è già presente
    
    Args:
        html_content: Contenuto HTML dell'email
        
    Returns:
        HTML con firma aggiunta
    """
    signature = get_email_signature_html()
    
    # Controlla se la firma è già presente (cerca indicatori chiave)
    if "Dott. Ing. Giovanni Pitton" in html_content and "ME.KO. SRL UNIPERSONALE" in html_content:
        return html_content  # Firma già presente
    
    # Rimuovi eventuali tag di chiusura body/html per inserire la firma prima
    # Inserisci la firma prima della chiusura del contenuto principale
    
    # Se il contenuto termina con tag di chiusura, inseriamo prima
    if html_content.strip().endswith('</body>') or html_content.strip().endswith('</html>'):
        # Inserisci prima del tag di chiusura
        html_content = html_content.replace('</body>', signature + '</body>').replace('</html>', signature + '</html>')
    else:
        # Aggiungi semplicemente alla fine
        html_content = html_content + signature
    
    return html_content


def add_signature_to_text(text_content: str) -> str:
    """
    Aggiunge la firma email al testo se non è già presente
    
    Args:
        text_content: Contenuto testuale dell'email
        
    Returns:
        Testo con firma aggiunta
    """
    signature = get_email_signature_text()
    
    # Controlla se la firma è già presente
    if "Dott. Ing. Giovanni Pitton" in text_content:
        return text_content  # Firma già presente
    
    # Aggiungi la firma alla fine
    return text_content + "\n" + signature


def add_signature_to_email(html_content: str = None, text_content: str = None) -> tuple:
    """
    Aggiunge la firma sia all'HTML che al testo
    
    Args:
        html_content: Contenuto HTML (opzionale)
        text_content: Contenuto testuale (opzionale)
        
    Returns:
        Tupla (html_content, text_content) con firme aggiunte
    """
    html = add_signature_to_html(html_content) if html_content else None
    text = add_signature_to_text(text_content) if text_content else None
    
    return (html, text)







