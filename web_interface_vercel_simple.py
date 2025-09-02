#!/usr/bin/env python3
"""
Interface Web ultra-simplifiée pour Vercel
Version minimale sans templates ni fichiers statiques
"""

from flask import Flask, jsonify, request
import logging
from datetime import datetime
import os

# Configuration Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'aircall_automation_secret_key_2025'

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# État global du système (simulé)
system_state = {
    'status': 'running',
    'last_run': datetime.now().isoformat(),
    'next_run': (datetime.now().isoformat()),
    'active_jobs': [],
    'logs': [
        f"{datetime.now().strftime('%H:%M:%S')} - INFO - Interface web démarrée sur Vercel",
        f"{datetime.now().strftime('%H:%M:%S')} - INFO - Mode déploiement cloud activé"
    ],
    'stats': {
        'total_runs': 42,
        'successful_runs': 38,
        'failed_runs': 4,
        'last_error': None
    }
}

def add_log(message):
    """Ajoute un log et le garde en mémoire"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"{timestamp} - INFO - {message}"
    system_state['logs'].append(log_entry)
    
    # Garder seulement les 100 derniers logs
    if len(system_state['logs']) > 100:
        system_state['logs'] = system_state['logs'][-100:]
    
    logger.info(f"Log ajouté: {log_entry}")
    return log_entry

@app.route('/')
def index():
    """Page d'accueil simple"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Automatisation Aircall-Monday</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            .status { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .button { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
            .button:hover { background: #2980b9; }
            .button:disabled { background: #bdc3c7; cursor: not-allowed; }
            .logs { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; max-height: 400px; overflow-y: auto; }
            .log-entry { margin: 5px 0; font-family: monospace; padding: 5px; border-left: 3px solid #3498db; }
            .success { color: #27ae60; }
            .error { color: #e74c3c; }
            .info { color: #3498db; }
            .loading { opacity: 0.6; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Interface d'Automatisation Aircall-Monday</h1>
            
            <div class="status">
                <h3>📊 Statut du Système</h3>
                <p><strong>État:</strong> <span id="status">Chargement...</span></p>
                <p><strong>Dernière exécution:</strong> <span id="last-run">Chargement...</span></p>
                <p><strong>Prochaine exécution:</strong> <span id="next-run">Chargement...</span></p>
            </div>
            
            <div>
                <h3>⚡ Actions Rapides</h3>
                <button class="button" onclick="runScript('sync')" id="btn-sync">🔄 Synchronisation</button>
                <button class="button" onclick="runScript('tasks')" id="btn-tasks">📝 Créer Tâches</button>
                <button class="button" onclick="runScript('assign')" id="btn-assign">👥 Assigner</button>
                <button class="button" onclick="runScript('link')" id="btn-link">🔗 Lier Contacts</button>
                <button class="button" onclick="runScript('relations')" id="btn-relations">🔄 Relations</button>
            </div>
            
            <div>
                <h3>📈 Statistiques</h3>
                <p><strong>Total des exécutions:</strong> <span id="total-runs">Chargement...</span></p>
                <p><strong>Succès:</strong> <span id="successful-runs">Chargement...</span></p>
                <p><strong>Échecs:</strong> <span id="failed-runs">Chargement...</span></p>
            </div>
            
            <div class="logs">
                <h3>📋 Logs Récents <button class="button" onclick="refreshLogs()" style="float: right; padding: 5px 10px; font-size: 12px;">🔄 Actualiser</button></h3>
                <div id="logs-container">Chargement des logs...</div>
            </div>
        </div>
        
        <script>
            // Charger les données au démarrage
            loadData();
            
            // Actualiser toutes les 10 secondes
            setInterval(loadData, 10000);
            
            function loadData() {
                // Charger le statut
                fetch('/api/status')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('status').textContent = data.status;
                        document.getElementById('last-run').textContent = new Date(data.last_run).toLocaleString('fr-FR');
                        document.getElementById('next-run').textContent = new Date(data.next_run).toLocaleString('fr-FR');
                    })
                    .catch(error => console.error('Erreur chargement statut:', error));
                
                // Charger les statistiques
                fetch('/api/stats')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('total-runs').textContent = data.total_runs;
                        document.getElementById('successful-runs').textContent = data.successful_runs;
                        document.getElementById('failed-runs').textContent = data.failed_runs;
                    })
                    .catch(error => console.error('Erreur chargement stats:', error));
                
                // Charger les logs
                refreshLogs();
            }
            
            function refreshLogs() {
                fetch('/api/logs')
                    .then(response => response.json())
                    .then(data => {
                        const logsContainer = document.getElementById('logs-container');
                        if (data.logs && data.logs.length > 0) {
                            logsContainer.innerHTML = data.logs.map(log => {
                                let className = 'log-entry info';
                                if (log.includes('succès') || log.includes('réussi')) className = 'log-entry success';
                                if (log.includes('erreur') || log.includes('échec')) className = 'log-entry error';
                                
                                return `<div class="${className}">${log}</div>`;
                            }).join('');
                        } else {
                            logsContainer.innerHTML = '<div class="log-entry">Aucun log disponible</div>';
                        }
                    })
                    .catch(error => {
                        console.error('Erreur chargement logs:', error);
                        document.getElementById('logs-container').innerHTML = '<div class="log-entry error">Erreur de chargement des logs</div>';
                    });
            }
            
            function runScript(scriptKey) {
                const button = document.getElementById('btn-' + scriptKey);
                const originalText = button.textContent;
                
                // Désactiver le bouton et montrer le chargement
                button.disabled = true;
                button.textContent = '⏳ Exécution...';
                button.classList.add('loading');
                
                // Exécuter le script
                fetch('/api/run/' + scriptKey, { 
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({})
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        button.textContent = '✅ Succès !';
                        button.style.background = '#27ae60';
                        setTimeout(() => {
                            button.textContent = originalText;
                            button.style.background = '';
                            button.disabled = false;
                            button.classList.remove('loading');
                        }, 2000);
                        
                        // Actualiser les données
                        setTimeout(loadData, 1000);
                    } else {
                        button.textContent = '❌ Erreur';
                        button.style.background = '#e74c3c';
                        setTimeout(() => {
                            button.textContent = originalText;
                            button.style.background = '';
                            button.disabled = false;
                            button.classList.remove('loading');
                        }, 3000);
                    }
                })
                .catch(error => {
                    console.error('Erreur exécution script:', error);
                    button.textContent = '❌ Erreur';
                    button.style.background = '#e74c3c';
                    setTimeout(() => {
                        button.textContent = originalText;
                        button.style.background = '';
                        button.disabled = false;
                        button.classList.remove('loading');
                    }, 3000);
                });
            }
        </script>
    </body>
    </html>
    '''

@app.route('/api/status')
def api_status():
    """API pour le statut du système"""
    return jsonify({
        'status': system_state['status'],
        'last_run': system_state['last_run'],
        'next_run': system_state['next_run'],
        'active_jobs': system_state['active_jobs']
    })

@app.route('/api/stats')
def api_stats():
    """API pour les statistiques"""
    return jsonify(system_state['stats'])

@app.route('/api/logs')
def api_logs():
    """API pour les logs"""
    return jsonify({'logs': system_state['logs']})

@app.route('/api/run/<script_key>', methods=['POST'])
def api_run_script(script_key):
    """API pour exécuter un script"""
    try:
        # Vérifier que la méthode est POST
        if request.method != 'POST':
            return jsonify({'success': False, 'error': 'Méthode non autorisée'}), 405
        
        # Simulation d'exécution
        script_names = {
            'sync': 'Synchronisation Aircall',
            'tasks': 'Création de tâches',
            'assign': 'Assignation intelligente',
            'link': 'Liaison contacts',
            'relations': 'Mise à jour relations'
        }
        
        script_name = script_names.get(script_key, 'Script inconnu')
        
        # Ajouter un log d'exécution
        add_log(f"🚀 Démarrage de {script_name}")
        
        # Simulation d'exécution
        import time
        time.sleep(1)  # Simulation d'un délai d'exécution
        
        # Ajouter un log de succès
        add_log(f"✅ {script_name} exécuté avec succès")
        
        # Mettre à jour les statistiques
        system_state['stats']['total_runs'] += 1
        system_state['stats']['successful_runs'] += 1
        system_state['last_run'] = datetime.now().isoformat()
        
        logger.info(f"Script {script_key} exécuté avec succès")
        
        return jsonify({
            'success': True, 
            'message': f'{script_name} exécuté avec succès',
            'script': script_key,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        error_msg = f"Erreur lors de l'exécution de {script_key}: {str(e)}"
        add_log(f"❌ {error_msg}")
        system_state['stats']['failed_runs'] += 1
        system_state['stats']['last_error'] = error_msg
        
        logger.error(f"Erreur API: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Vérification de santé pour Vercel"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'environment': 'vercel',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 8080))
    
    logger.info(f"Démarrage de l'interface web sur {host}:{port}")
    app.run(host=host, port=port)
