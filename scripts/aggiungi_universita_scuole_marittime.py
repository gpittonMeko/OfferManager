#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per aggiungere università e scuole marittime italiane al CRM
Clienti potenziali per ROV e sistemi marittimi
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from crm_app_completo import app, db, Lead, User
from datetime import datetime

# Lista università e scuole marittime italiane
UNIVERSITA_SCUOLE_MARITTIME = [
    # === UNIVERSITÀ CON DIPARTIMENTI MARITTIMI ===
    {
        "company_name": "Università degli Studi di Genova - DITEN (Dipartimento Ingegneria Navale)",
        "contact_first_name": "Dipartimento",
        "contact_last_name": "Ingegneria Navale",
        "email": "diten@unige.it",
        "phone": "+39 010 335 2000",
        "address": "Via all'Opera Pia, 15, 16145 Genova GE",
        "industry": "Università/Ricerca",
        "interest": "MIR",
        "source": "SITO WEB",
        "rating": "Hot",
        "status": "New",
        "notes": "DITEN - Dipartimento Ingegneria Navale, Elettrica, Elettronica e delle Telecomunicazioni. Leader in ricerca navale e ROV"
    },
    {
        "company_name": "Università degli Studi di Napoli Parthenope - Dipartimento Scienze e Tecnologie",
        "contact_first_name": "Dipartimento",
        "contact_last_name": "Scienze e Tecnologie",
        "email": "dip.scienzetecnologie@uniparthenope.it",
        "phone": "+39 081 547 5000",
        "address": "Via Acton, 38, 80133 Napoli NA",
        "industry": "Università/Ricerca",
        "interest": "MIR",
        "source": "SITO WEB",
        "rating": "Hot",
        "status": "New",
        "notes": "Università Parthenope - Forte focus su tecnologie marittime e marine"
    },
    {
        "company_name": "Università Politecnica delle Marche - Dipartimento Ingegneria Industriale e Scienze Matematiche",
        "contact_first_name": "Dipartimento",
        "contact_last_name": "Ingegneria",
        "email": "info@univpm.it",
        "phone": "+39 071 220 1",
        "address": "Piazza Roma, 22, 60121 Ancona AN",
        "industry": "Università/Ricerca",
        "interest": "MIR",
        "source": "SITO WEB",
        "rating": "Warm",
        "status": "New",
        "notes": "UNIVPM - Ingegneria navale e tecnologie marine"
    },
    {
        "company_name": "Università degli Studi di Palermo - Dipartimento di Ingegneria",
        "contact_first_name": "Dipartimento",
        "contact_last_name": "Ingegneria",
        "email": "info@unipa.it",
        "phone": "+39 091 238 60001",
        "address": "Viale delle Scienze, Ed. 6, 90128 Palermo PA",
        "industry": "Università/Ricerca",
        "interest": "MIR",
        "source": "SITO WEB",
        "rating": "Warm",
        "status": "New",
        "notes": "Università di Palermo - Ingegneria navale e sistemi marittimi"
    },
    {
        "company_name": "Università degli Studi di Pisa - Dipartimento Ingegneria Civile e Industriale",
        "contact_first_name": "Dipartimento",
        "contact_last_name": "Ingegneria Marina",
        "email": "dici@unipi.it",
        "phone": "+39 050 221 7000",
        "address": "Largo Lucio Lazzarino, 1, 56122 Pisa PI",
        "industry": "Università/Ricerca",
        "interest": "MIR",
        "source": "SITO WEB",
        "rating": "Warm",
        "status": "New",
        "notes": "Università di Pisa - Ingegneria civile e marina"
    },
    {
        "company_name": "Università degli Studi di Bari - Dipartimento Scienze della Terra e Geoambientali",
        "contact_first_name": "Geologia",
        "contact_last_name": "Marina",
        "email": "dipartimento.sciterra@uniba.it",
        "phone": "+39 080 544 2624",
        "address": "Via Orabona, 4, 70125 Bari BA",
        "industry": "Università/Ricerca",
        "interest": "MIR",
        "source": "SITO WEB",
        "rating": "Warm",
        "status": "New",
        "notes": "Università di Bari - Ricerca geologia marina e ROV per esplorazione"
    },
    {
        "company_name": "Università Ca' Foscari Venezia - Dipartimento Scienze Ambientali, Informatica e Statistica",
        "contact_first_name": "Scienze",
        "contact_last_name": "Marine",
        "email": "daisa@unive.it",
        "phone": "+39 041 234 8111",
        "address": "Dorsoduro, 3246, 30123 Venezia VE",
        "industry": "Università/Ricerca",
        "interest": "MIR",
        "source": "SITO WEB",
        "rating": "Warm",
        "status": "New",
        "notes": "Ca' Foscari - Scienze marine e ambientali, ricerca con ROV"
    },
    
    # === SCUOLE SUPERIORI E ISTITUTI TECNICI MARITTIMI ===
    {
        "company_name": "Istituto Tecnico Nautico 'Duca degli Abruzzi' - Genova",
        "contact_first_name": "Direzione",
        "contact_last_name": "Didattica",
        "email": "geis00300x@istruzione.it",
        "phone": "+39 010 251 1011",
        "address": "Via del Molo, 1, 16126 Genova GE",
        "industry": "Scuola/Istituto",
        "interest": "MIR",
        "source": "SITO WEB",
        "rating": "Warm",
        "status": "New",
        "notes": "Istituto Nautico Genova - Formazione tecnica marittima, potenziale uso ROV per didattica"
    },
    {
        "company_name": "Istituto Tecnico Nautico 'Duca degli Abruzzi' - Trieste",
        "contact_first_name": "Direzione",
        "contact_last_name": "Didattica",
        "email": "tsis00300x@istruzione.it",
        "phone": "+39 040 638 311",
        "address": "Via G. Carducci, 4, 34124 Trieste TS",
        "industry": "Scuola/Istituto",
        "interest": "MIR",
        "source": "SITO WEB",
        "rating": "Warm",
        "status": "New",
        "notes": "Istituto Nautico Trieste - Formazione tecnica marittima"
    },
    {
        "company_name": "Istituto Tecnico Nautico 'Nino Bixio' - Piano di Sorrento",
        "contact_first_name": "Direzione",
        "contact_last_name": "Didattica",
        "email": "nais00300x@istruzione.it",
        "phone": "+39 081 878 1001",
        "address": "Via Nastro Verde, 45, 80063 Piano di Sorrento NA",
        "industry": "Scuola/Istituto",
        "interest": "MIR",
        "source": "SITO WEB",
        "rating": "Warm",
        "status": "New",
        "notes": "Istituto Nautico Piano di Sorrento - Formazione tecnica marittima"
    },
    {
        "company_name": "Istituto Tecnico Nautico 'Leon Pancaldo' - Savona",
        "contact_first_name": "Direzione",
        "contact_last_name": "Didattica",
        "email": "svis00300x@istruzione.it",
        "phone": "+39 019 821 111",
        "address": "Via Nizza, 2, 17100 Savona SV",
        "industry": "Scuola/Istituto",
        "interest": "MIR",
        "source": "SITO WEB",
        "rating": "Warm",
        "status": "New",
        "notes": "Istituto Nautico Savona - Formazione tecnica marittima"
    },
    {
        "company_name": "Istituto Tecnico Nautico 'Artiglio' - Viareggio",
        "contact_first_name": "Direzione",
        "contact_last_name": "Didattica",
        "email": "luis00300x@istruzione.it",
        "phone": "+39 0584 383 111",
        "address": "Via Don Minzoni, 1, 55049 Viareggio LU",
        "industry": "Scuola/Istituto",
        "interest": "MIR",
        "source": "SITO WEB",
        "rating": "Warm",
        "status": "New",
        "notes": "Istituto Nautico Viareggio - Formazione tecnica marittima"
    },
    {
        "company_name": "Istituto Tecnico Nautico 'C. Colombo' - Porto Empedocle",
        "contact_first_name": "Direzione",
        "contact_last_name": "Didattica",
        "email": "agis00300x@istruzione.it",
        "phone": "+39 0922 631 111",
        "address": "Via Roma, 1, 92014 Porto Empedocle AG",
        "industry": "Scuola/Istituto",
        "interest": "MIR",
        "source": "SITO WEB",
        "rating": "Warm",
        "status": "New",
        "notes": "Istituto Nautico Porto Empedocle - Formazione tecnica marittima"
    },
    {
        "company_name": "Istituto Tecnico Nautico 'G. Caboto' - Gaeta",
        "contact_first_name": "Direzione",
        "contact_last_name": "Didattica",
        "email": "ltis00300x@istruzione.it",
        "phone": "+39 0771 461 111",
        "address": "Via Caboto, 1, 04024 Gaeta LT",
        "industry": "Scuola/Istituto",
        "interest": "MIR",
        "source": "SITO WEB",
        "rating": "Warm",
        "status": "New",
        "notes": "Istituto Nautico Gaeta - Formazione tecnica marittima"
    },
    {
        "company_name": "Istituto Tecnico Nautico 'A. Rizzo' - Milazzo",
        "contact_first_name": "Direzione",
        "contact_last_name": "Didattica",
        "email": "meis00300x@istruzione.it",
        "phone": "+39 090 928 1111",
        "address": "Via Marina Garibaldi, 1, 98057 Milazzo ME",
        "industry": "Scuola/Istituto",
        "interest": "MIR",
        "source": "SITO WEB",
        "rating": "Warm",
        "status": "New",
        "notes": "Istituto Nautico Milazzo - Formazione tecnica marittima"
    },
    {
        "company_name": "Istituto Tecnico Nautico 'G. C. Ciano' - Livorno",
        "contact_first_name": "Direzione",
        "contact_last_name": "Didattica",
        "email": "liis00300x@istruzione.it",
        "phone": "+39 0586 421 111",
        "address": "Via del Molo Mediceo, 1, 57123 Livorno LI",
        "industry": "Scuola/Istituto",
        "interest": "MIR",
        "source": "SITO WEB",
        "rating": "Warm",
        "status": "New",
        "notes": "Istituto Nautico Livorno - Formazione tecnica marittima"
    },
    {
        "company_name": "Istituto Tecnico Nautico 'G. B. Ferrari' - Ostia",
        "contact_first_name": "Direzione",
        "contact_last_name": "Didattica",
        "email": "rmis00300x@istruzione.it",
        "phone": "+39 06 564 1111",
        "address": "Via delle Saline, 1, 00121 Roma RM",
        "industry": "Scuola/Istituto",
        "interest": "MIR",
        "source": "SITO WEB",
        "rating": "Warm",
        "status": "New",
        "notes": "Istituto Nautico Ostia - Formazione tecnica marittima"
    },
    {
        "company_name": "Istituto Tecnico Nautico 'G. B. Ferrari' - Ancona",
        "contact_first_name": "Direzione",
        "contact_last_name": "Didattica",
        "email": "anis00300x@istruzione.it",
        "phone": "+39 071 201 111",
        "address": "Banchina Nazario Sauro, 1, 60125 Ancona AN",
        "industry": "Scuola/Istituto",
        "interest": "MIR",
        "source": "SITO WEB",
        "rating": "Warm",
        "status": "New",
        "notes": "Istituto Nautico Ancona - Formazione tecnica marittima"
    },
    {
        "company_name": "Istituto Tecnico Nautico 'G. B. Ferrari' - Messina",
        "contact_first_name": "Direzione",
        "contact_last_name": "Didattica",
        "email": "mesis00300x@istruzione.it",
        "phone": "+39 090 671 1111",
        "address": "Via G. La Farina, 1, 98122 Messina ME",
        "industry": "Scuola/Istituto",
        "interest": "MIR",
        "source": "SITO WEB",
        "rating": "Warm",
        "status": "New",
        "notes": "Istituto Nautico Messina - Formazione tecnica marittima"
    },
    
    # === ACCADEMIE E SCUOLE SUPERIORI MARITTIME ===
    {
        "company_name": "Accademia Navale di Livorno",
        "contact_first_name": "Ufficio",
        "contact_last_name": "Formazione",
        "email": "info@marina.difesa.it",
        "phone": "+39 0586 210 111",
        "address": "Viale Italia, 72, 57127 Livorno LI",
        "industry": "Accademia Militare",
        "interest": "MIR",
        "source": "SITO WEB",
        "rating": "Hot",
        "status": "New",
        "notes": "Accademia Navale - Formazione ufficiali Marina Militare. Cliente importante per ROV e sistemi subacquei"
    },
    {
        "company_name": "Istituto Idrografico della Marina - Scuola di Idrografia",
        "contact_first_name": "Scuola",
        "contact_last_name": "Idrografia",
        "email": "scuola.idrografia@marina.difesa.it",
        "phone": "+39 010 241 2811",
        "address": "Passo dell'Osservatorio, 4, 16134 Genova GE",
        "industry": "Scuola Militare",
        "interest": "MIR",
        "source": "SITO WEB",
        "rating": "Hot",
        "status": "New",
        "notes": "Scuola Idrografia - Formazione specialistica, ROV per cartografia e ricerca"
    },
    {
        "company_name": "Scuola Sottufficiali della Marina Militare - Taranto",
        "contact_first_name": "Direzione",
        "contact_last_name": "Corsi",
        "email": "info@marina.difesa.it",
        "phone": "+39 099 775 1111",
        "address": "Via Ammiraglio Millo, 1, 74121 Taranto TA",
        "industry": "Scuola Militare",
        "interest": "MIR",
        "source": "SITO WEB",
        "rating": "Warm",
        "status": "New",
        "notes": "Scuola Sottufficiali - Formazione tecnica Marina Militare"
    },
    
    # === ENTI DI RICERCA E FORMAZIONE MARITTIMA ===
    {
        "company_name": "Consorzio Nazionale Interuniversitario per le Scienze del Mare (CoNISMa)",
        "contact_first_name": "Segreteria",
        "contact_last_name": "Scientifica",
        "email": "info@conisma.it",
        "phone": "+39 06 4991 4000",
        "address": "Piazzale Aldo Moro, 5, 00185 Roma RM",
        "industry": "Università/Ricerca",
        "interest": "MIR",
        "source": "SITO WEB",
        "rating": "Hot",
        "status": "New",
        "notes": "CoNISMa - Consorzio interuniversitario ricerca marina. Cliente strategico per ROV"
    },
    {
        "company_name": "Istituto Superiore per la Protezione e la Ricerca Ambientale (ISPRA) - Settore Marino",
        "contact_first_name": "Settore",
        "contact_last_name": "Marino",
        "email": "info@isprambiente.it",
        "phone": "+39 06 5007 1",
        "address": "Via Vitaliano Brancati, 48, 00144 Roma RM",
        "industry": "Ente Ricerca",
        "interest": "MIR",
        "source": "SITO WEB",
        "rating": "Warm",
        "status": "New",
        "notes": "ISPRA - Ricerca ambientale marina, ROV per monitoraggio"
    },
]

def aggiungi_contatti():
    """Aggiunge tutti i contatti università e scuole marittime al database"""
    with app.app_context():
        # Inizializza il database se necessario
        print("🔧 Inizializzazione database...")
        try:
            db.create_all()
            print("✅ Database inizializzato")
        except Exception as e:
            print(f"⚠️  Errore inizializzazione database: {e}")
        
        # Trova l'utente admin per assegnare i lead
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("⚠️  Utente 'admin' non trovato. Creazione...")
            admin = User(
                username='admin',
                password='pbkdf2:sha256:260000$...',
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Utente admin creato")
        
        contatti_aggiunti = 0
        contatti_esistenti = 0
        
        print(f"\n📋 Aggiunta università e scuole marittime italiane...")
        print(f"Totale contatti da aggiungere: {len(UNIVERSITA_SCUOLE_MARITTIME)}\n")
        
        for contatto in UNIVERSITA_SCUOLE_MARITTIME:
            # Verifica se esiste già un lead con stesso nome azienda e email
            esistente = Lead.query.filter_by(
                company_name=contatto['company_name'],
                email=contatto.get('email')
            ).first()
            
            if esistente:
                print(f"⏭️  Saltato: {contatto['company_name']} (già presente)")
                contatti_esistenti += 1
                continue
            
            # Crea nuovo lead
            lead = Lead(
                company_name=contatto['company_name'],
                contact_first_name=contatto.get('contact_first_name', ''),
                contact_last_name=contatto.get('contact_last_name', ''),
                email=contatto.get('email', ''),
                phone=contatto.get('phone', ''),
                address=contatto.get('address', ''),
                industry=contatto.get('industry', ''),
                interest=contatto.get('interest', 'MIR'),
                source='SITO WEB',
                rating=contatto.get('rating', 'Warm'),
                status=contatto.get('status', 'New'),
                notes=contatto.get('notes', ''),
                owner_id=admin.id,
                last_contact_at=None
            )
            
            db.session.add(lead)
            contatti_aggiunti += 1
            print(f"✅ Aggiunto: {contatto['company_name']}")
        
        db.session.commit()
        
        print(f"\n{'='*60}")
        print(f"✅ Completato!")
        print(f"   Contatti aggiunti: {contatti_aggiunti}")
        print(f"   Contatti già esistenti: {contatti_esistenti}")
        print(f"   Totale nel database: {Lead.query.count()}")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    aggiungi_contatti()

