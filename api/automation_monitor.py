#!/usr/bin/env python3
"""
Moniteur d'automatisation en temps réel
Logs détaillés pour surveiller le bon fonctionnement
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

def log_automation_start(automation_name):
    """Log le début d'une automatisation"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": "INFO",
        "automation": automation_name,
        "status": "STARTED",
        "message": f"🚀 Démarrage de {automation_name}",
        "data": {
            "start_time": datetime.now().isoformat(),
            "environment": "vercel",
            "version": "1.0"
        }
    }
    
    logger.info(f"📊 LOG START: {json.dumps(log_entry)}")
    return log_entry

def log_automation_progress(automation_name, step, details):
    """Log le progrès d'une automatisation"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": "INFO",
        "automation": automation_name,
        "status": "IN_PROGRESS",
        "message": f"🔄 {automation_name} - {step}",
        "data": {
            "step": step,
            "details": details,
            "progress_time": datetime.now().isoformat()
        }
    }
    
    logger.info(f"📊 LOG PROGRESS: {json.dumps(log_entry)}")
    return log_entry

def log_automation_success(automation_name, result):
    """Log le succès d'une automatisation"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": "SUCCESS",
        "automation": automation_name,
        "status": "COMPLETED",
        "message": f"✅ {automation_name} terminé avec succès",
        "data": {
            "result": result,
            "processed": result.get("processed", 0),
            "total": result.get("total", 0),
            "duration": "calculé",
            "end_time": datetime.now().isoformat()
        }
    }
    
    logger.info(f"📊 LOG SUCCESS: {json.dumps(log_entry)}")
    return log_entry

def log_automation_error(automation_name, error):
    """Log une erreur d'automatisation"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": "ERROR",
        "automation": automation_name,
        "status": "FAILED",
        "message": f"❌ {automation_name} échoué: {str(error)}",
        "data": {
            "error": str(error),
            "error_type": type(error).__name__,
            "end_time": datetime.now().isoformat()
        }
    }
    
    logger.error(f"📊 LOG ERROR: {json.dumps(log_entry)}")
    return log_entry

def store_log_in_monday(log_entry):
    """Stocke le log dans Monday.com"""
    try:
        MONDAY_API_URL = "https://api.monday.com/v2"
        headers = get_monday_headers()
        
        # Utiliser le tableau Aircall existant pour les logs
        log_item = {
            "query": """
            mutation ($boardId: ID!, $itemName: String!, $columnValues: JSON!) {
                create_item (board_id: $boardId, item_name: $itemName, column_values: $columnValues) {
                    id
                }
            }
            """,
            "variables": {
                "boardId": "2119815514",  # Tableau Aircall
                "itemName": f"📊 {log_entry['automation']} - {log_entry['timestamp'][:19]}",
                "columnValues": json.dumps({
                    "text_mkv8ydgs": log_entry['timestamp'],
                    "text_mkv8khr": log_entry['level'],
                    "text_mkv8g3v6": log_entry['automation'],
                    "long_text_mkv8khr": log_entry['message']
                })
            }
        }
        
        response = requests.post(MONDAY_API_URL, headers=headers, json=log_item, timeout=5)
        
        if response.status_code == 200:
            logger.info("✅ Log stocké dans Monday.com")
            return True
        else:
            logger.error(f"❌ Erreur stockage log: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur store_log_in_monday: {str(e)}")
        return False

@app.route('/api/monitor/start/<automation_name>', methods=['POST'])
def start_monitoring(automation_name):
    """Démarre le monitoring d'une automatisation"""
    try:
        log_entry = log_automation_start(automation_name)
        store_log_in_monday(log_entry)
        
        return jsonify({
            "success": True,
            "message": f"Monitoring démarré pour {automation_name}",
            "log_entry": log_entry
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/monitor/progress/<automation_name>', methods=['POST'])
def log_progress(automation_name):
    """Log le progrès d'une automatisation"""
    try:
        data = request.get_json()
        step = data.get('step', 'Unknown')
        details = data.get('details', {})
        
        log_entry = log_automation_progress(automation_name, step, details)
        store_log_in_monday(log_entry)
        
        return jsonify({
            "success": True,
            "message": f"Progrès loggé pour {automation_name}",
            "log_entry": log_entry
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/monitor/success/<automation_name>', methods=['POST'])
def log_success(automation_name):
    """Log le succès d'une automatisation"""
    try:
        data = request.get_json()
        result = data.get('result', {})
        
        log_entry = log_automation_success(automation_name, result)
        store_log_in_monday(log_entry)
        
        return jsonify({
            "success": True,
            "message": f"Succès loggé pour {automation_name}",
            "log_entry": log_entry
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/monitor/error/<automation_name>', methods=['POST'])
def log_error(automation_name):
    """Log une erreur d'automatisation"""
    try:
        data = request.get_json()
        error = data.get('error', 'Unknown error')
        
        log_entry = log_automation_error(automation_name, error)
        store_log_in_monday(log_entry)
        
        return jsonify({
            "success": True,
            "message": f"Erreur loggée pour {automation_name}",
            "log_entry": log_entry
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/monitor/status', methods=['GET'])
def get_monitoring_status():
    """Statut du système de monitoring"""
    return jsonify({
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "monitoring": {
            "vercel_logs": "Disponible dans Vercel Dashboard",
            "monday_logs": "Stockés dans le tableau Aircall",
            "real_time": "Temps réel activé"
        },
        "endpoints": [
            "/api/monitor/start/<automation_name>",
            "/api/monitor/progress/<automation_name>",
            "/api/monitor/success/<automation_name>",
            "/api/monitor/error/<automation_name>"
        ]
    })

def handler(request):
    """Handler Vercel pour le monitoring"""
    try:
        if request.method == 'GET':
            return get_monitoring_status()
        elif request.method == 'POST':
            # Gérer les différents endpoints de monitoring
            path = request.path
            if '/start/' in path:
                automation_name = path.split('/start/')[1]
                return start_monitoring(automation_name)
            elif '/progress/' in path:
                automation_name = path.split('/progress/')[1]
                return log_progress(automation_name)
            elif '/success/' in path:
                automation_name = path.split('/success/')[1]
                return log_success(automation_name)
            elif '/error/' in path:
                automation_name = path.split('/error/')[1]
                return log_error(automation_name)
            else:
                return {"error": "Endpoint not found"}, 404
        else:
            return {"error": "Method not allowed"}, 405
            
    except Exception as e:
        return {"error": str(e)}, 500

# Pour les tests locaux
if __name__ == '__main__':
    app.run(debug=True)
