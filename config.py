#!/usr/bin/env python3
"""
Configuration centralisée pour les automatisations Aircall → Monday.com
Tous les paramètres sont centralisés ici pour faciliter la maintenance
"""

import os
from datetime import time

# =============================================================================
# CONFIGURATION MONDAY.COM
# =============================================================================

# Token API Monday.com
MONDAY_API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjUxMDY4MTEzMywiYWFpIjoxMSwidWlkIjo3NTgyNDkxNSwiaWFkIjoiMjAyNS0wNS0wOVQxMzowMjozNi4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6Mjg2NzMzNDAsInJnbiI6ImV1YzEifQ.dOUcKOgJrE7I4QPW2Fc7SEsOC55RjFE5aJEnr7WrE7I"

# IDs des tableaux Monday.com
BOARD_IDS = {
    'aircall': "2119815514",           # Tableau des appels Aircall
    'todo_list': "2079297289",         # TO DO LIST
    'prospect': "1960967970",          # Tableau PROSPECT (acquéreurs)
    'proprietaire': "1960934403"       # Tableau PROPRIETAIRE (vendeurs)
}

# =============================================================================
# CONFIGURATION AIRCALL
# =============================================================================

# Credentials Aircall
AIRCALL_API_ID = "cc1c0e0e08b34c3394245889a4377872"
AIRCALL_API_TOKEN = "3e5d6de7ef4d4bd1ebbca9c590e2e981"

# =============================================================================
# MAPPING DES AGENTS
# =============================================================================

# Mapping des agents Monday.com
AGENTS = {
    'maxence_daviot': {
        'id': "75824915",
        'name': "Maxence DAVIOT",
        'email': "maxence.daviot@example.com"
    },
    'audrey_benoit': {
        'id': "75833289", 
        'name': "Audrey BENOIT",
        'email': "audrey.benoit@example.com"
    },
    'timothy_robin': {
        'id': "75833324",
        'name': "Timothy Robin",
        'email': "timothy.robin@example.com"
    }
}

# =============================================================================
# CONFIGURATION DES COLONNES
# =============================================================================

# Mapping des colonnes Aircall
AIRCALL_COLUMNS = {
    'ID_Aircall': 'text_mkv8ydgs',
    'Direction_Appel': 'color_mkv8s2zs',
    'Statut_Appel': 'color_mkv87rr1',
    'Duree_Appel': 'numeric_mkv8ke08',
    'Date_Debut': 'date_mkv8ctwx',
    'Date_Fin': 'date_mkv8zk78',
    'Numero_Telephone': 'text_mkv8hgj8',
    'Transcription_IA': 'long_text_mkv83f14',
    'Resume_IA': 'long_text_mkv8ctta',
    'Sentiment_IA': 'color_mkv88j2c',
    'Sujets_IA': 'text_mkv8np3m',
    'Actions_IA': 'long_text_mkv8khr',
    'Type_Source': 'color_mkv8ecf6',
    'Date_Import': 'date_mkv82dj7',
    'Agent_Responsable': 'text_mkv8g3v6',
    'Notes': 'long_text_mkv883fq',
    'Cout_Appel': 'numeric_mkv840v2',
    'Enregistrement': 'link_mkv8zdta',
    'Nom_Contact': 'text_mkv8510p',
    'Repondeur': 'color_mkv8hbc3',
    'Raison_Manque': 'text_mkv8qkkn',
    'Tags': 'text_mkv8jbqh',
    'Commentaires': 'long_text_mkv8ecn3',
    'Devise': 'text_mkv88hze',
    'Equipe': 'text_mkv89zwb'
}

# Mapping des colonnes TO DO LIST
TODO_COLUMNS = {
    'Nom': 'name',
    'Description': 'long_text',
    'Date': 'date',
    'Statut': 'status',
    'Priorite': 'priority',
    'Agent_Responsable': 'person',
    'Client': 'board_relation',
    'Fichiers': 'file',
    'Echeancier': 'timeline'
}

# =============================================================================
# CONFIGURATION DES AUTOMATISATIONS
# =============================================================================

# Paramètres d'exécution
EXECUTION_CONFIG = {
    'timeout': 300,                    # Timeout en secondes pour chaque script
    'retry_attempts': 3,               # Nombre de tentatives en cas d'échec
    'delay_between_calls': 1,          # Délai en secondes entre les appels API
    'max_items_per_batch': 50,         # Nombre maximum d'items traités par lot
    'hours_back': 24                   # Nombre d'heures en arrière pour récupérer les appels
}

# =============================================================================
# CONFIGURATION DU PLANIFICATEUR
# =============================================================================

# Horaires des tâches automatiques
SCHEDULE_CONFIG = {
    'sync_aircall': 'hourly',          # Synchronisation toutes les heures
    'create_tasks': '2h',              # Création de tâches toutes les 2h
    'assign_tasks': '4h',              # Assignation toutes les 4h
    'link_contacts': '6h',             # Liaison contacts toutes les 6h
    'update_relations': 'daily'        # Relations une fois par jour
}

# Horaires spécifiques
SPECIFIC_TIMES = {
    'full_sync': time(8, 0),           # Synchronisation complète à 8h00
    'daily_report': time(18, 0),       # Rapport quotidien à 18h00
    'maintenance': time(2, 0)          # Maintenance à 2h00 du matin
}

# =============================================================================
# CONFIGURATION DES LOGS
# =============================================================================

# Configuration du logging
LOGGING_CONFIG = {
    'log_level': 'INFO',               # Niveau de log (DEBUG, INFO, WARNING, ERROR)
    'log_file': 'automation.log',      # Fichier de log
    'max_log_size_mb': 10,            # Taille maximale du fichier de log en MB
    'backup_logs': True,               # Sauvegarder les anciens logs
    'console_output': True             # Afficher les logs dans la console
}

# =============================================================================
# CONFIGURATION DES RÈGLES D'ASSIGNATION
# =============================================================================

# Règles d'assignation intelligente des tâches
ASSIGNMENT_RULES = {
    'keywords_maxence': [
        'achat', 'vente', 'transaction', 'bien', 'immobilier',
        'maison', 'appartement', 'terrain', 'investissement'
    ],
    'keywords_audrey': [
        'visite', 'rendez-vous', 'planning', 'calendrier',
        'organisation', 'coordination', 'suivi'
    ],
    'keywords_timothy': [
        'technique', 'maintenance', 'réparation', 'rénovation',
        'diagnostic', 'expertise', 'conseil'
    ]
}

# =============================================================================
# CONFIGURATION DES NOTIFICATIONS
# =============================================================================

# Configuration des notifications
NOTIFICATION_CONFIG = {
    'enable_email': False,             # Activer les notifications par email
    'enable_slack': False,             # Activer les notifications Slack
    'enable_monday': True,             # Activer les notifications Monday.com
    'notify_on_success': False,        # Notifier en cas de succès
    'notify_on_error': True,           # Notifier en cas d'erreur
    'notify_on_completion': True       # Notifier à la fin de l'exécution
}

# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def get_agent_by_name(name: str) -> dict:
    """Récupère les informations d'un agent par son nom"""
    for agent_id, agent_info in AGENTS.items():
        if agent_info['name'].lower() == name.lower():
            return agent_info
    return None

def get_agent_by_id(agent_id: str) -> dict:
    """Récupère les informations d'un agent par son ID"""
    for agent_key, agent_info in AGENTS.items():
        if agent_info['id'] == agent_id:
            return agent_info
    return None

def get_board_id(board_name: str) -> str:
    """Récupère l'ID d'un tableau par son nom"""
    return BOARD_IDS.get(board_name.lower())

def get_column_id(board_name: str, column_name: str) -> str:
    """Récupère l'ID d'une colonne selon le tableau"""
    if board_name == 'aircall':
        return AIRCALL_COLUMNS.get(column_name)
    elif board_name == 'todo':
        return TODO_COLUMNS.get(column_name)
    return None

# =============================================================================
# VALIDATION DE LA CONFIGURATION
# =============================================================================

def validate_config():
    """Valide la configuration et affiche les erreurs éventuelles"""
    errors = []
    
    # Vérifier les tokens
    if not MONDAY_API_TOKEN or MONDAY_API_TOKEN == "your_token_here":
        errors.append("Token API Monday.com manquant ou invalide")
    
    if not AIRCALL_API_ID or AIRCALL_API_ID == "your_api_id_here":
        errors.append("API ID Aircall manquant ou invalide")
    
    if not AIRCALL_API_TOKEN or AIRCALL_API_TOKEN == "your_api_token_here":
        errors.append("Token API Aircall manquant ou invalide")
    
    # Vérifier les IDs des tableaux
    for board_name, board_id in BOARD_IDS.items():
        if not board_id or board_id == "your_board_id_here":
            errors.append(f"ID du tableau {board_name} manquant ou invalide")
    
    # Vérifier les agents
    for agent_name, agent_info in AGENTS.items():
        if not agent_info['id'] or not agent_info['name']:
            errors.append(f"Informations manquantes pour l'agent {agent_name}")
    
    if errors:
        print("❌ Erreurs de configuration détectées:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    print("✅ Configuration valide")
    return True

if __name__ == "__main__":
    # Test de la configuration
    print("🔧 Test de la configuration...")
    validate_config()

