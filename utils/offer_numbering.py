"""
Sistema di numerazione progressiva delle offerte
"""
import os
import re
from datetime import datetime
from typing import Optional, Tuple


class OfferNumbering:
    """Gestisce la numerazione progressiva delle offerte"""
    
    def __init__(self, base_directory: str = "./offerte_generate"):
        """
        Inizializza il sistema di numerazione
        
        Args:
            base_directory: Directory base dove salvare le offerte
        """
        self.base_directory = base_directory
        
        # Crea la directory se non esiste
        if not os.path.exists(self.base_directory):
            os.makedirs(self.base_directory)
            print(f"Creata directory: {self.base_directory}")
    
    def get_last_offer_number(self) -> int:
        """
        Trova l'ultimo numero di offerta creato
        
        Returns:
            Ultimo numero di offerta (0 se nessuna offerta esiste)
        """
        try:
            # Lista tutte le cartelle nella directory
            folders = [f for f in os.listdir(self.base_directory) 
                      if os.path.isdir(os.path.join(self.base_directory, f))]
            
            # Pattern per estrarre il numero: K####-YY
            pattern = r'^K(\d{4})-\d{2}'
            
            numbers = []
            for folder in folders:
                match = re.match(pattern, folder)
                if match:
                    numbers.append(int(match.group(1)))
            
            if numbers:
                last_number = max(numbers)
                print(f"Ultima offerta trovata: K{last_number:04d}")
                return last_number
            else:
                print("Nessuna offerta precedente trovata, inizio da K0001")
                return 0
                
        except Exception as e:
            print(f"Errore nella lettura offerte: {e}")
            return 0
    
    def get_next_offer_number(self) -> str:
        """
        Genera il prossimo numero di offerta
        
        Returns:
            Numero offerta formato (es: K0001-25)
        """
        last_number = self.get_last_offer_number()
        next_number = last_number + 1
        year = datetime.now().strftime('%y')
        
        offer_number = f"K{next_number:04d}-{year}"
        print(f"Prossimo numero offerta: {offer_number}")
        
        return offer_number
    
    def create_offer_folder(self, 
                           offer_number: str,
                           client_name: str,
                           product_description: str,
                           offer_date: Optional[datetime] = None) -> str:
        """
        Crea la cartella per l'offerta con il formato corretto
        
        Args:
            offer_number: Numero offerta (es: K0001-25)
            client_name: Nome cliente
            product_description: Descrizione prodotto
            offer_date: Data offerta (default: oggi)
            
        Returns:
            Percorso completo della cartella creata
        """
        if offer_date is None:
            offer_date = datetime.now()
        
        # Formatta la data
        date_str = offer_date.strftime('%d-%m-%Y')
        
        # Pulisci i nomi (rimuovi caratteri non validi per filesystem)
        client_clean = self._clean_filename(client_name)
        product_clean = self._clean_filename(product_description)
        
        # Crea il nome della cartella
        # Formato: K####-YY - CLIENTE - PRODOTTO - DD-MM-YYYY
        folder_name = f"{offer_number} - {client_clean} - {product_clean} - {date_str}"
        
        # Percorso completo
        folder_path = os.path.join(self.base_directory, folder_name)
        
        # Crea la cartella
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Cartella creata: {folder_name}")
        else:
            print(f"Cartella gia esistente: {folder_name}")
        
        return folder_path
    
    def _clean_filename(self, text: str) -> str:
        """
        Pulisce una stringa per usarla in un nome file/cartella
        
        Args:
            text: Testo da pulire
            
        Returns:
            Testo pulito
        """
        # Rimuovi caratteri non validi per Windows/Linux
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        clean_text = text
        
        for char in invalid_chars:
            clean_text = clean_text.replace(char, '')
        
        # Rimuovi spazi multipli
        clean_text = ' '.join(clean_text.split())
        
        # Limita lunghezza
        max_length = 50
        if len(clean_text) > max_length:
            clean_text = clean_text[:max_length].strip()
        
        return clean_text
    
    def get_offer_file_paths(self, 
                            folder_path: str,
                            offer_number: str,
                            client_name: str,
                            product_description: str,
                            offer_date: datetime) -> Tuple[str, str]:
        """
        Genera i percorsi per i file DOCX e PDF
        
        Args:
            folder_path: Percorso cartella
            offer_number: Numero offerta
            client_name: Nome cliente
            product_description: Descrizione prodotto
            offer_date: Data offerta
            
        Returns:
            Tupla (percorso_docx, percorso_pdf)
        """
        date_str = offer_date.strftime('%d-%m-%Y')
        client_clean = self._clean_filename(client_name)
        product_clean = self._clean_filename(product_description)
        
        # Formato: K####-YY - CLIENTE - PRODOTTO - DD-MM-YYYY.ext
        base_filename = f"{offer_number} - {client_clean} - {product_clean} - {date_str}"
        
        docx_path = os.path.join(folder_path, f"{base_filename}.docx")
        pdf_path = os.path.join(folder_path, f"{base_filename}.pdf")
        
        return docx_path, pdf_path
    
    def set_base_directory(self, directory: str):
        """
        Cambia la directory base per le offerte
        
        Args:
            directory: Nuova directory base
        """
        self.base_directory = directory
        
        if not os.path.exists(self.base_directory):
            os.makedirs(self.base_directory)
            print(f"Creata directory: {self.base_directory}")


def convert_docx_to_pdf(docx_path: str, pdf_path: str) -> bool:
    """
    Converte un file DOCX in PDF
    
    Args:
        docx_path: Percorso file DOCX
        pdf_path: Percorso output PDF
        
    Returns:
        True se conversione riuscita
    """
    try:
        # Metodo 1: Usando docx2pdf (Windows/Mac)
        try:
            from docx2pdf import convert
            convert(docx_path, pdf_path)
            print(f"PDF creato: {os.path.basename(pdf_path)}")
            return True
        except ImportError:
            pass
        
        # Metodo 2: Usando LibreOffice (se disponibile)
        import subprocess
        
        # Prova con libreoffice
        libreoffice_commands = [
            'libreoffice',
            'soffice',
            '/usr/bin/libreoffice',
            'C:\\Program Files\\LibreOffice\\program\\soffice.exe'
        ]
        
        for cmd in libreoffice_commands:
            try:
                result = subprocess.run(
                    [cmd, '--headless', '--convert-to', 'pdf', '--outdir', 
                     os.path.dirname(pdf_path), docx_path],
                    capture_output=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print(f"PDF creato con LibreOffice: {os.path.basename(pdf_path)}")
                    return True
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        
        # Metodo 3: Copia il DOCX come placeholder
        print("Conversione PDF non disponibile, salvato solo DOCX")
        print("   Installa: pip install docx2pdf")
        print("   O installa LibreOffice per conversione automatica")
        
        return False
        
    except Exception as e:
        print(f"Errore nella conversione PDF: {e}")
        return False


if __name__ == '__main__':
    # Test del sistema di numerazione
    print("="*60)
    print("TEST SISTEMA NUMERAZIONE OFFERTE")
    print("="*60)
    
    # Inizializza
    numbering = OfferNumbering()
    
    # Trova ultimo numero
    last = numbering.get_last_offer_number()
    
    # Genera prossimo numero
    next_num = numbering.get_next_offer_number()
    
    # Crea cartella di esempio
    folder = numbering.create_offer_folder(
        offer_number=next_num,
        client_name="CLIENTE TEST SRL",
        product_description="ROBOT UR10e E PROGRAMMAZIONE"
    )
    
    print(f"\nCartella creata: {folder}")
    
    # Genera percorsi file
    docx_path, pdf_path = numbering.get_offer_file_paths(
        folder_path=folder,
        offer_number=next_num,
        client_name="CLIENTE TEST SRL",
        product_description="ROBOT UR10e E PROGRAMMAZIONE",
        offer_date=datetime.now()
    )
    
    print(f"\nPercorsi file:")
    print(f"  DOCX: {docx_path}")
    print(f"  PDF:  {pdf_path}")

