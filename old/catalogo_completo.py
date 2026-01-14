#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Catalogo COMPLETO di tutti i prodotti
Basato su TUTTI i listini: Unitree, UR, MIR, ROEQ, Componenti
"""

# ========== UNITREE UMANOIDI ==========
UNITREE_UMANOIDI = {
    'G1-U6': {
        'nome': 'Unitree G1 U6',
        'descrizione': 'Robot umanoide 23 DOF, h:127cm, 35kg, vel:2m/s',
        'categoria': 'Unitree',
        'bronze': 16000, 'silver': 18000, 'gold': 20000
    },
    'G1-EDU': {
        'nome': 'Unitree G1 EDU',
        'descrizione': 'Versione educativa con SDK completo',
        'categoria': 'Unitree',
        'bronze': 14000, 'silver': 16000, 'gold': 18000
    },
    'H1': {
        'nome': 'Unitree H1 Full-Size',
        'descrizione': 'Umanoide avanzato 175cm, 47kg, AI integrata',
        'categoria': 'Unitree',
        'bronze': 90000, 'silver': 95000, 'gold': 100000
    },
    'H1-W': {
        'nome': 'Unitree H1-W Wheeled',
        'descrizione': 'Versione con ruote per mobilità aumentata',
        'categoria': 'Unitree',
        'bronze': 95000, 'silver': 100000, 'gold': 105000
    },
}

# ========== UNITREE QUADRUPEDI ==========
UNITREE_QUADRUPEDI = {
    'GO2-EDU': {
        'nome': 'Unitree GO2 EDU',
        'descrizione': 'Quadrupede educativo, payload 5kg, vel:3.5m/s',
        'categoria': 'Unitree',
        'bronze': 2800, 'silver': 3200, 'gold': 3600
    },
    'GO2-PRO': {
        'nome': 'Unitree GO2 Pro',
        'descrizione': 'Quadrupede Pro con AI 4TOPS, LiDAR 360°',
        'categoria': 'Unitree',
        'bronze': 3500, 'silver': 4000, 'gold': 4500
    },
    'GO2-W': {
        'nome': 'Unitree GO2-W Wheeled',
        'descrizione': 'Versione ibrida gambe+ruote, payload 8kg',
        'categoria': 'Unitree',
        'bronze': 4200, 'silver': 4800, 'gold': 5400
    },
    'B2': {
        'nome': 'Unitree B2 Industrial',
        'descrizione': 'Quadrupede industriale, payload 40kg, IP67',
        'categoria': 'Unitree',
        'bronze': 15000, 'silver': 17000, 'gold': 19000
    },
    'B2-W': {
        'nome': 'Unitree B2-W Wheeled',
        'descrizione': 'Con ruote, payload 120kg, logistica pesante',
        'categoria': 'Unitree',
        'bronze': 18000, 'silver': 20000, 'gold': 22000
    },
    'A2': {
        'nome': 'Unitree A2',
        'descrizione': 'Quadrupede avanzato ricerca, payload 15kg',
        'categoria': 'Unitree',
        'bronze': 8500, 'silver': 9500, 'gold': 10500
    },
    'A2-W': {
        'nome': 'Unitree A2-W Wheeled',
        'descrizione': 'Versione con ruote per terreni difficili',
        'categoria': 'Unitree',
        'bronze': 10000, 'silver': 11000, 'gold': 12000
    },
    'R1': {
        'nome': 'Unitree R1 Research',
        'descrizione': 'Piattaforma ricerca avanzata',
        'categoria': 'Unitree',
        'bronze': 12000, 'silver': 13500, 'gold': 15000
    },
}

# ========== UNIVERSAL ROBOTS ==========
UNIVERSAL_ROBOTS = {
    'UR3e': {
        'nome': 'UR3e Cobot',
        'descrizione': 'Compatto 3kg payload, reach 500mm, ±0.03mm',
        'categoria': 'UR',
        'bronze': 18000, 'silver': 20000, 'gold': 22000
    },
    'UR5e': {
        'nome': 'UR5e Cobot',
        'descrizione': 'Versatile 5kg payload, reach 850mm, 6 assi',
        'categoria': 'UR',
        'bronze': 25000, 'silver': 28000, 'gold': 31000
    },
    'UR10e': {
        'nome': 'UR10e Cobot',
        'descrizione': 'Medio 10kg payload, reach 1300mm',
        'categoria': 'UR',
        'bronze': 32000, 'silver': 35000, 'gold': 38000
    },
    'UR12e': {
        'nome': 'UR12e Cobot',
        'descrizione': 'Pesante 12.5kg payload, reach 1300mm',
        'categoria': 'UR',
        'bronze': 35000, 'silver': 38000, 'gold': 41000
    },
    'UR16e': {
        'nome': 'UR16e Cobot',
        'descrizione': 'Extra pesante 16kg payload, reach 900mm',
        'categoria': 'UR',
        'bronze': 38000, 'silver': 42000, 'gold': 46000
    },
    'UR20': {
        'nome': 'UR20 Cobot',
        'descrizione': 'Max payload 20kg, reach 1750mm',
        'categoria': 'UR',
        'bronze': 45000, 'silver': 50000, 'gold': 55000
    },
}

# ========== MIR (Mobile Industrial Robots) ==========
MIR_ROBOTS = {
    'MIR100': {
        'nome': 'MiR 100',
        'descrizione': 'AGV compatto, payload 100kg, vel:1.5m/s',
        'categoria': 'MIR',
        'bronze': 28000, 'silver': 32000, 'gold': 36000
    },
    'MIR250': {
        'nome': 'MiR 250',
        'descrizione': 'AGV medio, payload 250kg, top modules',
        'categoria': 'MIR',
        'bronze': 38000, 'silver': 42000, 'gold': 46000
    },
    'MIR600': {
        'nome': 'MiR 600',
        'descrizione': 'AGV pesante, payload 600kg, industriale',
        'categoria': 'MIR',
        'bronze': 55000, 'silver': 60000, 'gold': 65000
    },
    'MIR1200': {
        'nome': 'MiR 1200 Pallet Jack',
        'descrizione': 'Pallet jack autonomo, payload 1200kg',
        'categoria': 'MIR',
        'bronze': 68000, 'silver': 75000, 'gold': 82000
    },
    'MIR-HOOK': {
        'nome': 'MiR Hook Top Module',
        'descrizione': 'Modulo traino carrelli, MIR100/250 compatibile',
        'categoria': 'MIR',
        'bronze': 3500, 'silver': 4000, 'gold': 4500
    },
    'MIR-SHELF': {
        'nome': 'MiR Shelf Carrier',
        'descrizione': 'Modulo scaffale trasporto bins',
        'categoria': 'MIR',
        'bronze': 2800, 'silver': 3200, 'gold': 3600
    },
    'MIR-PALLET': {
        'nome': 'MiR Pallet Lifter',
        'descrizione': 'Sollevatore pallet automatico',
        'categoria': 'MIR',
        'bronze': 5500, 'silver': 6200, 'gold': 6900
    },
}

# ========== ROEQ COMPONENTI ==========
ROEQ_COMPONENTI = {
    'ROEQ-GRIPPER-2F': {
        'nome': 'ROEQ Gripper 2-Finger',
        'descrizione': 'Pinza elettrica 2 dita, apertura 85mm, forza 50N',
        'categoria': 'Componenti',
        'bronze': 1200, 'silver': 1400, 'gold': 1600
    },
    'ROEQ-GRIPPER-3F': {
        'nome': 'ROEQ Gripper 3-Finger',
        'descrizione': 'Pinza adattiva 3 dita, presa universale',
        'categoria': 'Componenti',
        'bronze': 2800, 'silver': 3200, 'gold': 3600
    },
    'ROEQ-VACUUM': {
        'nome': 'ROEQ Vacuum Gripper',
        'descrizione': 'Sistema vuoto multi-ventosa, superfici lisce',
        'categoria': 'Componenti',
        'bronze': 1800, 'silver': 2000, 'gold': 2200
    },
    'ROEQ-VISION-2D': {
        'nome': 'ROEQ Vision 2D',
        'descrizione': 'Camera industriale con riconoscimento oggetti',
        'categoria': 'Componenti',
        'bronze': 3500, 'silver': 4000, 'gold': 4500
    },
    'ROEQ-VISION-3D': {
        'nome': 'ROEQ Vision 3D Scanner',
        'descrizione': 'Scanner 3D per pick&place complesso',
        'categoria': 'Componenti',
        'bronze': 5500, 'silver': 6500, 'gold': 7500
    },
    'ROEQ-FORCE-SENSOR': {
        'nome': 'ROEQ Force/Torque Sensor',
        'descrizione': 'Sensore FT 6 assi, precisione assembly',
        'categoria': 'Componenti',
        'bronze': 4200, 'silver': 4800, 'gold': 5400
    },
}

# ========== SERVIZI ==========
SERVIZI = {
    'TRAINING-BASE': {
        'nome': 'Formazione Base (1 giorno)',
        'descrizione': 'Corso programmazione base, on-site',
        'categoria': 'Servizi',
        'bronze': 1200, 'silver': 1500, 'gold': 2000
    },
    'TRAINING-ADV': {
        'nome': 'Formazione Avanzata (3 giorni)',
        'descrizione': 'Corso avanzato + integrazione sistemi',
        'categoria': 'Servizi',
        'bronze': 3500, 'silver': 4000, 'gold': 4500
    },
    'INSTALLATION': {
        'nome': 'Installazione e Commissioning',
        'descrizione': 'Installazione completa, test, validazione',
        'categoria': 'Servizi',
        'bronze': 2500, 'silver': 3000, 'gold': 3500
    },
    'SUPPORT-1Y': {
        'nome': 'Supporto Tecnico 1 Anno',
        'descrizione': 'Assistenza telefonica, aggiornamenti SW',
        'categoria': 'Servizi',
        'bronze': 2000, 'silver': 2500, 'gold': 3000
    },
    'SUPPORT-3Y': {
        'nome': 'Supporto Tecnico 3 Anni',
        'descrizione': 'Contratto pluriennale con SLA, on-site',
        'categoria': 'Servizi',
        'bronze': 5500, 'silver': 6500, 'gold': 7500
    },
    'CUSTOMIZATION': {
        'nome': 'Sviluppo Custom',
        'descrizione': 'Programmazione specifica, integrazione ERP/MES',
        'categoria': 'Servizi',
        'bronze': 5000, 'silver': 7000, 'gold': 10000
    },
}

# ========== CATALOGO UNIFICATO ==========
CATALOGO_COMPLETO = {}
CATALOGO_COMPLETO.update(UNITREE_UMANOIDI)
CATALOGO_COMPLETO.update(UNITREE_QUADRUPEDI)
CATALOGO_COMPLETO.update(UNIVERSAL_ROBOTS)
CATALOGO_COMPLETO.update(MIR_ROBOTS)
CATALOGO_COMPLETO.update(ROEQ_COMPONENTI)
CATALOGO_COMPLETO.update(SERVIZI)

# Totale prodotti
print(f"Catalogo completo: {len(CATALOGO_COMPLETO)} prodotti")
print(f"  - Unitree: {len(UNITREE_UMANOIDI) + len(UNITREE_QUADRUPEDI)} prodotti")
print(f"  - UR: {len(UNIVERSAL_ROBOTS)} prodotti")
print(f"  - MIR: {len(MIR_ROBOTS)} prodotti")
print(f"  - ROEQ: {len(ROEQ_COMPONENTI)} prodotti")
print(f"  - Servizi: {len(SERVIZI)} prodotti")

