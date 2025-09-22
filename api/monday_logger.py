#!/usr/bin/env python3
"""
Logger spécialisé pour Monday.com
Crée un tableau dédié aux logs d'automatisation
"""

import os
import sys
import json
import logging
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_monday_headers
import requests

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_logs_board():
    """
    Crée un tableau Monday.com dédié aux logs
    """
    try:
        MONDAY_API_URL = "https://api.monday.com/v2"
        headers = get_monday_headers()
        
        # Créer un tableau pour les logs
        create_board = {
            "query": """
            mutation ($boardName: String!) {
                create_board (board_name: $boardName, board_kind: private) {
                    id
                }
            }
            """,
            "variables": {
                "boardName": "📊 Logs Automatisation Taskimmo"
            }
        }
        
        response = requests.post(MONDAY_API_URL, headers=headers, json=create_board, timeout=10)
        
        if response.status_code == 200:
            board_id = response.json()['data']['create_board']['id']
            logger.info(f"✅ Tableau logs créé: {board_id}")
            
            # Ajouter des colonnes au tableau
            add_columns(board_id)
            
            return board_id
        else:
            logger.error(f"❌ Erreur création tableau: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erreur create_logs_board: {str(e)}")
        return None

def add_columns(board_id):
    """
    Ajoute des colonnes au tableau de logs
    """
    try:
        MONDAY_API_URL = "https://api.monday.com/v2"
        headers = get_monday_headers()
        
        columns = [
            {"title": "Timestamp", "type": "date"},
            {"title": "Level", "type": "text"},
            {"title": "Automation", "type": "text"},
            {"title": "Message", "type": "long_text"},
            {"title": "Status", "type": "text"},
            {"title": "Processed", "type": "numbers"},
            {"title": "Total", "type": "numbers"}
        ]
        
        for col in columns:
            add_column = {
                "query": """
                mutation ($boardId: ID!, $title: String!, $type: ColumnType!) {
                    create_column (board_id: $boardId, title: $title, column_type: $type) {
                        id
                    }
                }
                """,
                "variables": {
                    "boardId": board_id,
                    "title": col["title"],
                    "type": col["type"]
                }
            }
            
            requests.post(MONDAY_API_URL, headers=headers, json=add_column, timeout=5)
            
        logger.info("✅ Colonnes ajoutées au tableau logs")
        
    except Exception as e:
        logger.error(f"❌ Erreur add_columns: {str(e)}")

def log_to_monday_board(automation_name, result):
    """
    Log dans le tableau Monday.com dédié
    """
    try:
        MONDAY_API_URL = "https://api.monday.com/v2"
        headers = get_monday_headers()
        
        # ID du tableau de logs (à remplacer par l'ID réel)
        LOGS_BOARD_ID = "LOGS_BOARD_ID_HERE"  # À remplacer
        
        log_item = {
            "query": """
            mutation ($boardId: ID!, $itemName: String!, $columnValues: JSON!) {
                create_item (board_id: $boardId, item_name: $itemName, column_values: $columnValues) {
                    id
                }
            }
            """,
            "variables": {
                "boardId": LOGS_BOARD_ID,
                "itemName": f"{automation_name} - {datetime.now().strftime('%H:%M:%S')}",
                "columnValues": json.dumps({
                    "date": datetime.now().isoformat(),
                    "text": result.get("level", "INFO"),
                    "text_1": automation_name,
                    "long_text": result.get("message", ""),
                    "text_2": "SUCCESS" if result.get("success") else "ERROR",
                    "numbers": result.get("processed", 0),
                    "numbers_1": result.get("total", 0)
                })
            }
        }
        
        response = requests.post(MONDAY_API_URL, headers=headers, json=log_item, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"✅ Log {automation_name} stocké dans Monday.com")
            return True
        else:
            logger.error(f"❌ Erreur stockage log: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur log_to_monday_board: {str(e)}")
        return False

def handler(request):
    """Handler Vercel pour la gestion des logs Monday.com"""
    try:
        if request.method == 'POST':
            data = request.get_json()
            result = log_to_monday_board(
                data.get("automation", "unknown"),
                data.get("result", {})
            )
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "success": result,
                    "timestamp": datetime.now().isoformat()
                })
            }
        else:
            return {
                "statusCode": 405,
                "body": json.dumps({"error": "Method not allowed"})
            }
            
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

# Pour les tests locaux
if __name__ == '__main__':
    result = handler(None)
    print(json.dumps(result, indent=2))
