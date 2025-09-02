#!/usr/bin/env python3
"""
Interface Web avec vraies automatisations pour Vercel
Version qui exécute les vrais scripts au lieu de les simuler
"""

from flask import Flask, render_template_string, request, redirect, url_for, flash
import logging
from datetime import datetime
import os
import time
import subprocess
import sys

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
            f"{datetime.now().strftime('%H:%M:%S')} - INFO - Mode automatisations réelles activé",
            f"{datetime.now().strftime('%H:%M:%S')} - INFO - Scripts Python prêts à l'exécution"
        ],
    'stats': {
        'total_runs': 0,
        'successful_runs': 0,
        'failed_runs': 0,
        'last_error': None
    }
}

# Configuration des vrais scripts
script_config = {
    'sync': {
        'name': 'Synchronisation Aircall',
        'description': 'Synchronise les nouveaux appels Aircall avec Monday.com',
        'script': 'aircall_monday_integration_v2.py',
        'args': ['--sync-only']
    },
    'tasks': {
        'name': 'Création de tâches',
        'description': 'Crée des tâches depuis les actions IA détectées',
        'script': 'create_tasks_with_agent.py',
        'args': []
    },
    'assign': {
        'name': 'Assignation intelligente',
        'description': 'Assigne les tâches aux bons agents selon leurs compétences',
        'script': 'smart_task_assigner.py',
        'args': []
    },
    'link': {
        'name': 'Liaison contacts',
        'description': 'Lie les appels aux contacts existants dans Monday.com',
        'script': 'link_calls_to_contacts.py',
        'args': []
    },
    'relations': {
        'name': 'Mise à jour relations',
        'description': 'Met à jour les relations entre tableaux Monday.com',
        'script': 'update_board_relations.py',
        'args': []
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

def execute_real_script(script_key):
    """Exécute le vrai script Python"""
    try:
        if script_key not in script_config:
            raise ValueError(f"Script inconnu: {script_key}")
        
        script_info = script_config[script_key]
        script_path = script_info['script']
        
        # Vérifier que le script existe
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script introuvable: {script_path}")
        
        add_log(f"🚀 Démarrage de {script_info['name']}")
        add_log(f"📁 Script: {script_path}")
        add_log(f"⚙️ Arguments: {script_info['args']}")
        
        # Préparer la commande
        cmd = [sys.executable, script_path] + script_info['args']
        add_log(f"💻 Commande: {' '.join(cmd)}")
        
        # Exécuter le script
        start_time = time.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes max
            cwd=os.getcwd()
        )
        execution_time = time.time() - start_time
        
        # Analyser le résultat
        if result.returncode == 0:
            add_log(f"✅ {script_info['name']} exécuté avec succès")
            add_log(f"⏱️ Temps d'exécution: {execution_time:.2f} secondes")
            
            # Log de la sortie si elle existe
            if result.stdout.strip():
                add_log(f"📤 Sortie: {result.stdout.strip()}")
            
            # Mettre à jour les statistiques
            system_state['stats']['total_runs'] += 1
            system_state['stats']['successful_runs'] += 1
            system_state['last_run'] = datetime.now().isoformat()
            
            return True, result.stdout
            
        else:
            error_msg = f"❌ {script_info['name']} a échoué (code: {result.returncode})"
            add_log(error_msg, 'ERROR')
            
            if result.stderr.strip():
                add_log(f"🚨 Erreur: {result.stderr.strip()}", 'ERROR')
            
            if result.stdout.strip():
                add_log(f"📤 Sortie: {result.stdout.strip()}")
            
            # Mettre à jour les statistiques
            system_state['stats']['total_runs'] += 1
            system_state['stats']['failed_runs'] += 1
            system_state['stats']['last_error'] = error_msg
            
            return False, result.stderr
        
    except subprocess.TimeoutExpired:
        error_msg = f"⏰ {script_info['name']} a dépassé le délai d'exécution (5 minutes)"
        add_log(error_msg, 'ERROR')
        system_state['stats']['failed_runs'] += 1
        system_state['stats']['last_error'] = error_msg
        return False, "Timeout d'exécution"
        
    except FileNotFoundError as e:
        error_msg = f"📁 Fichier introuvable: {str(e)}"
        add_log(error_msg, 'ERROR')
        system_state['stats']['failed_runs'] += 1
        system_state['stats']['last_error'] = error_msg
        return False, str(e)
        
    except Exception as e:
        error_msg = f"💥 Erreur système: {str(e)}"
        add_log(error_msg, 'ERROR')
        system_state['stats']['failed_runs'] += 1
        system_state['stats']['last_error'] = error_msg
        return False, str(e)

@app.route('/')
def index():
    """Page d'accueil avec formulaires simples"""
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Automatisation Aircall-Monday - Vraies Actions</title>
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
            .warning-banner {{ 
                background: #fff3cd; 
                color: #856404; 
                padding: 15px; 
                border-radius: 8px; 
                margin-bottom: 20px; 
                border: 1px solid #ffeaa7; 
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
            .script-info {{ 
                background: #f8f9fa; 
                padding: 15px; 
                border-radius: 8px; 
                margin: 20px 0; 
                border: 1px solid #dee2e6; 
            }}
            .script-info h4 {{ 
                margin-top: 0; 
                color: #2c3e50; 
            }}
            .script-info p {{ 
                margin: 8px 0; 
                color: #7f8c8d; 
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Interface d'Automatisation Aircall-Monday</h1>
            <div class="subtitle">Version avec vraies actions sur Monday.com et Aircall</div>
            
            <!-- Bannière d'avertissement -->
            <div class="warning-banner">
                ⚠️ <strong>ATTENTION :</strong> Cette interface exécute de VRAIES automatisations qui modifient vos données Monday.com et Aircall. Utilisez avec précaution !
            </div>
            
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
            
            <!-- Informations sur les scripts -->
            <div class="section">
                <h3>📋 Scripts d'Automatisation Disponibles</h3>
                {render_script_info()}
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
                <p><strong>Version:</strong> Automatisations réelles sur Vercel</p>
                <p><strong>Technologie:</strong> Python + APIs Monday.com + Aircall</p>
                <p><strong>Dernière mise à jour:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                <p><strong>⚠️ Attention:</strong> Les actions modifient vos vraies données !</p>
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
        elif 'erreur' in log or '❌' in log or '🚨' in log:
            css_class += ' error'
        elif 'WARNING' in log or '⚠️' in log:
            css_class += ' warning'
        
        html += f'<div class="{css_class}">{log}</div>'
    
    return html

def render_script_info():
    """Rend les informations sur les scripts disponibles"""
    html = ''
    for key, info in script_config.items():
        script_path = info['script']
        exists = os.path.exists(script_path)
        status = "✅ Disponible" if exists else "❌ Introuvable"
        status_color = "success" if exists else "error"
        
        html += f'''
        <div class="script-info">
            <h4>{info['name']}</h4>
            <p><strong>Description:</strong> {info['description']}</p>
            <p><strong>Fichier:</strong> {script_path}</p>
            <p><strong>Statut:</strong> <span class="message {status_color}">{status}</span></p>
        </div>
        '''
    
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
        
        if script_key not in script_config:
            flash(f'Automatisation inconnue: {script_key}', 'error')
            return redirect(url_for('index'))
        
        script_info = script_config[script_key]
        
        # Vérifier que le script existe
        if not os.path.exists(script_info['script']):
            flash(f'❌ Script introuvable: {script_info["script"]}', 'error')
            return redirect(url_for('index'))
        
        # Exécuter le vrai script
        success, output = execute_real_script(script_key)
        
        if success:
            flash(f'✅ {script_info["name"]} exécuté avec succès ! Vérifiez Monday.com', 'success')
        else:
            flash(f'❌ Erreur lors de l\'exécution de {script_info["name"]}: {output}', 'error')
        
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
        total_count = len(script_config)
        
        for script_key in script_config.keys():
            if os.path.exists(script_config[script_key]['script']):
                success, _ = execute_real_script(script_key)
                if success:
                    success_count += 1
            else:
                add_log(f"❌ Script introuvable: {script_config[script_key]['script']}", 'ERROR')
        
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
        'version': 'real-automations',
        'message': 'Interface avec vraies automatisations'
    }

if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 8080))
    
    logger.info(f"Démarrage de l'interface web avec vraies automatisations sur {host}:{port}")
    app.run(host=host, port=port)
