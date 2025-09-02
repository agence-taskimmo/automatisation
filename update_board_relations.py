#!/usr/bin/env python3
"""
Mise à jour des colonnes Connect Boards avec les IDs des contacts
"""

import requests
import json
import re

# Configuration
MONDAY_API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjUxMDY4MTEzMywiYWFpIjoxMSwidWlkIjo3NTgyNDkxNSwiaWFkIjoiMjAyNS0wNS0wOVQxMzowMjozNi4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6Mjg2NzMzNDAsInJnbiI6ImV1YzEifQ.dOUcKOgJrE7I4QPW2Fc7SEsOC55RjFE5aJEnr7WrE7I"

# IDs des tableaux
AIRCALL_BOARD_ID = "2119815514"
VENDEURS_BOARD_ID = "1960934403"
ACQUEREURS_BOARD_ID = "1960967970"

class MondayBoardRelationUpdater:
    """Mise à jour des colonnes Connect Boards"""
    
    def __init__(self):
        self.base_url = "https://api.monday.com/v2"
        self.headers = {
            "Authorization": MONDAY_API_TOKEN,
            "Content-Type": "application/json",
            "API-Version": "2023-10"
        }
    
    def get_board_columns(self, board_id: str):
        """Récupère toutes les colonnes d'un tableau"""
        query = """
        query ($boardId: ID!) {
            boards(ids: [$boardId]) {
                columns {
                    id
                    title
                    type
                }
            }
        }
        """
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={"query": query, "variables": {"boardId": board_id}},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                columns = data.get('data', {}).get('boards', [{}])[0].get('columns', [])
                return columns
            else:
                return []
                
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")
            return []
    
    def get_all_items_with_pagination(self, board_id: str):
        """Récupère tous les items d'un tableau avec pagination"""
        all_items = []
        cursor = None
        
        while True:
            if cursor:
                query = """
                query ($boardId: ID!, $cursor: String!) {
                    boards(ids: [$boardId]) {
                        items_page(limit: 100, cursor: $cursor) {
                            cursor
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
                variables = {"boardId": board_id, "cursor": cursor}
            else:
                query = """
                query ($boardId: ID!) {
                    boards(ids: [$boardId]) {
                        items_page(limit: 100) {
                            cursor
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
                variables = {"boardId": board_id}
            
            try:
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json={"query": query, "variables": variables},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    items_page = data.get('data', {}).get('boards', [{}])[0].get('items_page', {})
                    items = items_page.get('items', [])
                    cursor = items_page.get('cursor')
                    
                    all_items.extend(items)
                    
                    if not cursor or not items:
                        break
                else:
                    print(f"❌ Erreur HTTP: {response.status_code}")
                    break
                    
            except Exception as e:
                print(f"❌ Erreur: {str(e)}")
                break
        
        return all_items
    
    def normalize_phone(self, phone: str) -> str:
        """Normalise un numéro de téléphone"""
        if not phone:
            return ""
        digits_only = re.sub(r'[^\d]', '', phone)
        if digits_only.startswith('33'):
            digits_only = '0' + digits_only[2:]
        elif digits_only.startswith('0033'):
            digits_only = '0' + digits_only[4:]
        return digits_only
    
    def find_contact_by_phone(self, phone: str, contacts: list) -> dict:
        """Trouve un contact par numéro de téléphone"""
        normalized_phone = self.normalize_phone(phone)
        
        for contact in contacts:
            for col in contact.get('column_values', []):
                if 'phone' in col.get('id', '').lower():
                    contact_phone = col.get('text', '')
                    contact_normalized = self.normalize_phone(contact_phone)
                    
                    if contact_normalized == normalized_phone:
                        return contact
        
        return None
    
    def update_board_relation_column(self, item_id: str, column_id: str, linked_item_id: str, linked_board_id: str) -> bool:
        """Met à jour une colonne Connect Boards avec l'ID d'un élément lié"""
        query = """
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
        
        try:
            # Format pour les colonnes Connect Boards
            value = {
                "item_ids": [linked_item_id],
                "linkedPulseIds": [{"linkedPulseId": linked_item_id}]
            }
            
            variables = {
                "boardId": AIRCALL_BOARD_ID,
                "itemId": item_id,
                "columnId": column_id,
                "value": json.dumps(value)
            }
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={"query": query, "variables": variables},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'errors' in data:
                    print(f"❌ Erreur mise à jour: {data['errors']}")
                    return False
                return True
            else:
                print(f"❌ Erreur HTTP: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")
            return False
    
    def update_aircall_relations(self):
        """Met à jour les colonnes Connect Boards des appels Aircall"""
        print("🔗 MISE À JOUR DES COLONNES CONNECT BOARDS")
        print("=" * 60)
        
        # Étape 1: Récupérer les colonnes
        print("\n📋 Étape 1: Récupération des colonnes...")
        
        aircall_columns = self.get_board_columns(AIRCALL_BOARD_ID)
        
        # Trouver les colonnes de liaison
        connecter_col = None
        
        for col in aircall_columns:
            if col.get('title') == 'Connecter' and col.get('type') == 'board_relation':
                connecter_col = col.get('id')
                print(f"✅ Colonne 'Connecter' trouvée: {connecter_col}")
                break
        
        if not connecter_col:
            print("❌ Colonne 'Connecter' non trouvée")
            print("💡 Vérifiez que la colonne 'Connecter' existe et est de type 'Connect Boards'")
            return
        
        # Étape 2: Récupérer tous les items
        print("\n📋 Étape 2: Récupération des items...")
        
        aircall_items = self.get_all_items_with_pagination(AIRCALL_BOARD_ID)
        vendeurs = self.get_all_items_with_pagination(VENDEURS_BOARD_ID)
        acquereurs = self.get_all_items_with_pagination(ACQUEREURS_BOARD_ID)
        
        print(f"📞 {len(aircall_items)} appels Aircall trouvés")
        print(f"👥 {len(vendeurs)} vendeurs trouvés")
        print(f"👤 {len(acquereurs)} acquéreurs trouvés")
        
        # Étape 3: Mettre à jour les liaisons
        print("\n🔗 Étape 3: Mise à jour des liaisons...")
        
        updated_count = 0
        
        for aircall_item in aircall_items:
            # Trouver le numéro de téléphone de l'appel
            phone = None
            
            # Essayer d'abord la colonne Numero_Telephone
            for col in aircall_item.get('column_values', []):
                if col.get('id') == 'text_mkv6syen':  # Colonne Numero_Telephone
                    phone = col.get('text', '')
                    break
            
            # Si pas trouvé dans la colonne, extraire du nom de l'appel
            if not phone:
                item_name = aircall_item.get('name', '')
                if ' - ' in item_name:
                    phone = item_name.split(' - ')[-1]
                    print(f"   📱 Numéro extrait du nom: {phone}")
            
            if not phone:
                print(f"   ❌ Aucun numéro de téléphone trouvé")
                continue
            
            print(f"\n📞 Analyse de: {aircall_item.get('name', 'N/A')} - {phone}")
            print(f"   ID de l'appel: {aircall_item.get('id')}")
            
            # Chercher dans les vendeurs d'abord
            print(f"   🔍 Recherche dans les vendeurs...")
            vendeur_contact = self.find_contact_by_phone(phone, vendeurs)
            if vendeur_contact:
                print(f"   ✅ Vendeur trouvé: {vendeur_contact.get('name', 'N/A')} (ID: {vendeur_contact.get('id')})")
                
                # Mettre à jour la colonne Connecter
                success = self.update_board_relation_column(
                    aircall_item.get('id'),
                    connecter_col,
                    vendeur_contact.get('id'),
                    VENDEURS_BOARD_ID
                )
                
                if success:
                    print(f"   ✅ Colonne 'Connecter' mise à jour avec le vendeur")
                    updated_count += 1
                else:
                    print(f"   ❌ Échec de la mise à jour")
                continue
            
            # Chercher dans les acquéreurs si pas de vendeur trouvé
            print(f"   🔍 Recherche dans les acquéreurs...")
            acquereur_contact = self.find_contact_by_phone(phone, acquereurs)
            if acquereur_contact:
                print(f"   ✅ Acquéreur trouvé: {acquereur_contact.get('name', 'N/A')} (ID: {acquereur_contact.get('id')})")
                
                # Mettre à jour la colonne Connecter
                success = self.update_board_relation_column(
                    aircall_item.get('id'),
                    connecter_col,
                    acquereur_contact.get('id'),
                    ACQUEREURS_BOARD_ID
                )
                
                if success:
                    print(f"   ✅ Colonne 'Connecter' mise à jour avec l'acquéreur")
                    updated_count += 1
                else:
                    print(f"   ❌ Échec de la mise à jour")
                continue
            
            print(f"   ❌ Aucun contact trouvé")
        
        print(f"\n✅ Mise à jour terminée!")
        print(f"📊 Appels mis à jour: {updated_count}")

def main():
    """Fonction principale"""
    updater = MondayBoardRelationUpdater()
    updater.update_aircall_relations()

if __name__ == "__main__":
    main()
