"""
Generatore di offerte con elaborazione linguaggio naturale
"""
from typing import List, Dict, Optional, Tuple
import re
import os
from datetime import datetime
from pdf_parser import PDFPricelistParser, Product
from docx_handler import DOCXHandler
from company_searcher import search_company_cached, CompanySearcher
from offer_numbering import OfferNumbering, convert_docx_to_pdf


class OfferGenerator:
    """Generatore intelligente di offerte"""
    
    def __init__(self, template_path: Optional[str] = None, offers_directory: str = "./offerte_generate"):
        """
        Inizializza il generatore
        
        Args:
            template_path: Percorso al template DOCX (opzionale)
            offers_directory: Directory dove salvare le offerte (default: ./offerte_generate)
        """
        self.parser = PDFPricelistParser()
        self.template_path = template_path
        self.company_searcher = CompanySearcher()
        self.numbering = OfferNumbering(base_directory=offers_directory)
        
        # Configurazione predefinita
        self.default_supplier = {
            'name': 'ME.KO. Srl',
            'address': 'Via Example 123, 00100 Roma (RM)',
            'vat': '12345678901',
            'email': 'info@meko.it',
            'phone': '+39 06 1234567'
        }
    
    def load_pricelists(self, pdf_paths: List[str]):
        """
        Carica i listini PDF
        
        Args:
            pdf_paths: Lista di percorsi ai PDF
        """
        print("\nCaricamento listini...")
        for pdf_path in pdf_paths:
            print(f"  - {pdf_path}")
            products = self.parser.parse(pdf_path)
            print(f"    - {len(products)} prodotti caricati")
        
        total = len(self.parser.get_all_products())
        print(f"\nTotale prodotti disponibili: {total}")
    
    def parse_natural_request(self, request: str) -> Dict:
        """
        Analizza una richiesta in linguaggio naturale
        
        Args:
            request: Richiesta (es. "fammi un'offerta con due unitree g1 u6 prezzo bronze")
            
        Returns:
            Dizionario con parametri estratti
        """
        request_lower = request.lower()
        
        result = {
            'products': [],
            'price_level': 'bronze',
            'company_name': None
        }
        
        # Estrai livello prezzo
        if 'integrator' in request_lower or 'integratore' in request_lower:
            result['price_level'] = 'integrator'
        elif 'partner' in request_lower:
            result['price_level'] = 'partner'
        elif 'distributor' in request_lower or 'distributore' in request_lower:
            result['price_level'] = 'distributor'
        elif 'end user' in request_lower or 'end-user' in request_lower or 'cliente finale' in request_lower:
            result['price_level'] = 'end_user'
        elif 'gold' in request_lower or 'oro' in request_lower:
            result['price_level'] = 'gold'
        elif 'silver' in request_lower or 'argento' in request_lower:
            result['price_level'] = 'silver'
        elif 'bronze' in request_lower or 'bronzo' in request_lower:
            result['price_level'] = 'bronze'
        
        # Estrai prodotti e quantità
        # Pattern per quantità + prodotto
        # Es: "due unitree g1", "3 go2", "un robot b2"
        quantity_patterns = [
            (r'(\d+)\s+([a-z0-9\s]+?)(?:\s+prezzo|\s+con|\s+e\s|\s*$)', lambda m: (int(m.group(1)), m.group(2).strip())),
            (r'(un|uno|una)\s+([a-z0-9\s]+?)(?:\s+prezzo|\s+con|\s+e\s|\s*$)', lambda m: (1, m.group(2).strip())),
            (r'(due)\s+([a-z0-9\s]+?)(?:\s+prezzo|\s+con|\s+e\s|\s*$)', lambda m: (2, m.group(2).strip())),
            (r'(tre)\s+([a-z0-9\s]+?)(?:\s+prezzo|\s+con|\s+e\s|\s*$)', lambda m: (3, m.group(2).strip())),
            (r'(quattro)\s+([a-z0-9\s]+?)(?:\s+prezzo|\s+con|\s+e\s|\s*$)', lambda m: (4, m.group(2).strip())),
            (r'(cinque)\s+([a-z0-9\s]+?)(?:\s+prezzo|\s+con|\s+e\s|\s*$)', lambda m: (5, m.group(2).strip())),
        ]
        
        products_found = {}
        
        for pattern, extractor in quantity_patterns:
            matches = re.finditer(pattern, request_lower)
            for match in matches:
                qty, product_name = extractor(match)
                clean_name = self._clean_product_name(product_name)
                if not clean_name:
                    continue
                key = clean_name.lower()
                if key in products_found:
                    products_found[key]['quantity'] += qty
                else:
                    products_found[key] = {
                        'name': clean_name,
                        'quantity': qty
                    }
        
        result['products'] = list(products_found.values())
        
        # Se non ha trovato pattern espliciti, cerca nomi di prodotti conosciuti
        if not result['products']:
            # Cerca tutti i prodotti nel listino
            all_products = self.parser.get_all_products()
            for product in all_products:
                # Cerca il nome del prodotto nella richiesta
                product_name_clean = product.name.lower()
                product_code_clean = product.code.lower()
                
                if product_name_clean in request_lower or product_code_clean in request_lower:
                    # Cerca una quantità vicino al nome
                    idx = request_lower.find(product_name_clean)
                    if idx == -1:
                        idx = request_lower.find(product_code_clean)
                    
                    # Cerca numero prima del nome
                    before_text = request_lower[:idx]
                    qty_match = re.search(r'(\d+)\s*$', before_text)
                    
                    qty = int(qty_match.group(1)) if qty_match else 1
                    
                    clean_name = self._clean_product_name(product.name)
                    key = clean_name.lower()
                    if key in products_found:
                        products_found[key]['quantity'] += qty
                    else:
                        products_found[key] = {
                            'name': clean_name,
                            'quantity': qty
                        }
            
            if products_found and not result['products']:
                result['products'] = list(products_found.values())
        
        # Rimuovi eventuali match troppo generici (es. "edu") inclusi solo come parte di nomi più lunghi
        if result['products']:
            cleaned_list = []
            product_names_lower = [p['name'].lower() for p in result['products']]
            
            for idx, product in enumerate(result['products']):
                name_lower = product_names_lower[idx]
                tokens_count = len(product['name'].split())
                is_substring = any(
                    idx != other_idx and name_lower in other_name and name_lower != other_name
                    for other_idx, other_name in enumerate(product_names_lower)
                )
                
                if is_substring and tokens_count <= 1 and len(product['name']) <= 3:
                    continue
                
                cleaned_list.append(product)
            
            result['products'] = cleaned_list
        
        return result
    
    def create_offer(self,
                    request: str,
                    company_name: Optional[str] = None,
                    search_company_online: bool = True,
                    validity_days: int = 30) -> Tuple[DOCXHandler, Dict]:
        """
        Crea un'offerta da una richiesta in linguaggio naturale
        
        Args:
            request: Richiesta in linguaggio naturale
            company_name: Nome azienda cliente (opzionale)
            search_company_online: Se cercare info azienda online
            validity_days: Giorni di validità
            
        Returns:
            Tupla (DOCXHandler, dizionario con info offerta)
        """
        print(f"\n[CREATOR] Elaborazione richiesta: '{request}'")
        
        # Analizza la richiesta
        params = self.parse_natural_request(request)
        
        if company_name:
            params['company_name'] = company_name
        
        print(f"\n[CREATOR] Parametri estratti:")
        print(f"  - Livello prezzo: {params['price_level']}")
        print(f"  - Prodotti richiesti: {len(params['products'])}")
        
        # Cerca informazioni cliente
        client_info = None
        if params['company_name'] and search_company_online:
            print(f"\n[CREATOR] Ricerca informazioni per: {params['company_name']}")
            client_info = search_company_cached(params['company_name'])
            if client_info:
                print("  Informazioni trovate")
        
        # Cerca e prepara i prodotti
        products_data = []
        total_amount = 0.0
        
        print(f"\n[CREATOR] Ricerca prodotti nel listino...")
        for item in params['products']:
            product = self._find_product(item['name'])
            
            if product:
                price = product.get_price(params['price_level'])
                
                if price:
                    quantity = item['quantity']
                    total = price * quantity
                    total_amount += total
                    
                    products_data.append({
                        'code': product.code,
                        'name': product.name,
                        'description': product.description,
                        'quantity': quantity,
                        'unit_price': price,
                        'total': total
                    })
                    
                    print(f"  + {product.name} (x{quantity}) - €{price:.2f} cad. = €{total:.2f}")
                else:
                    print(f"  ! Prezzo {params['price_level']} non disponibile per {product.name}")
            else:
                print(f"  x Prodotto non trovato: {item['name']}")
        
        if not products_data:
            print("\n[ERRORE] Nessun prodotto valido trovato!")
            return None, {}
        
        # Genera numero offerta
        offer_number = self._generate_offer_number()
        
        # Crea documento
        print(f"\n[CREATOR] Generazione documento offerta...")
        doc_handler = DOCXHandler(self.template_path)
        
        # Intestazione fornitore
        doc_handler.set_company_header(self.default_supplier)
        
        # Intestazione offerta
        doc_handler.add_offer_header(
            offer_number=offer_number,
            client_name=params['company_name'] or 'Cliente Generico',
            client_info=client_info,
            validity_days=validity_days
        )
        
        # Tabella prodotti
        total = doc_handler.add_products_table(products_data)
        
        # Note
        notes = f"Listino applicato: {params['price_level'].upper()}\n"
        notes += "Consegna prevista: 30-45 giorni dalla conferma d'ordine.\n"
        notes += "I prezzi si intendono IVA esclusa."
        doc_handler.add_notes(notes)
        
        # Termini e condizioni
        doc_handler.add_terms_and_conditions([
            "Pagamento: 50% all'ordine, saldo alla consegna",
            "Garanzia: 12 mesi dalla data di consegna",
            "Trasporto: da quotare separatamente",
            "Formazione: inclusa (1 giornata on-site)",
            "Supporto tecnico: 12 mesi incluso"
        ])
        
        # Sezione firme
        doc_handler.add_signature_section()
        
        print("  Documento generato")
        print(f"\n[CREATOR] Totale offerta: €{total:.2f}")
        
        # Prepara info di ritorno
        offer_info = {
            'offer_number': offer_number,
            'client_name': params['company_name'] or 'Cliente Generico',
            'client_info': client_info,
            'products': products_data,
            'total': total,
            'price_level': params['price_level'],
            'date': datetime.now().strftime('%d/%m/%Y')
        }
        
        return doc_handler, offer_info
    
    def _clean_product_name(self, name: str) -> str:
        """
        Normalizza il nome del prodotto rimuovendo parole non rilevanti
        (es. livelli di prezzo o connettori).
        """
        if not name:
            return ""
        
        stopwords = {
            'prezzo', 'al', 'alla', 'con', 'e', 'ed', 'per', 'di', 'del', 'della',
            'dei', 'degli', 'delle', 'lo', 'la', 'il', 'uno', 'una', 'un'
        }
        price_keywords = {'bronze', 'bronzo', 'silver', 'argento', 'gold', 'oro'}
        
        tokens = re.split(r'\s+', name.strip())
        cleaned_tokens = [
            token for token in tokens
            if token and token.lower() not in stopwords | price_keywords
        ]
        
        return ' '.join(cleaned_tokens).strip()
    
    def _find_product(self, product_name: str) -> Optional[Product]:
        """
        Cerca un prodotto nel listino
        
        Args:
            product_name: Nome o codice prodotto
            
        Returns:
            Prodotto trovato o None
        """
        # Normalizza la query
        product_name_clean = self._clean_product_name(product_name)
        if not product_name_clean:
            return None
        
        # Cerca prima per match esatto
        product = self.parser.find_product(product_name_clean)
        
        if product:
            return product
        
        # Ricerca fuzzy più aggressiva
        product_name_clean = product_name_clean.lower().replace(' ', '')
        
        for product in self.parser.get_all_products():
            name_clean = product.name.lower().replace(' ', '')
            code_clean = product.code.lower().replace(' ', '')
            
            # Match parziale
            if product_name_clean in name_clean or name_clean in product_name_clean:
                return product
            
            if product_name_clean in code_clean or code_clean in product_name_clean:
                return product
        
        return None
    
    def _generate_offer_number(self) -> str:
        """
        Genera un numero di offerta univoco progressivo
        
        Returns:
            Numero offerta (es. K0001-25)
        """
        # Usa il sistema di numerazione progressiva
        return self.numbering.get_next_offer_number()
    
    def set_supplier_info(self, supplier_info: Dict[str, str]):
        """
        Imposta le informazioni del fornitore
        
        Args:
            supplier_info: Dizionario con info fornitore
        """
        self.default_supplier.update(supplier_info)
    
    def get_available_products(self) -> List[Product]:
        """Restituisce tutti i prodotti disponibili"""
        return self.parser.get_all_products()
    
    def save_offer(self, 
                   doc_handler: DOCXHandler, 
                   offer_info: Dict,
                   generate_pdf: bool = True) -> Tuple[str, str]:
        """
        Salva l'offerta in una cartella con DOCX e PDF
        
        Args:
            doc_handler: Handler del documento
            offer_info: Informazioni dell'offerta (da create_offer)
            generate_pdf: Se generare anche il PDF (default: True)
            
        Returns:
            Tupla (percorso_docx, percorso_pdf) o (percorso_docx, None)
        """
        try:
            # Estrai info
            offer_number = offer_info['offer_number']
            client_name = offer_info['client_name']
            
            # Descrizione prodotto (primi prodotti)
            product_desc = ", ".join([p['name'] for p in offer_info['products'][:2]])
            if len(offer_info['products']) > 2:
                product_desc += f" +{len(offer_info['products']) - 2} altri"
            
            # Data
            offer_date = datetime.strptime(offer_info['date'], '%d/%m/%Y')
            
            # Crea cartella
            folder_path = self.numbering.create_offer_folder(
                offer_number=offer_number,
                client_name=client_name,
                product_description=product_desc,
                offer_date=offer_date
            )
            
            # Genera percorsi file
            docx_path, pdf_path = self.numbering.get_offer_file_paths(
                folder_path=folder_path,
                offer_number=offer_number,
                client_name=client_name,
                product_description=product_desc,
                offer_date=offer_date
            )
            
            # Salva DOCX
            if doc_handler.save(docx_path):
                print(f"Documento DOCX salvato: {os.path.basename(docx_path)}")
                
                # Converti in PDF
                if generate_pdf:
                    if convert_docx_to_pdf(docx_path, pdf_path):
                        print(f"Documento PDF generato: {os.path.basename(pdf_path)}")
                        return docx_path, pdf_path
                    else:
                        print("Avviso: PDF non generato (solo DOCX disponibile)")
                        return docx_path, None
                
                return docx_path, None
            else:
                print("Errore nel salvataggio del DOCX")
                return None, None
                
        except Exception as e:
            print(f"Errore nel salvataggio offerta: {e}")
            import traceback
            traceback.print_exc()
            return None, None
    
    def set_offers_directory(self, directory: str):
        """
        Imposta la directory dove salvare le offerte
        
        Args:
            directory: Percorso directory (es: percorso di rete)
        """
        self.numbering.set_base_directory(directory)
        print(f"Directory offerte impostata: {directory}")


def create_offer_interactive():
    """Modalità interattiva per creare un'offerta"""
    print("="*60)
    print("  GENERATORE INTELLIGENTE DI OFFERTE")
    print("="*60)
    
    # Inizializza generatore
    generator = OfferGenerator()
    
    # Carica listini
    print("\nSpecificare i percorsi ai listini PDF (uno per riga, invio vuoto per terminare):")
    pdf_paths = []
    
    # Prova con i file nella directory corrente
    import os
    default_pdfs = [
        "08102025_ListinoUmanoidi_Partner.pdf",
        "08102025_ListinoQuadrupedi_Partner.pdf"
    ]
    
    for pdf in default_pdfs:
        if os.path.exists(pdf):
            pdf_paths.append(pdf)
    
    if pdf_paths:
        print(f"  Trovati listini: {', '.join(pdf_paths)}")
        use_default = input("  Usare questi listini? (S/n): ").strip().lower()
        if use_default == 'n':
            pdf_paths = []
    
    if not pdf_paths:
        while True:
            path = input("  Percorso PDF: ").strip()
            if not path:
                break
            if os.path.exists(path):
                pdf_paths.append(path)
            else:
                print(f"  File non trovato: {path}")
    
    if not pdf_paths:
        print("\n[ERRORE] Nessun listino caricato. Uscita.")
        return
    
    generator.load_pricelists(pdf_paths)
    
    # Richiesta offerta
    print("\n" + "="*60)
    print("  Inserisci la tua richiesta in linguaggio naturale")
    print("  Esempio: 'fammi un'offerta con due unitree g1 prezzo bronze'")
    print("="*60)
    
    request = input("\nRichiesta: ").strip()
    
    if not request:
        print("\n[ERRORE] Nessuna richiesta inserita. Uscita.")
        return
    
    # Cliente
    company_name = input("Nome azienda cliente (opzionale): ").strip()
    
    # Genera offerta
    doc_handler, offer_info = generator.create_offer(
        request=request,
        company_name=company_name if company_name else None,
        search_company_online=True
    )
    
    if not doc_handler:
        print("\n[ERRORE] Impossibile generare l'offerta.")
        return
    
    # Salva
    default_filename = f"offerta_{offer_info['offer_number']}.docx"
    output_path = input(f"\nNome file output (default: {default_filename}): ").strip()
    
    # Salva usando il nuovo sistema
    docx_path, pdf_path = generator.save_offer(doc_handler, offer_info)
    
    if docx_path:
        print(f"\nOfferta salvata con successo!")
        print(f"   DOCX: {docx_path}")
        if pdf_path:
            print(f"   PDF:  {pdf_path}")
        print(f"   Numero offerta: {offer_info['offer_number']}")
        print(f"   Totale: €{offer_info['total']:.2f}")
    else:
        print("\n[ERRORE] Errore nel salvataggio dell'offerta.")


if __name__ == '__main__':
    # Modalità interattiva
    create_offer_interactive()

