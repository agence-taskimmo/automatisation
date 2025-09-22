#!/usr/bin/env python3
"""
Planificateur Vercel pour l'automatisation 24h/24
Utilise des webhooks et des fonctions serverless
"""

import os
import sys
import json
import requests
import logging
from datetime import datetime, time
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration des automatisations
AUTOMATION_SCHEDULE = {
    "sync": {
        "frequency": "hourly",  # Toutes les heures
        "hours": list(range(9, 19)),  # 9h à 18h
        "days": [1, 2, 3, 4, 5],  # Lundi à vendredi
        "endpoint": "/api/automation/sync"
    },
    "tasks": {
        "frequency": "2hourly",  # Toutes les 2 heures
        "hours": [9, 11, 13, 15, 17],  # 9h, 11h, 13h, 15h, 17h
        "days": [1, 2, 3, 4, 5],  # Lundi à vendredi
        "endpoint": "/api/automation/tasks"
    },
    "assign": {
        "frequency": "4hourly",  # Toutes les 4 heures
        "hours": [9, 13, 17],  # 9h, 13h, 17h
        "days": [1, 2, 3, 4, 5],  # Lundi à vendredi
        "endpoint": "/api/automation/assign"
    },
    "link": {
        "frequency": "6hourly",  # Toutes les 6 heures
        "hours": [10, 16],  # 10h, 16h
        "days": [1, 2, 3, 4, 5],  # Lundi à vendredi
        "endpoint": "/api/automation/link"
    },
    "relations": {
        "frequency": "daily",  # Une fois par jour
        "hours": [12],  # 12h
        "days": [1, 2, 3, 4, 5],  # Lundi à vendredi
        "endpoint": "/api/automation/relations"
    }
}

def should_run_automation(automation_name, current_time):
    """Détermine si une automatisation doit s'exécuter"""
    config = AUTOMATION_SCHEDULE.get(automation_name)
    if not config:
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

def trigger_automation(automation_name):
    """Déclenche une automatisation"""
    try:
        config = AUTOMATION_SCHEDULE.get(automation_name)
        if not config:
            return {"error": f"Automatisation {automation_name} non trouvée"}
        
        # URL de l'endpoint (à adapter selon votre déploiement Vercel)
        base_url = os.getenv('VERCEL_URL', 'http://localhost:3000')
        endpoint_url = f"{base_url}{config['endpoint']}"
        
        logger.info(f"🚀 Déclenchement de {automation_name} via {endpoint_url}")
        
        # Appel HTTP POST à l'endpoint
        response = requests.post(endpoint_url, timeout=300)
        
        if response.status_code == 200:
            logger.info(f"✅ {automation_name} exécuté avec succès")
            return {"success": True, "response": response.json()}
        else:
            logger.error(f"❌ Erreur HTTP {response.status_code} pour {automation_name}")
            return {"error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        logger.error(f"❌ Erreur dans {automation_name}: {str(e)}")
        return {"error": str(e)}

@app.route('/api/scheduler/check', methods=['GET'])
def check_schedule():
    """Vérifie le planning et exécute les automatisations nécessaires"""
    current_time = datetime.now()
    results = {}
    
    logger.info(f"🕐 Vérification du planning à {current_time.strftime('%H:%M:%S')}")
    
    for automation_name in AUTOMATION_SCHEDULE.keys():
        if should_run_automation(automation_name, current_time):
            logger.info(f"⏰ {automation_name} programmé pour maintenant")
            results[automation_name] = trigger_automation(automation_name)
        else:
            logger.info(f"⏸️ {automation_name} pas programmé pour maintenant")
            results[automation_name] = {"skipped": True, "reason": "Not scheduled"}
    
    return jsonify({
        "timestamp": current_time.isoformat(),
        "results": results
    })

@app.route('/api/scheduler/status', methods=['GET'])
def get_scheduler_status():
    """Statut du planificateur"""
    current_time = datetime.now()
    
    status = {
        "timestamp": current_time.isoformat(),
        "scheduler": "active",
        "automations": {}
    }
    
    for name, config in AUTOMATION_SCHEDULE.items():
        status["automations"][name] = {
            "frequency": config["frequency"],
            "hours": config["hours"],
            "days": config["days"],
            "should_run": should_run_automation(name, current_time)
        }
    
    return jsonify(status)

@app.route('/api/scheduler/trigger/<automation_name>', methods=['POST'])
def trigger_manual(automation_name):
    """Déclenche manuellement une automatisation"""
    result = trigger_automation(automation_name)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
