#!/usr/bin/env python3
"""
Script de configuration des colonnes Monday.com pour l'intégration Aircall
"""

import requests
import json

# Configuration directe
MONDAY_API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjUxMDY4MTEzMywiYWFpIjoxMSwidWlkIjo3NTgyNDkxNSwiaWFkIjoiMjAyNS0wNS0wOVQxMzowMjozNi4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6Mjg2NzMzNDAsInJnbiI6ImV1YzEifQ.dOUcKOgJrE7I4QPW2Fc7SEsOC55RjFE5aJEnr7WrE7I"
MONDAY_BOARD_ID = "2115759144"

def get_board_structure():
    """Récupère la structure complète du tableau Monday.com"""
    headers = {
        "Authorization": MONDAY_API_TOKEN,
        "Content-Type": "application/json",
        "API-Version": "2023-10"
    }
    
    query = """
    query ($boardId: ID!) {
        boards(ids: [$boardId]) {
            columns {
                id
                title
                type
            }
            groups {
                id
                title
            }
        }
    }
    """
    
    try:
        response = requests.post(
            "https://api.monday.com/v2",
            headers=headers,
            json={"query": query, "variables": {"boardId": MONDAY_BOARD_ID}},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            board_data = data.get('data', {}).get('boards', [{}])[0]
            
            columns = board_data.get('columns', [])
            groups = board_data.get('groups', [])
            
            print("📋 STRUCTURE DU TABLEAU MONDAY.COM")
            print("=" * 50)
            
            print("\n🏷️ COLONNES DISPONIBLES:")
            print("-" * 30)
            for col in columns:
                col_id = col.get('id', '')
                col_title = col.get('title', '')
                col_type = col.get('type', '')
                print(f"📝 {col_title}")
                print(f"   ID: {col_id}")
                print(f"   Type: {col_type}")
                print()
            
            print("\n📂 GROUPES DISPONIBLES:")
            print("-" * 30)
            for group in groups:
                group_id = group.get('id', '')
                group_title = group.get('title', '')
                print(f"📁 {group_title}")
                print(f"   ID: {group_id}")
                print()
            
            return columns, groups
        else:
            print(f"❌ Erreur récupération structure: {response.status_code}")
            return [], []
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return [], []

def suggest_aircall_columns():
    """Suggère les colonnes nécessaires pour l'intégration Aircall"""
    print("🎯 COLONNES RECOMMANDÉES POUR L'INTÉGRATION AIRCALL")
    print("=" * 60)
    
    suggested_columns = [
        {
            "name": "ID_Aircall",
            "type": "text",
            "description": "Identifiant unique de l'appel Aircall (format: aircall_123456)",
            "required": True
        },
        {
            "name": "Direction_Appel",
            "type": "status",
            "description": "Direction de l'appel (inbound/outbound)",
            "required": True
        },
        {
            "name": "Statut_Appel",
            "type": "status",
            "description": "Statut de l'appel (initial/answered/done)",
            "required": True
        },
        {
            "name": "Duree_Appel",
            "type": "text",
            "description": "Durée de l'appel en secondes",
            "required": True
        },
        {
            "name": "Date_Debut",
            "type": "date",
            "description": "Date et heure de début de l'appel",
            "required": True
        },
        {
            "name": "Date_Fin",
            "type": "date",
            "description": "Date et heure de fin de l'appel",
            "required": False
        },
        {
            "name": "Transcription_IA",
            "type": "text",
            "description": "Transcription complète de l'appel générée par IA",
            "required": False
        },
        {
            "name": "Resume_IA",
            "type": "text",
            "description": "Résumé automatique de l'appel généré par IA",
            "required": False
        },
        {
            "name": "Sentiment_IA",
            "type": "status",
            "description": "Analyse de sentiment (Positif/Négatif/Neutre)",
            "required": False
        },
        {
            "name": "Sujets_IA",
            "type": "text",
            "description": "Sujets clés identifiés dans l'appel",
            "required": False
        },
        {
            "name": "Actions_IA",
            "type": "text",
            "description": "Actions à suivre identifiées par IA",
            "required": False
        },
        {
            "name": "Type_Source",
            "type": "status",
            "description": "Source des données (Aircall)",
            "required": True
        },
        {
            "name": "Date_Import",
            "type": "date",
            "description": "Date d'import des données",
            "required": True
        }
    ]
    
    print("\n📋 COLONNES NÉCESSAIRES:")
    print("-" * 30)
    for i, col in enumerate(suggested_columns, 1):
        required = "🔴 OBLIGATOIRE" if col["required"] else "🟡 OPTIONNEL"
        print(f"{i:2d}. {col['name']} ({col['type']}) - {required}")
        print(f"    📝 {col['description']}")
        print()
    
    return suggested_columns

def create_column_mapping(columns):
    """Crée un mapping des colonnes suggérées avec les colonnes existantes"""
    print("🔗 MAPPING DES COLONNES")
    print("=" * 30)
    
    # Colonnes existantes par nom
    existing_columns = {col.get('title', ''): col for col in columns}
    
    mapping = {}
    
    # Mapping automatique basé sur les noms similaires
    auto_mappings = {
        "ID": ["ID", "ID_Aircall", "Identifiant"],
        "Titre": ["Titre", "Nom", "Title"],
        "Direction_Appel": ["Direction_Appel", "Direction", "Type_Appel"],
        "Statut_Appel": ["Statut_Appel", "Statut", "Status"],
        "Duree_Appel": ["Duree_Appel", "Duree", "Duration"],
        "Date_Debut": ["Date_Debut", "Date_Debut", "Start_Date"],
        "Date_Fin": ["Date_Fin", "Date_Fin", "End_Date"],
        "Transcription_IA": ["Transcription_IA", "Transcription"],
        "Resume_IA": ["Resume_IA", "Resume", "Summary"],
        "Sentiment_IA": ["Sentiment_IA", "Sentiment"],
        "Sujets_IA": ["Sujets_IA", "Sujets", "Topics"],
        "Actions_IA": ["Actions_IA", "Actions", "Action_Items"],
        "Type_Source": ["Type_Source", "Source"],
        "Date_Import": ["Date_Import", "Import_Date"]
    }
    
    for suggested_name, possible_names in auto_mappings.items():
        found = False
        for possible_name in possible_names:
            if possible_name in existing_columns:
                existing_col = existing_columns[possible_name]
                mapping[suggested_name] = {
                    "id": existing_col.get('id'),
                    "title": existing_col.get('title'),
                    "type": existing_col.get('type')
                }
                print(f"✅ {suggested_name} → {existing_col.get('title')} ({existing_col.get('id')})")
                found = True
                break
        
        if not found:
            print(f"❌ {suggested_name} → COLONNE MANQUANTE")
    
    return mapping

def generate_config_code(mapping):
    """Génère le code de configuration pour le script d'intégration"""
    print("\n🔧 CODE DE CONFIGURATION")
    print("=" * 40)
    
    print("Remplacez le mapping dans aircall_monday_integration.py :")
    print()
    print("column_mapping = {")
    
    for suggested_name, col_info in mapping.items():
        if col_info:
            col_id = col_info.get('id', '')
            print(f"    '{suggested_name}': '{col_id}',")
        else:
            print(f"    '{suggested_name}': 'COLONNE_MANQUANTE',")
    
    print("}")
    print()

def main():
    """Fonction principale"""
    print("🔧 CONFIGURATION DES COLONNES MONDAY.COM POUR AIRCALL")
    print("=" * 60)
    print()
    
    # Récupération de la structure du tableau
    columns, groups = get_board_structure()
    
    if not columns:
        print("❌ Impossible de récupérer la structure du tableau")
        return
    
    # Suggestion des colonnes nécessaires
    suggested_columns = suggest_aircall_columns()
    
    # Création du mapping
    mapping = create_column_mapping(columns)
    
    # Génération du code de configuration
    generate_config_code(mapping)
    
    print("📋 INSTRUCTIONS:")
    print("1. Créez les colonnes manquantes dans votre tableau Monday.com")
    print("2. Remplacez le mapping dans aircall_monday_integration.py")
    print("3. Configurez vos credentials Aircall")
    print("4. Testez l'intégration avec python aircall_monday_integration.py")
    print()
    print("🎯 Colonnes critiques manquantes:")
    
    critical_missing = []
    for suggested_name, col_info in mapping.items():
        if not col_info and suggested_name in ["ID_Aircall", "Direction_Appel", "Statut_Appel"]:
            critical_missing.append(suggested_name)
    
    if critical_missing:
        for col in critical_missing:
            print(f"   ❌ {col}")
    else:
        print("   ✅ Toutes les colonnes critiques sont disponibles")

if __name__ == "__main__":
    main()
