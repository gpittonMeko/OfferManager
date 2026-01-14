#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/ubuntu/offermanager')
from crm_app_completo import app, db, User, Opportunity
with app.app_context():
    filippo_users = User.query.filter(User.username.ilike('%filippo%')).all()
    print(f'Trovati {len(filippo_users)} utenti con username contenente "filippo":')
    for u in filippo_users:
        opps_count = Opportunity.query.filter_by(owner_id=u.id).count()
        print(f'  ID: {u.id}, Username: {u.username}, Nome: {u.first_name} {u.last_name}, Email: {u.email}, Role: {u.role}, Opportunità: {opps_count}')
