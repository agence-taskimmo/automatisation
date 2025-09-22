#!/usr/bin/env python3
"""
API Vercel pour l'automatisation 24h/24
Exécute les scripts d'automatisation via des endpoints HTTP
"""

import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def execute_script(script_name, description):
    """Exécute un script Python et retourne le résultat"""
    try:
        logger.info(f"🚀 Exécution de {script_name}: {description}")
        
        # Import dynamique du script
        if script_name == "sync":
            from aircall_monday_integration_v2 import main as sync_main
            result = sync_main()
        elif script_name == "tasks":
            from create_tasks_with_agent import main as tasks_main
            result = tasks_main()
        elif script_name == "assign":
            from smart_task_assigner import main as assign_main
            result = assign_main()
        elif script_name == "link":
            from link_calls_to_contacts import main as link_main
            result = link_main()
        elif script_name == "relations":
            from update_board_relations import main as relations_main
            result = relations_main()
        else:
            return {"error": f"Script {script_name} non reconnu"}
        
        logger.info(f"✅ {script_name} exécuté avec succès")
        return {"success": True, "message": f"{description} exécuté avec succès", "timestamp": datetime.now().isoformat()}
        
    except Exception as e:
        logger.error(f"❌ Erreur dans {script_name}: {str(e)}")
        return {"error": str(e), "timestamp": datetime.now().isoformat()}

@app.route('/api/automation/sync', methods=['POST'])
def sync_aircall():
    """Synchronisation Aircall → Monday.com"""
    return jsonify(execute_script("sync", "Synchronisation Aircall"))

@app.route('/api/automation/tasks', methods=['POST'])
def create_tasks():
    """Création de tâches depuis les actions IA"""
    return jsonify(execute_script("tasks", "Création de tâches"))

@app.route('/api/automation/assign', methods=['POST'])
def assign_tasks():
    """Assignation intelligente des tâches"""
    return jsonify(execute_script("assign", "Assignation des tâches"))

@app.route('/api/automation/link', methods=['POST'])
def link_contacts():
    """Liaison des appels aux contacts"""
    return jsonify(execute_script("link", "Liaison des contacts"))

@app.route('/api/automation/relations', methods=['POST'])
def update_relations():
    """Mise à jour des relations"""
    return jsonify(execute_script("relations", "Mise à jour des relations"))

@app.route('/api/automation/full', methods=['POST'])
def full_automation():
    """Exécution complète de toutes les automatisations"""
    results = {}
    
    # Exécuter toutes les automatisations dans l'ordre
    scripts = [
        ("sync", "Synchronisation Aircall"),
        ("link", "Liaison des contacts"),
        ("tasks", "Création de tâches"),
        ("assign", "Assignation des tâches"),
        ("relations", "Mise à jour des relations")
    ]
    
    for script_name, description in scripts:
        results[script_name] = execute_script(script_name, description)
    
    return jsonify({
        "success": True,
        "message": "Automatisation complète exécutée",
        "results": results,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/automation/status', methods=['GET'])
def get_status():
    """Statut du système d'automatisation"""
    return jsonify({
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "available_endpoints": [
            "/api/automation/sync",
            "/api/automation/tasks", 
            "/api/automation/assign",
            "/api/automation/link",
            "/api/automation/relations",
            "/api/automation/full"
        ]
    })

if __name__ == '__main__':
    app.run(debug=True)
