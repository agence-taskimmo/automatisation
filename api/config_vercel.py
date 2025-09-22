#!/usr/bin/env python3
"""
Configuration simplifiée pour Vercel
Variables d'environnement pour les API
"""

import os
import base64

def get_monday_headers():
    """Headers pour l'API Monday.com"""
    token = os.getenv('MONDAY_API_TOKEN', '')
    return {
        'Authorization': token,
        'Content-Type': 'application/json'
    }

def get_aircall_headers():
    """Headers pour l'API Aircall"""
    api_id = os.getenv('AIRCALL_API_ID', '')
    api_token = os.getenv('AIRCALL_API_TOKEN', '')
    
    if api_id and api_token:
        auth_string = f"{api_id}:{api_token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        return {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/json'
        }
    else:
        return {
            'Content-Type': 'application/json'
        }

def get_board_ids():
    """IDs des tableaux Monday.com"""
    return {
        'aircall_board_id': os.getenv('AIRCALL_BOARD_ID', '2119815514'),
        'tasks_board_id': os.getenv('TASKS_BOARD_ID', '1960967970'),
        'vendeur_board_id': os.getenv('VENDEUR_BOARD_ID', '1960934403'),
        'acquereur_board_id': os.getenv('ACQUEREUR_BOARD_ID', '1960967970')
    }

def get_column_ids():
    """IDs des colonnes Monday.com"""
    return {
        'aircall_id_column': os.getenv('AIRCALL_ID_COLUMN', 'text_mkv8ydgs'),
        'actions_ia_column': os.getenv('ACTIONS_IA_COLUMN', 'long_text_mkv8khr'),
        'agent_name_column': os.getenv('AGENT_NAME_COLUMN', 'text_mkv8g3v6'),
        'contact_lie_column': os.getenv('CONTACT_LIE_COLUMN', 'board_relation_mkv896hf')
    }

def get_agent_mapping():
    """Mapping des agents"""
    return {
        'Maxence Daviot': os.getenv('AGENT_MAXENCE_ID', '123456789'),
        'Agent 2': os.getenv('AGENT_2_ID', '987654321'),
        'Agent 3': os.getenv('AGENT_3_ID', '456789123')
    }
