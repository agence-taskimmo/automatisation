#!/usr/bin/env python3
"""
Gestionnaire de logs pour Vercel
Stocke les logs dans Monday.com et fichiers locaux
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

def log_to_monday(log_data):
    """
    Stocke les logs dans Monday.com
    Crée un item dans un tableau de logs
    """
    try:
        MONDAY_API_URL = "https://api.monday.com/v2"
        headers = get_monday_headers()
        
        # Créer un item de log dans Monday.com
        log_item = {
            "query": """
            mutation ($boardId: ID!, $itemName: String!, $columnValues: JSON!) {
                create_item (board_id: $boardId, item_name: $itemName, column_values: $columnValues) {
                    id
                }
            }
            """,
            "variables": {
                "boardId": "2119815514",  # ID du tableau Aircall (ou créer un tableau dédié)
                "itemName": f"Log {datetime.now().strftime('%H:%M:%S')}",
                "columnValues": json.dumps({
                    "text_mkv8ydgs": log_data.get("timestamp", ""),
                    "text_mkv8khr": log_data.get("level", "INFO"),
                    "text_mkv8g3v6": log_data.get("message", ""),
                    "long_text_mkv8khr": json.dumps(log_data, indent=2)
                })
            }
        }
        
        response = requests.post(MONDAY_API_URL, headers=headers, json=log_item, timeout=10)
        
        if response.status_code == 200:
            logger.info("✅ Log stocké dans Monday.com")
            return True
        else:
            logger.error(f"❌ Erreur stockage log: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur log_to_monday: {str(e)}")
        return False

def log_to_file(log_data):
    """
    Stocke les logs dans un fichier local
    (Pour Vercel, utilise les logs natifs)
    """
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": log_data.get("level", "INFO"),
            "message": log_data.get("message", ""),
            "data": log_data.get("data", {})
        }
        
        # Log via le système de logging Python
        logger.info(f"📊 LOG: {json.dumps(log_entry)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur log_to_file: {str(e)}")
        return False

def log_automation_result(automation_name, result):
    """
    Log le résultat d'une automatisation
    """
    try:
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": "SUCCESS" if result.get("success") else "ERROR",
            "message": f"Automatisation {automation_name}",
            "data": {
                "automation": automation_name,
                "result": result,
                "processed": result.get("processed", 0),
                "total": result.get("total", 0)
            }
        }
        
        # Stocker dans Monday.com
        log_to_monday(log_data)
        
        # Stocker dans les logs Vercel
        log_to_file(log_data)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur log_automation_result: {str(e)}")
        return False

def get_logs_summary():
    """
    Récupère un résumé des logs
    """
    try:
        # Ici vous pourriez récupérer les logs depuis Monday.com
        # ou depuis un service de logs externe
        
        return {
            "total_logs": "Disponible dans Vercel Dashboard",
            "last_execution": datetime.now().isoformat(),
            "status": "active"
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur get_logs_summary: {str(e)}")
        return {"error": str(e)}

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Endpoint pour récupérer les logs"""
    summary = get_logs_summary()
    return jsonify(summary)

@app.route('/api/logs', methods=['POST'])
def create_log():
    """Endpoint pour créer un log"""
    try:
        log_data = request.get_json()
        result = log_automation_result(log_data.get("automation", "unknown"), log_data)
        
        return jsonify({
            "success": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def handler(request):
    """Handler Vercel pour la gestion des logs"""
    if request.method == 'GET':
        return get_logs()
    elif request.method == 'POST':
        return create_log()
    else:
        return {"error": "Method not allowed"}, 405

# Pour les tests locaux
if __name__ == '__main__':
    app.run(debug=True)
