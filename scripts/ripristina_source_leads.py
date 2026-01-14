#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ripristina il source dei leads esistenti a "Database Marittimo"
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from crm_app_completo import app, db, Lead

def ripristina_source():
    """Ripristina source dei leads esistenti a Database Marittimo"""
    with app.app_context():
        # Lista delle università/scuole marittime
        universita_scuole = [
            "Università degli Studi di Genova - DITEN",
            "Università degli Studi di Napoli Parthenope",
            "Università Politecnica delle Marche",
            "Università degli Studi di Palermo",
            "Università degli Studi di Pisa",
            "Università degli Studi di Bari",
            "Università Ca' Foscari Venezia",
            "Istituto Tecnico Nautico",
            "Accademia Navale di Livorno",
            "Istituto Idrografico della Marina",
            "Scuola Sottufficiali della Marina Militare",
            "Consorzio Nazionale Interuniversitario per le Scienze del Mare",
            "Istituto Superiore per la Protezione e la Ricerca Ambientale"
        ]
        
        aggiornati = 0
        
        print("🔄 Ripristino source leads esistenti a 'Database Marittimo'...\n")
        
        for nome in universita_scuole:
            leads = Lead.query.filter(Lead.company_name.contains(nome)).filter(Lead.source == 'SITO WEB').all()
            
            for lead in leads:
                lead.source = 'Database Marittimo'
                aggiornati += 1
                print(f"✅ Ripristinato: {lead.company_name} → Source: Database Marittimo")
        
        db.session.commit()
        
        print(f"\n{'='*60}")
        print(f"✅ Completato!")
        print(f"   Leads ripristinati: {aggiornati}")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    ripristina_source()

