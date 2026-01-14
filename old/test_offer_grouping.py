#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test raggruppamento offerte per cartella"""
import os
import sys
import re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sync_offers_from_folder import OFFERS_FOLDER, extract_offer_info

if __name__ == '__main__':
    print("="*60)
    print("TEST RAGGRUPPAMENTO OFFERTE")
    print("="*60)
    
    if not os.path.exists(OFFERS_FOLDER):
        print(f"Cartella non trovata: {OFFERS_FOLDER}")
        sys.exit(1)
    
    # Raccogli file
    offer_extensions = ['.docx', '.pdf', '.doc']
    all_files = []
    for root, dirs, files in os.walk(OFFERS_FOLDER):
        for file in files:
            if any(file.lower().endswith(ext) for ext in offer_extensions):
                all_files.append(os.path.join(root, file))
    
    print(f"\nFile totali: {len(all_files)}")
    
    # Raggruppa
    offer_groups = {}
    for file_path in all_files:
        filename = os.path.basename(file_path)
        dir_path = os.path.dirname(file_path)
        
        offer_info = extract_offer_info(filename)
        offer_number = offer_info.get('offer_number', '')
        
        base_number = None
        if offer_number:
            match = re.search(r'K(\d{4})', offer_number, re.IGNORECASE)
            if match:
                num = int(match.group(1))
                base_number = f"K{num // 10 * 10:04d}"
        
        if not base_number:
            folder_name = os.path.basename(dir_path)
            match = re.search(r'K(\d{4})', folder_name, re.IGNORECASE)
            if match:
                num = int(match.group(1))
                base_number = f"K{num // 10 * 10:04d}"
        
        if not base_number:
            base_number = os.path.basename(dir_path) or 'UNKNOWN'
        
        if base_number not in offer_groups:
            offer_groups[base_number] = []
        
        number_value = 0
        if offer_number:
            match = re.search(r'\d+', offer_number)
            if match:
                number_value = int(match.group())
        
        offer_groups[base_number].append({
            'path': file_path,
            'filename': filename,
            'offer_number': offer_number,
            'number_value': number_value
        })
    
    print(f"\nCartelle base trovate: {len(offer_groups)}")
    
    # Mostra esempi
    count = 0
    for base_folder, files in sorted(offer_groups.items())[:10]:
        files_sorted = sorted(files, key=lambda x: x['number_value'], reverse=True)
        print(f"\n  {base_folder}: {len(files)} offerte")
        print(f"    Ultima: {files_sorted[0]['offer_number']} - {files_sorted[0]['filename']}")
        if len(files_sorted) > 1:
            print(f"    Prima: {files_sorted[-1]['offer_number']}")
        count += 1
    
    # Conta offerte finali
    final_count = sum(1 for files in offer_groups.values() if files)
    print(f"\n\nOfferte finali da processare: {final_count}")




