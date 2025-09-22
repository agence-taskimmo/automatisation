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

def optimized_aircall_sync():
    """
    Synchronisation optimisée pour Vercel Pro
    - Limite à 10 appels maximum
    - Timeout de 50 secondes
    - Traitement par batch
    """
    try:
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
        
        return {
            "success": True,
            "processed": processed,
            "total_calls": len(calls),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
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
