#!/usr/bin/env python3
"""
Interface Web ultra-simplifiée pour Vercel
Version minimale sans templates ni fichiers statiques
"""

from flask import Flask, jsonify
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
            .logs { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; max-height: 300px; overflow-y: auto; }
            .log-entry { margin: 5px 0; font-family: monospace; }
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
                <button class="button" onclick="runScript('sync')">🔄 Synchronisation</button>
                <button class="button" onclick="runScript('tasks')">📝 Créer Tâches</button>
                <button class="button" onclick="runScript('assign')">👥 Assigner</button>
                <button class="button" onclick="runScript('link')">🔗 Lier Contacts</button>
                <button class="button" onclick="runScript('relations')">🔄 Relations</button>
            </div>
            
            <div>
                <h3>📈 Statistiques</h3>
                <p><strong>Total des exécutions:</strong> <span id="total-runs">Chargement...</span></p>
                <p><strong>Succès:</strong> <span id="successful-runs">Chargement...</span></p>
                <p><strong>Échecs:</strong> <span id="failed-runs">Chargement...</span></p>
            </div>
            
            <div class="logs">
                <h3>📋 Logs Récents</h3>
                <div id="logs-container">Chargement des logs...</div>
            </div>
        </div>
        
        <script>
            // Charger les données au démarrage
            loadData();
            
            // Actualiser toutes les 30 secondes
            setInterval(loadData, 30000);
            
            function loadData() {
                // Charger le statut
                fetch('/api/status')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('status').textContent = data.status;
                        document.getElementById('last-run').textContent = new Date(data.last_run).toLocaleString('fr-FR');
                        document.getElementById('next-run').textContent = new Date(data.next_run).toLocaleString('fr-FR');
                    });
                
                // Charger les statistiques
                fetch('/api/stats')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('total-runs').textContent = data.total_runs;
                        document.getElementById('successful-runs').textContent = data.successful_runs;
                        document.getElementById('failed-runs').textContent = data.failed_runs;
                    });
                
                // Charger les logs
                fetch('/api/logs')
                    .then(response => response.json())
                    .then(data => {
                        const logsContainer = document.getElementById('logs-container');
                        logsContainer.innerHTML = data.logs.map(log => 
                            `<div class="log-entry">${log}</div>`
                        ).join('');
                    });
            }
            
            function runScript(scriptKey) {
                fetch('/api/run/' + scriptKey, { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('Script exécuté avec succès !');
                            loadData(); // Recharger les données
                        } else {
                            alert('Erreur: ' + data.error);
                        }
                    })
                    .catch(error => {
                        alert('Erreur de connexion: ' + error);
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
        # Simulation d'exécution
        script_names = {
            'sync': 'Synchronisation Aircall',
            'tasks': 'Création de tâches',
            'assign': 'Assignation intelligente',
            'link': 'Liaison contacts',
            'relations': 'Mise à jour relations'
        }
        
        script_name = script_names.get(script_key, 'Script inconnu')
        
        # Ajouter un log
        log_entry = f"{datetime.now().strftime('%H:%M:%S')} - INFO - {script_name} exécuté via interface web"
        system_state['logs'].append(log_entry)
        
        # Mettre à jour les statistiques
        system_state['stats']['total_runs'] += 1
        system_state['stats']['successful_runs'] += 1
        system_state['last_run'] = datetime.now().isoformat()
        
        # Garder seulement les 50 derniers logs
        if len(system_state['logs']) > 50:
            system_state['logs'] = system_state['logs'][-50:]
        
        return jsonify({'success': True, 'message': f'{script_name} exécuté avec succès'})
        
    except Exception as e:
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
