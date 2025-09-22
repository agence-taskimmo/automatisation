#!/usr/bin/env python3
"""
Liaison des appels Aircall aux prospects/vendeurs existants
"""

import requests
import json
import time
import re
from datetime import datetime

# Configuration directe
MONDAY_API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjUxMDY4MTEzMywiYWFpIjoxMSwidWlkIjo3NTgyNDkxNSwiaWFkIjoiMjAyNS0wNS0wOVQxMzowMjozNi4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6Mjg2NzMzNDAsInJnbiI6ImV1YzEifQ.dOUcKOgJrE7I4QPW2Fc7SEsOC55RjFE5aJEnr7WrE7I"

# IDs des tableaux
AIRCALL_BOARD_ID = "2119815514"
VENDEURS_BOARD_ID = "1960934403"
ACQUEREURS_BOARD_ID = "1960967970"

class PhoneNumberMatcher:
    """Classe pour normaliser et comparer les numéros de téléphone"""
    
    @staticmethod
    def normalize_phone(phone: str) -> str:
        """Normalise un numéro de téléphone pour la comparaison"""
        if not phone:
            return ""
        
        # Supprimer tous les caractères non numériques
        digits_only = re.sub(r'[^\d]', '', phone)
        
        # Gérer les numéros français
        if digits_only.startswith('33'):
            digits_only = '0' + digits_only[2:]
        elif digits_only.startswith('0033'):
            digits_only = '0' + digits_only[4:]
        
        # S'assurer qu'on a un numéro français valide (10 chiffres)
        if len(digits_only) == 10 and digits_only.startswith('0'):
            return digits_only
        
        return digits_only
    
    @staticmethod
    def phones_match(phone1: str, phone2: str) -> bool:
        """Vérifie si deux numéros de téléphone correspondent"""
        norm1 = PhoneNumberMatcher.normalize_phone(phone1)
        norm2 = PhoneNumberMatcher.normalize_phone(phone2)
        
        return norm1 == norm2 and norm1 != ""

class MondayContactLinker:
    """Liaison des appels aux contacts Monday.com"""
    
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
            return []
    
    def get_all_items(self, board_id: str):
        """Récupère tous les items d'un tableau avec pagination"""
        all_items = []
        cursor = None
        
        while True:
            # Construire la requête avec pagination
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
                    
                    # Si pas de cursor ou pas d'items, on a fini
                    if not cursor or not items:
                        break
                else:
                    print(f"❌ Erreur HTTP: {response.status_code}")
                    break
                    
            except Exception as e:
                print(f"❌ Erreur: {str(e)}")
                break
        
        return all_items
    
    def create_contact_column(self, title: str) -> str:
        """Crée une nouvelle colonne pour le contact lié"""
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
                "boardId": AIRCALL_BOARD_ID,
                "title": title,
                "columnType": "text"
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
                    print(f"❌ Erreur création colonne: {data['errors']}")
                    return None
                
                column_id = data.get('data', {}).get('create_column', {}).get('id')
                return column_id
            else:
                return None
                
        except Exception as e:
            return None
    
    def update_contact_column(self, item_id: str, column_id: str, value: str) -> bool:
        """Met à jour la colonne contact"""
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
                result = response.json()
                if 'errors' in result:
                    return False
                else:
                    return True
            else:
                return False
                
        except Exception as e:
            return False

def main():
    """Fonction principale"""
    print("🔗 LIAISON DES APPELS AUX CONTACTS")
    print("=" * 50)
    
    linker = MondayContactLinker()
    matcher = PhoneNumberMatcher()
    
    # 1. Vérifier si la colonne Contact_Lié existe déjà
    print("\n📋 Étape 1: Vérification de la colonne Contact_Lié...")
    aircall_columns = linker.get_board_columns(AIRCALL_BOARD_ID)
    
    contact_column_id = None
    for col in aircall_columns:
        if col['title'] == 'Contact_Lié':
            contact_column_id = col['id']
            print(f"✅ Colonne Contact_Lié trouvée (ID: {contact_column_id})")
            break
    
    if not contact_column_id:
        print("➕ Création de la colonne Contact_Lié...")
        contact_column_id = linker.create_contact_column('Contact_Lié')
        if contact_column_id:
            print(f"✅ Colonne Contact_Lié créée (ID: {contact_column_id})")
        else:
            print("❌ Impossible de créer la colonne Contact_Lié")
            return
    
    # 2. Récupération des vendeurs
    print(f"\n👥 Étape 2: Récupération des vendeurs...")
    vendeurs = linker.get_all_items(VENDEURS_BOARD_ID)
    print(f"📋 {len(vendeurs)} vendeurs trouvés (avec pagination)")
    
    # Trouver la colonne téléphone des vendeurs
    vendeurs_columns = linker.get_board_columns(VENDEURS_BOARD_ID)
    vendeurs_phone_column_id = None
    for col in vendeurs_columns:
        if col['title'] == 'Téléphone':
            vendeurs_phone_column_id = col['id']
            break
    
    if not vendeurs_phone_column_id:
        print("❌ Colonne Téléphone non trouvée dans le tableau vendeurs")
        return
    
    # Créer un dictionnaire vendeurs par téléphone
    vendeurs_by_phone = {}
    for vendeur in vendeurs:
        vendeur_id = vendeur['id']
        vendeur_name = vendeur['name']
        
        for col in vendeur.get('column_values', []):
            if col.get('id') == vendeurs_phone_column_id:
                phone = col.get('text', '')
                if phone:
                    normalized_phone = matcher.normalize_phone(phone)
                    if normalized_phone:
                        vendeurs_by_phone[normalized_phone] = {
                            'id': vendeur_id,
                            'name': vendeur_name,
                            'type': 'Vendeur'
                        }
                break
    
    print(f"📞 {len(vendeurs_by_phone)} vendeurs avec numéro de téléphone")
    
    # 3. Récupération des acquéreurs
    print(f"\n👤 Étape 3: Récupération des acquéreurs...")
    acquereurs = linker.get_all_items(ACQUEREURS_BOARD_ID)
    print(f"📋 {len(acquereurs)} acquéreurs trouvés (avec pagination)")
    
    # Trouver la colonne téléphone des acquéreurs
    acquereurs_columns = linker.get_board_columns(ACQUEREURS_BOARD_ID)
    acquereurs_phone_column_id = None
    for col in acquereurs_columns:
        if col['title'] == 'Téléphone':
            acquereurs_phone_column_id = col['id']
            break
    
    if not acquereurs_phone_column_id:
        print("❌ Colonne Téléphone non trouvée dans le tableau acquéreurs")
        return
    
    # Créer un dictionnaire acquéreurs par téléphone
    acquereurs_by_phone = {}
    for acquereur in acquereurs:
        acquereur_id = acquereur['id']
        acquereur_name = acquereur['name']
        
        for col in acquereur.get('column_values', []):
            if col.get('id') == acquereurs_phone_column_id:
                phone = col.get('text', '')
                if phone:
                    normalized_phone = matcher.normalize_phone(phone)
                    if normalized_phone:
                        acquereurs_by_phone[normalized_phone] = {
                            'id': acquereur_id,
                            'name': acquereur_name,
                            'type': 'Acquéreur'
                        }
                break
    
    print(f"📞 {len(acquereurs_by_phone)} acquéreurs avec numéro de téléphone")
    
    # 4. Récupération des appels Aircall
    print(f"\n📞 Étape 4: Récupération des appels Aircall...")
    aircall_items = linker.get_all_items(AIRCALL_BOARD_ID)
    print(f"📋 {len(aircall_items)} items trouvés")
    
    # Trouver la colonne téléphone des appels Aircall
    aircall_phone_column_id = None
    for col in aircall_columns:
        if col['title'] == 'Numero_Telephone':
            aircall_phone_column_id = col['id']
            break
    
    if not aircall_phone_column_id:
        print("❌ Colonne Numero_Telephone non trouvée dans le tableau Aircall")
        return
    
    # 5. Liaison des appels aux contacts
    print(f"\n🔗 Étape 5: Liaison des appels aux contacts...")
    success_count = 0
    error_count = 0
    
    for item in aircall_items:
        item_id = item['id']
        item_name = item['name']
        
        # Vérifier si c'est un item Aircall
        aircall_id = None
        for col in item.get('column_values', []):
            if col.get('id') == 'text_mkv8ydgs':  # ID_Aircall
                call_id_text = col.get('text', '')
                if call_id_text.startswith('aircall_'):
                    aircall_id = call_id_text.replace('aircall_', '')
                    break
        
        if not aircall_id:
            print(f"⏭️ Ignoré (pas un item Aircall): {item_name}")
            continue
        
        # Récupérer le numéro de téléphone de l'appel
        call_phone = None
        for col in item.get('column_values', []):
            if col.get('id') == aircall_phone_column_id:
                call_phone = col.get('text', '')
                break
        
        if not call_phone:
            print(f"📞 Pas de numéro pour: {item_name}")
            continue
        
        normalized_call_phone = matcher.normalize_phone(call_phone)
        if not normalized_call_phone:
            print(f"📞 Numéro invalide pour: {item_name} ({call_phone})")
            continue
        
        print(f"\n📞 Analyse de: {item_name}")
        print(f"   Numéro: {call_phone} (normalisé: {normalized_call_phone})")
        
        # Chercher dans les vendeurs
        if normalized_call_phone in vendeurs_by_phone:
            contact = vendeurs_by_phone[normalized_call_phone]
            contact_info = f"{contact['type']}: {contact['name']} (ID: {contact['id']})"
            
            if linker.update_contact_column(item_id, contact_column_id, contact_info):
                print(f"   ✅ Lié au vendeur: {contact['name']}")
                success_count += 1
            else:
                print(f"   ❌ Erreur liaison vendeur")
                error_count += 1
        
        # Chercher dans les acquéreurs
        elif normalized_call_phone in acquereurs_by_phone:
            contact = acquereurs_by_phone[normalized_call_phone]
            contact_info = f"{contact['type']}: {contact['name']} (ID: {contact['id']})"
            
            if linker.update_contact_column(item_id, contact_column_id, contact_info):
                print(f"   ✅ Lié à l'acquéreur: {contact['name']}")
                success_count += 1
            else:
                print(f"   ❌ Erreur liaison acquéreur")
                error_count += 1
        
        else:
            print(f"   ❌ Aucun contact trouvé")
            # Marquer comme "Non trouvé"
            if linker.update_contact_column(item_id, contact_column_id, "Contact non trouvé"):
                print(f"   ✅ Marqué comme 'Contact non trouvé'")
            error_count += 1
        
        # Pause entre les items
        time.sleep(1)
    
    print(f"\n✅ Liaison terminée!")
    print(f"📊 Appels liés avec succès: {success_count}")
    print(f"❌ Erreurs/Non trouvés: {error_count}")
    print(f"🎯 Colonne Contact_Lié: {contact_column_id}")

if __name__ == "__main__":
    main()
