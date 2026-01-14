#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica dove sono i contatti VOX e Marittimi"""
import sys
sys.path.insert(0, '/home/ubuntu/offermanager')
from crm_app_completo import app, db
from sqlalchemy import text

with app.app_context():
    print("=" * 70)
    print("🔍 VERIFICA CONTATTI VOX E MARITTIMO")
    print("=" * 70)
    print()
    
    # Lead VOX
    vox_leads_total = db.session.execute(text("""
        SELECT COUNT(*) FROM leads 
        WHERE (source LIKE '%VOX%' OR source LIKE '%Vox%' OR notes LIKE '%VOX%' OR notes LIKE '%Vox%')
    """)).fetchone()[0]
    
    vox_leads_converted = db.session.execute(text("""
        SELECT COUNT(*) FROM leads 
        WHERE status = 'Converted'
        AND (source LIKE '%VOX%' OR source LIKE '%Vox%' OR notes LIKE '%VOX%' OR notes LIKE '%Vox%')
    """)).fetchone()[0]
    
    vox_leads_not_converted = db.session.execute(text("""
        SELECT COUNT(*) FROM leads 
        WHERE status != 'Converted'
        AND (source LIKE '%VOX%' OR source LIKE '%Vox%' OR notes LIKE '%VOX%' OR notes LIKE '%Vox%')
    """)).fetchone()[0]
    
    print(f"📧 LEAD VOX:")
    print(f"  Totale: {vox_leads_total}")
    print(f"  Convertiti: {vox_leads_converted}")
    print(f"  Non convertiti: {vox_leads_not_converted}")
    
    # Opportunità da Lead VOX
    vox_opps = db.session.execute(text("""
        SELECT COUNT(*) FROM opportunities o
        JOIN leads l ON o.lead_id = l.id
        WHERE (l.source LIKE '%VOX%' OR l.source LIKE '%Vox%' OR l.notes LIKE '%VOX%' OR l.notes LIKE '%Vox%')
    """)).fetchone()[0]
    
    print(f"  Opportunità create: {vox_opps}")
    
    # Lead Marittimi/ROV
    marittimo_leads_total = db.session.execute(text("""
        SELECT COUNT(*) FROM leads 
        WHERE (
            interest LIKE '%ROV%' OR 
            industry LIKE '%Marina%' OR 
            industry LIKE '%Marittim%' OR
            notes LIKE '%ROV%' OR
            notes LIKE '%marittimo%' OR
            notes LIKE '%subacqueo%' OR
            source LIKE '%Marittimo%' OR
            source LIKE '%marittimo%'
        )
    """)).fetchone()[0]
    
    marittimo_leads_converted = db.session.execute(text("""
        SELECT COUNT(*) FROM leads 
        WHERE status = 'Converted'
        AND (
            interest LIKE '%ROV%' OR 
            industry LIKE '%Marina%' OR 
            industry LIKE '%Marittim%' OR
            notes LIKE '%ROV%' OR
            notes LIKE '%marittimo%' OR
            notes LIKE '%subacqueo%' OR
            source LIKE '%Marittimo%' OR
            source LIKE '%marittimo%'
        )
    """)).fetchone()[0]
    
    marittimo_leads_not_converted = db.session.execute(text("""
        SELECT COUNT(*) FROM leads 
        WHERE status != 'Converted'
        AND (
            interest LIKE '%ROV%' OR 
            industry LIKE '%Marina%' OR 
            industry LIKE '%Marittim%' OR
            notes LIKE '%ROV%' OR
            notes LIKE '%marittimo%' OR
            notes LIKE '%subacqueo%' OR
            source LIKE '%Marittimo%' OR
            source LIKE '%marittimo%'
        )
    """)).fetchone()[0]
    
    print(f"\n🌊 LEAD MARITTIMO/ROV:")
    print(f"  Totale: {marittimo_leads_total}")
    print(f"  Convertiti: {marittimo_leads_converted}")
    print(f"  Non convertiti: {marittimo_leads_not_converted}")
    
    # Opportunità da Lead Marittimi
    marittimo_opps = db.session.execute(text("""
        SELECT COUNT(*) FROM opportunities o
        JOIN leads l ON o.lead_id = l.id
        WHERE (
            l.interest LIKE '%ROV%' OR 
            l.industry LIKE '%Marina%' OR 
            l.industry LIKE '%Marittim%' OR
            l.notes LIKE '%ROV%' OR
            l.notes LIKE '%marittimo%' OR
            l.notes LIKE '%subacqueo%' OR
            l.source LIKE '%Marittimo%' OR
            l.source LIKE '%marittimo%'
        )
    """)).fetchone()[0]
    
    print(f"  Opportunità create: {marittimo_opps}")
    
    # Mostra alcuni Lead VOX non convertiti
    if vox_leads_not_converted > 0:
        print(f"\n📋 Primi 5 Lead VOX non convertiti:")
        vox_leads = db.session.execute(text("""
            SELECT id, company_name, email, source, notes, status
            FROM leads 
            WHERE status != 'Converted'
            AND (source LIKE '%VOX%' OR source LIKE '%Vox%' OR notes LIKE '%VOX%' OR notes LIKE '%Vox%')
            LIMIT 5
        """)).fetchall()
        
        for lead in vox_leads:
            print(f"   ID: {lead[0]}, Azienda: {lead[1]}, Email: {lead[2]}, Source: {lead[3]}, Status: {lead[5]}")
    
    # Mostra alcuni Lead Marittimi non convertiti
    if marittimo_leads_not_converted > 0:
        print(f"\n📋 Primi 5 Lead Marittimi non convertiti:")
        marittimo_leads = db.session.execute(text("""
            SELECT id, company_name, email, interest, industry, notes, status
            FROM leads 
            WHERE status != 'Converted'
            AND (
                interest LIKE '%ROV%' OR 
                industry LIKE '%Marina%' OR 
                industry LIKE '%Marittim%' OR
                notes LIKE '%ROV%' OR
                notes LIKE '%marittimo%' OR
                notes LIKE '%subacqueo%' OR
                source LIKE '%Marittimo%' OR
                source LIKE '%marittimo%'
            )
            LIMIT 5
        """)).fetchall()
        
        for lead in marittimo_leads:
            print(f"   ID: {lead[0]}, Azienda: {lead[1]}, Email: {lead[2]}, Interest: {lead[3]}, Industry: {lead[4]}, Status: {lead[6]}")
    
    print(f"\n✅ Verifica completata!")
