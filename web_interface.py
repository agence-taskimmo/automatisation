#!/usr/bin/env python3
"""
Interface Web pour la gestion des automatisations Aircall → Monday.com
Interface accessible via navigateur pour contrôler les automatisations à distance
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_socketio import SocketIO, emit
import threading
import time
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import sys
import os

# Ajouter le répertoire courant au path Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import validate_config
from scheduler import AutomationScheduler

# Configuration Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'aircall_automation_secret_key_2025'
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('web_interface.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# État global du système
system_state = {
    'status': 'stopped',  # stopped, running, error
    'last_run': None,
    'next_run': None,
    'active_jobs': [],
    'logs': [],
    'stats': {
        'total_runs': 0,
        'successful_runs': 0,
        'failed_runs': 0,
        'last_error': None
    }
}

# Planificateur global
scheduler = None
scheduler_thread = None

class WebAutomationManager:
    """Gestionnaire des automatisations pour l'interface web"""
    
    def __init__(self):
        self.scripts = {
            'sync': {
                'name': 'Synchronisation Aircall',
                'script': 'aircall_monday_integration_v2.py',
                'description': 'Synchronise les nouveaux appels Aircall'
            },
            'tasks': {
                'name': 'Création de tâches',
                'script': 'create_tasks_with_agent.py',
                'description': 'Crée des tâches depuis les actions IA'
            },
            'assign': {
                'name': 'Assignation intelligente',
                'script': 'smart_task_assigner.py',
                'description': 'Assigne les tâches aux bons agents'
            },
            'link': {
                'name': 'Liaison contacts',
                'script': 'link_calls_to_contacts.py',
                'description': 'Lie les appels aux contacts existants'
            },
            'relations': {
                'name': 'Mise à jour relations',
                'script': 'update_board_relations.py',
                'description': 'Met à jour les relations entre tableaux'
            }
        }
    
    def run_script(self, script_key: str, user: str = "Interface Web") -> dict:
        """Exécute un script et retourne le résultat"""
        try:
            script_info = self.scripts[script_key]
            script_path = Path(script_info['script'])
            
            if not script_path.exists():
                return {
                    'success': False,
                    'error': f"Script non trouvé: {script_info['script']}"
                }
            
            logger.info(f"🚀 Exécution de {script_info['name']} par {user}")
            
            # Exécution du script
            result = subprocess.run(
                [sys.executable, script_info['script']],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info(f"✅ {script_info['name']} exécuté avec succès")
                return {
                    'success': True,
                    'script': script_info['name'],
                    'output': result.stdout,
                    'execution_time': datetime.now().isoformat()
                }
            else:
                error_msg = result.stderr if result.stderr else "Erreur inconnue"
                logger.error(f"❌ {script_info['name']} a échoué: {error_msg}")
                return {
                    'success': False,
                    'script': script_info['name'],
                    'error': error_msg,
                    'execution_time': datetime.now().isoformat()
                }
                
        except subprocess.TimeoutExpired:
            error_msg = f"Timeout pour {script_info['name']} (plus de 5 minutes)"
            logger.error(f"⏰ {error_msg}")
            return {
                'success': False,
                'script': script_info['name'],
                'error': error_msg,
                'execution_time': datetime.now().isoformat()
            }
        except Exception as e:
            error_msg = f"Erreur lors de l'exécution: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                'success': False,
                'script': script_info['name'],
                'error': error_msg,
                'execution_time': datetime.now().isoformat()
            }
    
    def run_full_sync(self, user: str = "Interface Web") -> dict:
        """Exécute la synchronisation complète"""
        logger.info(f"🚀 Synchronisation complète lancée par {user}")
        
        results = {}
        total_scripts = len(self.scripts)
        
        for i, (key, script_info) in enumerate(self.scripts.items(), 1):
            logger.info(f"📋 [{i}/{total_scripts}] {script_info['name']}")
            
            result = self.run_script(key, user)
            results[key] = result
            
            # Pause entre les scripts
            if i < total_scripts:
                time.sleep(5)
        
        # Calcul des statistiques
        success_count = sum(1 for r in results.values() if r['success'])
        
        logger.info(f"📊 Synchronisation complète terminée: {success_count}/{total_scripts} réussies")
        
        return {
            'success': success_count == total_scripts,
            'total_scripts': total_scripts,
            'successful_scripts': success_count,
            'results': results,
            'execution_time': datetime.now().isoformat()
        }

# Instance du gestionnaire
automation_manager = WebAutomationManager()

def start_scheduler():
    """Démarre le planificateur en arrière-plan"""
    global scheduler, system_state
    
    try:
        scheduler = AutomationScheduler()
        scheduler.setup_schedule()
        
        system_state['status'] = 'running'
        system_state['last_run'] = datetime.now().isoformat()
        
        logger.info("✅ Planificateur démarré")
        
        # Boucle de planification
        while system_state['status'] == 'running':
            schedule.run_pending()
            time.sleep(60)  # Vérifier toutes les minutes
            
    except Exception as e:
        logger.error(f"❌ Erreur dans le planificateur: {str(e)}")
        system_state['status'] = 'error'
        system_state['stats']['last_error'] = str(e)

def stop_scheduler():
    """Arrête le planificateur"""
    global system_state
    system_state['status'] = 'stopped'
    logger.info("⏹️ Planificateur arrêté")

# Routes Flask
@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html', system_state=system_state)

@app.route('/dashboard')
def dashboard():
    """Tableau de bord principal"""
    return render_template('dashboard.html', system_state=system_state)

@app.route('/automations')
def automations():
    """Gestion des automatisations"""
    return render_template('automations.html', 
                         scripts=automation_manager.scripts,
                         system_state=system_state)

@app.route('/logs')
def logs():
    """Affichage des logs"""
    return render_template('logs.html', system_state=system_state)

@app.route('/config')
def config():
    """Configuration du système"""
    return render_template('config.html', system_state=system_state)

# API Routes
@app.route('/api/status')
def api_status():
    """API pour récupérer le statut du système"""
    return jsonify(system_state)

@app.route('/api/run/<script_key>', methods=['POST'])
def api_run_script(script_key):
    """API pour exécuter un script"""
    try:
        user = request.json.get('user', 'Interface Web')
        
        if script_key not in automation_manager.scripts:
            return jsonify({'success': False, 'error': 'Script inconnu'}), 400
        
        # Exécuter le script
        result = automation_manager.run_script(script_key, user)
        
        # Mettre à jour les statistiques
        if result['success']:
            system_state['stats']['successful_runs'] += 1
        else:
            system_state['stats']['failed_runs'] += 1
            system_state['stats']['last_error'] = result['error']
        
        system_state['stats']['total_runs'] += 1
        system_state['last_run'] = datetime.now().isoformat()
        
        # Notifier via WebSocket
        socketio.emit('script_result', result)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Erreur API: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/run/full', methods=['POST'])
def api_run_full_sync():
    """API pour exécuter la synchronisation complète"""
    try:
        user = request.json.get('user', 'Interface Web')
        
        # Exécuter la synchronisation complète
        result = automation_manager.run_full_sync(user)
        
        # Mettre à jour les statistiques
        if result['success']:
            system_state['stats']['successful_runs'] += 1
        else:
            system_state['stats']['failed_runs'] += 1
        
        system_state['stats']['total_runs'] += 1
        system_state['last_run'] = datetime.now().isoformat()
        
        # Notifier via WebSocket
        socketio.emit('full_sync_result', result)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Erreur API synchronisation complète: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scheduler/start', methods=['POST'])
def api_start_scheduler():
    """API pour démarrer le planificateur"""
    global scheduler_thread, system_state
    
    try:
        if system_state['status'] == 'running':
            return jsonify({'success': False, 'error': 'Planificateur déjà en cours'})
        
        # Démarrer le planificateur dans un thread séparé
        scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
        scheduler_thread.start()
        
        return jsonify({'success': True, 'message': 'Planificateur démarré'})
        
    except Exception as e:
        logger.error(f"❌ Erreur démarrage planificateur: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scheduler/stop', methods=['POST'])
def api_stop_scheduler():
    """API pour arrêter le planificateur"""
    global system_state
    
    try:
        stop_scheduler()
        return jsonify({'success': True, 'message': 'Planificateur arrêté'})
        
    except Exception as e:
        logger.error(f"❌ Erreur arrêt planificateur: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/logs')
def api_logs():
    """API pour récupérer les logs"""
    try:
        # Lire les derniers logs
        log_file = Path('automation.log')
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Retourner les 100 dernières lignes
                recent_logs = lines[-100:] if len(lines) > 100 else lines
                return jsonify({'logs': recent_logs})
        else:
            return jsonify({'logs': []})
            
    except Exception as e:
        logger.error(f"❌ Erreur lecture logs: {str(e)}")
        return jsonify({'logs': [], 'error': str(e)})

@app.route('/api/config/validate')
def api_validate_config():
    """API pour valider la configuration"""
    try:
        is_valid = validate_config()
        return jsonify({'valid': is_valid})
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)})

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Gestion de la connexion WebSocket"""
    logger.info("🔌 Client WebSocket connecté")
    emit('status_update', system_state)

@socketio.on('disconnect')
def handle_disconnect():
    """Gestion de la déconnexion WebSocket"""
    logger.info("🔌 Client WebSocket déconnecté")

# Fonction de mise à jour périodique
def update_system_state():
    """Met à jour l'état du système périodiquement"""
    while True:
        try:
            # Mettre à jour l'état
            if system_state['status'] == 'running':
                system_state['next_run'] = (datetime.now() + timedelta(minutes=1)).isoformat()
            
            # Notifier les clients WebSocket
            socketio.emit('status_update', system_state)
            
            time.sleep(30)  # Mise à jour toutes les 30 secondes
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour état: {str(e)}")
            time.sleep(60)

if __name__ == '__main__':
    # Démarrer la mise à jour de l'état en arrière-plan
    update_thread = threading.Thread(target=update_system_state, daemon=True)
    update_thread.start()
    
    # Configuration du serveur
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"🚀 Démarrage de l'interface web sur {host}:{port}")
    
    # Démarrer le serveur
    socketio.run(app, host=host, port=port, debug=debug)
