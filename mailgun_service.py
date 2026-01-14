#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servizio Mailgun per invio email
Usa la stessa configurazione dell'email marketing
"""
import os
import requests
from typing import Dict, List, Optional

class MailgunService:
    def __init__(self):
        self.api_key = os.getenv('MAILGUN_API_KEY')
        self.domain = os.getenv('MAILGUN_DOMAIN')
        self.from_email = os.getenv('MAILGUN_FROM_EMAIL', 'noreply@infomekosrl.it')
        self.from_name = os.getenv('MAILGUN_FROM_NAME', 'ME.KO. Srl')
        self.api_region = os.getenv('MAILGUN_API_REGION', 'eu')
        
        if not self.api_key or not self.domain:
            raise ValueError("MAILGUN_API_KEY e MAILGUN_DOMAIN devono essere configurati")
        
        # URL API Mailgun
        if self.api_region == 'eu':
            self.api_url = f"https://api.eu.mailgun.net/v3/{self.domain}"
        else:
            self.api_url = f"https://api.mailgun.net/v3/{self.domain}"
    
    def send_single_email(self, to_email: str, to_name: str, email_data: Dict) -> Dict:
        """Invia una singola email"""
        try:
            response = requests.post(
                f"{self.api_url}/messages",
                auth=("api", self.api_key),
                data={
                    "from": f"{self.from_name} <{self.from_email}>",
                    "to": f"{to_name} <{to_email}>",
                    "subject": email_data.get('subject', 'Notifica CRM'),
                    "text": email_data.get('text_content', ''),
                    "html": email_data.get('html_content', '')
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message_id': response.json().get('id'),
                    'message': response.json().get('message', 'Email inviata')
                }
            else:
                return {
                    'success': False,
                    'error': f"Errore Mailgun: {response.status_code} - {response.text}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_campaign_email(self, campaign_data: Dict, recipients: List[Dict]) -> Dict:
        """Invia email di campagna a più destinatari"""
        results = []
        sent = 0
        failed = 0
        
        for recipient in recipients:
            result = self.send_single_email(
                to_email=recipient['email'],
                to_name=recipient.get('name', recipient.get('first_name', '')),
                email_data={
                    'subject': campaign_data['subject'],
                    'html_content': campaign_data['html_content'],
                    'text_content': campaign_data.get('text_content', '')
                }
            )
            
            results.append({
                'success': result['success'],
                'recipient': recipient,
                'message_id': result.get('message_id'),
                'error': result.get('error')
            })
            
            if result['success']:
                sent += 1
            else:
                failed += 1
        
        return {
            'total': len(recipients),
            'sent': sent,
            'failed': failed,
            'results': results
        }
