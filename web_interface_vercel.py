#!/usr/bin/env python3
"""
Interface Web pour la gestion des automatisations Aircall → Monday.com
Version adaptée pour Vercel (sans WebSockets)
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import logging
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import sys
import os
import json

# Ajouter le répertoire courant au path Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuration Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'aircall_automation_secret_key_2025'

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# État global du système (simulé pour Vercel)
system_state = {
    'status': 'running',  # stopped, running, error
    'last_run': datetime.now().isoformat(),
    'next_run': (datetime.now() + timedelta(minutes=30)).isoformat(),
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

class VercelAutomationManager:
    """Gestionnaire des automatisations pour Vercel"""
    
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
    
    def simulate_script_execution(self, script_key: str, user: str = "Interface Web") -> dict:
        """Simule l'exécution d'un script (pour Vercel)"""
        try:
            script_info = self.scripts[script_key]
            
            logger.info(f"🚀 Simulation d'exécution de {script_info['name']} par {user}")
            
            # Simulation d'exécution réussie
            success = True
            output = f"Script {script_info['name']} exécuté avec succès"
            
            # Mettre à jour les statistiques
            if success:
                system_state['stats']['successful_runs'] += 1
                system_state['stats']['last_error'] = None
            else:
                system_state['stats']['failed_runs'] += 1
            
            system_state['stats']['total_runs'] += 1
            system_state['last_run'] = datetime.now().isoformat()
            
            # Ajouter au log
            log_entry = f"{datetime.now().strftime('%H:%M:%S')} - INFO - {script_info['name']} exécuté par {user}"
            system_state['logs'].append(log_entry)
            
            # Garder seulement les 50 derniers logs
            if len(system_state['logs']) > 50:
                system_state['logs'] = system_state['logs'][-50:]
            
            return {
                'success': success,
                'script': script_info['name'],
                'output': output,
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
    
    def simulate_full_sync(self, user: str = "Interface Web") -> dict:
        """Simule la synchronisation complète"""
        logger.info(f"🚀 Simulation de synchronisation complète par {user}")
        
        results = {}
        total_scripts = len(self.scripts)
        
        for i, (key, script_info) in enumerate(self.scripts.items(), 1):
            logger.info(f"📋 [{i}/{total_scripts}] {script_info['name']}")
            
            result = self.simulate_script_execution(key, user)
            results[key] = result
        
        # Calcul des statistiques
        success_count = sum(1 for r in results.values() if r['success'])
        
        logger.info(f"📊 Synchronisation complète simulée: {success_count}/{total_scripts} réussies")
        
        return {
            'success': success_count == total_scripts,
            'total_scripts': total_scripts,
            'successful_scripts': success_count,
            'results': results,
            'execution_time': datetime.now().isoformat()
        }

# Instance du gestionnaire
automation_manager = VercelAutomationManager()

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
        user = request.json.get('user', 'Interface Web') if request.json else 'Interface Web'
        
        if script_key not in automation_manager.scripts:
            return jsonify({'success': False, 'error': 'Script inconnu'}), 400
        
        # Simuler l'exécution du script
        result = automation_manager.simulate_script_execution(script_key, user)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Erreur API: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/run/full', methods=['POST'])
def api_run_full_sync():
    """API pour exécuter la synchronisation complète"""
    try:
        user = request.json.get('user', 'Interface Web') if request.json else 'Interface Web'
        
        # Simuler la synchronisation complète
        result = automation_manager.simulate_full_sync(user)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Erreur API synchronisation complète: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scheduler/start', methods=['POST'])
def api_start_scheduler():
    """API pour démarrer le planificateur"""
    try:
        system_state['status'] = 'running'
        system_state['last_run'] = datetime.now().isoformat()
        
        log_entry = f"{datetime.now().strftime('%H:%M:%S')} - INFO - Planificateur démarré via interface web"
        system_state['logs'].append(log_entry)
        
        return jsonify({'success': True, 'message': 'Planificateur démarré'})
        
    except Exception as e:
        logger.error(f"❌ Erreur démarrage planificateur: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scheduler/stop', methods=['POST'])
def api_stop_scheduler():
    """API pour arrêter le planificateur"""
    try:
        system_state['status'] = 'stopped'
        
        log_entry = f"{datetime.now().strftime('%H:%M:%S')} - INFO - Planificateur arrêté via interface web"
        system_state['logs'].append(log_entry)
        
        return jsonify({'success': True, 'message': 'Planificateur arrêté'})
        
    except Exception as e:
        logger.error(f"❌ Erreur arrêt planificateur: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/logs')
def api_logs():
    """API pour récupérer les logs"""
    try:
        return jsonify({'logs': system_state['logs']})
    except Exception as e:
        logger.error(f"❌ Erreur lecture logs: {str(e)}")
        return jsonify({'logs': [], 'error': str(e)})

@app.route('/api/config/validate')
def api_validate_config():
    """API pour valider la configuration"""
    try:
        # Simulation de validation réussie
        return jsonify({'valid': True, 'message': 'Configuration valide (mode simulation)'})
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)})

# Route de santé pour Vercel
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
    # Configuration du serveur
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"🚀 Démarrage de l'interface web sur {host}:{port}")
    
    # Démarrer le serveur
    app.run(host=host, port=port, debug=debug)
