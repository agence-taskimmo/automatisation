#!/usr/bin/env python3
"""
Version optimisée pour Vercel Pro
Création de tâches (timeout 60s)
"""

import os
import sys
import json
import logging
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import get_monday_headers
except ImportError:
    # Utiliser la configuration Vercel
    from config_vercel import get_monday_headers

import requests

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def optimized_task_creation():
    """
    Création de tâches optimisée pour Vercel Pro
    - Limite à 5 tâches maximum
    - Timeout de 50 secondes
    - Traitement simplifié
    """
    try:
        logger.info("🚀 Démarrage création de tâches optimisée")
        
        # Configuration
        MONDAY_API_URL = "https://api.monday.com/v2"
        headers = get_monday_headers()
        
        # Récupérer les appels avec actions IA (limite à 5)
        query = """
        query {
            boards(ids: [2119815514]) {
                items(limit: 5) {
                    id
                    name
                    column_values(ids: ["long_text_mkv8khr", "text_mkv8g3v6"]) {
                        text
                    }
                }
            }
        }
        """
        
        response = requests.post(
            MONDAY_API_URL,
            headers=headers,
            json={"query": query},
            timeout=30
        )
        
        if response.status_code != 200:
            return {"error": f"Erreur Monday.com API: {response.status_code}"}
        
        data = response.json()
        items = data.get('data', {}).get('boards', [{}])[0].get('items', [])
        
        logger.info(f"📋 {len(items)} items récupérés")
        
        # Créer maximum 3 tâches (optimisation)
        created_tasks = 0
        for item in items[:3]:  # Limite à 3 tâches
            try:
                # Récupérer les données de l'item
                actions_text = ""
                agent_name = "Maxence DAVIOT"
                
                for col in item.get('column_values', []):
                    if 'mkv8khr' in col.get('id', ''):  # Actions IA
                        actions_text = col.get('text', '')
                    elif 'mkv8g3v6' in col.get('id', ''):  # Agent
                        agent_name = col.get('text', 'Maxence DAVIOT')
                
                if not actions_text or "Non disponible" in actions_text:
                    continue
                
                # Créer une tâche simplifiée
                task_data = {
                    "query": """
                    mutation ($boardId: ID!, $itemName: String!, $columnValues: JSON!) {
                        create_item (board_id: $boardId, item_name: $itemName, column_values: $columnValues) {
                            id
                        }
                    }
                    """,
                    "variables": {
                        "boardId": "1960967970",  # ID du tableau TO DO LIST
                        "itemName": f"Tâche depuis {item.get('name', 'Appel')}",
                        "columnValues": json.dumps({
                            "text_mkv896hf": agent_name,  # Agent
                            "long_text_mkv8khr": actions_text[:200]  # Actions (tronquées)
                        })
                    }
                }
                
                task_response = requests.post(
                    MONDAY_API_URL,
                    headers=headers,
                    json=task_data,
                    timeout=20
                )
                
                if task_response.status_code == 200:
                    created_tasks += 1
                    logger.info(f"✅ Tâche créée pour {item.get('name')}")
                else:
                    logger.error(f"❌ Erreur création tâche: {task_response.status_code}")
                    
            except Exception as e:
                logger.error(f"❌ Erreur traitement item {item.get('id')}: {str(e)}")
                continue
        
        return {
            "success": True,
            "created_tasks": created_tasks,
            "total_items": len(items),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur création tâches: {str(e)}")
        return {"error": str(e)}

def handler(request):
    """Handler Vercel pour la création de tâches optimisée"""
    result = optimized_task_creation()
    
    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }

# Pour les tests locaux
if __name__ == '__main__':
    result = handler(None)
    print(json.dumps(result, indent=2))
