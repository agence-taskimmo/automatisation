#!/usr/bin/env python3
"""
Assignation intelligente des tâches selon l'agent responsable
"""

import requests
import json

# Configuration
MONDAY_API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjUxMDY4MTEzMywiYWFpIjoxMSwidWlkIjo3NTgyNDkxNSwiaWFkIjoiMjAyNS0wNS0wOVQxMzowMjozNi4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6Mjg2NzMzNDAsInJnbiI6ImV1YzEifQ.dOUcKOgJrE7I4QPW2Fc7SEsOC55RjFE5aJEnr7WrE7I"

# ID du tableau TO DO LIST
TASKS_BOARD_ID = "2079297289"

class SmartTaskAssigner:
    """Assignation intelligente des tâches selon l'agent responsable"""
    
    def __init__(self):
        self.base_url = "https://api.monday.com/v2"
        self.headers = {
            "Authorization": MONDAY_API_TOKEN,
            "Content-Type": "application/json",
            "API-Version": "2023-10"
        }
        
        # Mapping des agents disponibles avec leurs IDs
        self.agent_mapping = {
            "Maxence Daviot": {"name": "Maxence DAVIOT", "id": 75824915},
            "Maxence DAVIOT": {"name": "Maxence DAVIOT", "id": 75824915},
            "Audrey BENOIT": {"name": "Audrey BENOIT", "id": 75833289},
            "Timothy Robin": {"name": "Timothy Robin", "id": 75833324},
            "Assistante": {"name": "Assistante", "id": 13160608, "kind": "team"}
        }
    
    def assign_tasks_intelligently(self):
        """Assigne les tâches aux bonnes personnes selon l'agent responsable"""
        query = """
        query ($boardId: ID!) {
            boards(ids: [$boardId]) {
                items_page(limit: 50) {
                    items {
                        id
                        name
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
                self.base_url,
                headers=self.headers,
                json={"query": query, "variables": {"boardId": TASKS_BOARD_ID}},
                timeout=30
            )
            
            print(f"🧠 ASSIGNATION INTELLIGENTE DES TÂCHES")
            print("=" * 60)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('data', {}).get('boards', [{}])[0].get('items_page', {}).get('items', [])
                
                assigned_count = 0
                skipped_count = 0
                
                for item in items:
                    item_id = item.get('id', '')
                    item_name = item.get('name', '')
                    
                    # Vérifier si c'est une tâche créée automatiquement non assignée
                    is_auto_task = False
                    agent_responsable = ""
                    already_assigned = False
                    
                    for col in item.get('column_values', []):
                        col_id = col.get('id', '')
                        col_text = col.get('text', '')
                        
                        # Vérifier si c'est une tâche auto et récupérer l'agent
                        if col_id == 'text9' and 'Tâche générée automatiquement' in col_text:
                            is_auto_task = True
                            # Extraire l'agent responsable des remarques
                            if 'Agent responsable:' in col_text:
                                agent_line = [line for line in col_text.split('\n') if 'Agent responsable:' in line]
                                if agent_line:
                                    agent_responsable = agent_line[0].replace('Agent responsable:', '').strip()
                        
                        # Vérifier si l'admin est déjà assigné
                        elif col_id == 'project_owner':
                            if col_text:  # Déjà assigné
                                already_assigned = True
                    
                    # Assigner la tâche si elle est auto et non assignée
                    if is_auto_task and not already_assigned and agent_responsable:
                        print(f"📝 Traitement: {item_name[:50]}...")
                        print(f"   👤 Agent responsable: {agent_responsable}")
                        
                        # Trouver l'agent correspondant
                        assigned_agent = None
                        for agent_key, agent_info in self.agent_mapping.items():
                            if agent_key.lower() in agent_responsable.lower() or agent_responsable.lower() in agent_key.lower():
                                assigned_agent = agent_info
                                break
                        
                        if assigned_agent:
                            print(f"   ✅ Assignation à: {assigned_agent['name']}")
                            
                            # Mutation pour assigner l'agent
                            assign_query = """
                            mutation ($boardId: ID!, $itemId: ID!, $columnId: String!, $value: JSON!) {
                                change_column_value (
                                    board_id: $boardId,
                                    item_id: $itemId,
                                    column_id: $columnId,
                                    value: $value
                                ) {
                                    id
                                }
                            }
                            """
                            
                            # Préparer la valeur selon le type (person ou team)
                            if assigned_agent.get('kind') == 'team':
                                value = {
                                    "personsAndTeams": [{"id": assigned_agent['id'], "kind": "team"}]
                                }
                            else:
                                value = {
                                    "personsAndTeams": [{"id": assigned_agent['id'], "kind": "person"}]
                                }
                            
                            variables = {
                                "boardId": TASKS_BOARD_ID,
                                "itemId": item_id,
                                "columnId": "project_owner",
                                "value": json.dumps(value)
                            }
                            
                            assign_response = requests.post(
                                self.base_url,
                                headers=self.headers,
                                json={"query": assign_query, "variables": variables},
                                timeout=30
                            )
                            
                            if assign_response.status_code == 200:
                                assign_data = assign_response.json()
                                if 'errors' in assign_data:
                                    print(f"   ❌ Erreur: {assign_data['errors']}")
                                else:
                                    print(f"   ✅ {assigned_agent['name']} assigné")
                                    assigned_count += 1
                            else:
                                print(f"   ❌ Erreur HTTP: {assign_response.status_code}")
                        else:
                            print(f"   ⚠️ Agent non trouvé: {agent_responsable}")
                            skipped_count += 1
                
                print(f"\n🎯 RÉSUMÉ:")
                print(f"   ✅ {assigned_count} tâches assignées")
                print(f"   ⚠️ {skipped_count} tâches ignorées (agent non trouvé)")
                
            else:
                print(f"❌ Erreur HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")

def main():
    """Fonction principale"""
    assigner = SmartTaskAssigner()
    assigner.assign_tasks_intelligently()

if __name__ == "__main__":
    main()







