#!/usr/bin/env python3
"""
Création des tâches avec l'agent responsable dans la colonne Admin
"""

import requests
import json
from datetime import datetime

# Configuration
MONDAY_API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjUxMDY4MTEzMywiYWFpIjoxMSwidWlkIjo3NTgyNDkxNSwiaWFkIjoiMjAyNS0wNS0wOVQxMzowMjozNi4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6Mjg2NzMzNDAsInJnbiI6ImV1YzEifQ.dOUcKOgJrE7I4QPW2Fc7SEsOC55RjFE5aJEnr7WrE7I"

# IDs des tableaux
AIRCALL_BOARD_ID = "2119815514"
TASKS_BOARD_ID = "2079297289"
PROSPECT_BOARD_ID = "1960967970"  # 🛒 PROSPECT - Suivi acquéreur
PROPRIETAIRE_BOARD_ID = "1960934403"  # 🏠 PROPRIETAIRE - Suivi vendeur

# Mapping des agents
AGENT_MAPPING = {
    "Maxence Daviot": {"id": 75824915, "name": "Maxence DAVIOT"},
    "Maxence DAVIOT": {"id": 75824915, "name": "Maxence DAVIOT"},
    "Audrey BENOIT": {"id": 75833289, "name": "Audrey BENOIT"},
    "Timothy Robin": {"id": 75833324, "name": "Timothy Robin"},
    "Agent inconnu": {"id": 75824915, "name": "Maxence DAVIOT"},  # Par défaut
}

def create_tasks_with_agent():
    """Crée des tâches avec l'agent responsable dans la colonne Admin"""
    print("📅 CRÉATION DES TÂCHES AVEC AGENT RESPONSABLE")
    print("=" * 60)
    
    headers = {
        "Authorization": MONDAY_API_TOKEN,
        "Content-Type": "application/json",
        "API-Version": "2023-10"
    }
    
    # Étape 1: Récupérer tous les appels Aircall
    print("📞 Étape 1: Récupération de tous les appels Aircall...")
    
    aircall_query = """
    query ($boardId: ID!) {
        boards(ids: [$boardId]) {
            items_page(limit: 100) {
                items {
                    id
                    name
                    created_at
                    column_values {
                        id
                        text
                        value
                    }
                }
            }
        }
    }
    """
    
    try:
        response = requests.post(
            "https://api.monday.com/v2",
            headers=headers,
            json={"query": aircall_query, "variables": {"boardId": AIRCALL_BOARD_ID}},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return
        
        aircall_data = response.json()
        aircall_items = aircall_data.get('data', {}).get('boards', [{}])[0].get('items_page', {}).get('items', [])
        
        print(f"📋 {len(aircall_items)} appels trouvés")
        
        # Filtrer les appels avec des actions IA
        calls_with_actions = []
        
        for item in aircall_items:
            item_name = item.get('name', '')
            created_at = item.get('created_at', '')
            
            # Chercher les actions IA
            actions_ia = []
            client_info = None
            aircall_id = None
            agent_name = None
            
            for col in item.get('column_values', []):
                col_id = col.get('id', '')
                col_text = col.get('text', '')
                col_value = col.get('value', '')
                
                # Récupérer l'ID de l'appel Aircall
                if col_id == 'text_mkv8ydgs' and 'aircall_' in col_text:
                    aircall_id = col_text.replace('aircall_', '')
                
                # Récupérer les actions IA (colonne long_text_mkv8khr)
                if col_id == 'long_text_mkv8khr' and col_text:
                    # Extraire les actions IA (lignes commençant par "🤖 IA:")
                    lines = col_text.split('\n')
                    for line in lines:
                        if line.strip().startswith('🤖 IA:'):
                            action = line.replace('🤖 IA:', '').strip()
                            if action:
                                actions_ia.append(action)
                
                # Récupérer l'agent responsable (colonne text_mkv8g3v6)
                if col_id == 'text_mkv8g3v6' and col_text:
                    agent_name = col_text
                
                # Récupérer l'info client
                if col_id == 'board_relation_mkv8jmms':
                    if col_value and col_value != "{}":
                        try:
                            parsed = json.loads(col_value)
                            linked_ids = parsed.get('linkedPulseIds', [])
                            if linked_ids:
                                client_id = linked_ids[0].get('linkedPulseId')
                                client_info = {'client_id': client_id}
                        except:
                            pass
                
                # Récupérer le type de client
                if col_id == 'text_mkv8s52r':
                    print(f"      🔍 Type client: {col_text}")
                    if 'Acquéreur:' in col_text:
                        client_type = 'acquéreur'
                        print(f"         ✅ Type acquéreur détecté")
                    elif 'Vendeur:' in col_text:
                        client_type = 'vendeur'
                        print(f"         ✅ Type vendeur détecté")
            
            if actions_ia and client_info and aircall_id and client_type:
                # Ajouter le type et le board_id au client_info
                client_info['client_type'] = client_type
                if client_type == 'acquéreur':
                    client_info['board_id'] = PROSPECT_BOARD_ID
                else:  # vendeur
                    client_info['board_id'] = PROPRIETAIRE_BOARD_ID
                    
                calls_with_actions.append({
                    'aircall_id': aircall_id,
                    'item_name': item_name,
                    'actions_ia': actions_ia,
                    'client_info': client_info,
                    'agent_name': agent_name,
                    'created_at': created_at
                })
                print(f"   📞 Appel #{aircall_id}: {len(actions_ia)} actions IA trouvées")
                print(f"   👤 Agent: {agent_name}")
            elif actions_ia and aircall_id:
                print(f"   ⚠️ Appel #{aircall_id}: Actions IA trouvées mais client info incomplet")
        
        print(f"📋 {len(calls_with_actions)} appels avec actions IA trouvés")
        
        # Étape 2: Créer les tâches pour chaque action IA
        print("\n📝 Étape 2: Création des tâches...")
        
        today = datetime.now()
        created_tasks = []
        
        for call in calls_with_actions:
            aircall_id = call['aircall_id']
            item_name = call['item_name']
            actions_ia = call['actions_ia']
            client_info = call['client_info']
            agent_name = call['agent_name']
            
            print(f"\n📞 Appel #{aircall_id}: {item_name[:50]}...")
            print(f"   👥 Client ID: {client_info['client_id']} ({client_info['client_type']})")
            print(f"   👤 Agent: {agent_name}")
            
            # Trouver l'agent dans le mapping
            agent_info = AGENT_MAPPING.get(agent_name, AGENT_MAPPING["Agent inconnu"])
            print(f"   🎯 Agent assigné: {agent_info['name']} (ID: {agent_info['id']})")
            
            for i, action in enumerate(actions_ia):
                print(f"   📝 Action {i+1}: {action[:50]}...")
                
                # Créer la tâche
                task_name = f"{action}"
                
                # Créer la description avec les détails de l'appel
                task_description = f"""Tâche générée automatiquement à partir de l'appel Aircall: Appel #{aircall_id} - {item_name}

Action IA: {action}

Agent responsable: {agent_name}"""
                
                # Créer la tâche
                create_task_query = """
                mutation ($boardId: ID!, $itemName: String!, $columnValues: JSON!) {
                    create_item(board_id: $boardId, item_name: $itemName, column_values: $columnValues) {
                        id
                        name
                    }
                }
                """
                
                # Préparer les valeurs des colonnes
                column_values = {
                    "text9": task_description,  # Description de la tâche
                    "date": {"date": today.strftime("%Y-%m-%d")},  # Date d'aujourd'hui
                    "project_status": {"index": 0},  # En cours
                    "priority_1": {"index": 1},  # Long terme
                    "board_relation_mkv896hf": {  # Colonne Client
                        "item_ids": [client_info['client_id']],
                        "board_id": client_info['board_id']
                    },
                    "project_owner": {  # Colonne Admin
                        "personsAndTeams": [{"id": agent_info['id'], "kind": "person"}]
                    }
                }
                
                try:
                    create_response = requests.post(
                        "https://api.monday.com/v2",
                        headers=headers,
                        json={
                            "query": create_task_query,
                            "variables": {
                                "boardId": TASKS_BOARD_ID,
                                "itemName": task_name,
                                "columnValues": json.dumps(column_values)
                            }
                        },
                        timeout=30
                    )
                    
                    if create_response.status_code == 200:
                        task_data = create_response.json()
                        task_id = task_data.get('data', {}).get('create_item', {}).get('id')
                        if task_id:
                            created_tasks.append({
                                'task_id': task_id,
                                'task_name': task_name,
                                'aircall_id': aircall_id,
                                'client_info': client_info,
                                'agent_name': agent_info['name']
                            })
                            print(f"   ✅ Tâche créée: {task_id}")
                        else:
                            print(f"   ❌ Erreur: Pas d'ID de tâche retourné")
                    else:
                        print(f"   ❌ Erreur HTTP: {create_response.status_code}")
                        print(f"   Response: {create_response.text}")
                        
                except Exception as e:
                    print(f"   ❌ Erreur: {str(e)}")
        
        print(f"\n🎯 RÉSUMÉ:")
        print(f"   ✅ {len(created_tasks)} tâches créées pour aujourd'hui")
        print(f"   📅 Date: {today.strftime('%Y-%m-%d')}")
        
        if created_tasks:
            print(f"\n📋 Tâches créées:")
            for task in created_tasks:
                print(f"   • {task['task_name'][:50]}... (ID: {task['task_id']})")
                print(f"     📞 Appel: #{task['aircall_id']}")
                print(f"     👥 Client: {task['client_info']['client_type']}")
                print(f"     👤 Agent: {task['agent_name']}")
        
    except Exception as e:
        print(f"❌ Erreur générale: {str(e)}")

if __name__ == "__main__":
    create_tasks_with_agent()

