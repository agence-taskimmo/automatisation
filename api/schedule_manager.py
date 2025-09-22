#!/usr/bin/env python3
"""
Gestionnaire d'horaires pour l'interface Vercel
Permet de modifier les intervalles via l'interface web
"""

import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration des horaires (stockée en mémoire)
SCHEDULE_CONFIG = {
    "sync": {
        "enabled": True,
        "schedule": "0 9-18 * * 1-5",
        "description": "Synchronisation Aircall",
        "last_modified": datetime.now().isoformat()
    },
    "tasks": {
        "enabled": True,
        "schedule": "0 9,11,13,15,17 * * 1-5",
        "description": "Création de tâches",
        "last_modified": datetime.now().isoformat()
    }
}

def update_schedule_config(automation_name, new_schedule):
    """Met à jour la configuration d'un horaire"""
    try:
        if automation_name in SCHEDULE_CONFIG:
            SCHEDULE_CONFIG[automation_name]["schedule"] = new_schedule
            SCHEDULE_CONFIG[automation_name]["last_modified"] = datetime.now().isoformat()
            logger.info(f"✅ Horaires mis à jour pour {automation_name}: {new_schedule}")
            return True
        else:
            logger.error(f"❌ Automatisation {automation_name} non trouvée")
            return False
    except Exception as e:
        logger.error(f"❌ Erreur update_schedule_config: {str(e)}")
        return False

def toggle_automation(automation_name, enabled):
    """Active/désactive une automatisation"""
    try:
        if automation_name in SCHEDULE_CONFIG:
            SCHEDULE_CONFIG[automation_name]["enabled"] = enabled
            SCHEDULE_CONFIG[automation_name]["last_modified"] = datetime.now().isoformat()
            status = "activée" if enabled else "désactivée"
            logger.info(f"✅ {automation_name} {status}")
            return True
        else:
            logger.error(f"❌ Automatisation {automation_name} non trouvée")
            return False
    except Exception as e:
        logger.error(f"❌ Erreur toggle_automation: {str(e)}")
        return False

@app.route('/api/schedule/config', methods=['GET'])
def get_schedule_config():
    """Retourne la configuration actuelle des horaires"""
    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "config": SCHEDULE_CONFIG
    })

@app.route('/api/schedule/config', methods=['POST'])
def update_schedule_config_endpoint():
    """Met à jour la configuration des horaires"""
    try:
        data = request.get_json()
        automation_name = data.get("automation")
        new_schedule = data.get("schedule")
        enabled = data.get("enabled")
        
        if not automation_name:
            return jsonify({"error": "automation name required"}), 400
        
        success = True
        
        if new_schedule:
            success &= update_schedule_config(automation_name, new_schedule)
        
        if enabled is not None:
            success &= toggle_automation(automation_name, enabled)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Configuration mise à jour pour {automation_name}",
                "config": SCHEDULE_CONFIG[automation_name]
            })
        else:
            return jsonify({"error": f"Erreur mise à jour {automation_name}"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/schedule/validate', methods=['POST'])
def validate_schedule():
    """Valide une expression cron"""
    try:
        data = request.get_json()
        schedule = data.get("schedule")
        
        if not schedule:
            return jsonify({"error": "schedule required"}), 400
        
        # Validation simple de l'expression cron
        parts = schedule.split()
        if len(parts) != 5:
            return jsonify({"valid": False, "error": "Format cron invalide"})
        
        # Vérifier que chaque partie est valide
        valid = True
        for part in parts:
            if not part.replace('*', '').replace(',', '').replace('-', '').replace('/', '').isdigit():
                valid = False
                break
        
        return jsonify({
            "valid": valid,
            "schedule": schedule,
            "message": "Format valide" if valid else "Format invalide"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/schedule/preset', methods=['GET'])
def get_schedule_presets():
    """Retourne des presets d'horaires prédéfinis"""
    presets = {
        "hourly": {
            "schedule": "0 * * * *",
            "description": "Toutes les heures"
        },
        "every_2_hours": {
            "schedule": "0 */2 * * *",
            "description": "Toutes les 2 heures"
        },
        "business_hours": {
            "schedule": "0 9-18 * * 1-5",
            "description": "Heures ouvrables (9h-18h, lun-ven)"
        },
        "morning": {
            "schedule": "0 9,12,15 * * 1-5",
            "description": "Matin (9h, 12h, 15h, lun-ven)"
        },
        "evening": {
            "schedule": "0 18,20 * * 1-5",
            "description": "Soir (18h, 20h, lun-ven)"
        }
    }
    
    return jsonify(presets)

def handler(request):
    """Handler Vercel pour le gestionnaire d'horaires"""
    try:
        if request.method == 'GET':
            if '/config' in request.path:
                return get_schedule_config()
            elif '/preset' in request.path:
                return get_schedule_presets()
            else:
                return {"error": "Endpoint not found"}, 404
        elif request.method == 'POST':
            if '/config' in request.path:
                return update_schedule_config_endpoint()
            elif '/validate' in request.path:
                return validate_schedule()
            else:
                return {"error": "Endpoint not found"}, 404
        else:
            return {"error": "Method not allowed"}, 405
            
    except Exception as e:
        return {"error": str(e)}, 500

# Pour les tests locaux
if __name__ == '__main__':
    app.run(debug=True)
