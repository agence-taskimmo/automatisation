#!/usr/bin/env python3
"""
Test simple pour Vercel
Vérifie que les fonctions de base fonctionnent
"""

import os
import json
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_function():
    """Fonction de test simple"""
    try:
        logger.info("🚀 Test function démarrée")
        
        # Test des variables d'environnement
        monday_token = os.getenv('MONDAY_API_TOKEN', 'NOT_SET')
        aircall_id = os.getenv('AIRCALL_API_ID', 'NOT_SET')
        
        result = {
            "status": "success",
            "message": "Test function exécutée avec succès",
            "timestamp": "2025-01-22T15:30:00Z",
            "environment": {
                "monday_token_set": monday_token != 'NOT_SET',
                "aircall_id_set": aircall_id != 'NOT_SET'
            }
        }
        
        logger.info(f"✅ Test réussi: {result}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Erreur test: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": "2025-01-22T15:30:00Z"
        }

def handler(request):
    """Handler Vercel pour le test"""
    try:
        result = test_function()
        return {
            'statusCode': 200,
            'headers': { 'Content-Type': 'application/json' },
            'body': json.dumps(result)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': { 'Content-Type': 'application/json' },
            'body': json.dumps({"error": str(e)})
        }
