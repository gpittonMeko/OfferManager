#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OfferManager CRM - Sistema Completo con Dashboard
"""
import sys
import os

# Fix encoding Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'meko-offermanager-crm-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///offerte_crm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ==================== MODELLI DATABASE ====================

class User(db.Model):
    """Utente/Commerciale"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    nome = db.Column(db.String(100))
    cognome = db.Column(db.String(100))
    email = db.Column(db.String(100))
    ruolo = db.Column(db.String(20), default='commerciale')  # commerciale, admin
    offerte = db.relationship('Offerta', backref='commerciale', lazy=True)


class Lead(db.Model):
    """Lead/Potenziale cliente"""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    azienda = db.Column(db.String(200))
    email = db.Column(db.String(100))
    telefono = db.Column(db.String(50))
    piva = db.Column(db.String(20))
    indirizzo = db.Column(db.Text)
    
    # Categorizzazione
    settore = db.Column(db.String(100))
    interesse = db.Column(db.String(50))  # MIR, UR, Unitree, Componenti, Servizi
    
    # Status
    stato = db.Column(db.String(20), default='nuovo')  # nuovo, contattato, qualificato, convertito, perso
    priorita = db.Column(db.String(20), default='media')  # bassa, media, alta
    
    # Info
    note = db.Column(db.Text)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_contatto = db.Column(db.DateTime)
    
    # Relazioni
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    offerte = db.relationship('Offerta', backref='lead_ref', lazy=True)


class Offerta(db.Model):
    """Offerta commerciale"""
    id = db.Column(db.Integer, primary_key=True)
    numero_offerta = db.Column(db.String(20), unique=True, nullable=False)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    data_validita = db.Column(db.DateTime)
    
    # Cliente
    cliente_nome = db.Column(db.String(200), nullable=False)
    cliente_piva = db.Column(db.String(20))
    cliente_indirizzo = db.Column(db.Text)
    
    # Categorizzazione
    categoria = db.Column(db.String(50))  # MIR, UR, Unitree, Componenti, Servizi
    sotto_categoria = db.Column(db.String(100))
    
    # Valori
    valore_totale = db.Column(db.Float, nullable=False)
    quantita_prodotti = db.Column(db.Integer, default=1)
    
    # Info
    descrizione = db.Column(db.Text)
    note = db.Column(db.Text)
    
    # Stato
    stato = db.Column(db.String(20), default='draft')  # draft, inviata, accettata, rifiutata, scaduta
    probabilita = db.Column(db.Integer, default=50)  # % probabilità chiusura
    
    # Files
    file_docx = db.Column(db.String(500))
    file_pdf = db.Column(db.String(500))
    
    # Generazione automatica
    richiesta_nlp = db.Column(db.Text)  # Richiesta in linguaggio naturale
    generata_auto = db.Column(db.Boolean, default=False)
    
    # Relazioni
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lead_id = db.Column(db.Integer, db.ForeignKey('lead.id'))


# ==================== ROUTES ====================

@app.route('/')
def index():
    """Home - redirect a login o dashboard"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login commerciali"""
    if request.method == 'POST':
        data = request.json
        
        user = User.query.filter_by(username=data['username']).first()
        
        if user and check_password_hash(user.password, data['password']):
            session['user_id'] = user.id
            session['username'] = user.username
            session['nome'] = user.nome
            return jsonify({'success': True})
        
        return jsonify({'success': False, 'error': 'Credenziali errate'}), 401
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    """Dashboard principale"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', 
                         username=session.get('nome', session.get('username')))


@app.route('/api/stats/personal')
def personal_stats():
    """Statistiche personali commerciale"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non autorizzato'}), 401
    
    user_id = session['user_id']
    
    # Offerte del commerciale
    offerte = Offerta.query.filter_by(user_id=user_id).all()
    
    # Statistiche
    totale_valore = sum(o.valore_totale for o in offerte)
    totale_offerte = len(offerte)
    
    # Per categoria
    per_categoria = {}
    for o in offerte:
        cat = o.categoria or 'Altro'
        if cat not in per_categoria:
            per_categoria[cat] = {'count': 0, 'valore': 0}
        per_categoria[cat]['count'] += 1
        per_categoria[cat]['valore'] += o.valore_totale
    
    # Per stato
    per_stato = {}
    for o in offerte:
        stato = o.stato or 'draft'
        if stato not in per_stato:
            per_stato[stato] = 0
        per_stato[stato] += 1
    
    return jsonify({
        'success': True,
        'totale_valore': totale_valore,
        'totale_offerte': totale_offerte,
        'per_categoria': per_categoria,
        'per_stato': per_stato,
        'offerte_recenti': [{
            'numero': o.numero_offerta,
            'cliente': o.cliente_nome,
            'valore': o.valore_totale,
            'categoria': o.categoria,
            'data': o.data_creazione.strftime('%d/%m/%Y')
        } for o in sorted(offerte, key=lambda x: x.data_creazione, reverse=True)[:10]]
    })


@app.route('/api/stats/team')
def team_stats():
    """Statistiche di team (tutti i commerciali)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non autorizzato'}), 401
    
    # Tutti i commerciali
    commerciali = User.query.filter_by(ruolo='commerciale').all()
    
    stats_commerciali = []
    for comm in commerciali:
        offerte = Offerta.query.filter_by(user_id=comm.id).all()
        
        stats_commerciali.append({
            'nome': f"{comm.nome} {comm.cognome}" if comm.nome else comm.username,
            'offerte_count': len(offerte),
            'valore_totale': sum(o.valore_totale for o in offerte)
        })
    
    # Statistiche globali
    tutte_offerte = Offerta.query.all()
    
    return jsonify({
        'success': True,
        'commerciali': stats_commerciali,
        'totale_globale': sum(o.valore_totale for o in tutte_offerte),
        'offerte_globali': len(tutte_offerte)
    })


@app.route('/api/stats/analytics')
def analytics():
    """Analytics per grafici"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non autorizzato'}), 401
    
    periodo = request.args.get('periodo', 'mese')  # giorno, settimana, mese
    user_id = session['user_id']
    solo_mie = request.args.get('solo_mie', 'true') == 'true'
    
    # Query base
    query = Offerta.query
    if solo_mie:
        query = query.filter_by(user_id=user_id)
    
    offerte = query.all()
    
    # Raggruppa per periodo
    dati_temporali = {}
    
    for o in offerte:
        if periodo == 'mese':
            key = o.data_creazione.strftime('%Y-%m')
            label = o.data_creazione.strftime('%m/%Y')
        elif periodo == 'settimana':
            key = o.data_creazione.strftime('%Y-W%W')
            label = f"Sett. {o.data_creazione.strftime('%W/%Y')}"
        else:  # giorno
            key = o.data_creazione.strftime('%Y-%m-%d')
            label = o.data_creazione.strftime('%d/%m/%Y')
        
        if key not in dati_temporali:
            dati_temporali[key] = {
                'label': label,
                'MIR': 0,
                'UR': 0,
                'Unitree': 0,
                'Componenti': 0,
                'Servizi': 0,
                'totale': 0
            }
        
        cat = o.categoria or 'Altro'
        dati_temporali[key][cat] = dati_temporali[key].get(cat, 0) + o.valore_totale
        dati_temporali[key]['totale'] += o.valore_totale
    
    # Converti in lista ordinata
    timeline = sorted(dati_temporali.items())
    
    return jsonify({
        'success': True,
        'periodo': periodo,
        'dati': [v for k, v in timeline]
    })


@app.route('/api/offerte', methods=['GET', 'POST'])
def offerte():
    """Gestione offerte"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non autorizzato'}), 401
    
    if request.method == 'GET':
        # Lista offerte
        solo_mie = request.args.get('solo_mie', 'true') == 'true'
        
        query = Offerta.query
        if solo_mie:
            query = query.filter_by(user_id=session['user_id'])
        
        offerte = query.order_by(Offerta.data_creazione.desc()).all()
        
        return jsonify({
            'success': True,
            'offerte': [{
                'id': o.id,
                'numero': o.numero_offerta,
                'cliente': o.cliente_nome,
                'categoria': o.categoria,
                'valore': o.valore_totale,
                'quantita': o.quantita_prodotti,
                'stato': o.stato,
                'data': o.data_creazione.strftime('%d/%m/%Y'),
                'note': o.note
            } for o in offerte]
        })
    
    elif request.method == 'POST':
        # Nuova offerta
        data = request.json
        
        # Genera numero offerta
        from offer_numbering import OfferNumbering
        numbering = OfferNumbering()
        numero = numbering.get_next_offer_number()
        
        offerta = Offerta(
            numero_offerta=numero,
            cliente_nome=data['cliente_nome'],
            categoria=data.get('categoria', 'Altro'),
            valore_totale=float(data['valore_totale']),
            quantita_prodotti=int(data.get('quantita', 1)),
            descrizione=data.get('descrizione', ''),
            note=data.get('note', ''),
            stato=data.get('stato', 'draft'),
            probabilita=int(data.get('probabilita', 50)),
            user_id=session['user_id'],
            data_validita=datetime.utcnow() + timedelta(days=30)
        )
        
        db.session.add(offerta)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'offerta_id': offerta.id,
            'numero': offerta.numero_offerta
        })


@app.route('/api/offerte/<int:offerta_id>', methods=['PUT', 'DELETE'])
def gestisci_offerta(offerta_id):
    """Modifica o elimina offerta"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non autorizzato'}), 401
    
    offerta = Offerta.query.get_or_404(offerta_id)
    
    # Verifica permessi
    if offerta.user_id != session['user_id']:
        user = User.query.get(session['user_id'])
        if user.ruolo != 'admin':
            return jsonify({'error': 'Non autorizzato'}), 403
    
    if request.method == 'PUT':
        data = request.json
        
        if 'stato' in data:
            offerta.stato = data['stato']
        if 'probabilita' in data:
            offerta.probabilita = int(data['probabilita'])
        if 'note' in data:
            offerta.note = data['note']
        if 'valore_totale' in data:
            offerta.valore_totale = float(data['valore_totale'])
        
        db.session.commit()
        
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        db.session.delete(offerta)
        db.session.commit()
        
        return jsonify({'success': True})


def init_db():
    """Inizializza database con utenti demo"""
    with app.app_context():
        db.create_all()
        
        # Crea admin se non esiste
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password=generate_password_hash('admin123'),
                nome='Amministratore',
                cognome='Sistema',
                ruolo='admin'
            )
            db.session.add(admin)
        
        # Crea commerciali demo
        commerciali_demo = [
            ('marco', 'Marco', 'Rossi'),
            ('laura', 'Laura', 'Bianchi'),
            ('giuseppe', 'Giuseppe', 'Verdi'),
        ]
        
        for username, nome, cognome in commerciali_demo:
            if not User.query.filter_by(username=username).first():
                user = User(
                    username=username,
                    password=generate_password_hash('demo123'),
                    nome=nome,
                    cognome=cognome,
                    ruolo='commerciale'
                )
                db.session.add(user)
        
        db.session.commit()
        print("✓ Database inizializzato")


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)

