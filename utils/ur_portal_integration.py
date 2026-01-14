#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integrazione con portale UR per sincronizzazione leads/opportunities/accounts
"""
import sys
import re
import logging
from pathlib import Path
from datetime import datetime

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [UR Integration] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ur_portal_sync.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Prova a importare da progetto UR esistente
# Cerca in varie posizioni possibili
UR_PROJECT_DIR = None
possible_paths = [
    Path(__file__).resolve().parent.parent / "UR Twenty integration",
    Path(__file__).resolve().parent / "UR Twenty integration",
    Path("/home/ubuntu/UR Twenty integration"),
    Path("/opt/UR Twenty integration"),
]
for path in possible_paths:
    if path.exists():
        UR_PROJECT_DIR = path
        break


def sync_ur_portal(db_session, user_id: int = 1):
    """
    Sincronizza dati dal portale UR
    
    Args:
        db_session: SQLAlchemy session
        user_id: ID utente proprietario
    
    Returns:
        dict con statistiche sincronizzazione
    """
    from crm_app_completo import Lead, Account, Contact, Opportunity
    
    logger.info("=" * 60)
    logger.info("🔄 INIZIO SINCRONIZZAZIONE UR PORTAL")
    logger.info("=" * 60)
    logger.info(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"👤 User ID: {user_id}")
    
    stats = {
        'leads_imported': 0,
        'leads_updated': 0,
        'opportunities_imported': 0,
        'opportunities_updated': 0,
        'accounts_created': 0,
        'errors': []
    }
    
    try:
        opportunities_data = []
        leads_data = []
        
        # Prova prima integrazione diretta con Playwright
        logger.info("🔍 Tentativo integrazione diretta con Playwright...")
        try:
            from ur_portal_direct_playwright import fetch_ur_data_direct
            logger.info("✓ Modulo ur_portal_direct_playwright importato")
            logger.info("📥 Chiamata fetch_ur_data_direct()...")
            try:
                result = fetch_ur_data_direct()
                logger.info(f"✓ Risultato ricevuto, tipo: {type(result)}")
                if isinstance(result, dict):
                    opportunities_data = result.get('opportunities', [])
                    leads_data = result.get('leads', [])
                    logger.info(f"✓ Dati estratti da dict: {len(opportunities_data)} opportunità, {len(leads_data)} leads")
                elif isinstance(result, (list, tuple)) and len(result) == 2:
                    opportunities_data, leads_data = result
                    logger.info(f"✓ Dati estratti da tupla: {len(opportunities_data)} opportunità, {len(leads_data)} leads")
                else:
                    logger.error(f"❌ Tipo risultato non supportato: {type(result)}, valore: {result}")
                    opportunities_data = []
                    leads_data = []
                logger.info(f"✓ Dati finali: {len(opportunities_data)} opportunità, {len(leads_data)} leads")
                logger.info(f"🔍 DEBUG: opportunities_data tipo={type(opportunities_data)}, len={len(opportunities_data) if opportunities_data else 0}")
                logger.info(f"🔍 DEBUG: leads_data tipo={type(leads_data)}, len={len(leads_data) if leads_data else 0}")
                
                # Scarica HTML nella cartella Download
                logger.info("📥 Download HTML pagine nella cartella Download...")
                try:
                    from download_ur_htmls import download_html_files
                    download_html_files()
                    logger.info("✓ HTML scaricati nella cartella Download")
                except Exception as download_error:
                    logger.warning(f"⚠ Errore download HTML: {download_error}")
                    logger.info("💡 Esegui manualmente: python download_ur_htmls.py")
                
                # IMPORTANTE: Se abbiamo dati, NON entrare nel fallback!
                logger.info(f"✅ Fetch completato con successo: {len(opportunities_data)} opportunità, {len(leads_data)} leads")
            except Exception as fetch_error:
                error_msg = f"Errore durante fetch dati UR: {fetch_error}"
                logger.error(f"❌ {error_msg}")
                logger.error(f"   Tipo errore: {type(fetch_error).__name__}")
                import traceback
                logger.error(f"   Traceback completo: {traceback.format_exc()}")
                # Continua con liste vuote invece di fallire completamente
                opportunities_data = []
                leads_data = []
                stats['errors'].append(error_msg)
                logger.warning("⚠ Continuo con dati vuoti, verranno importati solo dati già presenti")
        except ImportError as e:
            logger.warning(f"⚠ ImportError Playwright: {e}, provo Selenium...")
            # Fallback a Selenium
            try:
                from ur_portal_direct import fetch_ur_data_direct
                logger.info("✓ Modulo ur_portal_direct (Selenium) importato")
                logger.info("📥 Chiamata fetch_ur_data_direct()...")
                try:
                    opportunities_data, leads_data = fetch_ur_data_direct()
                    logger.info(f"✓ Dati ricevuti: {len(opportunities_data)} opportunità, {len(leads_data)} leads")
                except Exception as fetch_error:
                    error_msg = f"Errore durante fetch dati UR: {fetch_error}"
                    logger.error(f"❌ {error_msg}")
                    logger.error(f"   Tipo errore: {type(fetch_error).__name__}")
                    import traceback
                    logger.debug(f"   Traceback: {traceback.format_exc()}")
                    opportunities_data = []
                    leads_data = []
                    stats['errors'].append(error_msg)
                    logger.warning("⚠ Continuo con dati vuoti")
            except ImportError as e2:
                logger.warning(f"⚠ ImportError Selenium: {e2}")
        
        # Fallback: prova progetto UR esistente se entrambi i metodi falliscono
        logger.info(f"🔍 DEBUG PRIMA FALLBACK: opportunities_data={len(opportunities_data) if opportunities_data else 0}, leads_data={len(leads_data) if leads_data else 0}")
        if not opportunities_data and not leads_data:
            logger.warning(f"⚠ Nessun dato ottenuto, provo progetto UR esistente...")
            logger.info("🔄 Fallback: ricerca progetto UR esistente...")
            if UR_PROJECT_DIR and UR_PROJECT_DIR.exists():
                logger.info(f"✓ Trovato progetto UR in: {UR_PROJECT_DIR}")
                sys.path.insert(0, str(UR_PROJECT_DIR))
                try:
                    from ur_sync import fetch_ur_data
                    logger.info("✓ Modulo ur_sync importato")
                    opportunities_data, leads_data = fetch_ur_data()
                    logger.info(f"✓ Dati ricevuti: {len(opportunities_data)} opportunità, {len(leads_data)} leads")
                except ImportError as e:
                    error_msg = f"Impossibile importare moduli UR: {e}"
                    logger.error(f"❌ {error_msg}")
                    stats['errors'].append(error_msg)
                    return stats
                finally:
                    try:
                        sys.path.remove(str(UR_PROJECT_DIR))
                    except ValueError:
                        pass
            else:
                error_msg = "Directory progetto UR non trovata e integrazione diretta non disponibile"
                logger.error(f"❌ {error_msg}")
                logger.error(f"🔍 DEBUG: opportunities_data={opportunities_data}, leads_data={leads_data}")
                stats['errors'].append(error_msg)
                # NON fare return qui! Continua con l'importazione anche se i dati sono vuoti
                logger.warning("⚠ Continuo comunque con l'importazione (potrebbero esserci dati già estratti)")
        
    except Exception as e:
        # Se c'è un errore nel blocco try principale, gestiscilo ma NON fermare l'importazione
        error_msg = f"Errore integrazione UR diretta: {e}"
        logger.error(f"❌ {error_msg}")
        logger.error(f"   Tipo errore: {type(e).__name__}")
        import traceback
        logger.error(f"   Traceback completo: {traceback.format_exc()}")
        stats['errors'].append(error_msg)
        # IMPORTANTE: Se abbiamo già dati, NON resettarli!
        logger.info(f"🔍 DEBUG EXCEPTION: opportunities_data={len(opportunities_data) if opportunities_data else 0}, leads_data={len(leads_data) if leads_data else 0}")
        # Prova progetto esistente come fallback SOLO se non abbiamo dati
        if not opportunities_data and not leads_data:
            logger.info("🔄 Tentativo fallback con progetto UR esistente...")
            if UR_PROJECT_DIR and UR_PROJECT_DIR.exists():
                try:
                    sys.path.insert(0, str(UR_PROJECT_DIR))
                    from ur_sync import fetch_ur_data
                    logger.info("✓ Modulo ur_sync importato (fallback)")
                    try:
                        opportunities_data, leads_data = fetch_ur_data()
                        logger.info(f"✓ Dati ricevuti: {len(opportunities_data)} opportunità, {len(leads_data)} leads")
                    except Exception as fetch_error2:
                        error_msg2 = f"Errore durante fetch dati UR (fallback): {fetch_error2}"
                        logger.error(f"❌ {error_msg2}")
                        opportunities_data = []
                        leads_data = []
                        stats['errors'].append(error_msg2)
                except Exception as e2:
                    error_msg2 = f"Errore anche con progetto UR: {e2}"
                    logger.error(f"❌ {error_msg2}")
                    stats['errors'].append(error_msg2)
                    opportunities_data = []
                    leads_data = []
                finally:
                    try:
                        sys.path.remove(str(UR_PROJECT_DIR))
                    except ValueError:
                        pass
            else:
                if not opportunities_data and not leads_data:
                    opportunities_data = []
                    leads_data = []
                    logger.warning("⚠ Nessun fallback disponibile, continuo con dati vuoti")
                else:
                    logger.info(f"✅ Ho già dati estratti: {len(opportunities_data)} opportunità, {len(leads_data)} leads - continuo con questi")
    
    # IMPORTANTE: L'importazione deve essere FUORI dal blocco try/except per essere sempre eseguita
    # Anche se c'è stato un errore nel fetch, proviamo comunque ad importare i dati che abbiamo
    logger.info(f"🔍 DEBUG PRIMA IMPORT: opportunities_data={len(opportunities_data) if opportunities_data else 0}, leads_data={len(leads_data) if leads_data else 0}")
    
    # Importa Leads
    logger.info("=" * 60)
    logger.info("💾 SALVATAGGIO LEADS NEL DATABASE")
    logger.info("=" * 60)
    logger.info(f"🔍 Verifica leads_data: tipo={type(leads_data)}, lunghezza={len(leads_data) if leads_data else 0}")
    if leads_data and len(leads_data) > 0:
            logger.info(f"📋 Elaborazione {len(leads_data)} leads...")
            logger.info(f"   Primo lead esempio: {leads_data[0] if leads_data else 'N/A'}")
            for idx, lead_data in enumerate(leads_data, 1):
                try:
                    if not lead_data or not isinstance(lead_data, dict):
                        logger.warning(f"  ⚠ Lead {idx} dati non validi, saltato")
                        continue
                    
                    # Estrai nome completo (può essere "Nome Cognome" o solo nome)
                    full_name = lead_data.get('name', '').strip()
                    if not full_name:
                        logger.warning(f"  ⚠ Lead {idx} senza nome, saltato")
                        continue
                    
                    # Dividi nome e cognome se possibile
                    name_parts = full_name.split(maxsplit=1)
                    first_name = name_parts[0] if len(name_parts) > 0 else ''
                    last_name = name_parts[1] if len(name_parts) > 1 else ''
                    
                    # Usa company se disponibile, altrimenti usa partner o email domain
                    company_name = lead_data.get('company', '').strip() or lead_data.get('partner', '').strip()
                    
                    # Pulisci company_name da testi di sistema
                    if company_name:
                        # Rimuovi pattern comuni di sistema
                        company_name = re.sub(r'\s*Locked Partner:?\s*Item\s*', '', company_name, flags=re.IGNORECASE)
                        company_name = re.sub(r'\s*Locked Account.*?:?\s*Item\s*', '', company_name, flags=re.IGNORECASE)
                        company_name = re.sub(r'\s*Edit\s+.*?:?\s*Item\s*', '', company_name, flags=re.IGNORECASE)
                        company_name = re.sub(r'\s*SQL\s+Edit\s+.*?:?\s*Item\s*', '', company_name, flags=re.IGNORECASE)
                        company_name = re.sub(r'\s*Locked\s+.*?:?\s*Item\s*', '', company_name, flags=re.IGNORECASE)
                        # Rimuovi anche "Item null" o "Item Treviso" alla fine
                        company_name = re.sub(r'\s+Item\s+.*$', '', company_name, flags=re.IGNORECASE)
                        company_name = company_name.strip()
                    
                    if not company_name:
                        # Prova a estrarre dominio dall'email
                        email = lead_data.get('email', '').strip()
                        if email and '@' in email:
                            domain = email.split('@')[1]
                            # Rimuovi estensioni comuni
                            domain_parts = domain.split('.')
                            company_name = domain_parts[0].capitalize() if domain_parts else 'Unknown Company'
                        else:
                            company_name = last_name or first_name or 'Unknown Company'
                    
                    # Skip leads con nomi chiaramente di sistema/test
                    bad_patterns = ['Locked Partner', 'Edit Lead Status', 'SQL Edit', 'Test Company', 'Locked Account', 'Item null', 'Item Item']
                    if any(bad in company_name for bad in bad_patterns) or company_name.lower() in ['item', 'null', 'locked']:
                        logger.warning(f"  ⚠ Lead {idx} saltato: company_name contiene testo di sistema: {company_name}")
                        continue
                    
                    # Skip se company_name è troppo corto o sembra un errore
                    if len(company_name) < 3:
                        logger.warning(f"  ⚠ Lead {idx} saltato: company_name troppo corto: {company_name}")
                        continue
                    
                    email = lead_data.get('email', '').strip() or ''
                    phone = lead_data.get('phone', '').strip() or ''
                    
                    logger.info(f"  📝 Lead {idx}/{len(leads_data)}: {full_name} - {company_name}")
                    logger.info(f"    📧 Email: {email}, 📞 Phone: {phone}")
                    
                    # Crea o aggiorna Lead (usa email come identificatore univoco se disponibile)
                    if email:
                        existing_lead = Lead.query.filter_by(email=email).first()
                    else:
                        existing_lead = Lead.query.filter_by(
                            company_name=company_name,
                            contact_first_name=first_name,
                            contact_last_name=last_name
                        ).first()
                    
                    # Estrai e normalizza lo status
                    raw_status = lead_data.get('lead_status', '').strip()
                    # Se lo status è vuoto o contiene solo spazi, usa 'New'
                    if not raw_status:
                        normalized_status = 'New'
                    else:
                        # Mantieni lo status così com'è (SQL, MQL, ecc.) - NON convertire in "Converted"
                        normalized_status = raw_status
                    
                    if not existing_lead:
                        lead = Lead(
                            company_name=company_name,
                            contact_first_name=first_name,
                            contact_last_name=last_name,
                            email=email,
                            phone=phone,
                            interest='UR',
                            source='UR Portal',
                            status=normalized_status,
                            rating='Warm',
                            owner_id=user_id
                        )
                        db_session.add(lead)
                        stats['leads_imported'] += 1
                        logger.info(f"    ✓ Lead creato: {full_name} ({company_name}) - Status: {normalized_status}")
                    else:
                        # Aggiorna lead esistente con nuovi dati
                        if first_name:
                            existing_lead.contact_first_name = first_name
                        if last_name:
                            existing_lead.contact_last_name = last_name
                        if email:
                            existing_lead.email = email
                        if phone:
                            existing_lead.phone = phone
                        if company_name:
                            existing_lead.company_name = company_name
                        # Aggiorna sempre lo status dal portale UR
                        existing_lead.status = normalized_status
                        existing_lead.source = 'UR Portal'
                        stats['leads_updated'] += 1
                        logger.info(f"    ✓ Lead aggiornato: {company_name} - Status: {normalized_status}")
                except Exception as e:
                    error_msg = f"Errore salvataggio lead {idx}: {e}"
                    logger.error(f"    ❌ {error_msg}")
                    logger.exception(e)
                    stats['errors'].append(error_msg)
                    continue  # Continua con il prossimo lead invece di fermarsi
    else:
        logger.warning(f"⚠ Nessun lead da importare - leads_data: {leads_data}, tipo: {type(leads_data)}")
    
    # Importa Opportunities
    logger.info("=" * 60)
    logger.info("💾 SALVATAGGIO OPPORTUNITA' NEL DATABASE")
    logger.info("=" * 60)
    if opportunities_data and len(opportunities_data) > 0:
            logger.info(f"📋 Elaborazione {len(opportunities_data)} opportunità...")
            for idx, opp_data in enumerate(opportunities_data, 1):
                try:
                    if not opp_data or not isinstance(opp_data, dict):
                        logger.warning(f"  ⚠ Opportunità {idx} dati non validi, saltata")
                        continue
                    
                    opp_name = opp_data.get('name', '').strip() or f'UR Opportunity {idx}'
                    account_name = opp_data.get('account_name', '').strip() or 'Unknown'
                    logger.info(f"  📝 Opportunità {idx}/{len(opportunities_data)}: {opp_name}")
                    logger.info(f"    🏢 Account: {account_name}")
                    
                    # Crea Account se necessario
                    account = Account.query.filter_by(name=account_name).first()
                    
                    if not account:
                        account = Account(
                            name=account_name,
                            industry=opp_data.get('industry', '').strip() or '',
                            owner_id=user_id
                        )
                        db_session.add(account)
                        db_session.flush()
                        stats['accounts_created'] += 1
                        logger.info(f"    ✓ Account creato: {account_name}")
                    else:
                        logger.info(f"    ⏭ Account già esistente: {account_name}")
                    
                    # Crea o aggiorna Opportunity
                    existing_opp = Opportunity.query.filter_by(name=opp_name).first()
                    
                    if not existing_opp:
                        try:
                            # Valida e converti amount - deve essere un numero
                            amount_str = str(opp_data.get('amount', 0) or 0).strip()
                            # Rimuovi caratteri non numerici (tranne punto e virgola per decimali)
                            amount_clean = re.sub(r'[^\d.,]', '', amount_str)
                            if amount_clean:
                                # Sostituisci virgola con punto per decimali
                                amount_clean = amount_clean.replace(',', '.')
                                amount = float(amount_clean)
                            else:
                                amount = 0.0
                            
                            # Valida probability
                            prob_str = str(opp_data.get('probability', 10) or 10).strip()
                            prob_clean = re.sub(r'[^\d]', '', prob_str)
                            probability = int(prob_clean) if prob_clean else 10
                            if probability < 0 or probability > 100:
                                probability = 10
                        except (ValueError, TypeError):
                            amount = 0.0
                            probability = 10
                        
                        opportunity = Opportunity(
                            name=opp_name,
                            stage=opp_data.get('stage', 'Qualification').strip() or 'Qualification',
                            amount=amount,
                            probability=probability,
                            supplier_category='Universal Robots',  # Tutte le opportunità UR sono Universal Robots
                            account_id=account.id,
                            owner_id=user_id
                        )
                        db_session.add(opportunity)
                        stats['opportunities_imported'] += 1
                        logger.info(f"    ✓ Opportunità creata: {opp_name} (€{amount})")
                    else:
                        # Aggiorna opportunità esistente con nuovi dati
                        if opp_data.get('stage'):
                            existing_opp.stage = opp_data.get('stage', '').strip() or existing_opp.stage
                        
                        # Aggiorna supplier_category se non è già impostata
                        if not existing_opp.supplier_category:
                            existing_opp.supplier_category = 'Universal Robots'
                        
                        try:
                            # Valida e converti amount
                            if opp_data.get('amount') is not None:
                                amount_str = str(opp_data.get('amount', 0)).strip()
                                # Rimuovi caratteri non numerici
                                amount_clean = re.sub(r'[^\d.,]', '', amount_str)
                                if amount_clean:
                                    amount_clean = amount_clean.replace(',', '.')
                                    existing_opp.amount = float(amount_clean)
                                # Se non è un numero valido, mantieni il valore esistente
                            
                            # Valida probability
                            if opp_data.get('probability') is not None:
                                prob_str = str(opp_data.get('probability', 10)).strip()
                                prob_clean = re.sub(r'[^\d]', '', prob_str)
                                if prob_clean:
                                    prob_val = int(prob_clean)
                                    if 0 <= prob_val <= 100:
                                        existing_opp.probability = prob_val
                        except (ValueError, TypeError) as ve:
                            logger.warning(f"    ⚠ Errore conversione numeri: {ve}")
                        
                        # Aggiorna account se necessario
                        if existing_opp.account_id != account.id:
                            existing_opp.account_id = account.id
                        stats['opportunities_updated'] += 1
                        logger.info(f"    ✓ Opportunità aggiornata: {opp_name} (€{existing_opp.amount})")
                except Exception as e:
                    error_msg = f"Errore salvataggio opportunità {idx}: {e}"
                    logger.error(f"    ❌ {error_msg}")
                    logger.exception(e)
                    stats['errors'].append(error_msg)
                    continue  # Continua con la prossima opportunità invece di fermarsi
    else:
        logger.warning(f"⚠ Nessuna opportunità da importare - opportunities_data: {opportunities_data}, tipo: {type(opportunities_data)}")
    
    # Commit solo se ci sono modifiche
    try:
        logger.info("💾 Commit database...")
        db_session.commit()
        logger.info("✓ Database aggiornato con successo")
    except Exception as commit_error:
        logger.error(f"❌ Errore durante commit: {commit_error}")
        db_session.rollback()
        stats['errors'].append(f"Errore commit database: {commit_error}")
        logger.info("↩️  Rollback eseguito")
    
    logger.info("=" * 60)
    logger.info("📊 STATISTICHE SINCRONIZZAZIONE")
    logger.info("=" * 60)
    logger.info(f"👥 Leads creati: {stats['leads_imported']}")
    logger.info(f"🔄 Leads aggiornati: {stats['leads_updated']}")
    logger.info(f"📊 Opportunità create: {stats['opportunities_imported']}")
    logger.info(f"🔄 Opportunità aggiornate: {stats['opportunities_updated']}")
    logger.info(f"🏢 Account creati: {stats['accounts_created']}")
    logger.info(f"❌ Errori: {len(stats['errors'])}")
    if stats['errors']:
        for error in stats['errors']:
            logger.error(f"   - {error}")
    logger.info(f"📅 Timestamp fine: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    return stats
