#!/usr/bin/env python3
"""
Fonction Vercel Cron pour l'automatisation 24h/24
S'exécute automatiquement selon un planning défini
"""

import os
import sys
import json
import requests
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handler(request):
    """
    Handler principal pour les tâches cron Vercel
    S'exécute automatiquement selon le planning configuré
    """
    
    # URL de base de votre déploiement Vercel
    base_url = os.getenv('VERCEL_URL', 'http://localhost:3000')
    
    current_time = datetime.now()
    logger.info(f"🕐 Exécution cron à {current_time.strftime('%H:%M:%S')}")
    
    results = {}
    
    # Définir le planning des automatisations
    schedule = {
        "sync": {
            "hours": list(range(9, 19)),  # 9h à 18h
            "days": [1, 2, 3, 4, 5],  # Lundi à vendredi
            "endpoint": "/api/automation/sync"
        },
        "tasks": {
            "hours": [9, 11, 13, 15, 17],  # 9h, 11h, 13h, 15h, 17h
            "days": [1, 2, 3, 4, 5],  # Lundi à vendredi
            "endpoint": "/api/automation/tasks"
        },
        "assign": {
            "hours": [9, 13, 17],  # 9h, 13h, 17h
            "days": [1, 2, 3, 4, 5],  # Lundi à vendredi
            "endpoint": "/api/automation/assign"
        },
        "link": {
            "hours": [10, 16],  # 10h, 16h
            "days": [1, 2, 3, 4, 5],  # Lundi à vendredi
            "endpoint": "/api/automation/link"
        },
        "relations": {
            "hours": [12],  # 12h
            "days": [1, 2, 3, 4, 5],  # Lundi à vendredi
            "endpoint": "/api/automation/relations"
        }
    }
    
    # Vérifier quelles automatisations doivent s'exécuter
    current_hour = current_time.hour
    current_day = current_time.weekday() + 1  # 1=Lundi, 7=Dimanche
    
    for automation_name, config in schedule.items():
        should_run = (
            current_day in config["days"] and 
            current_hour in config["hours"]
        )
        
        if should_run:
            logger.info(f"⏰ Exécution de {automation_name}")
            
            try:
                # Appel à l'endpoint d'automatisation
                endpoint_url = f"{base_url}{config['endpoint']}"
                response = requests.post(endpoint_url, timeout=300)
                
                if response.status_code == 200:
                    results[automation_name] = {
                        "success": True,
                        "response": response.json()
                    }
                    logger.info(f"✅ {automation_name} exécuté avec succès")
                else:
                    results[automation_name] = {
                        "error": f"HTTP {response.status_code}"
                    }
                    logger.error(f"❌ Erreur HTTP {response.status_code} pour {automation_name}")
                    
            except Exception as e:
                results[automation_name] = {
                    "error": str(e)
                }
                logger.error(f"❌ Erreur dans {automation_name}: {str(e)}")
        else:
            logger.info(f"⏸️ {automation_name} pas programmé pour {current_hour}h")
            results[automation_name] = {
                "skipped": True,
                "reason": f"Not scheduled for {current_hour}h"
            }
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "timestamp": current_time.isoformat(),
            "results": results
        })
    }

# Pour les tests locaux
if __name__ == '__main__':
    result = handler(None)
    print(json.dumps(result, indent=2))
