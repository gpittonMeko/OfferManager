#!/usr/bin/env python3
# Crea interfaccia completa Email Marketing
import re

template_file = 'templates/app_mekocrm_completo.html'

with open(template_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Interfaccia completa Email Marketing
email_marketing_ui = '''        <!-- Email Marketing -->
        <section id="email-marketing-view" class="view">
            <div class="hero">
                <div>
                    <h2>📧 Email Marketing</h2>
                    <p style="color: var(--text-light);">Gestisci campagne email, liste contatti e template</p>
                </div>
                <div class="hero-actions">
                    <button class="button" onclick="showNewCampaignForm()">+ Nuova Campagna</button>
                    <button class="button secondary" onclick="initEmailTemplates()">📥 Carica Template Predefiniti</button>
                </div>
            </div>
            
            <!-- Tab Navigation -->
            <div style="display: flex; gap: 12px; margin-bottom: 24px; border-bottom: 2px solid var(--border-color);">
                <button class="email-tab-btn active" onclick="switchEmailTab('campaigns')" data-tab="campaigns">📬 Campagne</button>
                <button class="email-tab-btn" onclick="switchEmailTab('lists')" data-tab="lists">👥 Liste Contatti</button>
                <button class="email-tab-btn" onclick="switchEmailTab('templates')" data-tab="templates">📄 Template</button>
                <button class="email-tab-btn" onclick="switchEmailTab('compose')" data-tab="compose">✉️ Componi Email</button>
            </div>
            
            <!-- Tab: Campagne -->
            <div id="email-tab-campaigns" class="email-tab-content active">
                <div class="card">
                    <h3 style="margin-bottom: 16px;">Le tue Campagne</h3>
                    <div class="table-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    <th>Nome</th>
                                    <th>Oggetto</th>
                                    <th>Lista</th>
                                    <th>Destinatari</th>
                                    <th>Inviate</th>
                                    <th>Stato</th>
                                    <th>Azioni</th>
                                </tr>
                            </thead>
                            <tbody id="campaigns-table"></tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- Tab: Liste -->
            <div id="email-tab-lists" class="email-tab-content">
                <div class="card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                        <h3>Liste Contatti</h3>
                        <button class="button" onclick="showNewListForm()">+ Nuova Lista</button>
                    </div>
                    <div class="table-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    <th>Nome</th>
                                    <th>Descrizione</th>
                                    <th>Contatti</th>
                                    <th>Azioni</th>
                                </tr>
                            </thead>
                            <tbody id="email-lists-table"></tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- Tab: Template -->
            <div id="email-tab-templates" class="email-tab-content">
                <div class="card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                        <h3>Template Email</h3>
                        <button class="button" onclick="showNewTemplateForm()">+ Nuovo Template</button>
                    </div>
                    <div class="table-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    <th>Nome</th>
                                    <th>Categoria</th>
                                    <th>Oggetto</th>
                                    <th>Azioni</th>
                                </tr>
                            </thead>
                            <tbody id="email-templates-table"></tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- Tab: Componi -->
            <div id="email-tab-compose" class="email-tab-content">
                <div class="card">
                    <h3 style="margin-bottom: 16px;">Componi Nuova Email</h3>
                    <form id="compose-email-form" class="form-grid">
                        <div class="form-group">
                            <label>Destinatari *</label>
                            <select id="compose-list-id" name="list_id" required>
                                <option value="">Seleziona lista...</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Oggetto *</label>
                            <input type="text" id="compose-subject" name="subject" required>
                        </div>
                        <div class="form-group">
                            <label>Template (opzionale)</label>
                            <select id="compose-template-id" name="template_id">
                                <option value="">Nessun template</option>
                            </select>
                        </div>
                        <div class="form-group full">
                            <label>Contenuto HTML *</label>
                            <textarea id="compose-html-content" name="html_content" style="min-height: 400px; font-family: monospace;" required></textarea>
                            <small style="color: var(--text-light);">Puoi usare variabili: %nome%, %first_name%, %last_name%</small>
                        </div>
                        <div class="form-group full" style="display: flex; gap: 12px; justify-content: flex-end;">
                            <button type="button" class="button secondary" onclick="previewEmail()">👁️ Anteprima</button>
                            <button type="button" class="button secondary" onclick="testEmail()">📧 Test Email</button>
                            <button type="button" class="button secondary" onclick="saveAsDraft()">💾 Salva Bozza</button>
                            <button type="submit" class="button">🚀 Crea Campagna</button>
                        </div>
                    </form>
                </div>
            </div>
        </section>'''

# Sostituisci la vecchia sezione
old_section = r'<!-- Email Marketing -->.*?</section>'
content = re.sub(old_section, email_marketing_ui, content, flags=re.DOTALL)

# Aggiungi CSS per tab email
email_css = '''
        <style>
            .email-tab-btn {
                padding: 10px 20px;
                border: none;
                background: transparent;
                border-bottom: 3px solid transparent;
                cursor: pointer;
                font-weight: 600;
                color: var(--text-light);
                transition: all 0.3s;
            }
            .email-tab-btn:hover {
                color: var(--primary);
            }
            .email-tab-btn.active {
                color: var(--primary);
                border-bottom-color: var(--primary);
            }
            .email-tab-content {
                display: none;
            }
            .email-tab-content.active {
                display: block;
            }
        </style>
'''

# Inserisci CSS prima di </head>
if '</head>' in content and '.email-tab-btn' not in content:
    content = content.replace('</head>', email_css + '</head>')

# Salva
with open(template_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Interfaccia Email Marketing creata!")







