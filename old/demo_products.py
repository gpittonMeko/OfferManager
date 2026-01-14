"""
Prodotti demo per testing quando i listini PDF non vengono parsati correttamente
"""
from pdf_parser import Product


def get_demo_products():
    """Restituisce una lista di prodotti demo"""
    
    products = [
        # Unitree Umanoidi
        Product(
            code="G1-U6",
            name="Unitree G1 U6",
            description="Robot umanoide di nuova generazione con 23 DOF, altezza 127cm, peso 35kg",
            price_bronze=16000.00,
            price_silver=18000.00,
            price_gold=20000.00,
            category="Umanoidi"
        ),
        Product(
            code="G1-EDU",
            name="Unitree G1 EDU",
            description="Versione educativa del robot umanoide G1",
            price_bronze=14000.00,
            price_silver=16000.00,
            price_gold=18000.00,
            category="Umanoidi"
        ),
        Product(
            code="H1",
            name="Unitree H1",
            description="Robot umanoide avanzato full-size con capacità di manipolazione",
            price_bronze=90000.00,
            price_silver=95000.00,
            price_gold=100000.00,
            category="Umanoidi"
        ),
        
        # Unitree Quadrupedi
        Product(
            code="GO2-EDU",
            name="Unitree GO2 EDU",
            description="Robot quadrupede educativo, payload 5kg, velocità max 3.5m/s",
            price_bronze=2800.00,
            price_silver=3200.00,
            price_gold=3600.00,
            category="Quadrupedi"
        ),
        Product(
            code="GO2-PRO",
            name="Unitree GO2 Pro",
            description="Robot quadrupede professionale con AI integrata",
            price_bronze=3500.00,
            price_silver=4000.00,
            price_gold=4500.00,
            category="Quadrupedi"
        ),
        Product(
            code="B2",
            name="Unitree B2",
            description="Robot quadrupede industriale, payload 40kg",
            price_bronze=15000.00,
            price_silver=17000.00,
            price_gold=19000.00,
            category="Quadrupedi"
        ),
        Product(
            code="B2-W",
            name="Unitree B2-W",
            description="Robot quadrupede industriale con ruote, payload 120kg",
            price_bronze=18000.00,
            price_silver=20000.00,
            price_gold=22000.00,
            category="Quadrupedi"
        ),
        
        # Accessori
        Product(
            code="SDK-DEV",
            name="SDK Sviluppo",
            description="Kit sviluppo software con documentazione e supporto",
            price_bronze=500.00,
            price_silver=800.00,
            price_gold=1000.00,
            category="Accessori"
        ),
        Product(
            code="TRAINING",
            name="Formazione On-Site",
            description="Giornata di formazione presso sede cliente",
            price_bronze=1200.00,
            price_silver=1500.00,
            price_gold=2000.00,
            category="Servizi"
        ),
        Product(
            code="SUPPORT-1Y",
            name="Supporto Tecnico 1 Anno",
            description="Supporto tecnico esteso per 12 mesi",
            price_bronze=2000.00,
            price_silver=2500.00,
            price_gold=3000.00,
            category="Servizi"
        ),
    ]
    
    return products


def load_demo_products_into_parser(parser):
    """
    Carica i prodotti demo nel parser
    
    Args:
        parser: Istanza di PDFPricelistParser
    """
    demo_products = get_demo_products()
    parser.products.extend(demo_products)
    return len(demo_products)

