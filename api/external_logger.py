#!/usr/bin/env python3
"""
Logger pour services externes
Logstash, Elasticsearch, ou services cloud
"""

import os
import sys
import json
import logging
from datetime import datetime
import requests

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_to_elasticsearch(log_data):
    """
    Envoie les logs vers Elasticsearch
    """
    try:
        # Configuration Elasticsearch
        ELASTICSEARCH_URL = os.getenv('ELASTICSEARCH_URL', 'https://your-elasticsearch.com')
        ELASTICSEARCH_INDEX = 'taskimmo-automation-logs'
        
        # Préparer le document
        document = {
            "timestamp": datetime.now().isoformat(),
            "level": log_data.get("level", "INFO"),
            "automation": log_data.get("automation", "unknown"),
            "message": log_data.get("message", ""),
            "data": log_data.get("data", {}),
            "source": "vercel-automation"
        }
        
        # Envoyer vers Elasticsearch
        response = requests.post(
            f"{ELASTICSEARCH_URL}/{ELASTICSEARCH_INDEX}/_doc",
            json=document,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            logger.info("✅ Log envoyé vers Elasticsearch")
            return True
        else:
            logger.error(f"❌ Erreur Elasticsearch: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur log_to_elasticsearch: {str(e)}")
        return False

def log_to_webhook(log_data):
    """
    Envoie les logs vers un webhook externe
    """
    try:
        # Configuration webhook
        WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'https://your-webhook.com/logs')
        
        # Préparer le payload
        payload = {
            "timestamp": datetime.now().isoformat(),
            "level": log_data.get("level", "INFO"),
            "automation": log_data.get("automation", "unknown"),
            "message": log_data.get("message", ""),
            "data": log_data.get("data", {}),
            "source": "vercel-automation"
        }
        
        # Envoyer vers le webhook
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info("✅ Log envoyé vers webhook")
            return True
        else:
            logger.error(f"❌ Erreur webhook: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur log_to_webhook: {str(e)}")
        return False

def log_to_cloudwatch(log_data):
    """
    Envoie les logs vers AWS CloudWatch
    """
    try:
        # Configuration CloudWatch
        CLOUDWATCH_URL = os.getenv('CLOUDWATCH_URL', 'https://logs.amazonaws.com')
        
        # Préparer le log
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": log_data.get("level", "INFO"),
            "automation": log_data.get("automation", "unknown"),
            "message": log_data.get("message", ""),
            "data": log_data.get("data", {}),
            "source": "vercel-automation"
        }
        
        # Envoyer vers CloudWatch
        response = requests.post(
            CLOUDWATCH_URL,
            json=log_entry,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info("✅ Log envoyé vers CloudWatch")
            return True
        else:
            logger.error(f"❌ Erreur CloudWatch: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur log_to_cloudwatch: {str(e)}")
        return False

def handler(request):
    """Handler Vercel pour la gestion des logs externes"""
    try:
        if request.method == 'POST':
            data = request.get_json()
            
            # Essayer plusieurs services
            results = {
                "elasticsearch": log_to_elasticsearch(data),
                "webhook": log_to_webhook(data),
                "cloudwatch": log_to_cloudwatch(data)
            }
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "success": any(results.values()),
                    "results": results,
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
