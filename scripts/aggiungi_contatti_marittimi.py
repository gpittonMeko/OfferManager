#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per aggiungere contatti marittimi (marine, università, enti) al CRM
Clienti potenziali per ROV (Remotely Operated Vehicles)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from crm_app_completo import app, db, Lead, User
from datetime import datetime

# Lista completa di contatti marittimi
CONTATTI_MARITTIMI = [
    # === MARINE MILITARI ===
    {
        "company_name": "Marina Militare Italiana",
        "contact_first_name": "Ufficio",
        "contact_last_name": "Acquisizioni",
        "email": "acquisti@marina.difesa.it",
        "phone": "+39 06 3680 1",
        "address": "Piazzale della Marina, 1, 00196 Roma RM",
        "industry": "Marina Militare",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Hot",
        "status": "New",
        "notes": "Marina Militare Italiana - Potenziale cliente per ROV e sistemi subacquei"
    },
    {
        "company_name": "US Navy - Naval Sea Systems Command",
        "contact_first_name": "Procurement",
        "contact_last_name": "Office",
        "email": "navsea@navy.mil",
        "phone": "+1 202 781 0000",
        "address": "1333 Isaac Hull Avenue SE, Washington Navy Yard, DC 20376",
        "industry": "Marina Militare",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Hot",
        "status": "New",
        "notes": "US Navy - Cliente importante per ROV e sistemi navali avanzati"
    },
    {
        "company_name": "Royal Navy - Ministry of Defence",
        "contact_first_name": "Defence",
        "contact_last_name": "Equipment & Support",
        "email": "defenceequipmentandsupport@mod.gov.uk",
        "phone": "+44 207 218 9000",
        "address": "Ministry of Defence, Whitehall, London SW1A 2HB, UK",
        "industry": "Marina Militare",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Hot",
        "status": "New",
        "notes": "Royal Navy - Potenziale cliente per tecnologie marittime avanzate"
    },
    {
        "company_name": "Marine Nationale",
        "contact_first_name": "Service",
        "contact_last_name": "Acquisition",
        "email": "achats@defense.gouv.fr",
        "phone": "+33 1 42 19 30 11",
        "address": "Place Joffre, 75700 Paris SP 07, France",
        "industry": "Marina Militare",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "Marine Nationale francese - Sistemi ROV e subacquei"
    },
    {
        "company_name": "Deutsche Marine",
        "contact_first_name": "Beschaffungsamt",
        "contact_last_name": "der Bundeswehr",
        "email": "beschaffungsamt@bundeswehr.org",
        "phone": "+49 228 5507 0",
        "address": "Ferdinand-Sauerbruch-Straße 1, 56073 Koblenz, Germany",
        "industry": "Marina Militare",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "Marina tedesca - Cliente potenziale per ROV"
    },
    {
        "company_name": "Armada Española",
        "contact_first_name": "Dirección",
        "contact_last_name": "de Adquisiciones",
        "email": "adquisiciones@armada.mde.es",
        "phone": "+34 915 795 000",
        "address": "Paseo de la Castellana, 109, 28046 Madrid, Spain",
        "industry": "Marina Militare",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "Armada Española - Sistemi marittimi e ROV"
    },
    
    # === UNIVERSITÀ E ISTITUTI DI RICERCA MARITTIMA ===
    {
        "company_name": "Università degli Studi di Genova - DITEN",
        "contact_first_name": "Prof.",
        "contact_last_name": "Ricerca Marina",
        "email": "diten@unige.it",
        "phone": "+39 010 335 2000",
        "address": "Via all'Opera Pia, 15, 16145 Genova GE",
        "industry": "Università/Ricerca",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "Dipartimento Ingegneria Navale - Ricerca su ROV e sistemi marini"
    },
    {
        "company_name": "CNR - Istituto di Scienze Marine",
        "contact_first_name": "Ricerca",
        "contact_last_name": "Oceanografica",
        "email": "ismar@cnr.it",
        "phone": "+39 041 240 4711",
        "address": "Arsenale - Tesa 104, Castello 2737/F, 30122 Venezia VE",
        "industry": "Università/Ricerca",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "CNR - Ricerca oceanografica e ROV per studi marini"
    },
    {
        "company_name": "ENEA - Dipartimento Sostenibilità",
        "contact_first_name": "Ricerca",
        "contact_last_name": "Tecnologie Marine",
        "email": "dtsn@enea.it",
        "phone": "+39 06 9400 1",
        "address": "Lungotevere Thaon di Revel, 76, 00196 Roma RM",
        "industry": "Università/Ricerca",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "ENEA - Ricerca tecnologie marine sostenibili e ROV"
    },
    {
        "company_name": "MIT - Center for Ocean Engineering",
        "contact_first_name": "Ocean",
        "contact_last_name": "Engineering Lab",
        "email": "ocean-eng@mit.edu",
        "phone": "+1 617 253 4331",
        "address": "77 Massachusetts Avenue, Cambridge, MA 02139, USA",
        "industry": "Università/Ricerca",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Hot",
        "status": "New",
        "notes": "MIT - Leader mondiale in ingegneria oceanica e ROV"
    },
    {
        "company_name": "WHOI - Woods Hole Oceanographic Institution",
        "contact_first_name": "ROV",
        "contact_last_name": "Operations",
        "email": "rovops@whoi.edu",
        "phone": "+1 508 289 2252",
        "address": "266 Woods Hole Road, Woods Hole, MA 02543, USA",
        "industry": "Università/Ricerca",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Hot",
        "status": "New",
        "notes": "WHOI - Istituzione leader mondiale in ricerca oceanica e ROV"
    },
    {
        "company_name": "Heriot-Watt University - Ocean Systems Laboratory",
        "contact_first_name": "Ocean",
        "contact_last_name": "Systems Lab",
        "email": "osl@hw.ac.uk",
        "phone": "+44 131 451 3000",
        "address": "Edinburgh EH14 4AS, UK",
        "industry": "Università/Ricerca",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "Heriot-Watt - Ricerca su sistemi ROV e robotica subacquea"
    },
    {
        "company_name": "Università degli Studi di Napoli Parthenope",
        "contact_first_name": "Dipartimento",
        "contact_last_name": "Scienze e Tecnologie",
        "email": "dip.scienzetecnologie@uniparthenope.it",
        "phone": "+39 081 547 5000",
        "address": "Via Acton, 38, 80133 Napoli NA",
        "industry": "Università/Ricerca",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "Università Parthenope - Ricerca tecnologie marittime"
    },
    {
        "company_name": "TU Delft - Marine and Transport Technology",
        "contact_first_name": "Marine",
        "contact_last_name": "Technology",
        "email": "mtt@tudelft.nl",
        "phone": "+31 15 278 1000",
        "address": "Mekelweg 2, 2628 CD Delft, Netherlands",
        "industry": "Università/Ricerca",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "TU Delft - Tecnologie marine e ROV"
    },
    
    # === ENTI E ORGANIZZAZIONI MARITTIME ===
    {
        "company_name": "Autorità di Sistema Portuale del Mar Ligure Occidentale",
        "contact_first_name": "Ufficio",
        "contact_last_name": "Tecnico",
        "email": "info@porto.genova.it",
        "phone": "+39 010 241 241",
        "address": "Piazza Caricamento, 16123 Genova GE",
        "industry": "Porto/Autorità Marittima",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "Porto di Genova - Potenziale uso ROV per ispezioni portuali"
    },
    {
        "company_name": "Autorità di Sistema Portuale del Mar Adriatico Settentrionale",
        "contact_first_name": "Ufficio",
        "contact_last_name": "Tecnico",
        "email": "info@port.venice.it",
        "phone": "+39 041 533 4111",
        "address": "Zattere, 1401, 30123 Venezia VE",
        "industry": "Porto/Autorità Marittima",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "Porto di Venezia - Tecnologie per gestione portuale"
    },
    {
        "company_name": "Coast Guard - Guardia Costiera",
        "contact_first_name": "Ufficio",
        "contact_last_name": "Acquisizioni",
        "email": "acquisti@guardiacostiera.gov.it",
        "phone": "+39 06 5908 1",
        "address": "Via dell'Arte, 16, 00144 Roma RM",
        "industry": "Guardia Costiera",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Hot",
        "status": "New",
        "notes": "Guardia Costiera - ROV per operazioni di ricerca e soccorso"
    },
    {
        "company_name": "Istituto Idrografico della Marina",
        "contact_first_name": "Ufficio",
        "contact_last_name": "Ricerca",
        "email": "info@marina.difesa.it",
        "phone": "+39 010 241 2811",
        "address": "Passo dell'Osservatorio, 4, 16134 Genova GE",
        "industry": "Marina Militare",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "Istituto Idrografico - Cartografia e ricerca idrografica con ROV"
    },
    {
        "company_name": "ISMAR-CNR - Istituto di Scienze Marine",
        "contact_first_name": "Ricerca",
        "contact_last_name": "Oceanografica",
        "email": "direzione@ismar.cnr.it",
        "phone": "+39 071 207 8841",
        "address": "Largo Fiera della Pesca, 1, 60125 Ancona AN",
        "industry": "Università/Ricerca",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "CNR ISMAR Ancona - Ricerca oceanografica"
    },
    {
        "company_name": "Stazione Zoologica Anton Dohrn",
        "contact_first_name": "Ricerca",
        "contact_last_name": "Biologia Marina",
        "email": "info@szn.it",
        "phone": "+39 081 583 3111",
        "address": "Villa Comunale, 80121 Napoli NA",
        "industry": "Università/Ricerca",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "Stazione Zoologica - Ricerca biologia marina e ROV per esplorazione"
    },
    {
        "company_name": "Università Politecnica delle Marche - Dipartimento Ingegneria",
        "contact_first_name": "Ingegneria",
        "contact_last_name": "Navale",
        "email": "info@univpm.it",
        "phone": "+39 071 220 1",
        "address": "Piazza Roma, 22, 60121 Ancona AN",
        "industry": "Università/Ricerca",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "UNIVPM - Ingegneria navale e tecnologie marine"
    },
    {
        "company_name": "IFREMER - Institut Français de Recherche pour l'Exploitation de la Mer",
        "contact_first_name": "ROV",
        "contact_last_name": "Department",
        "email": "contact@ifremer.fr",
        "phone": "+33 2 98 22 40 00",
        "address": "1625 Route de Sainte-Anne, 29280 Plouzané, France",
        "industry": "Università/Ricerca",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Hot",
        "status": "New",
        "notes": "IFREMER - Leader francese in ricerca oceanica e ROV"
    },
    {
        "company_name": "NOC - National Oceanography Centre",
        "contact_first_name": "Marine",
        "contact_last_name": "Technology",
        "email": "enquiries@noc.ac.uk",
        "phone": "+44 23 8059 6666",
        "address": "European Way, Southampton SO14 3ZH, UK",
        "industry": "Università/Ricerca",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Hot",
        "status": "New",
        "notes": "NOC - Centro nazionale oceanografico UK - ROV e tecnologie marine"
    },
    {
        "company_name": "AWI - Alfred Wegener Institute",
        "contact_first_name": "Polar",
        "contact_last_name": "Ocean Research",
        "email": "info@awi.de",
        "phone": "+49 471 4831 0",
        "address": "Am Handelshafen 12, 27570 Bremerhaven, Germany",
        "industry": "Università/Ricerca",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "AWI - Ricerca polare e oceanografica con ROV"
    },
    {
        "company_name": "Università degli Studi di Bari - Dipartimento Scienze della Terra",
        "contact_first_name": "Geologia",
        "contact_last_name": "Marina",
        "email": "dipartimento.sciterra@uniba.it",
        "phone": "+39 080 544 2624",
        "address": "Via Orabona, 4, 70125 Bari BA",
        "industry": "Università/Ricerca",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "Università di Bari - Ricerca geologia marina"
    },
    {
        "company_name": "Università Ca' Foscari Venezia - Dipartimento Scienze Ambientali",
        "contact_first_name": "Scienze",
        "contact_last_name": "Marine",
        "email": "daisa@unive.it",
        "phone": "+39 041 234 8111",
        "address": "Dorsoduro, 3246, 30123 Venezia VE",
        "industry": "Università/Ricerca",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "Ca' Foscari - Scienze marine e ambientali"
    },
    {
        "company_name": "Università di Palermo - Dipartimento di Ingegneria",
        "contact_first_name": "Ingegneria",
        "contact_last_name": "Navale",
        "email": "info@unipa.it",
        "phone": "+39 091 238 60001",
        "address": "Viale delle Scienze, Ed. 6, 90128 Palermo PA",
        "industry": "Università/Ricerca",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "Università di Palermo - Ingegneria navale"
    },
    {
        "company_name": "Università degli Studi di Pisa - Dipartimento Ingegneria Civile e Industriale",
        "contact_first_name": "Ingegneria",
        "contact_last_name": "Marina",
        "email": "dici@unipi.it",
        "phone": "+39 050 221 7000",
        "address": "Largo Lucio Lazzarino, 1, 56122 Pisa PI",
        "industry": "Università/Ricerca",
        "interest": "MIR",
        "source": "Database Marittimo",
        "rating": "Warm",
        "status": "New",
        "notes": "Università di Pisa - Ingegneria civile e marina"
    },
]

def aggiungi_contatti():
    """Aggiunge tutti i contatti marittimi al database"""
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
                password='pbkdf2:sha256:260000$...',  # Password hash placeholder
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Utente admin creato")
        
        contatti_aggiunti = 0
        contatti_esistenti = 0
        
        print(f"\n📋 Aggiunta contatti marittimi...")
        print(f"Totale contatti da aggiungere: {len(CONTATTI_MARITTIMI)}\n")
        
        for contatto in CONTATTI_MARITTIMI:
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

