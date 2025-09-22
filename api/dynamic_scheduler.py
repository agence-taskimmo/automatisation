#!/usr/bin/env python3
"""
Planificateur dynamique pour Vercel
Permet de modifier les intervalles via l'interface
"""

import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_monday_headers
import requests

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration dynamique des automatisations
DYNAMIC_SCHEDULE = {
    "sync": {
        "enabled": True,
        "frequency": "hourly",
        "hours": list(range(9, 19)),  # 9h à 18h
        "days": [1, 2, 3, 4, 5],  # Lundi à vendredi
        "endpoint": "/api/optimized_sync"
    },
    "tasks": {
        "enabled": True,
        "frequency": "2hourly",
        "hours": [9, 11, 13, 15, 17],  # 9h, 11h, 13h, 15h, 17h
        "days": [1, 2, 3, 4, 5],  # Lundi à vendredi
        "endpoint": "/api/optimized_tasks"
    }
}

def should_run_automation(automation_name, current_time):
    """Détermine si une automatisation doit s'exécuter selon la config dynamique"""
    config = DYNAMIC_SCHEDULE.get(automation_name)
    if not config or not config.get("enabled", False):
        return False
    
    current_hour = current_time.hour
    current_day = current_time.weekday() + 1  # 1=Lundi, 7=Dimanche
    
    # Vérifier le jour
    if current_day not in config["days"]:
        return False
    
    # Vérifier l'heure
    if current_hour not in config["hours"]:
        return False
    
    return True

def update_schedule(automation_name, new_config):
    """Met à jour la configuration d'une automatisation"""
    try:
        if automation_name in DYNAMIC_SCHEDULE:
            DYNAMIC_SCHEDULE[automation_name].update(new_config)
            logger.info(f"✅ Configuration mise à jour pour {automation_name}")
            return True
        else:
            logger.error(f"❌ Automatisation {automation_name} non trouvée")
            return False
    except Exception as e:
        logger.error(f"❌ Erreur update_schedule: {str(e)}")
        return False

def get_schedule_status():
    """Retourne le statut actuel de toutes les automatisations"""
    current_time = datetime.now()
    
    status = {
        "timestamp": current_time.isoformat(),
        "automations": {}
    }
    
    for name, config in DYNAMIC_SCHEDULE.items():
        status["automations"][name] = {
            "enabled": config.get("enabled", False),
            "frequency": config.get("frequency", "unknown"),
            "hours": config.get("hours", []),
            "days": config.get("days", []),
            "should_run": should_run_automation(name, current_time),
            "next_run": calculate_next_run(name, current_time)
        }
    
    return status

def calculate_next_run(automation_name, current_time):
    """Calcule la prochaine exécution d'une automatisation"""
    config = DYNAMIC_SCHEDULE.get(automation_name)
    if not config or not config.get("enabled", False):
        return "disabled"
    
    # Logique simple pour calculer la prochaine exécution
    current_hour = current_time.hour
    current_day = current_time.weekday() + 1
    
    # Trouver la prochaine heure programmée
    next_hours = [h for h in config["hours"] if h > current_hour]
    if next_hours:
        next_hour = min(next_hours)
        return f"Today at {next_hour}:00"
    else:
        # Demain à la première heure
        next_hour = min(config["hours"])
        return f"Tomorrow at {next_hour}:00"

@app.route('/api/schedule/status', methods=['GET'])
def get_schedule():
    """Retourne le statut du planificateur"""
    return jsonify(get_schedule_status())

@app.route('/api/schedule/update/<automation_name>', methods=['POST'])
def update_automation_schedule(automation_name):
    """Met à jour la configuration d'une automatisation"""
    try:
        data = request.get_json()
        
        # Validation des données
        allowed_fields = ['enabled', 'frequency', 'hours', 'days']
        new_config = {k: v for k, v in data.items() if k in allowed_fields}
        
        if update_schedule(automation_name, new_config):
            return jsonify({
                "success": True,
                "message": f"Configuration mise à jour pour {automation_name}",
                "new_config": DYNAMIC_SCHEDULE[automation_name]
            })
        else:
            return jsonify({"error": f"Erreur mise à jour {automation_name}"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/schedule/trigger/<automation_name>', methods=['POST'])
def trigger_automation_now(automation_name):
    """Déclenche une automatisation immédiatement"""
    try:
        config = DYNAMIC_SCHEDULE.get(automation_name)
        if not config:
            return jsonify({"error": f"Automatisation {automation_name} non trouvée"}), 404
        
        # Déclencher l'automatisation
        endpoint = config.get("endpoint", f"/api/{automation_name}")
        base_url = os.getenv('VERCEL_URL', 'http://localhost:3000')
        endpoint_url = f"{base_url}{endpoint}"
        
        logger.info(f"🚀 Déclenchement manuel de {automation_name}")
        
        # Appel HTTP POST
        response = requests.post(endpoint_url, timeout=60)
        
        if response.status_code == 200:
            return jsonify({
                "success": True,
                "message": f"{automation_name} déclenché avec succès",
                "response": response.json()
            })
        else:
            return jsonify({
                "error": f"Erreur HTTP {response.status_code}",
                "response": response.text
            }), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/schedule/check', methods=['GET'])
def check_schedule():
    """Vérifie le planning et exécute les automatisations nécessaires"""
    current_time = datetime.now()
    results = {}
    
    logger.info(f"🕐 Vérification du planning à {current_time.strftime('%H:%M:%S')}")
    
    for automation_name in DYNAMIC_SCHEDULE.keys():
        if should_run_automation(automation_name, current_time):
            logger.info(f"⏰ {automation_name} programmé pour maintenant")
            # Ici vous pourriez déclencher l'automatisation
            results[automation_name] = {"status": "scheduled", "time": current_time.isoformat()}
        else:
            results[automation_name] = {"status": "not_scheduled", "time": current_time.isoformat()}
    
    return jsonify({
        "timestamp": current_time.isoformat(),
        "results": results
    })

def handler(request):
    """Handler Vercel pour le planificateur dynamique"""
    try:
        if request.method == 'GET':
            if '/status' in request.path:
                return get_schedule()
            elif '/check' in request.path:
                return check_schedule()
            else:
                return {"error": "Endpoint not found"}, 404
        elif request.method == 'POST':
            if '/update/' in request.path:
                automation_name = request.path.split('/update/')[1]
                return update_automation_schedule(automation_name)
            elif '/trigger/' in request.path:
                automation_name = request.path.split('/trigger/')[1]
                return trigger_automation_now(automation_name)
            else:
                return {"error": "Endpoint not found"}, 404
        else:
            return {"error": "Method not allowed"}, 405
            
    except Exception as e:
        return {"error": str(e)}, 500

# Pour les tests locaux
if __name__ == '__main__':
    app.run(debug=True)
