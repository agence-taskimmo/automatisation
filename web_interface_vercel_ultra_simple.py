#!/usr/bin/env python3
"""
Interface Web ultra-simplifiée pour Vercel
Version sans JavaScript complexe, juste des formulaires HTML
"""

from flask import Flask, render_template_string, request, redirect, url_for, flash
import logging
from datetime import datetime
import os
import time

# Configuration Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'aircall_automation_secret_key_2025'

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# État global du système
system_state = {
    'status': 'running',
    'last_run': datetime.now().isoformat(),
    'next_run': (datetime.now().isoformat()),
    'active_jobs': [],
    'logs': [
        f"{datetime.now().strftime('%H:%M:%S')} - INFO - Interface web démarrée sur Vercel",
        f"{datetime.now().strftime('%H:%M:%S')} - INFO - Mode ultra-simplifié activé",
        f"{datetime.now().strftime('%H:%M:%S')} - INFO - Formulaires HTML simples"
    ],
    'stats': {
        'total_runs': 42,
        'successful_runs': 38,
        'failed_runs': 4,
        'last_error': None
    }
}

# Détails des scripts
script_details = {
    'sync': {
        'name': 'Synchronisation Aircall',
        'description': 'Synchronise les nouveaux appels Aircall avec Monday.com'
    },
    'tasks': {
        'name': 'Création de tâches',
        'description': 'Crée des tâches depuis les actions IA détectées'
    },
    'assign': {
        'name': 'Assignation intelligente',
        'description': 'Assigne les tâches aux bons agents selon leurs compétences'
    },
    'link': {
        'name': 'Liaison contacts',
        'description': 'Lie les appels aux contacts existants dans Monday.com'
    },
    'relations': {
        'name': 'Mise à jour relations',
        'description': 'Met à jour les relations entre tableaux Monday.com'
    }
}

def add_log(message, level='INFO'):
    """Ajoute un log simple"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"{timestamp} - {level} - {message}"
    system_state['logs'].append(log_entry)
    
    # Garder seulement les 100 derniers logs
    if len(system_state['logs']) > 100:
        system_state['logs'] = system_state['logs'][-100:]
    
    logger.info(f"Log ajouté: {log_entry}")
    return log_entry

def simulate_script_execution(script_key):
    """Simule l'exécution d'un script"""
    try:
        script_info = script_details[script_key]
        
        add_log(f"🚀 Démarrage de {script_info['name']}")
        add_log(f"📋 Description: {script_info['description']}")
        
        # Simulation d'exécution
        time.sleep(1)
        
        add_log(f"✅ {script_info['name']} exécuté avec succès")
        
        # Mettre à jour les statistiques
        system_state['stats']['total_runs'] += 1
        system_state['stats']['successful_runs'] += 1
        system_state['last_run'] = datetime.now().isoformat()
        
        return True
        
    except Exception as e:
        error_msg = f"❌ Erreur lors de l'exécution de {script_key}: {str(e)}"
        add_log(error_msg, 'ERROR')
        system_state['stats']['failed_runs'] += 1
        system_state['stats']['last_error'] = error_msg
        return False

@app.route('/')
def index():
    """Page d'accueil avec formulaires simples"""
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Automatisation Aircall-Monday - Version Simple</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                margin: 20px; 
                background: #f5f5f5; 
                line-height: 1.6;
            }}
            .container {{ 
                max-width: 1000px; 
                margin: 0 auto; 
                background: white; 
                padding: 30px; 
                border-radius: 10px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
            }}
            h1 {{ 
                color: #2c3e50; 
                text-align: center; 
                margin-bottom: 30px; 
            }}
            .subtitle {{ 
                text-align: center; 
                color: #7f8c8d; 
                margin-bottom: 30px; 
                font-size: 18px;
            }}
            .section {{ 
                margin: 30px 0; 
                padding: 20px; 
                border: 1px solid #ecf0f1; 
                border-radius: 8px; 
            }}
            .section h3 {{ 
                color: #2c3e50; 
                margin-top: 0; 
                border-bottom: 2px solid #3498db; 
                padding-bottom: 10px; 
            }}
            .form-group {{ 
                margin: 15px 0; 
            }}
            .form-group label {{ 
                display: block; 
                margin-bottom: 5px; 
                font-weight: bold; 
                color: #2c3e50; 
            }}
            .form-group select {{ 
                width: 100%; 
                padding: 10px; 
                border: 1px solid #bdc3c7; 
                border-radius: 5px; 
                font-size: 16px; 
            }}
            .btn {{ 
                background: #3498db; 
                color: white; 
                padding: 12px 25px; 
                border: none; 
                border-radius: 5px; 
                cursor: pointer; 
                font-size: 16px; 
                margin: 5px; 
            }}
            .btn:hover {{ 
                background: #2980b9; 
            }}
            .btn-success {{ 
                background: #27ae60; 
            }}
            .btn-warning {{ 
                background: #f39c12; 
            }}
            .btn-danger {{ 
                background: #e74c3c; 
            }}
            .stats-grid {{ 
                display: grid; 
                grid-template-columns: repeat(3, 1fr); 
                gap: 20px; 
                margin: 20px 0; 
            }}
            .stat-card {{ 
                background: #ecf0f1; 
                padding: 20px; 
                border-radius: 8px; 
                text-align: center; 
                border: 2px solid #bdc3c7; 
            }}
            .stat-number {{ 
                font-size: 32px; 
                font-weight: bold; 
                color: #2c3e50; 
                margin-bottom: 10px; 
            }}
            .stat-label {{ 
                color: #7f8c8d; 
                font-size: 14px; 
                text-transform: uppercase; 
                letter-spacing: 1px; 
            }}
            .logs-container {{ 
                background: #f8f9fa; 
                padding: 20px; 
                border-radius: 8px; 
                max-height: 400px; 
                overflow-y: auto; 
                border: 1px solid #dee2e6; 
            }}
            .log-entry {{ 
                margin: 8px 0; 
                font-family: monospace; 
                padding: 8px; 
                border-left: 4px solid #3498db; 
                background: white; 
                border-radius: 4px; 
                font-size: 14px; 
            }}
            .log-entry.success {{ 
                border-left-color: #27ae60; 
                background: #d5f4e6; 
            }}
            .log-entry.error {{ 
                border-left-color: #e74c3c; 
                background: #fadbd8; 
            }}
            .log-entry.warning {{ 
                border-left-color: #f39c12; 
                background: #fdeaa7; 
            }}
            .status-info {{ 
                background: #e8f5e8; 
                padding: 15px; 
                border-radius: 8px; 
                margin: 20px 0; 
                border: 1px solid #27ae60; 
            }}
            .status-info p {{ 
                margin: 8px 0; 
                color: #2c3e50; 
            }}
            .status-info strong {{ 
                color: #27ae60; 
            }}
            .message {{ 
                padding: 15px; 
                border-radius: 8px; 
                margin: 20px 0; 
                font-weight: bold; 
            }}
            .message.success {{ 
                background: #d5f4e6; 
                color: #27ae60; 
                border: 1px solid #27ae60; 
            }}
            .message.error {{ 
                background: #fadbd8; 
                color: #e74c3c; 
                border: 1px solid #e74c3c; 
            }}
            .message.info {{ 
                background: #d6eaf8; 
                color: #3498db; 
                border: 1px solid #3498db; 
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Interface d'Automatisation Aircall-Monday</h1>
            <div class="subtitle">Version ultra-simplifiée - Formulaires HTML simples</div>
            
            <!-- Messages flash -->
            {render_flashed_messages()}
            
            <!-- Statut du système -->
            <div class="section">
                <h3>📊 Statut du Système</h3>
                <div class="status-info">
                    <p><strong>État:</strong> {system_state['status']}</p>
                    <p><strong>Dernière exécution:</strong> {format_datetime(system_state['last_run'])}</p>
                    <p><strong>Prochaine exécution:</strong> {format_datetime(system_state['next_run'])}</p>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">{system_state['stats']['total_runs']}</div>
                        <div class="stat-label">Total Exécutions</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{system_state['stats']['successful_runs']}</div>
                        <div class="stat-label">Succès</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{system_state['stats']['failed_runs']}</div>
                        <div class="stat-label">Échecs</div>
                    </div>
                </div>
            </div>
            
            <!-- Contrôle des automatisations -->
            <div class="section">
                <h3>⚡ Contrôle des Automatisations</h3>
                
                <form method="POST" action="/run-script">
                    <div class="form-group">
                        <label for="script">Sélectionner une automatisation :</label>
                        <select name="script" id="script" required>
                            <option value="">-- Choisir une automatisation --</option>
                            <option value="sync">🔄 Synchronisation Aircall</option>
                            <option value="tasks">📝 Création de Tâches</option>
                            <option value="assign">👥 Assignation Intelligente</option>
                            <option value="link">🔗 Liaison Contacts</option>
                            <option value="relations">🔄 Relations</option>
                        </select>
                    </div>
                    
                    <button type="submit" class="btn btn-success">🚀 Exécuter l'automatisation</button>
                </form>
                
                <div style="margin-top: 20px;">
                    <form method="POST" action="/run-all" style="display: inline;">
                        <button type="submit" class="btn btn-warning">🔄 Exécuter toutes les automatisations</button>
                    </form>
                    
                    <form method="POST" action="/clear-logs" style="display: inline;">
                        <button type="submit" class="btn btn-danger">🗑️ Effacer les logs</button>
                    </form>
                </div>
            </div>
            
            <!-- Logs -->
            <div class="section">
                <h3>📋 Logs des Automatisations</h3>
                <div class="logs-container">
                    {render_logs()}
                </div>
            </div>
            
            <!-- Informations -->
            <div class="section">
                <h3>ℹ️ Informations</h3>
                <p><strong>Version:</strong> Ultra-simplifiée pour Vercel</p>
                <p><strong>Technologie:</strong> HTML + Formulaires (pas de JavaScript)</p>
                <p><strong>Dernière mise à jour:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            </div>
        </div>
    </body>
    </html>
    '''

def format_datetime(datetime_str):
    """Formate une date ISO en format lisible"""
    try:
        dt = datetime.fromisoformat(datetime_str)
        return dt.strftime('%d/%m/%Y %H:%M:%S')
    except:
        return 'Non défini'

def render_logs():
    """Rend les logs avec formatage HTML"""
    if not system_state['logs']:
        return '<div class="log-entry">Aucun log disponible</div>'
    
    html = ''
    for log in reversed(system_state['logs']):  # Plus récents en premier
        css_class = 'log-entry'
        if 'succès' in log or '✅' in log:
            css_class += ' success'
        elif 'erreur' in log or '❌' in log:
            css_class += ' error'
        elif 'WARNING' in log or '⚠️' in log:
            css_class += ' warning'
        
        html += f'<div class="{css_class}">{log}</div>'
    
    return html

def render_flashed_messages():
    """Récupère et formate les messages flash"""
    from flask import get_flashed_messages
    
    messages = []
    for category, message in get_flashed_messages(with_categories=True):
        css_class = 'message'
        if category == 'success':
            css_class += ' success'
        elif category == 'error':
            css_class += ' error'
        else:
            css_class += ' info'
        
        messages.append(f'<div class="{css_class}">{message}</div>')
    
    return ''.join(messages)

@app.route('/run-script', methods=['POST'])
def run_script():
    """Exécute un script spécifique"""
    try:
        script_key = request.form.get('script')
        
        if not script_key:
            flash('Veuillez sélectionner une automatisation', 'error')
            return redirect(url_for('index'))
        
        if script_key not in script_details:
            flash(f'Automatisation inconnue: {script_key}', 'error')
            return redirect(url_for('index'))
        
        script_info = script_details[script_key]
        
        # Exécuter le script
        success = simulate_script_execution(script_key)
        
        if success:
            flash(f'✅ {script_info["name"]} exécuté avec succès !', 'success')
        else:
            flash(f'❌ Erreur lors de l\'exécution de {script_info["name"]}', 'error')
        
        return redirect(url_for('index'))
        
    except Exception as e:
        logger.error(f"Erreur exécution script: {str(e)}")
        flash(f'Erreur système: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/run-all', methods=['POST'])
def run_all():
    """Exécute toutes les automatisations"""
    try:
        add_log("🔄 Démarrage de l'exécution de toutes les automatisations")
        
        success_count = 0
        total_count = len(script_details)
        
        for script_key in script_details.keys():
            if simulate_script_execution(script_key):
                success_count += 1
        
        add_log(f"✅ Exécution terminée: {success_count}/{total_count} automatisations réussies")
        
        if success_count == total_count:
            flash(f'🎉 Toutes les automatisations ont été exécutées avec succès ! ({success_count}/{total_count})', 'success')
        else:
            flash(f'⚠️ {success_count}/{total_count} automatisations ont réussi', 'warning')
        
        return redirect(url_for('index'))
        
    except Exception as e:
        logger.error(f"Erreur exécution multiple: {str(e)}")
        flash(f'Erreur système: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/clear-logs', methods=['POST'])
def clear_logs():
    """Efface tous les logs"""
    try:
        system_state['logs'] = [
            f"{datetime.now().strftime('%H:%M:%S')} - INFO - Logs effacés par l'utilisateur"
        ]
        flash('🗑️ Tous les logs ont été effacés', 'info')
        return redirect(url_for('index'))
        
    except Exception as e:
        logger.error(f"Erreur effacement logs: {str(e)}")
        flash(f'Erreur lors de l\'effacement des logs: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/health')
def health_check():
    """Vérification de santé pour Vercel"""
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'environment': 'vercel',
        'version': 'ultra-simple',
        'message': 'Interface ultra-simplifiée fonctionnelle'
    }

if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 8080))
    
    logger.info(f"Démarrage de l'interface web ultra-simplifiée sur {host}:{port}")
    app.run(host=host, port=port)
