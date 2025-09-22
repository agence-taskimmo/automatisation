#!/usr/bin/env python3
"""
Version optimisée pour Vercel Pro
Synchronisation Aircall → Monday.com (timeout 60s)
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_monday_headers, get_aircall_headers
import requests

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_automation_start(automation_name):
    """Log le début d'une automatisation"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": "INFO",
        "automation": automation_name,
        "status": "STARTED",
        "message": f"🚀 Démarrage de {automation_name}"
    }
    logger.info(f"📊 LOG START: {json.dumps(log_entry)}")

def log_automation_progress(automation_name, step, details):
    """Log le progrès d'une automatisation"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": "INFO",
        "automation": automation_name,
        "status": "IN_PROGRESS",
        "message": f"🔄 {automation_name} - {step}",
        "data": details
    }
    logger.info(f"📊 LOG PROGRESS: {json.dumps(log_entry)}")

def log_automation_success(automation_name, result):
    """Log le succès d'une automatisation"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": "SUCCESS",
        "automation": automation_name,
        "status": "COMPLETED",
        "message": f"✅ {automation_name} terminé avec succès",
        "data": result
    }
    logger.info(f"📊 LOG SUCCESS: {json.dumps(log_entry)}")

def log_automation_error(automation_name, error):
    """Log une erreur d'automatisation"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": "ERROR",
        "automation": automation_name,
        "status": "FAILED",
        "message": f"❌ {automation_name} échoué: {str(error)}"
    }
    logger.error(f"📊 LOG ERROR: {json.dumps(log_entry)}")

def optimized_aircall_sync():
    """
    Synchronisation optimisée pour Vercel Pro
    - Limite à 10 appels maximum
    - Timeout de 50 secondes
    - Traitement par batch
    """
    try:
        # Log du début
        log_automation_start("sync_aircall")
        logger.info("🚀 Démarrage synchronisation optimisée Aircall")
        
        # Configuration
        AIRCALL_API_URL = "https://api.aircall.io/v1/calls"
        MONDAY_API_URL = "https://api.monday.com/v2"
        
        # Headers
        aircall_headers = get_aircall_headers()
        monday_headers = get_monday_headers()
        
        # Récupérer seulement les 10 derniers appels (optimisation)
        params = {
            'per_page': 10,
            'order': 'desc'
        }
        
        # Log du progrès
        log_automation_progress("sync_aircall", "fetching_calls", {"params": params})
        logger.info("📞 Récupération des 10 derniers appels Aircall...")
        response = requests.get(AIRCALL_API_URL, headers=aircall_headers, params=params, timeout=30)
        
        if response.status_code != 200:
            return {"error": f"Erreur Aircall API: {response.status_code}"}
        
        calls = response.json().get('calls', [])
        logger.info(f"✅ {len(calls)} appels récupérés")
        
        # Traitement par batch de 3 appels maximum
        processed = 0
        for i, call in enumerate(calls[:3]):  # Limite à 3 appels
            if processed >= 3:  # Sécurité timeout
                break
                
            try:
                # Créer l'item Monday.com (version simplifiée)
                monday_data = {
                    "query": """
                    mutation ($boardId: ID!, $itemName: String!, $columnValues: JSON!) {
                        create_item (board_id: $boardId, item_name: $itemName, column_values: $columnValues) {
                            id
                        }
                    }
                    """,
                    "variables": {
                        "boardId": "2119815514",  # ID du tableau Aircall
                        "itemName": f"Appel #{call.get('id', 'N/A')}",
                        "columnValues": json.dumps({
                            "text_mkv8ydgs": str(call.get('id', '')),
                            "text_mkv8khr": call.get('raw_digits', ''),
                            "text_mkv8g3v6": call.get('user', {}).get('name', 'N/A')
                        })
                    }
                }
                
                monday_response = requests.post(
                    MONDAY_API_URL, 
                    headers=monday_headers, 
                    json=monday_data,
                    timeout=20
                )
                
                if monday_response.status_code == 200:
                    processed += 1
                    logger.info(f"✅ Appel {call.get('id')} synchronisé")
                else:
                    logger.error(f"❌ Erreur Monday.com pour l'appel {call.get('id')}")
                    
            except Exception as e:
                logger.error(f"❌ Erreur traitement appel {call.get('id')}: {str(e)}")
                continue
        
        result = {
            "success": True,
            "processed": processed,
            "total_calls": len(calls),
            "timestamp": datetime.now().isoformat()
        }
        
        # Log du succès
        log_automation_success("sync_aircall", result)
        return result
        
    except Exception as e:
        # Log de l'erreur
        log_automation_error("sync_aircall", e)
        logger.error(f"❌ Erreur synchronisation: {str(e)}")
        return {"error": str(e)}

def handler(request):
    """Handler Vercel pour la synchronisation optimisée"""
    result = optimized_aircall_sync()
    
    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }

# Pour les tests locaux
if __name__ == '__main__':
    result = handler(None)
    print(json.dumps(result, indent=2))
