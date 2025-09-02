#!/usr/bin/env python3
"""
Création d'un nouveau tableau Monday.com pour les appels Aircall
"""

import requests
import json

# Configuration directe
MONDAY_API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjUxMDY4MTEzMywiYWFpIjoxMSwidWlkIjo3NTgyNDkxNSwiaWFkIjoiMjAyNS0wNS0wOVQxMzowMjozNi4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6Mjg2NzMzNDAsInJnbiI6ImV1YzEifQ.dOUcKOgJrE7I4QPW2Fc7SEsOC55RjFE5aJEnr7WrE7I"

def create_aircall_board():
    """Crée un nouveau tableau pour les appels Aircall"""
    headers = {
        "Authorization": MONDAY_API_TOKEN,
        "Content-Type": "application/json",
        "API-Version": "2023-10"
    }
    
    # Création du tableau
    create_board_query = """
    mutation ($boardName: String!, $boardKind: BoardKind!) {
        create_board (
            board_name: $boardName,
            board_kind: $boardKind
        ) {
            id
            name
        }
    }
    """
    
    try:
        response = requests.post(
            "https://api.monday.com/v2",
            headers=headers,
            json={
                "query": create_board_query,
                "variables": {
                    "boardName": "Appels Aircall - IA",
                    "boardKind": "public"
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                print(f"❌ Erreur création tableau: {data['errors']}")
                return None
            
            board_id = data.get('data', {}).get('create_board', {}).get('id')
            board_name = data.get('data', {}).get('create_board', {}).get('name')
            
            print(f"✅ Tableau créé: {board_name} (ID: {board_id})")
            return board_id
        else:
            print(f"❌ Erreur création tableau: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return None

def create_column(board_id: str, column_title: str, column_type: str):
    """Crée une colonne dans le tableau"""
    headers = {
        "Authorization": MONDAY_API_TOKEN,
        "Content-Type": "application/json",
        "API-Version": "2023-10"
    }
    
    query = """
    mutation ($boardId: ID!, $title: String!, $columnType: ColumnType!) {
        create_column (
            board_id: $boardId,
            title: $title,
            column_type: $columnType
        ) {
            id
            title
        }
    }
    """
    
    try:
        variables = {
            "boardId": board_id,
            "title": column_title,
            "columnType": column_type
        }
        
        response = requests.post(
            "https://api.monday.com/v2",
            headers=headers,
            json={"query": query, "variables": variables},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                print(f"❌ Erreur création colonne {column_title}: {data['errors']}")
                return None
            
            column_id = data.get('data', {}).get('create_column', {}).get('id')
            print(f"✅ Colonne créée: {column_title} (ID: {column_id})")
            return column_id
        else:
            print(f"❌ Erreur création colonne {column_title}: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur création colonne {column_title}: {str(e)}")
        return None

def create_groups(board_id: str):
    """Crée les groupes dans le tableau"""
    headers = {
        "Authorization": MONDAY_API_TOKEN,
        "Content-Type": "application/json",
        "API-Version": "2023-10"
    }
    
    groups = [
        "Appels Entrants",
        "Appels Sortants", 
        "Appels avec IA",
        "Appels sans IA"
    ]
    
    created_groups = {}
    
    for group_name in groups:
        query = """
        mutation ($boardId: ID!, $groupName: String!) {
            create_group (
                board_id: $boardId,
                group_name: $groupName
            ) {
                id
                title
            }
        }
        """
        
        try:
            response = requests.post(
                "https://api.monday.com/v2",
                headers=headers,
                json={
                    "query": query,
                    "variables": {
                        "boardId": board_id,
                        "groupName": group_name
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'errors' in data:
                    print(f"❌ Erreur création groupe {group_name}: {data['errors']}")
                    continue
                
                group_id = data.get('data', {}).get('create_group', {}).get('id')
                created_groups[group_name] = group_id
                print(f"✅ Groupe créé: {group_name} (ID: {group_id})")
            else:
                print(f"❌ Erreur création groupe {group_name}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erreur création groupe {group_name}: {str(e)}")
    
    return created_groups

def main():
    """Fonction principale"""
    print("🚀 CRÉATION DU TABLEAU AIRCALL")
    print("=" * 40)
    
    # 1. Création du tableau
    print("\n📋 Étape 1: Création du tableau...")
    board_id = create_aircall_board()
    
    if not board_id:
        print("❌ Impossible de créer le tableau")
        return
    
    # 2. Création des colonnes
    print("\n🏷️ Étape 2: Création des colonnes...")
    
    columns_config = [
        # Colonnes de base
        ("ID_Aircall", "text"),
        ("Direction_Appel", "status"),
        ("Statut_Appel", "status"),
        ("Duree_Appel", "numbers"),
        ("Date_Debut", "date"),
        ("Date_Fin", "date"),
        ("Numero_Telephone", "text"),
        
        # Colonnes IA
        ("Transcription_IA", "long_text"),
        ("Resume_IA", "long_text"),
        ("Sentiment_IA", "status"),
        ("Sujets_IA", "text"),
        ("Actions_IA", "long_text"),
        
        # Colonnes métadonnées
        ("Type_Source", "status"),
        ("Date_Import", "date"),
        ("Agent_Responsable", "text"),
        ("Notes", "long_text")
    ]
    
    created_columns = {}
    
    for col_config in columns_config:
        col_title = col_config[0]
        col_type = col_config[1]
        
        column_id = create_column(board_id, col_title, col_type)
        if column_id:
            created_columns[col_title] = column_id
        
        # Pause entre les créations
        import time
        time.sleep(1)
    
    # 3. Création des groupes
    print("\n📂 Étape 3: Création des groupes...")
    created_groups = create_groups(board_id)
    
    # 4. Génération du code de configuration
    print("\n🔧 CODE DE CONFIGURATION")
    print("=" * 40)
    print(f"MONDAY_BOARD_ID = \"{board_id}\"")
    print()
    print("column_mapping = {")
    for col_title, col_id in created_columns.items():
        print(f"    '{col_title}': '{col_id}',")
    print("}")
    print()
    print("group_mapping = {")
    for group_name, group_id in created_groups.items():
        print(f"    '{group_name}': '{group_id}',")
    print("}")
    
    print("\n✅ Tableau Aircall créé avec succès!")
    print(f"📋 ID du tableau: {board_id}")
    print(f"🏷️ Colonnes créées: {len(created_columns)}")
    print(f"📂 Groupes créés: {len(created_groups)}")

if __name__ == "__main__":
    main()
