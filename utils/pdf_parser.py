"""
Parser per estrarre dati dai listini PDF
"""
import pdfplumber
import re
from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class Product:
    """Rappresenta un prodotto del listino"""
    code: str
    name: str
    description: str
    price_bronze: Optional[float] = None
    price_silver: Optional[float] = None
    price_gold: Optional[float] = None
    category: str = ""
    image_path: Optional[str] = None
    price_levels: Dict[str, float] = field(default_factory=dict)
    
    def get_price(self, level: str) -> Optional[float]:
        """Restituisce il prezzo per il livello specificato"""
        level = level.lower()
        if level in self.price_levels:
            return self.price_levels.get(level)
        if level in ['bronze', 'bronzo']:
            return self.price_bronze
        elif level in ['silver', 'argento']:
            return self.price_silver
        elif level in ['gold', 'oro']:
            return self.price_gold
        return None


class PDFPricelistParser:
    """Parser per listini in formato PDF"""
    
    def __init__(self):
        self.products: List[Product] = []
        
    def parse(self, pdf_path: str) -> List[Product]:
        """
        Estrae i prodotti dal PDF del listino
        
        Args:
            pdf_path: Percorso al file PDF
            
        Returns:
            Lista di prodotti estratti
        """
        products = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    # Estrai testo
                    text = page.extract_text()
                    if text:
                        products.extend(self._parse_text(text))
                    
                    # Estrai tabelle
                    tables = page.extract_tables()
                    for table in tables:
                        products.extend(self._parse_table(table))
                        
        except Exception as e:
            print(f"Errore durante il parsing del PDF {pdf_path}: {e}")
            
        self.products = products
        return products
    
    def _parse_text(self, text: str) -> List[Product]:
        """Estrae prodotti dal testo libero"""
        products = []
        
        # Pattern per riconoscere prodotti
        # Esempio: "Unitree G1 U6" seguito da prezzi
        lines = text.split('\n')
        
        current_product = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Cerca nomi di prodotti comuni
            if any(keyword in line.upper() for keyword in ['UNITREE', 'G1', 'GO2', 'B2', 'H1']):
                # Possibile nome prodotto
                product_name = line
                current_product = {
                    'name': product_name,
                    'description': '',
                    'prices': {}
                }
                
            # Cerca prezzi (formato: €1.234,56 o 1234.56)
            price_matches = re.findall(r'€?\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)', line)
            if price_matches and current_product:
                # Interpreta i prezzi trovati
                for price_str in price_matches:
                    # Normalizza il formato
                    price_str = price_str.replace('.', '').replace(',', '.')
                    try:
                        price = float(price_str)
                        current_product['prices'][len(current_product['prices'])] = price
                    except ValueError:
                        pass
                        
        return products
    
    def _parse_table(self, table: List[List]) -> List[Product]:
        """Estrae prodotti da una tabella"""
        products = []
        
        if not table or len(table) < 2:
            return products
            
        # La prima riga di solito contiene gli header
        headers = [str(cell).strip().upper() if cell else '' for cell in table[0]]
        
        # Trova gli indici delle colonne
        name_col = self._find_column(headers, ['PRODOTTO', 'NOME', 'NAME', 'ARTICOLO'])
        desc_col = self._find_column(headers, ['DESCRIZIONE', 'DESCRIPTION', 'DESC'])
        bronze_col = self._find_column(headers, ['BRONZE', 'BRONZO', 'PREZZO BRONZE'])
        silver_col = self._find_column(headers, ['SILVER', 'ARGENTO', 'PREZZO SILVER'])
        gold_col = self._find_column(headers, ['GOLD', 'ORO', 'PREZZO GOLD'])
        
        # Processa le righe dati
        for row in table[1:]:
            if not row or all(cell is None or str(cell).strip() == '' for cell in row):
                continue
                
            try:
                product = Product(
                    code=self._extract_code(row, name_col),
                    name=self._safe_get(row, name_col, ''),
                    description=self._safe_get(row, desc_col, ''),
                    price_bronze=self._parse_price(self._safe_get(row, bronze_col)),
                    price_silver=self._parse_price(self._safe_get(row, silver_col)),
                    price_gold=self._parse_price(self._safe_get(row, gold_col))
                )
                
                if product.name:  # Solo se ha un nome
                    products.append(product)
                    
            except Exception as e:
                print(f"Errore parsing riga: {e}")
                continue
                
        return products
    
    def _find_column(self, headers: List[str], keywords: List[str]) -> Optional[int]:
        """Trova l'indice della colonna che contiene una delle keywords"""
        for i, header in enumerate(headers):
            if any(keyword in header for keyword in keywords):
                return i
        return None
    
    def _safe_get(self, row: List, index: Optional[int], default='') -> str:
        """Estrae un valore dalla riga in modo sicuro"""
        if index is None or index >= len(row):
            return default
        value = row[index]
        return str(value).strip() if value is not None else default
    
    def _extract_code(self, row: List, name_index: Optional[int]) -> str:
        """Estrae un codice prodotto dal nome"""
        name = self._safe_get(row, name_index, '')
        # Cerca pattern come "G1", "GO2", "B2-W", etc.
        match = re.search(r'([A-Z]\d+[A-Z]?[-\w]*)', name.upper())
        return match.group(1) if match else name[:10].upper().replace(' ', '_')
    
    def _parse_price(self, price_str: str) -> Optional[float]:
        """Converte una stringa di prezzo in float"""
        if not price_str or price_str == '':
            return None
            
        # Rimuovi simboli di valuta e spazi
        price_str = price_str.replace('€', '').replace('$', '').strip()
        
        # Gestisci formati europei (1.234,56) e americani (1,234.56)
        if ',' in price_str and '.' in price_str:
            # Determina quale è il separatore decimale
            if price_str.rindex(',') > price_str.rindex('.'):
                # Formato europeo
                price_str = price_str.replace('.', '').replace(',', '.')
            else:
                # Formato americano
                price_str = price_str.replace(',', '')
        elif ',' in price_str:
            # Solo virgola - assumo formato europeo se ci sono 2 cifre dopo
            parts = price_str.split(',')
            if len(parts) == 2 and len(parts[1]) == 2:
                price_str = price_str.replace(',', '.')
            else:
                price_str = price_str.replace(',', '')
        
        try:
            return float(price_str)
        except ValueError:
            return None
    
    def find_product(self, query: str) -> Optional[Product]:
        """
        Cerca un prodotto per nome o codice
        
        Args:
            query: Stringa di ricerca (es. "unitree g1 u6")
            
        Returns:
            Prodotto trovato o None
        """
        query = query.lower()
        
        for product in self.products:
            if query in product.name.lower() or query in product.code.lower():
                return product
                
        # Ricerca fuzzy
        for product in self.products:
            # Rimuovi spazi e confronta
            query_clean = query.replace(' ', '')
            name_clean = product.name.lower().replace(' ', '')
            if query_clean in name_clean:
                return product
                
        return None
    
    def search_products(self, query: str) -> List[Product]:
        """
        Cerca tutti i prodotti che matchano la query
        
        Args:
            query: Stringa di ricerca
            
        Returns:
            Lista di prodotti trovati
        """
        query = query.lower()
        results = []
        
        for product in self.products:
            if (query in product.name.lower() or 
                query in product.code.lower() or
                query in product.description.lower()):
                results.append(product)
                
        return results
    
    def get_all_products(self) -> List[Product]:
        """Restituisce tutti i prodotti caricati"""
        return self.products


if __name__ == '__main__':
    # Test del parser
    parser = PDFPricelistParser()
    
    # Test con i file forniti
    import os
    
    pdf_files = [
        "08102025_ListinoUmanoidi_Partner.pdf",
        "08102025_ListinoQuadrupedi_Partner.pdf"
    ]
    
    for pdf_file in pdf_files:
        if os.path.exists(pdf_file):
            print(f"\n{'='*50}")
            print(f"Parsing: {pdf_file}")
            print('='*50)
            products = parser.parse(pdf_file)
            print(f"Trovati {len(products)} prodotti")
            
            for product in products[:5]:  # Mostra i primi 5
                print(f"\n{product.name}")
                print(f"  Codice: {product.code}")
                if product.price_bronze:
                    print(f"  Bronze: €{product.price_bronze:.2f}")
                if product.price_silver:
                    print(f"  Silver: €{product.price_silver:.2f}")
                if product.price_gold:
                    print(f"  Gold: €{product.price_gold:.2f}")

