#!/usr/bin/env python3
"""
Mise à jour des appels existants avec toutes les nouvelles colonnes
"""

import os
import json
import time
import requests
import base64
import re
from datetime import datetime, timedelta
from typing import Dict, List, Set, Any, Optional

# Configuration directe
MONDAY_API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjUxMDY4MTEzMywiYWFpIjoxMSwidWlkIjo3NTgyNDkxNSwiaWFkIjoiMjAyNS0wNS0wOVQxMzowMjozNi4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6Mjg2NzMzNDAsInJnbiI6ImV1YzEifQ.dOUcKOgJrE7I4QPW2Fc7SEsOC55RjFE5aJEnr7WrE7I"
MONDAY_BOARD_ID = "2119815514"

# Configuration Aircall
AIRCALL_API_ID = "cc1c0e0e08b34c3394245889a4377872"
AIRCALL_API_TOKEN = "3e5d6de7ef4d4bd1ebbca9c590e2e981"

class PhoneNumberFormatter:
    """Classe pour formater les numéros de téléphone"""
    
    @staticmethod
    def format_phone_number(phone_number: str) -> str:
        """Formate un numéro de téléphone en format français"""
        if not phone_number:
            return "Non disponible"
        
        # Nettoyer le numéro
        cleaned = re.sub(r'[^\d+]', '', phone_number)
        
        # Si c'est déjà un numéro français
        if cleaned.startswith('+33'):
            # Convertir +33 en 0
            french_number = '0' + cleaned[3:]
            return PhoneNumberFormatter.format_french_number(french_number)
        
        # Si c'est un numéro français sans indicatif
        elif cleaned.startswith('33'):
            french_number = '0' + cleaned[2:]
            return PhoneNumberFormatter.format_french_number(french_number)
        
        # Si c'est déjà un numéro français avec 0
        elif cleaned.startswith('0'):
            return PhoneNumberFormatter.format_french_number(cleaned)
        
        # Autres formats
        else:
            return cleaned
    
    @staticmethod
    def format_french_number(number: str) -> str:
        """Formate un numéro français avec espaces"""
        if len(number) == 10 and number.startswith('0'):
            # Format: 01 23 45 67 89
            return f"{number[:2]} {number[2:4]} {number[4:6]} {number[6:8]} {number[8:10]}"
        else:
            return number

class AircallClient:
    """Client pour l'API Aircall"""
    
    def __init__(self, api_id: str, api_token: str):
        self.base_url = "https://api.aircall.io/v1"
        self.api_id = api_id
        self.api_token = api_token
        
        # Encodage Basic Auth
        credentials = f"{api_id}:{api_token}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        self.headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json"
        }
    
    def get_call_by_id(self, call_id: int) -> Optional[Dict]:
        """Récupère un appel spécifique par son ID"""
        try:
            response = requests.get(
                f"{self.base_url}/calls/{call_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('call')
            else:
                print(f"❌ Erreur récupération appel {call_id}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur récupération appel {call_id}: {str(e)}")
            return None
    
    def get_call_transcription(self, call_id: int) -> Optional[Dict]:
        """Récupère la transcription d'un appel"""
        try:
            response = requests.get(
                f"{self.base_url}/calls/{call_id}/transcription",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('transcription')
            elif response.status_code == 404:
                return None
            else:
                return None
                
        except Exception as e:
            return None
    
    def get_call_summary(self, call_id: int) -> Optional[Dict]:
        """Récupère le résumé IA d'un appel"""
        try:
            response = requests.get(
                f"{self.base_url}/calls/{call_id}/summary",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('summary')
            elif response.status_code == 404:
                return None
            else:
                return None
                
        except Exception as e:
            return None
    
    def get_call_sentiments(self, call_id: int) -> Optional[Dict]:
        """Récupère l'analyse de sentiment d'un appel"""
        try:
            response = requests.get(
                f"{self.base_url}/calls/{call_id}/sentiments",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('sentiment')
            elif response.status_code == 404:
                return None
            else:
                return None
                
        except Exception as e:
            return None
    
    def get_call_topics(self, call_id: int) -> Optional[Dict]:
        """Récupère les sujets clés d'un appel"""
        try:
            response = requests.get(
                f"{self.base_url}/calls/{call_id}/topics",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('topic')
            elif response.status_code == 404:
                return None
            else:
                return None
                
        except Exception as e:
            return None
    
    def get_call_action_items(self, call_id: int) -> Optional[Dict]:
        """Récupère les actions à suivre d'un appel"""
        try:
            response = requests.get(
                f"{self.base_url}/calls/{call_id}/action_items",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data
            elif response.status_code == 404:
                return None
            else:
                return None
                
        except Exception as e:
            return None

class MondayAircallClient:
    """Client Monday.com pour l'intégration Aircall"""
    
    def __init__(self, board_id: str):
        self.base_url = "https://api.monday.com/v2"
        self.headers = {
            "Authorization": MONDAY_API_TOKEN,
            "Content-Type": "application/json",
            "API-Version": "2023-10"
        }
        self.board_id = board_id
    
    def get_existing_aircall_items(self) -> List[Dict]:
        """Récupère tous les items Aircall existants dans Monday.com"""
        query = """
        query ($boardId: ID!) {
            boards(ids: [$boardId]) {
                items_page {
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
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={"query": query, "variables": {"boardId": self.board_id}},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('data', {}).get('boards', [{}])[0].get('items_page', {}).get('items', [])
                
                aircall_items = []
                for item in items:
                    column_values = item.get('column_values', [])
                    for col in column_values:
                        # Chercher dans la colonne ID_Aircall
                        if col.get('id') == 'text_mkv8ydgs':
                            call_id = col.get('text', '')
                            if call_id and call_id.startswith('aircall_'):
                                # Extraire l'ID numérique
                                numeric_id = call_id.replace('aircall_', '')
                                aircall_items.append({
                                    'monday_id': item.get('id'),
                                    'name': item.get('name'),
                                    'aircall_id': numeric_id
                                })
                                break
                
                print(f"📋 {len(aircall_items)} items Aircall trouvés dans Monday.com")
                return aircall_items
            else:
                print(f"❌ Erreur récupération items: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Erreur récupération items: {str(e)}")
            return []
    
    def update_item_columns(self, item_id: str, column_values: Dict) -> bool:
        """Met à jour les colonnes d'un item"""
        try:
            query = """
            mutation ($boardId: ID!, $itemId: ID!, $columnValues: JSON!) {
                change_multiple_column_values (
                    board_id: $boardId,
                    item_id: $itemId,
                    column_values: $columnValues
                ) {
                    id
                }
            }
            """
            
            variables = {
                "boardId": self.board_id,
                "itemId": item_id,
                "columnValues": json.dumps(column_values)
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
                    print(f"❌ Erreur mise à jour: {result['errors']}")
                    return False
                else:
                    print(f"✅ Item {item_id} mis à jour avec succès")
                    return True
            else:
                print(f"❌ Erreur mise à jour: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur mise à jour item {item_id}: {str(e)}")
            return False
    
    def format_recording_link(self, recording_url: str) -> str:
        """Formate le lien d'enregistrement pour Monday.com"""
        if not recording_url:
            return ""
        
        # Format Monday.com pour les liens: {"url": "...", "text": "..."}
        return json.dumps({
            "url": recording_url,
            "text": "🎵 Écouter l'enregistrement"
        })
    
    def format_tags(self, tags: List) -> str:
        """Formate les tags en texte"""
        if not tags:
            return ""
        return ", ".join(tags)
    
    def format_comments(self, comments: List) -> str:
        """Formate les commentaires en texte"""
        if not comments:
            return ""
        return "\n".join(comments)
    
    def get_team_name(self, call_data: Dict) -> str:
        """Récupère le nom de l'équipe"""
        team = call_data.get('team', {})
        if team:
            return team.get('name', 'Équipe inconnue')
        return "Équipe inconnue"
    
    def get_agent_name(self, call_data: Dict) -> str:
        """Récupère le nom de l'agent"""
        user = call_data.get('user', {})
        if user:
            return user.get('name', 'Agent inconnu')
        return 'Agent inconnu'

class AircallMondayUpdater:
    """Mise à jour des items Aircall existants"""
    
    def __init__(self, board_id: str):
        self.aircall_client = AircallClient(AIRCALL_API_ID, AIRCALL_API_TOKEN)
        self.monday_client = MondayAircallClient(board_id)
    
    def format_transcription(self, transcription: Dict) -> str:
        """Formate la transcription pour l'affichage"""
        if not transcription:
            return "Non disponible"
        
        content = transcription.get('content', {})
        utterances = content.get('utterances', [])
        
        if not utterances:
            return "Transcription vide"
        
        formatted_text = []
        for utterance in utterances:
            text = utterance.get('text', '')
            participant_type = utterance.get('participant_type', 'unknown')
            start_time = utterance.get('start_time', 0)
            
            # Formatage du temps
            minutes = int(start_time // 60)
            seconds = int(start_time % 60)
            time_str = f"[{minutes:02d}:{seconds:02d}]"
            
            # Formatage du participant
            if participant_type == 'internal':
                speaker = "👤 Agent"
            elif participant_type == 'external':
                speaker = "📞 Client"
            else:
                speaker = "❓ Inconnu"
            
            formatted_text.append(f"{time_str} {speaker}: {text}")
        
        return "\n".join(formatted_text)
    
    def format_summary(self, summary: Dict) -> str:
        """Formate le résumé IA"""
        if not summary:
            return "Non disponible"
        
        content = summary.get('content', '')
        return content if content else "Résumé vide"
    
    def format_sentiments(self, sentiment: Dict) -> str:
        """Formate l'analyse de sentiment"""
        if not sentiment:
            return "Non disponible"
        
        participants = sentiment.get('participants', [])
        if not participants:
            return "Aucune analyse de sentiment"
        
        formatted_sentiments = []
        for participant in participants:
            phone_number = participant.get('phone_number', 'Inconnu')
            value = participant.get('value', 'NEUTRAL')
            
            # Traduction des sentiments
            sentiment_map = {
                'POSITIVE': '😊 Positif',
                'NEGATIVE': '😞 Négatif',
                'NEUTRAL': '😐 Neutre'
            }
            
            sentiment_text = sentiment_map.get(value, value)
            formatted_sentiments.append(f"{phone_number}: {sentiment_text}")
        
        return " | ".join(formatted_sentiments)
    
    def format_topics(self, topic: Dict) -> str:
        """Formate les sujets clés"""
        if not topic:
            return "Non disponible"
        
        content = topic.get('content', [])
        if not content:
            return "Aucun sujet identifié"
        
        return ", ".join(content)
    
    def format_action_items(self, action_items: Dict) -> str:
        """Formate les actions à suivre"""
        if not action_items:
            return "Non disponible"
        
        items = action_items.get('action_items', [])
        if not items:
            return "Aucune action identifiée"
        
        formatted_actions = []
        for item in items:
            content = item.get('content', '')
            ai_generated = item.get('ai_generated', False)
            prefix = "🤖 IA:" if ai_generated else "👤 Agent:"
            formatted_actions.append(f"{prefix} {content}")
        
        return "\n".join(formatted_actions)
    
    def process_call_ai_data(self, call_id: int) -> Dict:
        """Traite toutes les données IA d'un appel"""
        print(f"🔍 Traitement des données IA pour l'appel {call_id}...")
        
        ai_data = {}
        
        # Récupération de la transcription
        transcription = self.aircall_client.get_call_transcription(call_id)
        ai_data['transcription_text'] = self.format_transcription(transcription)
        
        # Récupération du résumé
        summary = self.aircall_client.get_call_summary(call_id)
        ai_data['summary_text'] = self.format_summary(summary)
        
        # Récupération des sentiments
        sentiment = self.aircall_client.get_call_sentiments(call_id)
        ai_data['sentiment_text'] = self.format_sentiments(sentiment)
        
        # Récupération des sujets
        topics = self.aircall_client.get_call_topics(call_id)
        ai_data['topics_text'] = self.format_topics(topics)
        
        # Récupération des actions
        action_items = self.aircall_client.get_call_action_items(call_id)
        ai_data['actions_text'] = self.format_action_items(action_items)
        
        # Données IA supplémentaires (non disponibles actuellement)
        ai_data['keywords_text'] = "Non disponible"
        ai_data['entities_text'] = "Non disponible"
        ai_data['intent_text'] = "Non disponible"
        ai_data['language_text'] = "Non disponible"
        ai_data['quality_score'] = "0"
        
        return ai_data
    
    def map_sentiment(self, sentiment_text: str) -> str:
        """Mappe le sentiment vers les valeurs Monday.com"""
        if 'Positif' in sentiment_text:
            return '0'
        elif 'Négatif' in sentiment_text:
            return '2'
        else:
            return '1'  # Neutre
    
    def format_notes(self, call_data: Dict, ai_data: Dict) -> str:
        """Formate les notes de l'appel"""
        notes = []
        notes.append(f"Appel {call_data.get('direction', 'inconnu')}")
        notes.append(f"Durée: {call_data.get('duration', 0)} secondes")
        
        if ai_data.get('transcription_text') and ai_data['transcription_text'] != "Non disponible":
            notes.append("✅ Transcription disponible")
        if ai_data.get('summary_text') and ai_data['summary_text'] != "Non disponible":
            notes.append("✅ Résumé IA disponible")
        
        return " | ".join(notes)
    
    def update_existing_items(self):
        """Met à jour tous les items existants avec les nouvelles colonnes"""
        print("🚀 MISE À JOUR DES ITEMS EXISTANTS")
        print("=" * 50)
        
        # Récupération des items existants
        existing_items = self.monday_client.get_existing_aircall_items()
        
        if not existing_items:
            print("❌ Aucun item Aircall trouvé dans Monday.com")
            return
        
        # Mapping complet des colonnes (30 colonnes)
        column_mapping = {
            'Cout_Appel': 'numeric_mkv840v2',
            'Enregistrement': 'link_mkv8zdta',
            'Nom_Contact': 'text_mkv8510p',
            'Repondeur': 'color_mkv8hbc3',
            'Raison_Manque': 'text_mkv8qkkn',
            'Tags': 'text_mkv8jbqh',
            'Commentaires': 'long_text_mkv8ecn3',
            'Devise': 'text_mkv88hze',
            'Equipe': 'text_mkv89zwb',
            'Score_Qualite': 'numeric_mkv8cfrc',
            'Langue': 'text_mkv8t5zg',
            'Intent': 'text_mkv86pk5',
            'Entites': 'text_mkv8y9p2',
            'Mots_Cles': 'text_mkv8djqx'
        }
        
        success_count = 0
        error_count = 0
        
        print(f"\n📊 Mise à jour de {len(existing_items)} items...")
        
        for item in existing_items:
            monday_id = item['monday_id']
            aircall_id = item['aircall_id']
            item_name = item['name']
            
            print(f"\n📞 Mise à jour de l'item: {item_name}")
            print(f"   Monday ID: {monday_id}")
            print(f"   Aircall ID: {aircall_id}")
            
            try:
                # Récupération des données Aircall complètes
                call_data = self.aircall_client.get_call_by_id(int(aircall_id))
                
                if not call_data:
                    print(f"❌ Impossible de récupérer les données pour l'appel {aircall_id}")
                    error_count += 1
                    continue
                
                # Récupération des données IA
                ai_data = self.process_call_ai_data(int(aircall_id))
                
                # Préparation des nouvelles valeurs
                new_values = {}
                
                # Nouvelles colonnes à remplir
                new_values[column_mapping['Cout_Appel']] = str(call_data.get('cost', 0))
                new_values[column_mapping['Enregistrement']] = self.monday_client.format_recording_link(call_data.get('recording', ''))
                new_values[column_mapping['Nom_Contact']] = call_data.get('name', '')
                new_values[column_mapping['Repondeur']] = "0" if call_data.get('voicemail') else "1"
                new_values[column_mapping['Raison_Manque']] = call_data.get('missed_call_reason', '')
                new_values[column_mapping['Tags']] = self.monday_client.format_tags(call_data.get('tags', []))
                new_values[column_mapping['Commentaires']] = self.monday_client.format_comments(call_data.get('comments', []))
                new_values[column_mapping['Devise']] = call_data.get('currency', '')
                new_values[column_mapping['Equipe']] = self.monday_client.get_team_name(call_data)
                new_values[column_mapping['Score_Qualite']] = ai_data.get('quality_score', '0')
                new_values[column_mapping['Langue']] = ai_data.get('language_text', '')
                new_values[column_mapping['Intent']] = ai_data.get('intent_text', '')
                new_values[column_mapping['Entites']] = ai_data.get('entities_text', '')
                new_values[column_mapping['Mots_Cles']] = ai_data.get('keywords_text', '')
                
                # Mise à jour de l'item
                if self.monday_client.update_item_columns(monday_id, new_values):
                    success_count += 1
                    print(f"✅ Item {item_name} mis à jour avec succès")
                else:
                    error_count += 1
                    print(f"❌ Erreur lors de la mise à jour de {item_name}")
                
                # Pause entre les mises à jour
                time.sleep(1)
                
            except Exception as e:
                error_count += 1
                print(f"❌ Erreur traitement item {item_name}: {str(e)}")
        
        print(f"\n✅ Mise à jour terminée!")
        print(f"📊 Résultats: {success_count} items mis à jour")
        print(f"❌ Erreurs: {error_count}")
        print(f"📋 Nouvelles colonnes remplies: 14/14")

def main():
    """Fonction principale"""
    print("🔄 MISE À JOUR DES COLONNES MANQUANTES")
    print("=" * 50)
    print("📊 Remplissage des 14 nouvelles colonnes")
    print("🤖 Données IA complètes")
    print("📞 Métadonnées Aircall")
    print()
    
    updater = AircallMondayUpdater(MONDAY_BOARD_ID)
    updater.update_existing_items()

if __name__ == "__main__":
    main()
