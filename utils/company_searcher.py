"""
Modulo per la ricerca online di informazioni aziendali
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import re
import time


class CompanySearcher:
    """Cerca informazioni sulle aziende online"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_company(self, company_name: str) -> Optional[Dict[str, str]]:
        """
        Cerca informazioni su un'azienda
        
        Args:
            company_name: Nome dell'azienda
            
        Returns:
            Dizionario con info azienda o None
        """
        # Prova prima con il Registro Imprese (semplificato)
        info = self._search_google(company_name)
        
        if info:
            return info
        
        # Fallback: restituisci almeno il nome
        return {'name': company_name}
    
    def _search_google(self, company_name: str) -> Optional[Dict[str, str]]:
        """
        Cerca informazioni via Google (metodo semplificato)
        
        Args:
            company_name: Nome azienda
            
        Returns:
            Dizionario con informazioni
        """
        try:
            # Costruisci query di ricerca
            query = f"{company_name} indirizzo partita iva"
            search_url = f"https://www.google.com/search?q={query}"
            
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Estrai informazioni dal risultato
            info = {'name': company_name}
            
            # Cerca snippets di testo che potrebbero contenere info
            snippets = soup.find_all('div', class_='VwiC3b')
            
            for snippet in snippets[:3]:  # Primi 3 risultati
                text = snippet.get_text()
                
                # Cerca partita IVA
                vat_match = re.search(r'P\.?\s*IVA:?\s*(\d{11})', text, re.IGNORECASE)
                if vat_match and 'vat' not in info:
                    info['vat'] = vat_match.group(1)
                
                # Cerca indirizzo (pattern semplice)
                address_patterns = [
                    r'Via\s+[^,\n]+(?:,\s*\d{5}\s*[^,\n]+)?',
                    r'Viale\s+[^,\n]+(?:,\s*\d{5}\s*[^,\n]+)?',
                    r'Piazza\s+[^,\n]+(?:,\s*\d{5}\s*[^,\n]+)?',
                ]
                
                for pattern in address_patterns:
                    address_match = re.search(pattern, text, re.IGNORECASE)
                    if address_match and 'address' not in info:
                        info['address'] = address_match.group(0).strip()
                        break
                
                # Cerca email
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
                if email_match and 'email' not in info:
                    info['email'] = email_match.group(0)
                
                # Cerca telefono
                phone_patterns = [
                    r'\+?\d{2,3}[\s\-]?\d{2,3}[\s\-]?\d{6,8}',
                    r'\d{3}[\s\-]?\d{7}',
                ]
                
                for pattern in phone_patterns:
                    phone_match = re.search(pattern, text)
                    if phone_match and 'phone' not in info:
                        info['phone'] = phone_match.group(0).strip()
                        break
            
            # Se abbiamo trovato almeno qualche info aggiuntiva
            if len(info) > 1:
                return info
            
            return None
            
        except Exception as e:
            print(f"Errore nella ricerca online: {e}")
            return None
    
    def _search_pagine_gialle(self, company_name: str) -> Optional[Dict[str, str]]:
        """
        Cerca su Pagine Gialle (metodo di esempio)
        
        Args:
            company_name: Nome azienda
            
        Returns:
            Dizionario con informazioni
        """
        try:
            # URL di ricerca Pagine Gialle
            search_url = f"https://www.paginegialle.it/ricerca/{company_name.replace(' ', '%20')}"
            
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Estrai informazioni (questo è un esempio semplificato)
            # In realtà ogni sito ha la sua struttura HTML
            info = {'name': company_name}
            
            # Cerca elementi comuni
            address_elem = soup.find('div', class_='address')
            if address_elem:
                info['address'] = address_elem.get_text(strip=True)
            
            phone_elem = soup.find('a', href=re.compile(r'tel:'))
            if phone_elem:
                info['phone'] = phone_elem.get_text(strip=True)
            
            return info if len(info) > 1 else None
            
        except Exception as e:
            print(f"Errore nella ricerca su Pagine Gialle: {e}")
            return None
    
    def search_vat_number(self, company_name: str) -> Optional[str]:
        """
        Cerca solo la partita IVA
        
        Args:
            company_name: Nome azienda
            
        Returns:
            Partita IVA o None
        """
        info = self.search_company(company_name)
        return info.get('vat') if info else None
    
    def validate_vat_number(self, vat: str) -> bool:
        """
        Valida una partita IVA italiana
        
        Args:
            vat: Partita IVA da validare
            
        Returns:
            True se valida
        """
        # Rimuovi spazi e caratteri non numerici
        vat = re.sub(r'\D', '', vat)
        
        # La P.IVA italiana è di 11 cifre
        if len(vat) != 11:
            return False
        
        # Controlla che sia solo numeri
        if not vat.isdigit():
            return False
        
        # Calcolo checksum (algoritmo Luhn modificato)
        odd_sum = sum(int(vat[i]) for i in range(0, 11, 2))
        even_sum = 0
        
        for i in range(1, 10, 2):
            doubled = int(vat[i]) * 2
            even_sum += doubled if doubled < 10 else doubled - 9
        
        total = odd_sum + even_sum
        check_digit = (10 - (total % 10)) % 10
        
        return check_digit == int(vat[10])
    
    def format_company_info(self, info: Dict[str, str]) -> str:
        """
        Formatta le informazioni aziendali in stringa leggibile
        
        Args:
            info: Dizionario con info
            
        Returns:
            Stringa formattata
        """
        lines = []
        
        if 'name' in info:
            lines.append(info['name'])
        
        if 'address' in info:
            lines.append(info['address'])
        
        if 'vat' in info:
            lines.append(f"P.IVA: {info['vat']}")
        
        if 'email' in info:
            lines.append(f"Email: {info['email']}")
        
        if 'phone' in info:
            lines.append(f"Tel: {info['phone']}")
        
        return '\n'.join(lines)
    
    def get_mock_company_info(self, company_name: str) -> Dict[str, str]:
        """
        Restituisce dati mock per testing (quando la ricerca online non è disponibile)
        
        Args:
            company_name: Nome azienda
            
        Returns:
            Dizionario con dati mock
        """
        return {
            'name': company_name,
            'address': 'Via Example 123, 00100 Roma (RM)',
            'vat': '12345678901',
            'email': f"info@{company_name.lower().replace(' ', '').replace('.', '')[:10]}.it",
            'phone': '+39 06 12345678'
        }


class CompanyInfoCache:
    """Cache per le informazioni aziendali cercate"""
    
    def __init__(self):
        self.cache = {}
    
    def get(self, company_name: str) -> Optional[Dict[str, str]]:
        """Recupera info dalla cache"""
        return self.cache.get(company_name.lower())
    
    def set(self, company_name: str, info: Dict[str, str]):
        """Salva info in cache"""
        self.cache[company_name.lower()] = info
    
    def has(self, company_name: str) -> bool:
        """Verifica se è in cache"""
        return company_name.lower() in self.cache
    
    def clear(self):
        """Svuota la cache"""
        self.cache.clear()


# Istanza globale della cache
_global_cache = CompanyInfoCache()


def search_company_cached(company_name: str, use_cache: bool = True) -> Dict[str, str]:
    """
    Cerca informazioni azienda con cache
    
    Args:
        company_name: Nome azienda
        use_cache: Se usare la cache
        
    Returns:
        Dizionario con info
    """
    if use_cache and _global_cache.has(company_name):
        print(f"Info trovate in cache per: {company_name}")
        return _global_cache.get(company_name)
    
    searcher = CompanySearcher()
    info = searcher.search_company(company_name)
    
    if not info:
        # Fallback a dati mock
        info = searcher.get_mock_company_info(company_name)
    
    if use_cache:
        _global_cache.set(company_name, info)
    
    return info


if __name__ == '__main__':
    # Test del searcher
    searcher = CompanySearcher()
    
    # Test con aziende di esempio
    test_companies = [
        'ME.KO. Srl',
        'Microsoft Italia',
        'Google Italy'
    ]
    
    for company in test_companies:
        print(f"\n{'='*50}")
        print(f"Ricerca: {company}")
        print('='*50)
        
        info = search_company_cached(company)
        
        if info:
            print(searcher.format_company_info(info))
        else:
            print("Nessuna informazione trovata")
        
        time.sleep(1)  # Rate limiting

