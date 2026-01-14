#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carica template email predefiniti
"""
import os
from pathlib import Path


def load_email_template(template_name: str) -> str:
    """
    Carica un template email da file
    
    Args:
        template_name: Nome del template (es. 'newsletter_template.html')
    
    Returns:
        Contenuto HTML del template
    """
    template_dir = Path(__file__).parent / 'templates' / 'email'
    template_path = template_dir / template_name
    
    if not template_path.exists():
        raise FileNotFoundError(f"Template non trovato: {template_name}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def get_default_templates() -> dict:
    """Restituisce template email predefiniti"""
    templates = {
        'newsletter': {
            'name': 'Newsletter Base',
            'subject': 'Newsletter ME.KO. - Novità dal Mondo della Robotica',
            'html_content': load_email_template('newsletter_template.html'),
            'category': 'newsletter'
        },
        'promotional': {
            'name': 'Offerta Promozionale',
            'subject': 'Offerta Speciale - ME.KO. Srl',
            'html_content': load_email_template('promotional_template.html'),
            'category': 'promotional'
        },
        'transactional': {
            'name': 'Email Transazionale',
            'subject': 'Conferma - ME.KO. Srl',
            'html_content': load_email_template('transactional_template.html'),
            'category': 'transactional'
        }
    }
    
    return templates


def create_sample_content() -> dict:
    """Crea contenuti di esempio per i template"""
    return {
        'newsletter': '''
            <div style="margin-bottom: 30px;">
                <h2 style="color: #1e293b; font-size: 24px; margin: 0 0 15px 0;">🚀 Nuove Soluzioni Robotica</h2>
                <p style="color: #64748b; font-size: 16px; line-height: 1.6; margin: 0 0 15px 0;">
                    Scopri le ultime novità nel settore della robotica industriale. I nostri nuovi prodotti 
                    sono progettati per migliorare l'efficienza e la produttività della tua azienda.
                </p>
                <ul style="color: #64748b; font-size: 16px; line-height: 1.8; margin: 15px 0; padding-left: 20px;">
                    <li>Robotica Collaborativa (UR, MiR)</li>
                    <li>Robot Umanoidi (Unitree)</li>
                    <li>Soluzioni Personalizzate</li>
                </ul>
            </div>
        ''',
        'promotional': '''
            <div style="margin-bottom: 30px; padding: 25px; background-color: #fef3c7; border-radius: 8px; border-left: 4px solid #f97316;">
                <h2 style="color: #1e293b; font-size: 24px; margin: 0 0 15px 0;">🎉 Offerta Limitata</h2>
                <p style="color: #64748b; font-size: 16px; line-height: 1.6; margin: 0 0 15px 0;">
                    Approfitta della nostra offerta speciale su tutti i prodotti Unitree. 
                    Sconto del 10% su tutti gli ordini effettuati entro il 30 del mese!
                </p>
                <p style="color: #92400e; font-size: 18px; font-weight: 700; margin: 15px 0 0 0;">
                    Valida fino al 30 del mese corrente
                </p>
            </div>
        ''',
        'transactional': '''
            <p style="color: #1e293b; font-size: 16px; line-height: 1.6; margin: 0 0 15px 0;">
                Gentile cliente,
            </p>
            <p style="color: #64748b; font-size: 16px; line-height: 1.6; margin: 0 0 15px 0;">
                La tua richiesta è stata ricevuta con successo. Ti contatteremo a breve.
            </p>
            <p style="color: #64748b; font-size: 16px; line-height: 1.6; margin: 20px 0 0 0;">
                Cordiali saluti,<br>
                <strong>Il Team ME.KO. Srl</strong>
            </p>
        '''
    }









