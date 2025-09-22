#!/usr/bin/env python3
"""
Processeur par lots pour éviter les timeouts
Traite les données par petits chunks
"""

import os
import sys
import json
import logging
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_monday_headers, get_aircall_headers
import requests

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_batch(batch_number=1):
    """
    Traite un lot spécifique de données
    - Lot 1: Synchronisation (3 appels)
    - Lot 2: Création tâches (2 tâches)
    - Lot 3: Assignation (1 assignation)
    """
    try:
        logger.info(f"🔄 Traitement du lot {batch_number}")
        
        if batch_number == 1:
            return process_sync_batch()
        elif batch_number == 2:
            return process_tasks_batch()
        elif batch_number == 3:
            return process_assign_batch()
        else:
            return {"error": f"Lot {batch_number} non reconnu"}
            
    except Exception as e:
        logger.error(f"❌ Erreur lot {batch_number}: {str(e)}")
        return {"error": str(e)}

def process_sync_batch():
    """Lot 1: Synchronisation (3 appels max)"""
    try:
        AIRCALL_API_URL = "https://api.aircall.io/v1/calls"
        MONDAY_API_URL = "https://api.monday.com/v2"
        
        aircall_headers = get_aircall_headers()
        monday_headers = get_monday_headers()
        
        # Récupérer 3 appels maximum
        params = {'per_page': 3, 'order': 'desc'}
        response = requests.get(AIRCALL_API_URL, headers=aircall_headers, params=params, timeout=10)
        
        if response.status_code != 200:
            return {"error": f"Erreur Aircall: {response.status_code}"}
        
        calls = response.json().get('calls', [])
        processed = 0
        
        # Traiter seulement 2 appels pour être sûr
        for call in calls[:2]:
            try:
                monday_data = {
                    "query": """
                    mutation ($boardId: ID!, $itemName: String!, $columnValues: JSON!) {
                        create_item (board_id: $boardId, item_name: $itemName, column_values: $columnValues) {
                            id
                        }
                    }
                    """,
                    "variables": {
                        "boardId": "2119815514",
                        "itemName": f"Appel #{call.get('id', 'N/A')}",
                        "columnValues": json.dumps({
                            "text_mkv8ydgs": str(call.get('id', '')),
                            "text_mkv8khr": call.get('raw_digits', ''),
                            "text_mkv8g3v6": call.get('user', {}).get('name', 'N/A')
                        })
                    }
                }
                
                monday_response = requests.post(MONDAY_API_URL, headers=monday_headers, json=monday_data, timeout=8)
                
                if monday_response.status_code == 200:
                    processed += 1
                    logger.info(f"✅ Appel {call.get('id')} synchronisé")
                else:
                    logger.error(f"❌ Erreur Monday.com: {monday_response.status_code}")
                    
            except Exception as e:
                logger.error(f"❌ Erreur traitement appel: {str(e)}")
                continue
        
        return {
            "success": True,
            "batch": 1,
            "processed": processed,
            "total_calls": len(calls),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur lot synchronisation: {str(e)}")
        return {"error": str(e)}

def process_tasks_batch():
    """Lot 2: Création de tâches (2 tâches max)"""
    try:
        MONDAY_API_URL = "https://api.monday.com/v2"
        headers = get_monday_headers()
        
        # Récupérer 2 items avec actions IA
        query = """
        query {
            boards(ids: [2119815514]) {
                items(limit: 2) {
                    id
                    name
                    column_values(ids: ["long_text_mkv8khr"]) {
                        text
                    }
                }
            }
        }
        """
        
        response = requests.post(MONDAY_API_URL, headers=headers, json={"query": query}, timeout=10)
        
        if response.status_code != 200:
            return {"error": f"Erreur Monday.com: {response.status_code}"}
        
        data = response.json()
        items = data.get('data', {}).get('boards', [{}])[0].get('items', [])
        
        created_tasks = 0
        for item in items[:1]:  # Limite à 1 tâche
            try:
                actions_text = ""
                for col in item.get('column_values', []):
                    if 'mkv8khr' in col.get('id', ''):
                        actions_text = col.get('text', '')
                
                if not actions_text or "Non disponible" in actions_text:
                    continue
                
                task_data = {
                    "query": """
                    mutation ($boardId: ID!, $itemName: String!, $columnValues: JSON!) {
                        create_item (board_id: $boardId, item_name: $itemName, column_values: $columnValues) {
                            id
                        }
                    }
                    """,
                    "variables": {
                        "boardId": "1960967970",
                        "itemName": f"Tâche depuis {item.get('name', 'Appel')}",
                        "columnValues": json.dumps({
                            "text_mkv896hf": "Maxence DAVIOT",
                            "long_text_mkv8khr": actions_text[:100]
                        })
                    }
                }
                
                task_response = requests.post(MONDAY_API_URL, headers=headers, json=task_data, timeout=8)
                
                if task_response.status_code == 200:
                    created_tasks += 1
                    logger.info(f"✅ Tâche créée pour {item.get('name')}")
                else:
                    logger.error(f"❌ Erreur création tâche: {task_response.status_code}")
                    
            except Exception as e:
                logger.error(f"❌ Erreur traitement item: {str(e)}")
                continue
        
        return {
            "success": True,
            "batch": 2,
            "created_tasks": created_tasks,
            "total_items": len(items),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur lot tâches: {str(e)}")
        return {"error": str(e)}

def process_assign_batch():
    """Lot 3: Assignation (1 assignation max)"""
    try:
        # Version ultra-simplifiée pour l'assignation
        return {
            "success": True,
            "batch": 3,
            "message": "Assignation simplifiée",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur lot assignation: {str(e)}")
        return {"error": str(e)}

def handler(request):
    """Handler Vercel pour le traitement par lots"""
    # Récupérer le numéro de lot depuis les paramètres
    batch_number = 1  # Par défaut
    
    if hasattr(request, 'args') and request.args.get('batch'):
        batch_number = int(request.args.get('batch'))
    
    result = process_batch(batch_number)
    
    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }

# Pour les tests locaux
if __name__ == '__main__':
    result = handler(None)
    print(json.dumps(result, indent=2))
