#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup sistema ticket: crea tabelle e utenti operatori
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from crm_app_completo import app, db, User, Ticket, TicketComment
from werkzeug.security import generate_password_hash

def setup_ticket_system():
    with app.app_context():
        # Crea tabelle
        db.create_all()
        print("✅ Tabelle database create/aggiornate")
        
        # Lista operatori autorizzati
        operatori = [
            {'username': 'sandy', 'first_name': 'Sandy', 'last_name': 'Turchetto', 'email': 'sandy@mekosrl.it', 'role': 'commerciale'},
            {'username': 'turchetto', 'first_name': 'Sandy', 'last_name': 'Turchetto', 'email': 'turchetto@mekosrl.it', 'role': 'commerciale'},
            {'username': 'luca', 'first_name': 'Luca', 'last_name': 'Furlan', 'email': 'luca@mekosrl.it', 'role': 'commerciale'},
            {'username': 'furlan', 'first_name': 'Luca', 'last_name': 'Furlan', 'email': 'furlan@mekosrl.it', 'role': 'commerciale'},
            {'username': 'leonardo', 'first_name': 'Leonardo', 'last_name': 'Furlan', 'email': 'leonardo@mekosrl.it', 'role': 'commerciale'},
            {'username': 'giovanni', 'first_name': 'Giovanni', 'last_name': 'Pitton', 'email': 'giovanni@mekosrl.it', 'role': 'commerciale'},
            {'username': 'pitton', 'first_name': 'Giovanni', 'last_name': 'Pitton', 'email': 'pitton@mekosrl.it', 'role': 'commerciale'},
            {'username': 'mattia', 'first_name': 'Mattia', 'last_name': 'Scevola', 'email': 'mattia@mekosrl.it', 'role': 'commerciale'},
            {'username': 'scevola', 'first_name': 'Mattia', 'last_name': 'Scevola', 'email': 'scevola@mekosrl.it', 'role': 'commerciale'},
            {'username': 'filippo', 'first_name': 'Filippo', 'last_name': 'Mariuzzo', 'email': 'filippo@mekosrl.it', 'role': 'commerciale'},
            {'username': 'mariuzzo', 'first_name': 'Filippo', 'last_name': 'Mariuzzo', 'email': 'mariuzzo@mekosrl.it', 'role': 'commerciale'},
        ]
        
        created = 0
        for op_data in operatori:
            existing = User.query.filter_by(username=op_data['username']).first()
            if not existing:
                user = User(
                    username=op_data['username'],
                    password=generate_password_hash(op_data['username'] + '2025'),
                    first_name=op_data['first_name'],
                    last_name=op_data['last_name'],
                    email=op_data['email'],
                    role=op_data['role']
                )
                db.session.add(user)
                created += 1
                print(f"✅ Creato operatore: {op_data['username']} (password: {op_data['username']}2025)")
            else:
                print(f"⚠️  Operatore {op_data['username']} già esistente")
        
        db.session.commit()
        print(f"\n✅ Setup completato! Creati {created} nuovi operatori")

if __name__ == "__main__":
    setup_ticket_system()
