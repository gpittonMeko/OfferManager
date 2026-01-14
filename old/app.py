#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OfferManager - Web App per Cloud (AWS EC2)
Versione ottimizzata e leggera
"""
from flask import Flask, render_template, request, jsonify, send_file
import os
from datetime import datetime
from offer_generator import OfferGenerator
from demo_products import load_demo_products_into_parser

app = Flask(__name__)
app.config['SECRET_KEY'] = 'offer-manager-meko-2025'

# Inizializza generatore
generator = OfferGenerator(offers_directory="./offerte_generate")

# Carica prodotti demo
load_demo_products_into_parser(generator.parser)
print(f"✓ {len(generator.get_available_products())} prodotti caricati")


@app.route('/')
def index():
    """Pagina principale"""
    return render_template('app.html')


@app.route('/api/products')
def get_products():
    """Lista prodotti"""
    products = generator.get_available_products()
    return jsonify({
        'success': True,
        'products': [{
            'code': p.code,
            'name': p.name,
            'description': p.description,
            'price_bronze': p.price_bronze,
            'price_silver': p.price_silver,
            'price_gold': p.price_gold,
            'category': p.category
        } for p in products]
    })


@app.route('/api/create-offer', methods=['POST'])
def create_offer():
    """Crea offerta"""
    try:
        data = request.json
        
        doc_handler, offer_info = generator.create_offer(
            request=data.get('request', ''),
            company_name=data.get('company_name'),
            search_company_online=data.get('search_online', False)
        )
        
        if not doc_handler:
            return jsonify({'success': False, 'error': 'Prodotti non trovati'}), 400
        
        # Salva
        docx_path, pdf_path = generator.save_offer(doc_handler, offer_info)
        
        if not docx_path:
            return jsonify({'success': False, 'error': 'Errore salvataggio'}), 500
        
        return jsonify({
            'success': True,
            'offer_number': offer_info['offer_number'],
            'client': offer_info['client_name'],
            'total': offer_info['total'],
            'products_count': len(offer_info['products'])
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/offers')
def list_offers():
    """Lista offerte create"""
    try:
        base_dir = generator.numbering.base_directory
        
        if not os.path.exists(base_dir):
            return jsonify({'success': True, 'offers': []})
        
        folders = sorted([f for f in os.listdir(base_dir) 
                         if os.path.isdir(os.path.join(base_dir, f))], reverse=True)
        
        offers = []
        for folder in folders[:50]:
            parts = folder.split(' - ')
            files = os.listdir(os.path.join(base_dir, folder))
            
            offers.append({
                'folder': folder,
                'number': parts[0] if parts else '',
                'client': parts[1] if len(parts) > 1 else '',
                'product': parts[2] if len(parts) > 2 else '',
                'date': parts[3] if len(parts) > 3 else '',
                'has_pdf': any(f.endswith('.pdf') for f in files)
            })
        
        return jsonify({'success': True, 'offers': offers})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/download/<folder>/<filename>')
def download(folder, filename):
    """Download file"""
    try:
        path = os.path.join(generator.numbering.base_directory, folder, filename)
        if os.path.exists(path):
            return send_file(path, as_attachment=True)
        return "File non trovato", 404
    except Exception as e:
        return str(e), 500


if __name__ == '__main__':
    # Produzione: usa gunicorn
    # Sviluppo: Flask dev server
    app.run(host='0.0.0.0', port=5000, debug=False)

