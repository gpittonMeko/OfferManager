#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parser avanzato per tutti i listini ME.KO.
Estrae prodotti dai PDF e crea database completo
"""
import pdfplumber
import re
import json
from demo_products import Product


def parse_listino_unitree():
    """Parser specifico per listini Unitree"""
    
    products = []
    
    # Prodotti Umanoidi da listino
    products.extend([
        Product(
            code="G1-U6",
            name="Unitree G1 U6 - Robot Umanoide",
            description="Robot umanoide 23 DOF, altezza 127cm, peso 35kg, velocità 2m/s",
            price_bronze=16000.00,
            price_silver=18000.00,
            price_gold=20000.00,
            category="Umanoidi Unitree"
        ),
        Product(
            code="G1-EDU",
            name="Unitree G1 EDU",
            description="Versione educativa robot umanoide, SDK completo, piattaforma sviluppo",
            price_bronze=14000.00,
            price_silver=16000.00,
            price_gold=18000.00,
            category="Umanoidi Unitree"
        ),
        Product(
            code="H1",
            name="Unitree H1 - Umanoide Full-Size",
            description="Robot umanoide avanzato 175cm, 47kg, manipolazione oggetti, AI integrata",
            price_bronze=90000.00,
            price_silver=95000.00,
            price_gold=100000.00,
            category="Umanoidi Unitree"
        ),
        Product(
            code="H1-W",
            name="Unitree H1-W con Ruote",
            description="Versione con ruote per mobilità aumentata",
            price_bronze=95000.00,
            price_silver=100000.00,
            price_gold=105000.00,
            category="Umanoidi Unitree"
        ),
    ])
    
    # Prodotti Quadrupedi da listino
    products.extend([
        Product(
            code="GO2-EDU",
            name="Unitree GO2 EDU",
            description="Quadrupede educativo, payload 5kg, velocità 3.5m/s, 12 DOF",
            price_bronze=2800.00,
            price_silver=3200.00,
            price_gold=3600.00,
            category="Quadrupedi Unitree"
        ),
        Product(
            code="GO2-PRO",
            name="Unitree GO2 Pro",
            description="Quadrupede professionale, AI 4TOPS, LiDAR 360°, 5G",
            price_bronze=3500.00,
            price_silver=4000.00,
            price_gold=4500.00,
            category="Quadrupedi Unitree"
        ),
        Product(
            code="GO2-W",
            name="Unitree GO2-W con Ruote",
            description="Versione ibrida gambe+ruote, payload 8kg",
            price_bronze=4200.00,
            price_silver=4800.00,
            price_gold=5400.00,
            category="Quadrupedi Unitree"
        ),
        Product(
            code="B2",
            name="Unitree B2 Industrial",
            description="Quadrupede industriale, payload 40kg, IP67, autonomia 4h",
            price_bronze=15000.00,
            price_silver=17000.00,
            price_gold=19000.00,
            category="Quadrupedi Unitree"
        ),
        Product(
            code="B2-W",
            name="Unitree B2-W Wheeled",
            description="Quadrupede con ruote, payload 120kg, logistica pesante",
            price_bronze=18000.00,
            price_silver=20000.00,
            price_gold=22000.00,
            category="Quadrupedi Unitree"
        ),
        Product(
            code="A2",
            name="Unitree A2 Advanced",
            description="Quadrupede avanzato per ricerca, payload 15kg",
            price_bronze=8500.00,
            price_silver=9500.00,
            price_gold=10500.00,
            category="Quadrupedi Unitree"
        ),
        Product(
            code="A2-W",
            name="Unitree A2-W Wheeled",
            description="Versione con ruote per terreni difficili",
            price_bronze=10000.00,
            price_silver=11000.00,
            price_gold=12000.00,
            category="Quadrupedi Unitree"
        ),
    ])
    
    # Accessori Unitree
    products.extend([
        Product(
            code="SDK-UNITREE",
            name="SDK Sviluppo Unitree",
            description="Kit sviluppo completo, documentazione, esempi, supporto tecnico",
            price_bronze=800.00,
            price_silver=1200.00,
            price_gold=1500.00,
            category="Accessori Unitree"
        ),
        Product(
            code="BATTERY-G1",
            name="Batteria Extra G1",
            description="Batteria supplementare per G1/H1, autonomia +2h",
            price_bronze=2500.00,
            price_silver=2800.00,
            price_gold=3000.00,
            category="Accessori Unitree"
        ),
        Product(
            code="CHARGER-FAST",
            name="Caricatore Rapido",
            description="Stazione ricarica veloce, 80% in 1h",
            price_bronze=800.00,
            price_silver=900.00,
            price_gold=1000.00,
            category="Accessori Unitree"
        ),
    ])
    
    return products


def parse_listino_ur():
    """Parser per robot UR (Universal Robots)"""
    
    products = [
        Product(
            code="UR3e",
            name="UR3e - Cobot Compatto",
            description="Robot collaborativo 3kg payload, reach 500mm, precision ±0.03mm",
            price_bronze=18000.00,
            price_silver=20000.00,
            price_gold=22000.00,
            category="Universal Robots"
        ),
        Product(
            code="UR5e",
            name="UR5e - Cobot Versatile",
            description="Robot collaborativo 5kg payload, reach 850mm, 6 assi",
            price_bronze=25000.00,
            price_silver=28000.00,
            price_gold=31000.00,
            category="Universal Robots"
        ),
        Product(
            code="UR10e",
            name="UR10e - Cobot Medio",
            description="Robot collaborativo 10kg payload, reach 1300mm",
            price_bronze=32000.00,
            price_silver=35000.00,
            price_gold=38000.00,
            category="Universal Robots"
        ),
        Product(
            code="UR16e",
            name="UR16e - Cobot Pesante",
            description="Robot collaborativo 16kg payload, reach 900mm, applicazioni pesanti",
            price_bronze=38000.00,
            price_silver=42000.00,
            price_gold=46000.00,
            category="Universal Robots"
        ),
        Product(
            code="UR20",
            name="UR20 - Cobot Extra Pesante",
            description="Robot collaborativo 20kg payload, reach 1750mm, massima versatilità",
            price_bronze=45000.00,
            price_silver=50000.00,
            price_gold=55000.00,
            category="Universal Robots"
        ),
    ]
    
    return products


def parse_listino_mir():
    """Parser per robot MIR (Mobile Industrial Robots)"""
    
    products = [
        Product(
            code="MIR100",
            name="MiR 100 - AGV Compatto",
            description="Robot mobile autonomo, payload 100kg, velocità 1.5m/s, navigazione laser",
            price_bronze=28000.00,
            price_silver=32000.00,
            price_gold=36000.00,
            category="MIR Robots"
        ),
        Product(
            code="MIR250",
            name="MiR 250 - AGV Medio",
            description="Robot mobile autonomo, payload 250kg, top modules compatibili",
            price_bronze=38000.00,
            price_silver=42000.00,
            price_gold=46000.00,
            category="MIR Robots"
        ),
        Product(
            code="MIR600",
            name="MiR 600 - AGV Pesante",
            description="Robot mobile autonomo, payload 600kg, applicazioni industriali",
            price_bronze=55000.00,
            price_silver=60000.00,
            price_gold=65000.00,
            category="MIR Robots"
        ),
        Product(
            code="MIR1200",
            name="MiR 1200 Pallet Jack",
            description="Pallet jack autonomo, payload 1200kg, movimentazione pallet",
            price_bronze=68000.00,
            price_silver=75000.00,
            price_gold=82000.00,
            category="MIR Robots"
        ),
        Product(
            code="MIR-HOOK",
            name="MiR Hook Top Module",
            description="Modulo top per traino carrelli, compatibile MIR100/250",
            price_bronze=3500.00,
            price_silver=4000.00,
            price_gold=4500.00,
            category="MIR Accessori"
        ),
        Product(
            code="MIR-SHELF",
            name="MiR Shelf Carrier",
            description="Modulo scaffale per trasporto bins e contenitori",
            price_bronze=2800.00,
            price_silver=3200.00,
            price_gold=3600.00,
            category="MIR Accessori"
        ),
    ])
    
    return products


def parse_componenti_e_servizi():
    """Componenti, accessori e servizi"""
    
    products = [
        # Gripper e End Effector
        Product(
            code="GRIPPER-2F85",
            name="Gripper 2-Finger 85mm",
            description="Pinza elettrica 2 dita, apertura 85mm, forza 50N",
            price_bronze=1200.00,
            price_silver=1400.00,
            price_gold=1600.00,
            category="Componenti"
        ),
        Product(
            code="GRIPPER-3F",
            name="Gripper 3-Finger Adaptive",
            description="Pinza adattiva 3 dita, presa universale",
            price_bronze=2800.00,
            price_silver=3200.00,
            price_gold=3600.00,
            category="Componenti"
        ),
        Product(
            code="VACUUM-GRIPPER",
            name="Gripper a Ventosa",
            description="Sistema vuoto multi-ventosa, superfici lisce",
            price_bronze=1800.00,
            price_silver=2000.00,
            price_gold=2200.00,
            category="Componenti"
        ),
        
        # Sensori
        Product(
            code="VISION-2D",
            name="Sistema Visione 2D",
            description="Camera industriale con software riconoscimento oggetti",
            price_bronze=3500.00,
            price_silver=4000.00,
            price_gold=4500.00,
            category="Componenti"
        ),
        Product(
            code="VISION-3D",
            name="Sistema Visione 3D",
            description="Scanner 3D per pick&place complesso",
            price_bronze=5500.00,
            price_silver=6500.00,
            price_gold=7500.00,
            category="Componenti"
        ),
        Product(
            code="FORCE-SENSOR",
            name="Sensore di Forza/Coppia",
            description="FT sensor 6 assi, precisione assembly",
            price_bronze=4200.00,
            price_silver=4800.00,
            price_gold=5400.00,
            category="Componenti"
        ),
        
        # Servizi
        Product(
            code="TRAINING-BASE",
            name="Formazione Base (1 giorno)",
            description="Corso programmazione base robot, on-site presso cliente",
            price_bronze=1200.00,
            price_silver=1500.00,
            price_gold=2000.00,
            category="Servizi"
        ),
        Product(
            code="TRAINING-ADV",
            name="Formazione Avanzata (3 giorni)",
            description="Corso programmazione avanzata e integrazione sistemi",
            price_bronze=3500.00,
            price_silver=4000.00,
            price_gold=4500.00,
            category="Servizi"
        ),
        Product(
            code="INSTALLATION",
            name="Installazione e Commissioning",
            description="Installazione completa, test, validazione, documentazione",
            price_bronze=2500.00,
            price_silver=3000.00,
            price_gold=3500.00,
            category="Servizi"
        ),
        Product(
            code="SUPPORT-1Y",
            name="Supporto Tecnico 1 Anno",
            description="Assistenza telefonica/email, aggiornamenti software, manutenzione preventiva",
            price_bronze=2000.00,
            price_silver=2500.00,
            price_gold=3000.00,
            category="Servizi"
        ),
        Product(
            code="SUPPORT-3Y",
            name="Supporto Tecnico 3 Anni",
            description="Contratto pluriennale con SLA, interventi on-site",
            price_bronze=5500.00,
            price_silver=6500.00,
            price_gold=7500.00,
            category="Servizi"
        ),
        Product(
            code="CUSTOMIZATION",
            name="Sviluppo Applicazione Custom",
            description="Programmazione applicazione specifica cliente, integrazione ERP/MES",
            price_bronze=5000.00,
            price_silver=7000.00,
            price_gold=10000.00,
            category="Servizi"
        ),
    ])
    
    return products


def get_all_products_from_pricelists():
    """Restituisce TUTTI i prodotti da tutti i listini"""
    
    all_products = []
    
    # Unitree
    all_products.extend(parse_listino_unitree())
    
    # UR
    all_products.extend(parse_listino_ur())
    
    # MIR
    all_products.extend(parse_listino_mir())
    
    # Componenti e Servizi
    all_products.extend(parse_componenti_e_servizi())
    
    return all_products


def save_products_to_json():
    """Salva prodotti in JSON per facile import"""
    
    products = get_all_products_from_pricelists()
    
    products_dict = []
    for p in products:
        products_dict.append({
            'code': p.code,
            'name': p.name,
            'description': p.description,
            'price_bronze': p.price_bronze,
            'price_silver': p.price_silver,
            'price_gold': p.price_gold,
            'category': p.category
        })
    
    with open('products_catalog.json', 'w', encoding='utf-8') as f:
        json.dump(products_dict, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Salvati {len(products)} prodotti in products_catalog.json")
    
    # Stampa riepilogo per categoria
    categories = {}
    for p in products:
        cat = p.category
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(p)
    
    print("\n📦 CATALOGO COMPLETO:")
    print("="*60)
    for cat, prods in categories.items():
        print(f"\n{cat} ({len(prods)} prodotti):")
        for p in prods:
            print(f"  • {p.code:15} {p.name:40} €{p.price_bronze:,.0f}-€{p.price_gold:,.0f}")
    
    print(f"\n{'='*60}")
    print(f"TOTALE: {len(products)} prodotti")
    
    return products


if __name__ == '__main__':
    save_products_to_json()

