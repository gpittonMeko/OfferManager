#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OfferManager CRM COMPLETO
- Dashboard commerciali con grafici
- Generatore offerte automatico
- Gestione lead e contatti
- Tutti i listini integrati
"""
import sys
import os
import io

# Fix encoding Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'meko-offermanager-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm_completo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ========== MODELLI ==========

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(200))
    nome = db.Column(db.String(100))
    ruolo = db.Column(db.String(20), default='commerciale')

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200))
    azienda = db.Column(db.String(200))
    email = db.Column(db.String(100))
    telefono = db.Column(db.String(50))
    interesse = db.Column(db.String(50))
    stato = db.Column(db.String(20), default='nuovo')
    priorita = db.Column(db.String(20), default='media')
    note = db.Column(db.Text)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Offerta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), unique=True)
    cliente = db.Column(db.String(200))
    categoria = db.Column(db.String(50))
    valore = db.Column(db.Float)
    quantita = db.Column(db.Integer, default=1)
    descrizione = db.Column(db.Text)
    note = db.Column(db.Text)
    stato = db.Column(db.String(20), default='draft')
    data = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    lead_id = db.Column(db.Integer, db.ForeignKey('lead.id'))


# ========== CATALOGO PRODOTTI ==========
from catalogo_completo import CATALOGO_COMPLETO as CATALOGO


# ========== ROUTES ==========

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        user = User.query.filter_by(username=data['username']).first()
        
        if user and check_password_hash(user.password, data['password']):
            session['user_id'] = user.id
            session['username'] = user.username
            session['nome'] = user.nome
            return jsonify({'success': True})
        
        return jsonify({'success': False}), 401
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard_completa.html', username=session.get('nome'))


# ========== API OFFERTE ==========

@app.route('/api/offerte', methods=['GET', 'POST'])
def offerte():
    if 'user_id' not in session:
        return jsonify({'error': 'Non autorizzato'}), 401
    
    if request.method == 'GET':
        offerte = Offerta.query.filter_by(user_id=session['user_id']).order_by(Offerta.data.desc()).all()
        return jsonify({
            'success': True,
            'offerte': [{
                'id': o.id, 'numero': o.numero, 'cliente': o.cliente,
                'categoria': o.categoria, 'valore': o.valore, 'quantita': o.quantita,
                'stato': o.stato, 'data': o.data.strftime('%d/%m/%Y'),
                'note': o.note or ''
            } for o in offerte]
        })
    
    else:  # POST
        data = request.json
        numero = f"K{Offerta.query.count() + 1:04d}-25"
        
        offerta = Offerta(
            numero=numero,
            cliente=data['cliente_nome'],
            categoria=data.get('categoria', 'Altro'),
            valore=float(data['valore_totale']),
            quantita=int(data.get('quantita', 1)),
            descrizione=data.get('descrizione', ''),
            note=data.get('note', ''),
            stato=data.get('stato', 'draft'),
            user_id=session['user_id']
        )
        
        db.session.add(offerta)
        db.session.commit()
        
        return jsonify({'success': True, 'numero': offerta.numero})


# ========== API GENERATORE OFFERTE ==========

@app.route('/api/genera-offerta', methods=['POST'])
def genera_offerta():
    if 'user_id' not in session:
        return jsonify({'error': 'Non autorizzato'}), 401
    
    try:
        data = request.json
        richiesta = data.get('richiesta', '')
        cliente = data.get('cliente', 'Cliente Generico')
        
        # Importa funzioni generazione
        from genera_offerta_completa import (
            trova_ultima_offerta_k_drive,
            crea_cartella_offerta_k_drive,
            genera_docx_offerta,
            genera_pdf_da_docx
        )
        
        # Parser richiesta
        qty_match = re.search(r'(\d+|un|uno|due|tre|quattro|cinque)', richiesta.lower())
        qty = 1
        if qty_match:
            qty_map = {'un': 1, 'uno': 1, 'due': 2, 'tre': 3, 'quattro': 4, 'cinque': 5}
            qty_str = qty_match.group(1)
            qty = qty_map.get(qty_str, int(qty_str) if qty_str.isdigit() else 1)
        
        # Trova prodotto
        prodotto_trovato = None
        livello = 'bronze'
        
        for code, info in CATALOGO.items():
            if code.lower() in richiesta.lower() or info['nome'].lower() in richiesta.lower():
                prodotto_trovato = (code, info)
                break
        
        if 'silver' in richiesta.lower():
            livello = 'silver'
        elif 'gold' in richiesta.lower():
            livello = 'gold'
        
        if not prodotto_trovato:
            return jsonify({'success': False, 'error': 'Prodotto non trovato'}), 400
        
        code, info = prodotto_trovato
        prezzo = info[livello]
        totale = prezzo * qty
        
        # Genera numero progressivo
        ultimo_k = trova_ultima_offerta_k_drive()
        numero = f"K{ultimo_k + 1:04d}-25"
        
        # Crea cartella in K:\
        prodotto_desc = f"{qty}x {info['nome']}"
        folder_path = crea_cartella_offerta_k_drive(numero, cliente, prodotto_desc)
        
        # Genera DOCX e PDF
        prodotti_lista = [{
            'code': code,
            'nome': info['nome'],
            'quantita': qty,
            'valore': totale
        }]
        
        docx_path = genera_docx_offerta(numero, cliente, prodotti_lista, totale, folder_path)
        pdf_path = genera_pdf_da_docx(docx_path)
        
        # Salva in database
        offerta = Offerta(
            numero=numero,
            cliente=cliente,
            categoria=info['categoria'],
            valore=totale,
            quantita=qty,
            descrizione=f"{qty}x {info['nome']} - {livello.upper()}",
            stato='draft',
            user_id=session['user_id']
        )
        
        db.session.add(offerta)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'numero': numero,
            'prodotto': info['nome'],
            'quantita': qty,
            'prezzo_unitario': prezzo,
            'totale': totale,
            'folder': os.path.basename(folder_path),
            'docx': os.path.basename(docx_path),
            'pdf': os.path.basename(pdf_path) if pdf_path else None
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ========== API LEAD ==========

@app.route('/api/lead', methods=['GET', 'POST'])
def lead():
    if 'user_id' not in session:
        return jsonify({'error': 'Non autorizzato'}), 401
    
    if request.method == 'GET':
        leads = Lead.query.filter_by(user_id=session['user_id']).order_by(Lead.data_creazione.desc()).all()
        return jsonify({
            'success': True,
            'lead': [{
                'id': l.id, 'nome': l.nome, 'azienda': l.azienda,
                'email': l.email, 'telefono': l.telefono,
                'interesse': l.interesse, 'stato': l.stato,
                'priorita': l.priorita, 'note': l.note or ''
            } for l in leads]
        })
    
    else:  # POST
        data = request.json
        lead = Lead(
            nome=data['nome'],
            azienda=data.get('azienda', ''),
            email=data.get('email', ''),
            telefono=data.get('telefono', ''),
            interesse=data.get('interesse', ''),
            stato=data.get('stato', 'nuovo'),
            priorita=data.get('priorita', 'media'),
            note=data.get('note', ''),
            user_id=session['user_id']
        )
        
        db.session.add(lead)
        db.session.commit()
        
        return jsonify({'success': True, 'id': lead.id})


@app.route('/api/lead/<int:lead_id>', methods=['PUT'])
def aggiorna_lead(lead_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Non autorizzato'}), 401
    
    lead = Lead.query.get_or_404(lead_id)
    data = request.json
    
    if 'stato' in data:
        lead.stato = data['stato']
    if 'priorita' in data:
        lead.priorita = data['priorita']
    if 'note' in data:
        lead.note = data['note']
    
    db.session.commit()
    return jsonify({'success': True})


# ========== API STATS ==========

@app.route('/api/stats')
def stats():
    if 'user_id' not in session:
        return jsonify({'error': 'Non autorizzato'}), 401
    
    offerte = Offerta.query.filter_by(user_id=session['user_id']).all()
    leads = Lead.query.filter_by(user_id=session['user_id']).all()
    
    totale_valore = sum(o.valore for o in offerte)
    
    # Per categoria
    per_cat = {}
    for o in offerte:
        cat = o.categoria or 'Altro'
        per_cat[cat] = per_cat.get(cat, 0) + o.valore
    
    # Per stato
    per_stato = {}
    for o in offerte:
        per_stato[o.stato] = per_stato.get(o.stato, 0) + 1
    
    return jsonify({
        'totale_valore': totale_valore,
        'totale_offerte': len(offerte),
        'totale_lead': len(leads),
        'per_categoria': per_cat,
        'per_stato': per_stato,
        'offerte': [{
            'numero': o.numero, 'cliente': o.cliente,
            'categoria': o.categoria, 'valore': o.valore,
            'data': o.data.strftime('%d/%m/%Y')
        } for o in sorted(offerte, key=lambda x: x.data, reverse=True)[:10]]
    })


@app.route('/api/analytics')
def analytics():
    if 'user_id' not in session:
        return jsonify({'error': 'Non autorizzato'}), 401
    
    offerte = Offerta.query.filter_by(user_id=session['user_id']).all()
    
    # Raggruppa per mese
    per_mese = {}
    for o in offerte:
        mese = o.data.strftime('%m/%Y')
        if mese not in per_mese:
            per_mese[mese] = {'MIR': 0, 'UR': 0, 'Unitree': 0, 'Componenti': 0, 'Servizi': 0}
        
        cat = o.categoria or 'Altro'
        per_mese[mese][cat] = per_mese[mese].get(cat, 0) + o.valore
    
    return jsonify({
        'success': True,
        'dati': [{'mese': m, **v} for m, v in sorted(per_mese.items())]
    })


@app.route('/api/catalogo')
def catalogo():
    return jsonify({
        'success': True,
        'prodotti': [{
            'code': k,
            'nome': v['nome'],
            'categoria': v['categoria'],
            'prezzi': {'bronze': v['bronze'], 'silver': v['silver'], 'gold': v['gold']}
        } for k, v in CATALOGO.items()]
    })


def init_db():
    with app.app_context():
        db.create_all()
        
        if not User.query.filter_by(username='admin').first():
            db.session.add(User(username='admin', password=generate_password_hash('admin123'), nome='Admin', ruolo='admin'))
            db.session.add(User(username='marco', password=generate_password_hash('demo123'), nome='Marco Rossi'))
            db.session.add(User(username='laura', password=generate_password_hash('demo123'), nome='Laura Bianchi'))
            db.session.commit()
        
        print("Database OK")


if __name__ == '__main__':
    init_db()
    print("\nServer avviato su: http://localhost:5000")
    print("Login: marco / demo123\n")
    app.run(host='0.0.0.0', port=5000, debug=False)

