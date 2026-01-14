#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per aggiungere contatti cantieri navali, produttori barche, armatori e operatori marittimi
Clienti potenziali per ROV e sistemi subacquei
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from crm_app_completo import app, db, Lead, User
from datetime import datetime

# Lista completa di contatti cantieri navali, produttori barche e operatori marittimi
CONTATTI_CANTIERI_NAVALI = [
    # === CANTIERI NAVALI ITALIANI ===
    {
        "company_name": "Fincantieri S.p.A.",
        "contact_first_name": "Ufficio",
        "contact_last_name": "Acquisizioni",
        "email": "acquisti@fincantieri.it",
        "phone": "+39 040 319 3111",
        "address": "Via Genova, 1, 34121 Trieste TS",
        "industry": "Cantiere Navale",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Hot",
        "status": "New",
        "notes": "Fincantieri - Leader mondiale nella costruzione navale. Potenziale cliente per ROV per ispezioni, manutenzioni e operazioni subacquee"
    },
    {
        "company_name": "Sanlorenzo S.p.A.",
        "contact_first_name": "Direzione",
        "contact_last_name": "Tecnica",
        "email": "info@sanlorenzo.it",
        "phone": "+39 0187 6181",
        "address": "Via Armezzone, 3, 19031 Ameglia SP",
        "industry": "Cantiere Navale",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Hot",
        "status": "New",
        "notes": "Sanlorenzo - Produttore yacht di lusso. ROV per ispezioni scafi e sistemi propulsivi"
    },
    {
        "company_name": "Ferretti Group",
        "contact_first_name": "Ufficio",
        "contact_last_name": "Innovazione",
        "email": "info@ferrettigroup.com",
        "phone": "+39 0541 709111",
        "address": "Via Ansaldo, 7, 47039 Forlì FC",
        "industry": "Cantiere Navale",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Hot",
        "status": "New",
        "notes": "Ferretti Group - Gruppo leader nella produzione di yacht. Tecnologie ROV per manutenzione e ispezioni"
    },
    {
        "company_name": "Azimut Benetti Group",
        "contact_first_name": "Dipartimento",
        "contact_last_name": "Ricerca e Sviluppo",
        "email": "info@azimutbenetti.com",
        "phone": "+39 011 93161",
        "address": "Via Michele Coppino, 104, 14100 Asti AT",
        "industry": "Cantiere Navale",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Hot",
        "status": "New",
        "notes": "Azimut Benetti - Leader mondiale nella produzione di superyacht. ROV per operazioni subacquee e manutenzioni"
    },
    {
        "company_name": "Cantiere Navale Baglietto",
        "contact_first_name": "Ufficio",
        "contact_last_name": "Tecnico",
        "email": "info@baglietto.com",
        "phone": "+39 0182 5311",
        "address": "Via Darsena, 4, 17023 Varazze SV",
        "industry": "Cantiere Navale",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "Baglietto - Cantiere storico specializzato in yacht di lusso. ROV per ispezioni e manutenzioni"
    },
    {
        "company_name": "Cantiere Navale Persico Marine",
        "contact_first_name": "Direzione",
        "contact_last_name": "Tecnica",
        "email": "info@persicomarine.com",
        "phone": "+39 035 710111",
        "address": "Via del Molino, 18, 24060 Nembro BG",
        "industry": "Cantiere Navale",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "Persico Marine - Costruzione barche da regata e yacht. ROV per operazioni subacquee"
    },
    {
        "company_name": "Overmarine Group (Mangusta)",
        "contact_first_name": "Ufficio",
        "contact_last_name": "Acquisizioni",
        "email": "info@overmarine.com",
        "phone": "+39 0584 3891",
        "address": "Via dei Pescatori, 2, 55049 Viareggio LU",
        "industry": "Cantiere Navale",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Hot",
        "status": "New",
        "notes": "Overmarine - Produttore Mangusta. ROV per manutenzioni e ispezioni"
    },
    
    # === CANTIERI NAVALI INTERNAZIONALI ===
    {
        "company_name": "Lürssen Yachts",
        "contact_first_name": "Technical",
        "contact_last_name": "Department",
        "email": "info@lurssen.com",
        "phone": "+49 421 6604 0",
        "address": "Zum Alten Speicher, 11, 28759 Bremen, Germany",
        "industry": "Cantiere Navale",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Hot",
        "status": "New",
        "notes": "Lürssen - Leader mondiale superyacht. Cliente importante per ROV"
    },
    {
        "company_name": "Oceanco",
        "contact_first_name": "Technical",
        "contact_last_name": "Services",
        "email": "info@oceanco.com",
        "phone": "+31 162 491 491",
        "address": "Cornelis Douwesweg 36, 1506 AL Zaandam, Netherlands",
        "industry": "Cantiere Navale",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Hot",
        "status": "New",
        "notes": "Oceanco - Costruzione superyacht. ROV per operazioni subacquee"
    },
    {
        "company_name": "Feadship",
        "contact_first_name": "Technical",
        "contact_last_name": "Department",
        "email": "info@feadship.nl",
        "phone": "+31 235 660 660",
        "address": "Houttuin 25, 2151 LB Aalsmeer, Netherlands",
        "industry": "Cantiere Navale",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Hot",
        "status": "New",
        "notes": "Feadship - Costruzione yacht di lusso. ROV per manutenzioni"
    },
    {
        "company_name": "Royal Huisman",
        "contact_first_name": "Technical",
        "contact_last_name": "Services",
        "email": "info@royalhuisman.com",
        "phone": "+31 527 243 131",
        "address": "Oude Molenweg 24, 8355 AA Giethoorn, Netherlands",
        "industry": "Cantiere Navale",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "Royal Huisman - Costruzione yacht a vela. ROV per ispezioni"
    },
    
    # === OPERATORI E SERVIZI MARITTIMI ===
    {
        "company_name": "RINA S.p.A.",
        "contact_first_name": "Marine",
        "contact_last_name": "Services",
        "email": "marine@rina.org",
        "phone": "+39 010 53851",
        "address": "Via Corsica, 12, 16128 Genova GE",
        "industry": "Servizi Marittimi",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Hot",
        "status": "New",
        "notes": "RINA - Certificazione e ispezioni navali. ROV per ispezioni e certificazioni"
    },
    {
        "company_name": "Bureau Veritas Marine",
        "contact_first_name": "Marine",
        "contact_last_name": "Services",
        "email": "marine@bureauveritas.com",
        "phone": "+33 1 55 24 70 00",
        "address": "67/71 Boulevard du Château, 92200 Neuilly-sur-Seine, France",
        "industry": "Servizi Marittimi",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Hot",
        "status": "New",
        "notes": "Bureau Veritas - Certificazione navale. ROV per ispezioni"
    },
    {
        "company_name": "DNV GL (DNV)",
        "contact_first_name": "Maritime",
        "contact_last_name": "Services",
        "email": "info@dnv.com",
        "phone": "+47 67 57 99 00",
        "address": "Veritasveien 1, 1363 Høvik, Norway",
        "industry": "Servizi Marittimi",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Hot",
        "status": "New",
        "notes": "DNV - Certificazione e classificazione navale. ROV per ispezioni"
    },
    {
        "company_name": "Lloyd's Register",
        "contact_first_name": "Marine",
        "contact_last_name": "Services",
        "email": "info@lr.org",
        "phone": "+44 20 7423 1540",
        "address": "71 Fenchurch Street, London EC3M 4BS, UK",
        "industry": "Servizi Marittimi",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Hot",
        "status": "New",
        "notes": "Lloyd's Register - Classificazione navale. ROV per ispezioni"
    },
    
    # === ARMATORI E OPERATORI MARITTIMI ===
    {
        "company_name": "Grimaldi Lines",
        "contact_first_name": "Fleet",
        "contact_last_name": "Management",
        "email": "info@grimaldi-lines.com",
        "phone": "+39 081 496 111",
        "address": "Via Marchese Campodisola, 13, 80133 Napoli NA",
        "industry": "Armatore",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "Grimaldi Lines - Trasporti marittimi. ROV per manutenzioni e ispezioni flotta"
    },
    {
        "company_name": "Costa Crociere",
        "contact_first_name": "Technical",
        "contact_last_name": "Services",
        "email": "info@costa.it",
        "phone": "+39 010 54831",
        "address": "Piazza Piccapietra, 48, 16121 Genova GE",
        "industry": "Armatore",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Hot",
        "status": "New",
        "notes": "Costa Crociere - Crociere. ROV per manutenzioni e ispezioni navi"
    },
    {
        "company_name": "MSC Crociere",
        "contact_first_name": "Fleet",
        "contact_last_name": "Management",
        "email": "info@msccruises.it",
        "phone": "+41 22 520 94 00",
        "address": "Chemin Rieu 12-14, 1208 Genève, Switzerland",
        "industry": "Armatore",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Hot",
        "status": "New",
        "notes": "MSC Crociere - Flotta crociere. ROV per manutenzioni"
    },
    {
        "company_name": "Tirrenia - Compagnia Italiana di Navigazione",
        "contact_first_name": "Fleet",
        "contact_last_name": "Management",
        "email": "info@tirrenia.it",
        "phone": "+39 091 602 1111",
        "address": "Via Enrico Amari, 14, 90139 Palermo PA",
        "industry": "Armatore",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "Tirrenia - Trasporti marittimi. ROV per manutenzioni"
    },
    
    # === SERVIZI OFFSHORE E SUBACQUEI ===
    {
        "company_name": "Saipem S.p.A.",
        "contact_first_name": "Offshore",
        "contact_last_name": "Services",
        "email": "info@saipem.com",
        "phone": "+39 02 442 21",
        "address": "Via Martiri di Cefalonia, 67, 20097 San Donato Milanese MI",
        "industry": "Offshore",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Hot",
        "status": "New",
        "notes": "Saipem - Servizi offshore e subacquei. Cliente importante per ROV"
    },
    {
        "company_name": "Tecnomare S.p.A.",
        "contact_first_name": "Engineering",
        "contact_last_name": "Services",
        "email": "info@tecnomare.it",
        "phone": "+39 041 509 5111",
        "address": "Via San Marco, 3581, 30124 Venezia VE",
        "industry": "Offshore",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Hot",
        "status": "New",
        "notes": "Tecnomare - Ingegneria offshore e sistemi subacquei. Cliente strategico per ROV"
    },
    {
        "company_name": "Fugro",
        "contact_first_name": "Offshore",
        "contact_last_name": "Services",
        "email": "info@fugro.com",
        "phone": "+31 70 311 14 22",
        "address": "Veurse Achterweg 10, 2264 SG Leidschendam, Netherlands",
        "industry": "Offshore",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Hot",
        "status": "New",
        "notes": "Fugro - Servizi geosservazione e offshore. Cliente importante per ROV"
    },
    {
        "company_name": "Oceaneering International",
        "contact_first_name": "ROV",
        "contact_last_name": "Services",
        "email": "info@oceaneering.com",
        "phone": "+1 713 329 4500",
        "address": "5875 North Sam Houston Parkway West, Houston, TX 77086, USA",
        "industry": "Offshore",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "Oceaneering - Servizi ROV e subacquei. Potenziale partnership"
    },
    
    # === PORTI E AUTORITÀ PORTUALI ===
    {
        "company_name": "Autorità di Sistema Portuale del Mar Tirreno Settentrionale (Livorno)",
        "contact_first_name": "Ufficio",
        "contact_last_name": "Tecnico",
        "email": "info@portolivorno.it",
        "phone": "+39 0586 210111",
        "address": "Piazzale dei Marmi, 1, 57123 Livorno LI",
        "industry": "Porto/Autorità Marittima",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "Porto di Livorno - Tecnologie per gestione portuale e ispezioni"
    },
    {
        "company_name": "Autorità di Sistema Portuale del Mar Adriatico Centrale (Ancona)",
        "contact_first_name": "Ufficio",
        "contact_last_name": "Tecnico",
        "email": "info@porto.ancona.it",
        "phone": "+39 071 207 81",
        "address": "Banchina Nazario Sauro, 1, 60125 Ancona AN",
        "industry": "Porto/Autorità Marittima",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "Porto di Ancona - Tecnologie marittime"
    },
    {
        "company_name": "Autorità di Sistema Portuale del Mar Ligure Orientale (La Spezia)",
        "contact_first_name": "Ufficio",
        "contact_last_name": "Tecnico",
        "email": "info@portodelleorientale.it",
        "phone": "+39 0187 546111",
        "address": "Via del Molo, 1, 19126 La Spezia SP",
        "industry": "Porto/Autorità Marittima",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "Porto della Spezia - Tecnologie portuali"
    },
]

def aggiungi_contatti():
    """Aggiunge tutti i contatti cantieri navali al database"""
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
        
        print(f"\n📋 Aggiunta contatti cantieri navali e operatori marittimi...")
        print(f"Totale contatti da aggiungere: {len(CONTATTI_CANTIERI_NAVALI)}\n")
        
        for contatto in CONTATTI_CANTIERI_NAVALI:
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
                source=contatto.get('source', 'Database Marittimo'),
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







