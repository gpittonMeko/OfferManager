#!/usr/bin/env python3
"""Script di test per l'assistente AI"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')

from dotenv import load_dotenv
load_dotenv()

from crm_app_completo import app, db
from sqlalchemy import text

# Test completo della logica query_data
with app.app_context():
    try:
        # Simula un'azione query_data
        action = {
            'type': 'query_data',
            'query_type': 'pipeline_opportunities',
            'limit': 10
        }
        
        query_type = action.get('query_type', '').strip()
        limit = 10
        query_results = []
        
        if query_type == 'pipeline_opportunities':
            query = text('''
                SELECT o.id, o.name, o.amount, o.stage, o.heat_level, o.supplier_category,
                       a.name as account_name, o.created_at
                FROM opportunities o
                LEFT JOIN accounts a ON o.account_id = a.id
                WHERE o.stage NOT IN ('Closed Won', 'Closed Lost')
                ORDER BY COALESCE(o.amount, 0) DESC
                LIMIT :limit
            ''')
            results = db.session.execute(query, {'limit': limit}).fetchall()
            for row in results:
                query_results.append({
                    'id': row[0],
                    'name': row[1],
                    'amount': row[2] or 0,
                    'stage': row[3],
                    'heat_level': row[4],
                    'category': row[5],
                    'account_name': row[6],
                    'created_at': row[7].isoformat() if row[7] and hasattr(row[7], 'isoformat') else (str(row[7]) if row[7] else None)
                })
        
        print(f'✅ Test query_data pipeline_opportunities: {len(query_results)} risultati')
        if query_results:
            for i, opp in enumerate(query_results[:3], 1):
                name = opp['name']
                amount = opp['amount']
                stage = opp['stage']
                print(f'  {i}. {name} - €{amount:,.2f} - {stage}')
        else:
            print('  ⚠️ Nessun risultato')
            
        # Verifica chiave OpenAI
        api_key = os.environ.get('OPENAI_API_KEY') or os.environ.get('OPENAI_KEY')
        if api_key:
            print(f'✅ OPENAI_API_KEY configurata (lunghezza: {len(api_key)})')
        else:
            print('❌ OPENAI_API_KEY NON configurata!')
            
    except Exception as e:
        print(f'❌ ERRORE: {e}')
        import traceback
        traceback.print_exc()
