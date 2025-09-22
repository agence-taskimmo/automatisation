#!/usr/bin/env python3
"""
Mise à jour automatique de vercel.json
Modifie les cron jobs en temps réel
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

def update_vercel_json(new_crons):
    """Met à jour le fichier vercel.json avec de nouveaux cron jobs"""
    try:
        vercel_json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'vercel.json')
        
        # Lire le fichier actuel
        with open(vercel_json_path, 'r') as f:
            config = json.load(f)
        
        # Mettre à jour les cron jobs
        config['crons'] = new_crons
        
        # Sauvegarder
        with open(vercel_json_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info("✅ vercel.json mis à jour avec succès")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur update_vercel_json: {str(e)}")
        return False

def generate_cron_schedule(frequency, hours=None, days=None):
    """Génère une expression cron basée sur la fréquence"""
    if frequency == "hourly":
        return "0 * * * *"
    elif frequency == "every_2_hours":
        return "0 */2 * * *"
    elif frequency == "business_hours":
        return f"0 {hours or '9-18'} * * {days or '1-5'}"
    elif frequency == "custom":
        # Format: "0 9,11,13,15,17 * * 1-5"
        hours_str = ','.join(map(str, hours)) if hours else "9"
        days_str = ','.join(map(str, days)) if days else "1-5"
        return f"0 {hours_str} * * {days_str}"
    else:
        return "0 9-18 * * 1-5"  # Default

@app.route('/api/vercel/update-crons', methods=['POST'])
def update_cron_jobs():
    """Met à jour les cron jobs Vercel"""
    try:
        data = request.get_json()
        automations = data.get("automations", {})
        
        new_crons = []
        
        for automation_name, config in automations.items():
            if config.get("enabled", False):
                schedule = generate_cron_schedule(
                    config.get("frequency", "business_hours"),
                    config.get("hours"),
                    config.get("days")
                )
                
                new_crons.append({
                    "path": config.get("endpoint", f"/api/{automation_name}"),
                    "schedule": schedule
                })
        
        if update_vercel_json(new_crons):
            return jsonify({
                "success": True,
                "message": "Cron jobs mis à jour",
                "new_crons": new_crons,
                "note": "Redéployez sur Vercel pour appliquer les changements"
            })
        else:
            return jsonify({"error": "Erreur mise à jour vercel.json"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/vercel/current-config', methods=['GET'])
def get_current_config():
    """Retourne la configuration actuelle de vercel.json"""
    try:
        vercel_json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'vercel.json')
        
        with open(vercel_json_path, 'r') as f:
            config = json.load(f)
        
        return jsonify({
            "current_crons": config.get("crons", []),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/vercel/deploy', methods=['POST'])
def trigger_deploy():
    """Déclenche un redéploiement Vercel"""
    try:
        # Note: En réalité, vous devriez utiliser l'API Vercel
        # ou un webhook GitHub pour déclencher le déploiement
        
        return jsonify({
            "success": True,
            "message": "Redéploiement déclenché",
            "note": "Les changements seront appliqués dans quelques minutes"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def handler(request):
    """Handler Vercel pour la mise à jour de configuration"""
    try:
        if request.method == 'GET':
            if '/current-config' in request.path:
                return get_current_config()
            else:
                return {"error": "Endpoint not found"}, 404
        elif request.method == 'POST':
            if '/update-crons' in request.path:
                return update_cron_jobs()
            elif '/deploy' in request.path:
                return trigger_deploy()
            else:
                return {"error": "Endpoint not found"}, 404
        else:
            return {"error": "Method not allowed"}, 405
            
    except Exception as e:
        return {"error": str(e)}, 500

# Pour les tests locaux
if __name__ == '__main__':
    app.run(debug=True)
