#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica opportunità create dai contatti del form"""
import sys
import os
sys.path.insert(0, '/home/ubuntu/offermanager')
from crm_app_completo import app, db
from sqlalchemy import text

with app.app_context():
    # Cerca opportunità con contatti che hanno email simili a quelle del form
    # Le email del form sono: miriamdimatera@hotmail.it, geomgv@gmail.co, fabio.cortinovis@ntsmoulding.com, etc.
    
    form_emails = [
        'miriamdimatera@hotmail.it',
        'geomgv@gmail.co',
        'fabio.cortinovis@ntsmoulding.com',
        'massimo.rienzi@innovagroup.it',
        'pspiezia@telsite.it',
        'antoniocapuano@hotmail.com',
        'chiara.tonanni@gmail.com',
        'acquisti@mb-fix.it',
        'ambrogio.valagussa@gmail.com',
        'az.agroforestaleporfidiorosario@gmail.com',
        'fedegotti0037@gmail.com',
        'andrea.piscitelli@3fedin.it',
        'o.pistamiglio@reply.it',
        'ufficiotecnico@omaricelettronica.com',
        'lg.energy@hotmail.com',
        'e.casarin@fimap.com',
        'antoniogiudicecl@gmail.com',
        'james@kingswellinnovation.com',
        'simoneisabella7@libero.it',
        'sr.srl.mo@gmail.com',
        'lorenzo.nannini@powersoft.com',
        'info@mectrotech.com',
        'samuele.colzi@leonardo.com',
        'alice.antoniali@pezzutti.it',
        'info@baseautomation.net',
        'michael.lee@marvtech.cn',
        'Claudio.Arioldi@merlettiaerospace.it',
        'matteo.aimone@libero.it',
        'INFO@CLLSRL.IT',
        'samuel@color-life.it',
        'patrick.sebastiani@autotest.it',
        'debbydebby1970@tiscali.it',
        'bosicalessio@gmail.com',
        'valerio.varone@mcengineering.eu',
        'info@effegimeccanica.it',
        'tozzi49@yahoo.it',
        'mauro.impianti@email.it',
        'christian@badpug.it',
        'livio.dario.brambilla@gmail.com',
        'ernesto.orofino@orofinopharma.com',
        'amministrazione@ballarinsafety.com',
        'federico.lionello@eurovo.com',
        'r.verdi@software-exp.com',
        'TGENGO@LIBERO.IT',
        'info@ibssrl.eu',
        'd.labate@medianet-turi.it',
        'giorgio.culpo@stevanatogroup.com',
        'alberto.borboni@unibs.it',
        'tizianomilqn7@gmail.com',
        's.pavolini@ozaf.it',
        'ferrariv@vignoni.net',
        'ramallavarapu@unibz.it',
        'inkpower2015@gmail.com',
        'gabsimo@proton.me',
        'bciancio@gruppobellucci.it',
        'tozzi49@yahoo.it',
        'tommaso.lisini@unisi.it',
        'francesco.diclemente@konicaminolta.it',
        'valter.amorini@i4m.it',
        'mmoretti@lumson.it',
        'f.spaliviero@wefert.it',
        'dario.ticali@unikore.it',
        'davide.barbati@csthermos.it',
        'ahmed@unigripper.com',
        'gvicini@pozzolispa.com',
        'andrea.loiacono@hmsit.it',
        'nicola@tornerialt.it',
        'ufficioservizi@skpvigilanza.it',
        'l.cavanini@univpm.it',
        'angelika.peer@unibz.it',
        'n.durante@icasystem.it',
        'gherardo.zaltron@unifarco.it',
        'd.rossetto@laserjetgroup.com',
        'lucian.cristea@robonnement.com',
        'pietro.pala@unifi.it',
        'wilmenorlandi@gmail.com'
    ]
    
    # Cerca opportunità con questi contatti
    placeholders = ','.join([':email' + str(i) for i in range(len(form_emails))])
    
    query = f"""
        SELECT o.id, o.name, o.stage, o.created_at, o.account_id, o.contact_id,
               a.name as account_name, c.first_name, c.last_name, c.email
        FROM opportunities o
        LEFT JOIN accounts a ON o.account_id = a.id
        LEFT JOIN contacts c ON o.contact_id = c.id
        WHERE c.email IN ({placeholders})
        ORDER BY o.created_at DESC
    """
    
    params = {f'email{i}': email for i, email in enumerate(form_emails)}
    
    opps = db.session.execute(text(query), params).fetchall()
    
    print(f"📊 Opportunità create da contatti del form:\n")
    
    for opp in opps:
        print(f"⚠️  ID: {opp[0]}")
        print(f"   Nome: {opp[1]}")
        print(f"   Stage: {opp[2]}")
        print(f"   Creata: {opp[3]}")
        print(f"   Account: {opp[6]}")
        print(f"   Contatto: {opp[7]} {opp[8]} ({opp[9]})")
        print()
    
    print(f"\n📈 Totale opportunità da form: {len(opps)}")
    
    if opps:
        print(f"\n💡 ID da eliminare: {[o[0] for o in opps]}")
