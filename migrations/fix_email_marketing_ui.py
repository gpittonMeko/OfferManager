#!/usr/bin/env python3
# Fix per aggiungere UI Email Marketing al template

template_file = 'templates/app_mekocrm_completo.html'

with open(template_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Email Marketing View HTML (da inserire prima di </main>)
email_marketing_view = '''
        <!-- Email Marketing -->
        <section id="email-marketing-view" class="view">
            <div class="hero">
                <div>
                    <h2>📧 Email Marketing</h2>
                    <p style="color: var(--text-light);">Gestisci campagne email e liste destinatari</p>
                </div>
            </div>
            
            <div class="card">
                <h3>Email Marketing</h3>
                <p>Sezione in sviluppo. Le API sono disponibili. Usa la console del browser per testare.</p>
                <button class="button" onclick="loadEmailMarketing()">Carica Email Marketing</button>
                <div id="email-marketing-content"></div>
            </div>
        </section>
'''

# JavaScript per Email Marketing (da aggiungere nello script)
email_marketing_js = '''
                if (target === 'email-marketing-view') {
                    loadEmailMarketing();
                }
'''

# Funzione loadEmailMarketing (da aggiungere prima della chiusura dello script)
load_email_marketing_func = '''
        async function loadEmailMarketing() {
            const container = document.getElementById('email-marketing-content');
            if (!container) return;
            
            try {
                container.innerHTML = '<p>Caricamento...</p>';
                
                // Carica liste
                const listsRes = await fetch('/api/email/lists');
                const listsData = await listsRes.json();
                
                // Carica template
                const templatesRes = await fetch('/api/email/templates');
                const templatesData = await templatesRes.json();
                
                // Carica campagne
                const campaignsRes = await fetch('/api/email/campaigns');
                const campaignsData = await campaignsRes.json();
                
                container.innerHTML = `
                    <h4>Liste Email (${listsData.lists?.length || 0})</h4>
                    <p>API funzionante: ${listsRes.ok ? '✅' : '❌'}</p>
                    
                    <h4>Template (${templatesData.templates?.length || 0})</h4>
                    <p>API funzionante: ${templatesRes.ok ? '✅' : '❌'}</p>
                    
                    <h4>Campagne (${campaignsData.campaigns?.length || 0})</h4>
                    <p>API funzionante: ${campaignsRes.ok ? '✅' : '❌'}</p>
                    
                    <button class="button" onclick="initEmailTemplates()">Carica Template Predefiniti</button>
                `;
            } catch (err) {
                container.innerHTML = `<p style="color: red;">Errore: ${err.message}</p>`;
                console.error(err);
            }
        }
        
        async function initEmailTemplates() {
            try {
                const res = await fetch('/api/email/templates/init-defaults', { method: 'POST' });
                const data = await res.json();
                alert(data.success ? 'Template caricati!' : 'Errore: ' + (data.error || 'Unknown'));
                loadEmailMarketing();
            } catch (err) {
                alert('Errore: ' + err.message);
            }
        }
'''

# Inserisci la view prima di </main>
if '</main>' in content and 'id="email-marketing-view"' not in content:
    content = content.replace('    </main>', email_marketing_view + '    </main>')
    print("✅ Aggiunta sezione email-marketing-view")

# Aggiungi il case nel navItems.forEach
if 'if (target === \'tasks-by-operator-view\')' in content and 'email-marketing-view' not in content.split('if (target === \'tasks-by-operator-view\')')[0].split('navItems.forEach')[1]:
    content = content.replace(
        '                if (target === \'tasks-by-operator-view\') {\n                    loadTasksByOperator();\n                }',
        '                if (target === \'tasks-by-operator-view\') {\n                    loadTasksByOperator();\n                }\n                if (target === \'email-marketing-view\') {\n                    loadEmailMarketing();\n                }'
    )
    print("✅ Aggiunto case email-marketing-view")

# Aggiungi le funzioni JavaScript prima della chiusura dello script
if '</script>' in content and 'async function loadEmailMarketing' not in content:
    # Trova l'ultimo </script> prima di </body>
    parts = content.rsplit('</script>', 1)
    if len(parts) == 2:
        content = parts[0] + load_email_marketing_func + '\n    </script>' + parts[1]
        print("✅ Aggiunta funzione loadEmailMarketing")

# Salva il file
with open(template_file, 'w', encoding='utf-8') as f:
    f.write(content)
    
print("✅ Template aggiornato con Email Marketing UI!")







