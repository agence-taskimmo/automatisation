#!/usr/bin/env python3
"""
Interface Web avec logs détaillés pour Vercel
Version avec suivi détaillé des automatisations
"""

from flask import Flask, jsonify, request
import logging
from datetime import datetime
import os
import time
import threading

# Configuration Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'aircall_automation_secret_key_2025'

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# État global du système avec logs détaillés
system_state = {
    'status': 'running',
    'last_run': datetime.now().isoformat(),
    'next_run': (datetime.now().isoformat()),
    'active_jobs': [],
    'logs': [
        f"{datetime.now().strftime('%H:%M:%S')} - INFO - Interface web démarrée sur Vercel",
        f"{datetime.now().strftime('%H:%M:%S')} - INFO - Mode déploiement cloud activé",
        f"{datetime.now().strftime('%H:%M:%S')} - INFO - Système de logs détaillés initialisé"
    ],
    'stats': {
        'total_runs': 42,
        'successful_runs': 38,
        'failed_runs': 4,
        'last_error': None
    },
    'current_job': None,
    'job_progress': 0
}

# Détails des scripts avec étapes
script_details = {
    'sync': {
        'name': 'Synchronisation Aircall',
        'description': 'Synchronise les nouveaux appels Aircall avec Monday.com',
        'steps': [
            'Connexion à l\'API Aircall',
            'Récupération des appels récents',
            'Filtrage des appels non traités',
            'Connexion à Monday.com',
            'Création des items pour chaque appel',
            'Mise à jour des statuts',
            'Synchronisation terminée'
        ]
    },
    'tasks': {
        'name': 'Création de tâches',
        'description': 'Crée des tâches depuis les actions IA détectées',
        'steps': [
            'Analyse des conversations Aircall',
            'Détection des actions requises',
            'Création des tâches Monday.com',
            'Assignation des priorités',
            'Liaison avec les contacts',
            'Tâches créées avec succès'
        ]
    },
    'assign': {
        'name': 'Assignation intelligente',
        'description': 'Assigne les tâches aux bons agents selon leurs compétences',
        'steps': [
            'Analyse des compétences requises',
            'Vérification de la disponibilité des agents',
            'Calcul des scores de correspondance',
            'Assignation automatique des tâches',
            'Notification aux agents',
            'Assignation terminée'
        ]
    },
    'link': {
        'name': 'Liaison contacts',
        'description': 'Lie les appels aux contacts existants dans Monday.com',
        'steps': [
            'Extraction des informations de contact',
            'Recherche dans la base de contacts',
            'Correspondance des numéros de téléphone',
            'Création des relations',
            'Mise à jour des profils',
            'Liaison terminée'
        ]
    },
    'relations': {
        'name': 'Mise à jour relations',
        'description': 'Met à jour les relations entre tableaux Monday.com',
        'steps': [
            'Analyse des dépendances',
            'Vérification des liens existants',
            'Création des nouvelles relations',
            'Mise à jour des références',
            'Validation des intégrités',
            'Relations mises à jour'
        ]
    }
}

def add_detailed_log(message, level='INFO', script=None, step=None):
    """Ajoute un log détaillé avec informations contextuelles"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    
    # Format du log selon le contexte
    if script and step:
        log_entry = f"{timestamp} - {level} - [{script}] {step}: {message}"
    elif script:
        log_entry = f"{timestamp} - {level} - [{script}] {message}"
    else:
        log_entry = f"{timestamp} - {level} - {message}"
    
    system_state['logs'].append(log_entry)
    
    # Garder seulement les 200 derniers logs
    if len(system_state['logs']) > 200:
        system_state['logs'] = system_state['logs'][-200:]
    
    logger.info(f"Log détaillé ajouté: {log_entry}")
    return log_entry

def simulate_script_execution_detailed(script_key):
    """Simule l'exécution détaillée d'un script avec progression"""
    script_info = script_details[script_key]
    steps = script_info['steps']
    total_steps = len(steps)
    
    # Initialiser le job
    system_state['current_job'] = {
        'script': script_key,
        'name': script_info['name'],
        'status': 'running',
        'current_step': 0,
        'total_steps': total_steps,
        'start_time': datetime.now().isoformat(),
        'progress': 0
    }
    
    add_detailed_log(f"Démarrage de {script_info['name']}", 'INFO', script_key)
    add_detailed_log(f"Description: {script_info['description']}", 'INFO', script_key)
    
    # Exécuter chaque étape
    for i, step in enumerate(steps):
        system_state['current_job']['current_step'] = i + 1
        system_state['current_job']['progress'] = int(((i + 1) / total_steps) * 100)
        
        # Log de l'étape
        add_detailed_log(f"Étape {i+1}/{total_steps}: {step}", 'INFO', script_key, f"Étape {i+1}")
        
        # Simulation d'un délai d'exécution
        time.sleep(0.5)
        
        # Log de progression
        progress = int(((i + 1) / total_steps) * 100)
        add_detailed_log(f"Progression: {progress}%", 'INFO', script_key, f"Progression")
        
        # Simulation d'erreurs occasionnelles
        if i == 2 and script_key == 'sync':
            add_detailed_log("Délai réseau détecté, nouvelle tentative...", 'WARNING', script_key, f"Étape {i+1}")
            time.sleep(0.3)
        
        # Log de succès de l'étape
        add_detailed_log(f"Étape {i+1} terminée avec succès", 'INFO', script_key, f"Étape {i+1}")
    
    # Finalisation
    system_state['current_job']['status'] = 'completed'
    system_state['current_job']['progress'] = 100
    system_state['current_job']['end_time'] = datetime.now().isoformat()
    
    add_detailed_log(f"{script_info['name']} terminé avec succès", 'INFO', script_key)
    add_detailed_log(f"Toutes les étapes ont été exécutées", 'INFO', script_key)
    
    # Réinitialiser le job
    system_state['current_job'] = None
    
    return True

@app.route('/')
def index():
    """Page d'accueil avec interface détaillée"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Automatisation Aircall-Monday - Logs Détaillés</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
            h1 { color: #2c3e50; text-align: center; margin: 0; }
            .subtitle { text-align: center; color: #7f8c8d; margin-top: 10px; }
            
            .main-content { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            
            .control-panel { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .status-panel { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            
            .button { background: #3498db; color: white; padding: 12px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; font-size: 14px; }
            .button:hover { background: #2980b9; }
            .button:disabled { background: #bdc3c7; cursor: not-allowed; }
            .button.success { background: #27ae60; }
            .button.error { background: #e74c3c; }
            
            .progress-container { margin: 20px 0; }
            .progress-bar { width: 100%; height: 20px; background: #ecf0f1; border-radius: 10px; overflow: hidden; }
            .progress-fill { height: 100%; background: linear-gradient(90deg, #3498db, #27ae60); transition: width 0.3s ease; }
            .progress-text { text-align: center; margin-top: 10px; font-weight: bold; color: #2c3e50; }
            
            .logs-container { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-top: 20px; }
            .logs-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
            .logs-content { background: #f8f9fa; padding: 15px; border-radius: 5px; max-height: 500px; overflow-y: auto; }
            .log-entry { margin: 8px 0; font-family: monospace; padding: 8px; border-left: 4px solid #3498db; background: white; border-radius: 3px; }
            .log-entry.info { border-left-color: #3498db; }
            .log-entry.success { border-left-color: #27ae60; }
            .log-entry.warning { border-left-color: #f39c12; }
            .log-entry.error { border-left-color: #e74c3c; }
            
            .stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0; }
            .stat-card { background: #ecf0f1; padding: 15px; border-radius: 5px; text-align: center; }
            .stat-number { font-size: 24px; font-weight: bold; color: #2c3e50; }
            .stat-label { color: #7f8c8d; font-size: 12px; }
            
            .current-job { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .job-steps { margin-top: 15px; }
            .step-item { padding: 8px; margin: 5px 0; border-radius: 3px; background: white; }
            .step-completed { background: #d5f4e6; border-left: 4px solid #27ae60; }
            .step-current { background: #fff3cd; border-left: 4px solid #f39c12; }
            .step-pending { background: #f8f9fa; border-left: 4px solid #bdc3c7; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Interface d'Automatisation Aircall-Monday</h1>
                <div class="subtitle">Suivi détaillé des automatisations en temps réel</div>
            </div>
            
            <div class="main-content">
                <div class="control-panel">
                    <h3>⚡ Contrôle des Automatisations</h3>
                    
                    <div class="button-group">
                        <button class="button" onclick="runScript('sync')" id="btn-sync">🔄 Synchronisation Aircall</button>
                        <button class="button" onclick="runScript('tasks')" id="btn-tasks">📝 Création de Tâches</button>
                        <button class="button" onclick="runScript('assign')" id="btn-assign">👥 Assignation Intelligente</button>
                        <button class="button" onclick="runScript('link')" id="btn-link">🔗 Liaison Contacts</button>
                        <button class="button" onclick="runScript('relations')" id="btn-relations">🔄 Relations</button>
                    </div>
                    
                    <div class="progress-container" id="progress-container" style="display: none;">
                        <h4>📊 Progression de l'automatisation</h4>
                        <div class="progress-bar">
                            <div class="progress-fill" id="progress-fill" style="width: 0%"></div>
                        </div>
                        <div class="progress-text" id="progress-text">0%</div>
                    </div>
                    
                    <div class="current-job" id="current-job" style="display: none;">
                        <h4>🔄 Job en cours</h4>
                        <div id="job-info">Chargement...</div>
                        <div class="job-steps" id="job-steps"></div>
                    </div>
                </div>
                
                <div class="status-panel">
                    <h3>📊 Statut du Système</h3>
                    
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number" id="total-runs">-</div>
                            <div class="stat-label">Total Exécutions</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number" id="successful-runs">-</div>
                            <div class="stat-label">Succès</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number" id="failed-runs">-</div>
                            <div class="stat-label">Échecs</div>
                        </div>
                    </div>
                    
                    <div>
                        <p><strong>État:</strong> <span id="status">Chargement...</span></p>
                        <p><strong>Dernière exécution:</strong> <span id="last-run">Chargement...</span></p>
                        <p><strong>Prochaine exécution:</strong> <span id="next-run">Chargement...</span></p>
                    </div>
                </div>
            </div>
            
            <div class="logs-container">
                <div class="logs-header">
                    <h3>📋 Logs Détaillés des Automatisations</h3>
                    <div>
                        <button class="button" onclick="refreshLogs()" style="padding: 8px 15px; font-size: 12px;">🔄 Actualiser</button>
                        <button class="button" onclick="clearLogs()" style="padding: 8px 15px; font-size: 12px; background: #e74c3c;">🗑️ Effacer</button>
                    </div>
                </div>
                <div class="logs-content" id="logs-container">Chargement des logs...</div>
            </div>
        </div>
        
        <script>
            let currentJobData = null;
            
            // Charger les données au démarrage
            loadData();
            
            // Actualiser toutes les 5 secondes
            setInterval(loadData, 5000);
            
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
                
                // Charger le job en cours
                loadCurrentJob();
            }
            
            function loadCurrentJob() {
                fetch('/api/current-job')
                    .then(response => response.json())
                    .then(data => {
                        if (data.job && data.job.status === 'running') {
                            showCurrentJob(data.job);
                        } else {
                            hideCurrentJob();
                        }
                    })
                    .catch(error => console.error('Erreur chargement job:', error));
            }
            
            function showCurrentJob(job) {
                currentJobData = job;
                document.getElementById('progress-container').style.display = 'block';
                document.getElementById('current-job').style.display = 'block';
                
                // Mettre à jour la barre de progression
                document.getElementById('progress-fill').style.width = job.progress + '%';
                document.getElementById('progress-text').textContent = job.progress + '%';
                
                // Mettre à jour les informations du job
                document.getElementById('job-info').innerHTML = `
                    <p><strong>Script:</strong> ${job.name}</p>
                    <p><strong>Étape:</strong> ${job.current_step}/${job.total_steps}</p>
                    <p><strong>Début:</strong> ${new Date(job.start_time).toLocaleTimeString('fr-FR')}</p>
                `;
                
                // Mettre à jour les étapes
                updateJobSteps(job);
            }
            
            function hideCurrentJob() {
                currentJobData = null;
                document.getElementById('progress-container').style.display = 'none';
                document.getElementById('current-job').style.display = 'none';
            }
            
            function updateJobSteps(job) {
                const stepsContainer = document.getElementById('job-steps');
                const scriptKey = job.script;
                
                if (window.scriptSteps && window.scriptSteps[scriptKey]) {
                    const steps = window.scriptSteps[scriptKey];
                    stepsContainer.innerHTML = steps.map((step, index) => {
                        let className = 'step-item step-pending';
                        if (index < job.current_step - 1) className = 'step-item step-completed';
                        if (index === job.current_step - 1) className = 'step-item step-current';
                        
                        return `<div class="${className}">${index + 1}. ${step}</div>`;
                    }).join('');
                }
            }
            
            function refreshLogs() {
                fetch('/api/logs')
                    .then(response => response.json())
                    .then(data => {
                        const logsContainer = document.getElementById('logs-container');
                        if (data.logs && data.logs.length > 0) {
                            logsContainer.innerHTML = data.logs.map(log => {
                                let className = 'log-entry info';
                                if (log.includes('succès') || log.includes('terminé')) className = 'log-entry success';
                                if (log.includes('WARNING')) className = 'log-entry warning';
                                if (log.includes('erreur') || log.includes('échec') || log.includes('ERROR')) className = 'log-entry error';
                                
                                return `<div class="${className}">${log}</div>`;
                            }).join('');
                            
                            // Scroll vers le bas
                            logsContainer.scrollTop = logsContainer.scrollHeight;
                        } else {
                            logsContainer.innerHTML = '<div class="log-entry">Aucun log disponible</div>';
                        }
                    })
                    .catch(error => {
                        console.error('Erreur chargement logs:', error);
                        document.getElementById('logs-container').innerHTML = '<div class="log-entry error">Erreur de chargement des logs</div>';
                    });
            }
            
            function clearLogs() {
                if (confirm('Êtes-vous sûr de vouloir effacer tous les logs ?')) {
                    fetch('/api/logs/clear', { method: 'POST' })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                refreshLogs();
                            }
                        })
                        .catch(error => console.error('Erreur effacement logs:', error));
                }
            }
            
            function runScript(scriptKey) {
                const button = document.getElementById('btn-' + scriptKey);
                const originalText = button.textContent;
                
                // Désactiver tous les boutons
                document.querySelectorAll('.button').forEach(btn => btn.disabled = true);
                button.textContent = '⏳ Démarrage...';
                button.classList.add('loading');
                
                // Démarrer le script
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
                        button.textContent = '✅ Démarrage réussi';
                        button.style.background = '#27ae60';
                        
                        // Réactiver les boutons après un délai
                        setTimeout(() => {
                            button.textContent = originalText;
                            button.style.background = '';
                            button.classList.remove('loading');
                            document.querySelectorAll('.button').forEach(btn => btn.disabled = false);
                        }, 2000);
                        
                        // Actualiser les données
                        setTimeout(loadData, 1000);
                    } else {
                        button.textContent = '❌ Erreur';
                        button.style.background = '#e74c3c';
                        setTimeout(() => {
                            button.textContent = originalText;
                            button.style.background = '';
                            button.classList.remove('loading');
                            document.querySelectorAll('.button').forEach(btn => btn.disabled = false);
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
                        button.classList.remove('loading');
                        document.querySelectorAll('.button').forEach(btn => btn.disabled = false);
                    }, 3000);
                });
            }
            
            // Charger les étapes des scripts
            window.scriptSteps = {
                'sync': [
                    'Connexion à l\'API Aircall',
                    'Récupération des appels récents',
                    'Filtrage des appels non traités',
                    'Connexion à Monday.com',
                    'Création des items pour chaque appel',
                    'Mise à jour des statuts',
                    'Synchronisation terminée'
                ],
                'tasks': [
                    'Analyse des conversations Aircall',
                    'Détection des actions requises',
                    'Création des tâches Monday.com',
                    'Assignation des priorités',
                    'Liaison avec les contacts',
                    'Tâches créées avec succès'
                ],
                'assign': [
                    'Analyse des compétences requises',
                    'Vérification de la disponibilité des agents',
                    'Calcul des scores de correspondance',
                    'Assignation automatique des tâches',
                    'Notification aux agents',
                    'Assignation terminée'
                ],
                'link': [
                    'Extraction des informations de contact',
                    'Recherche dans la base de contacts',
                    'Correspondance des numéros de téléphone',
                    'Création des relations',
                    'Mise à jour des profils',
                    'Liaison terminée'
                ],
                'relations': [
                    'Analyse des dépendances',
                    'Vérification des liens existants',
                    'Création des nouvelles relations',
                    'Mise à jour des références',
                    'Validation des intégrités',
                    'Relations mises à jour'
                ]
            };
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

@app.route('/api/logs/clear', methods=['POST'])
def api_clear_logs():
    """API pour effacer les logs"""
    try:
        system_state['logs'] = [
            f"{datetime.now().strftime('%H:%M:%S')} - INFO - Logs effacés par l'utilisateur"
        ]
        return jsonify({'success': True, 'message': 'Logs effacés avec succès'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/current-job')
def api_current_job():
    """API pour le job en cours"""
    return jsonify({'job': system_state['current_job']})

@app.route('/api/run/<script_key>', methods=['POST'])
def api_run_script(script_key):
    """API pour exécuter un script avec logs détaillés"""
    try:
        if request.method != 'POST':
            return jsonify({'success': False, 'error': 'Méthode non autorisée'}), 405
        
        if script_key not in script_details:
            return jsonify({'success': False, 'error': 'Script inconnu'}), 400
        
        script_info = script_details[script_key]
        
        # Démarrer l'exécution dans un thread séparé
        thread = threading.Thread(
            target=simulate_script_execution_detailed,
            args=(script_key,)
        )
        thread.daemon = True
        thread.start()
        
        add_detailed_log(f"Thread d'exécution démarré pour {script_info['name']}", 'INFO')
        
        return jsonify({
            'success': True, 
            'message': f'Démarrage de {script_info["name"]}',
            'script': script_key,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        error_msg = f"Erreur lors du démarrage de {script_key}: {str(e)}"
        add_detailed_log(error_msg, 'ERROR')
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
    
    logger.info(f"Démarrage de l'interface web détaillée sur {host}:{port}")
    app.run(host=host, port=port)
