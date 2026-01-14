#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per aggiornare il source dei leads università/scuole marittime a "SITO WEB"
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from crm_app_completo import app, db, Lead

def aggiorna_source():
    """Aggiorna il source dei leads università/scuole marittime a 'SITO WEB'"""
    with app.app_context():
        # Lista delle università/scuole marittime dal file originale
        universita_scuole = [
            "Università degli Studi di Genova - DITEN",
            "Università degli Studi di Napoli Parthenope",
            "Università Politecnica delle Marche",
            "Università degli Studi di Palermo",
            "Università degli Studi di Pisa",
            "Università degli Studi di Bari",
            "Università Ca' Foscari Venezia",
            "Istituto Tecnico Nautico 'Duca degli Abruzzi'",
            "Istituto Tecnico Nautico 'Nino Bixio'",
            "Istituto Tecnico Nautico 'Leon Pancaldo'",
            "Istituto Tecnico Nautico 'Artiglio'",
            "Istituto Tecnico Nautico 'C. Colombo'",
            "Istituto Tecnico Nautico 'G. Caboto'",
            "Istituto Tecnico Nautico 'A. Rizzo'",
            "Istituto Tecnico Nautico 'G. C. Ciano'",
            "Istituto Tecnico Nautico 'G. B. Ferrari'",
            "Accademia Navale di Livorno",
            "Istituto Idrografico della Marina",
            "Scuola Sottufficiali della Marina Militare",
            "Consorzio Nazionale Interuniversitario per le Scienze del Mare",
            "Istituto Superiore per la Protezione e la Ricerca Ambientale"
        ]
        
        aggiornati = 0
        
        print("🔄 Aggiornamento source leads università/scuole marittime...\n")
        
        for nome in universita_scuole:
            # Cerca leads che contengono il nome
            leads = Lead.query.filter(Lead.company_name.contains(nome)).all()
            
            for lead in leads:
                if lead.source != 'SITO WEB':
                    lead.source = 'SITO WEB'
                    aggiornati += 1
                    print(f"✅ Aggiornato: {lead.company_name} → Source: SITO WEB, Interest: {lead.interest}")
        
        db.session.commit()
        
        print(f"\n{'='*60}")
        print(f"✅ Completato!")
        print(f"   Leads aggiornati: {aggiornati}")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    aggiorna_source()

