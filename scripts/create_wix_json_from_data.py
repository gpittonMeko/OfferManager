#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crea un file JSON con i dati del form Wix Studio da importare
Questo script può essere modificato per leggere da API Wix o da export CSV
"""
import json
from datetime import datetime

# Dati estratti dal form Wix (esempio - sostituire con dati reali)
WIX_SUBMISSIONS = [
    {
        "name": "Elisa",
        "email": "miriamdimatera@hotmail.it",
        "phone": "+39 339 434 6599",
        "product": "Robot umanoide",
        "message": "Vorrei parlare con qualcuno per avere informazioni sul robot umanoide",
        "created_date": "2026-01-12T12:33:00Z"
    },
    {
        "name": "Mauro",
        "email": "geomgv@gmail.co",
        "phone": "+39 335 707 3211",
        "product": "Unitree G1",
        "message": "Buongiorno, avendo una impresa edile, esiste un robot capace di spostare pesi e muoversi in autonomia nei diversi luoghi dei cantiere cha vanno da terreno a locali intrerni passando dalle scale, ecc.... Grazie Cordiali saluti Mauri",
        "created_date": "2026-01-11T21:56:00Z"
    },
    {
        "name": "Fabio Cortinovis",
        "email": "fabio.cortinovis@ntsmoulding.com",
        "phone": "+39 349 282 8030",
        "product": "G1 EDU e altro",
        "message": "Buongiorno, vi contatto per chiedere informazioni sui robot umanoidi da voi rivenduti ed integrati. La finalità è quella di iniziare ad approcciare e valutare i possibili campi di utilizzo di questa tipologia di robot ed il grado attuale di sicurezza. Se possibile chiedo disponibilità per un incontro presso la nostra sede. Ringrazio fin d'ora per la disponibilità. Cordiali saluti Fabio Cortinovis R&D Manager NTS S.p.A. Via Morletta 10/12 - 24040 Lallio (BG) - ITALY Tel.: +39 035 6969 362 Mob.: +39 349 2828030 Fax: +39 035 6969 400",
        "created_date": "2026-01-08T17:57:00Z"
    },
    {
        "name": "Massimo Rienzi",
        "email": "massimo.rienzi@innovagroup.it",
        "phone": "+39 345 091 8532",
        "product": "Unitree",
        "message": "Buongiorno, sono Massimo Rienzi e sono a contattarvi da Innova Group S.p.A. vorrei approfondire il mondo di Unitree e capire se fosse possibile fare un POC nella nostra azienda. Noi produciamo packaging in cartone ondulato e vorremmo valutare l'utilizzo di robot umanoidi per piegare scatole di grandi formati. Resto in attesa di un gentile riscontro. Cordiali saluti MR",
        "created_date": "2026-01-07T11:09:00Z"
    },
    {
        "name": "Pierluigi Spiezia",
        "email": "pspiezia@telsite.it",
        "phone": "+39 335 150 3773",
        "product": "Unitree Go2",
        "message": "Con questo prodotto è possibile effettuare Pattugliamento dinamico e sorveglianza?",
        "created_date": "2026-01-02T18:05:00Z"
    },
    {
        "name": "Antonio Capuano",
        "email": "antoniocapuano@hotmail.com",
        "phone": "+39 335 699 3912",
        "product": "UNITREE G1-D",
        "message": "Salve, dopo varie ricerche ho deciso di utilizzare i prodotti humanoid di UNITREE. Sono interessato al prodtto G1-D. Ho visto che vendete i prodotti UNITREE ma non questo. Avrei bisogno di un preventivo. Sarebbe possibile essere contattato ? Ringrazio per la disponibilità Cordiali saluti",
        "created_date": "2026-01-02T12:37:00Z"
    },
    {
        "name": "Chiara Tonanni",
        "email": "chiara.tonanni@gmail.com",
        "phone": "+39 329 399 0343",
        "product": "",
        "message": "Gentilissimi, utilizzo questo form per chiedervi se è possibile realizzare un piccolo desiderio di mio figlio Pietro di 8 anni. Lui fin da piccolino è sempre stato appassionato di robot, negli ultimi anni il suo interesse si è particolarmente concentrato in quanto riguarda robotica, automazione, robot umanoidi e quant'altro. Noi abitiamo molto vicini alla vostra ditta e Pietro avrebbe il grande desiderio un giorno di poterla visitare ed eventualmente vedere qualche robot in azione: sarebbe possibile? Vi ringrazio per la cortese attenzione, cordialmente Chiara Tonanni",
        "created_date": "2026-01-01T13:29:00Z"
    },
    {
        "name": "Deborah",
        "email": "acquisti@mb-fix.it",
        "phone": "+39 0423 913803",
        "product": "Robot pallettizzatore o robot caricatore pezzi",
        "message": "Buongiorno, sono Deborah, responsabile acquisti della ditta MB FIX di Borso del Grappa (TV). Vi contatto per chiedervi di potermi contattare al seguente numero: 0423 - 913803 e/o alla seguente mail: acquisti@mb-fix.it perchè sono interessata ad avere un breve colloquio con il vostro rappresentate, presso la nostra sede. Vorremo implementare un nuovo robot nella nostra linea di confezionamento. Quello che stiamo cercando è un robot che possa caricare i nostri prodotti (staffe in lamiera per radiatori) dal cassone alla macchina, oppure un robot che possa pallettizzare. In attesa di un gentile riscontro, porgo cordiali saluti. Deborah",
        "created_date": "2025-12-29T10:52:00Z"
    }
    # Aggiungi altri contatti qui...
]

if __name__ == '__main__':
    output_file = 'wix_submissions.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(WIX_SUBMISSIONS, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Creato file {output_file} con {len(WIX_SUBMISSIONS)} submissions")
    print(f"\n💡 Per importare:")
    print(f"   python3 utils/wix_forms_import.py {output_file}")
