import pdfplumber

pdf_file = '08102025_ListinoUmanoidi_Partner.pdf'

print(f"Analisi di: {pdf_file}\n")

with pdfplumber.open(pdf_file) as pdf:
    print(f"Totale pagine: {len(pdf.pages)}\n")
    
    for i, page in enumerate(pdf.pages[:2]):  # Prime 2 pagine
        print(f"=== PAGINA {i+1} ===\n")
        
        # Testo
        text = page.extract_text()
        if text:
            print("TESTO (primi 800 caratteri):")
            print(text[:800])
            print()
        
        # Tabelle
        tables = page.extract_tables()
        print(f"Tabelle trovate: {len(tables)}\n")
        
        if tables:
            print("PRIMA TABELLA (prime 5 righe):")
            for row in tables[0][:5]:
                print(row)
            print()
        
        print("-" * 80)
        print()


















