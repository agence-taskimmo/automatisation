#!/usr/bin/env python3
"""
Intégration Aircall → Monday.com V2
Version nettoyée et optimisée
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

# Configuration Aircall
AIRCALL_API_ID = "cc1c0e0e08b34c3394245889a4377872"
AIRCALL_API_TOKEN = "3e5d6de7ef4d4bd1ebbca9c590e2e981"

# ID du tableau Aircall
MONDAY_BOARD_ID = "2119815514"

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
    
    def test_connection(self) -> bool:
        """Teste la connexion à l'API Aircall"""
        try:
            response = requests.get(f"{self.base_url}/ping", headers=self.headers, timeout=10)
            if response.status_code == 200:
                print("✅ Connexion Aircall réussie")
                return True
            else:
                print(f"❌ Erreur connexion Aircall: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erreur connexion Aircall: {str(e)}")
            return False
    
    def get_calls(self, from_date: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Récupère les appels récents"""
        try:
            params = {
                "per_page": limit,
                "order": "desc"
            }
            
            if from_date:
                params["from"] = from_date
            
            response = requests.get(
                f"{self.base_url}/calls",
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                calls = data.get('calls', [])
                print(f"✅ {len(calls)} appels récupérés depuis Aircall")
                return calls
            else:
                print(f"❌ Erreur récupération appels: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Erreur récupération appels: {str(e)}")
            return []
    
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
    
    def get_existing_aircall_calls(self) -> Set[str]:
        """Récupère les IDs d'appels Aircall déjà dans Monday.com"""
        query = """
        query ($boardId: ID!) {
            boards(ids: [$boardId]) {
                items_page {
                    items {
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
                
                existing_calls = set()
                for item in items:
                    column_values = item.get('column_values', [])
                    for col in column_values:
                        if col.get('id') == 'text_mkv8ydgs':
                            call_id = col.get('text', '')
                            if call_id and call_id.startswith('aircall_'):
                                existing_calls.add(call_id)
                
                print(f"📋 {len(existing_calls)} appels Aircall déjà dans Monday.com")
                return existing_calls
            else:
                print(f"❌ Erreur récupération appels existants: {response.status_code}")
                return set()
                
        except Exception as e:
            print(f"❌ Erreur récupération appels existants: {str(e)}")
            return set()
    
    def create_aircall_item(self, call_data: Dict, ai_data: Dict) -> bool:
        """Crée un item Monday.com avec les données Aircall et IA"""
        try:
            # Informations de base de l'appel
            call_id = call_data.get('id', '')
            call_direction = call_data.get('direction', '')
            call_status = call_data.get('status', '')
            call_duration = call_data.get('duration', 0)
            call_started_at = call_data.get('started_at', 0)
            call_ended_at = call_data.get('ended_at', 0)
            raw_digits = call_data.get('raw_digits', '')
            
            # Formatage du numéro de téléphone
            formatted_phone = PhoneNumberFormatter.format_phone_number(raw_digits)
            
            # Titre de l'item
            item_name = f"Appel #{call_id} - {formatted_phone}"
            
            # Mapping des colonnes
            column_mapping = {
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
            
            # Valeurs à mapper
            values_to_map = [
                ('ID_Aircall', f"aircall_{call_id}"),
                ('Direction_Appel', "0" if call_direction == "inbound" else "1"),
                ('Statut_Appel', self.map_call_status(call_status)),
                ('Duree_Appel', call_duration),
                ('Date_Debut', datetime.fromtimestamp(call_started_at).strftime('%Y-%m-%d')),
                ('Date_Fin', datetime.fromtimestamp(call_ended_at).strftime('%Y-%m-%d') if call_ended_at else None),
                ('Numero_Telephone', formatted_phone),
                ('Transcription_IA', ai_data.get('transcription_text', '')),
                ('Resume_IA', ai_data.get('summary_text', '')),
                ('Sentiment_IA', self.map_sentiment(ai_data.get('sentiment_text', ''))),
                ('Sujets_IA', ai_data.get('topics_text', '')),
                ('Actions_IA', ai_data.get('actions_text', '')),
                ('Type_Source', "0"),
                ('Date_Import', datetime.now().strftime('%Y-%m-%d')),
                ('Agent_Responsable', self.get_agent_name(call_data)),
                ('Notes', self.format_notes(call_data, ai_data)),
                ('Cout_Appel', call_data.get('cost', 0)),
                ('Enregistrement', self.format_recording_link(call_data.get('recording', ''))),
                ('Nom_Contact', call_data.get('name', '')),
                ('Repondeur', "0" if call_data.get('voicemail') else "1"),
                ('Raison_Manque', call_data.get('missed_call_reason', '')),
                ('Tags', self.format_tags(call_data.get('tags', []))),
                ('Commentaires', self.format_comments(call_data.get('comments', []))),
                ('Devise', call_data.get('currency', '')),
                ('Equipe', self.get_team_name(call_data))
            ]
            
            # Création des valeurs formatées
            formatted_values = {}
            for col_name, value in values_to_map:
                col_id = column_mapping.get(col_name)
                if col_id and value is not None:
                    formatted_values[col_id] = str(value)
            
            # Création de l'item
            query = """
            mutation ($boardId: ID!, $itemName: String!, $columnValues: JSON!) {
                create_item (
                    board_id: $boardId,
                    item_name: $itemName,
                    column_values: $columnValues
                ) {
                    id
                    name
                }
            }
            """
            
            variables = {
                "boardId": self.board_id,
                "itemName": item_name,
                "columnValues": json.dumps(formatted_values)
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
                    print(f"❌ Erreur création item: {result['errors']}")
                    return False
                else:
                    item_id = result.get('data', {}).get('create_item', {}).get('id', '')
                    print(f"✅ Item Aircall créé (ID: {item_id})")
                    return True
            else:
                print(f"❌ Erreur création: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur création item Aircall: {str(e)}")
            return False
    
    def map_call_status(self, status: str) -> str:
        """Mappe le statut d'appel vers les valeurs Monday.com"""
        status_mapping = {
            'initial': '0',
            'answered': '1',
            'done': '2'
        }
        return status_mapping.get(status, '0')
    
    def map_sentiment(self, sentiment_text: str) -> str:
        """Mappe le sentiment vers les valeurs Monday.com"""
        if 'Positif' in sentiment_text:
            return '0'
        elif 'Négatif' in sentiment_text:
            return '2'
        else:
            return '1'
    
    def get_agent_name(self, call_data: Dict) -> str:
        """Récupère le nom de l'agent"""
        user = call_data.get('user', {})
        if user:
            return user.get('name', 'Agent inconnu')
        return 'Agent inconnu'
    
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
    
    def format_recording_link(self, recording_url: str) -> str:
        """Formate le lien d'enregistrement pour Monday.com"""
        if not recording_url:
            return ""
        
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

class AircallMondayIntegration:
    """Intégration principale Aircall → Monday.com"""
    
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
        """Traite les données IA d'un appel"""
        print(f"🔍 Traitement des données IA pour l'appel {call_id}...")
        
        ai_data = {}
        
        # Récupération des données IA principales
        transcription = self.aircall_client.get_call_transcription(call_id)
        ai_data['transcription_text'] = self.format_transcription(transcription)
        
        summary = self.aircall_client.get_call_summary(call_id)
        ai_data['summary_text'] = self.format_summary(summary)
        
        sentiment = self.aircall_client.get_call_sentiments(call_id)
        ai_data['sentiment_text'] = self.format_sentiments(sentiment)
        
        topics = self.aircall_client.get_call_topics(call_id)
        ai_data['topics_text'] = self.format_topics(topics)
        
        action_items = self.aircall_client.get_call_action_items(call_id)
        ai_data['actions_text'] = self.format_action_items(action_items)
        
        return ai_data
    
    def run_integration(self, hours_back: int = 24):
        """Exécute l'intégration Aircall → Monday.com"""
        print("🚀 Démarrage de l'intégration Aircall → Monday.com V2")
        print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"⏰ Récupération des appels des {hours_back} dernières heures")
        
        # Test de connexion Aircall
        if not self.aircall_client.test_connection():
            print("❌ Impossible de se connecter à Aircall")
            return
        
        # Calcul de la date de début
        from_date = int((datetime.now() - timedelta(hours=hours_back)).timestamp())
        
        # Récupération des appels
        calls = self.aircall_client.get_calls(from_date=str(from_date), limit=20)
        
        if not calls:
            print("❌ Aucun appel trouvé")
            return
        
        # Récupération des appels déjà dans Monday.com
        existing_calls = self.monday_client.get_existing_aircall_calls()
        
        # Traitement des appels
        success_count = 0
        skipped_count = 0
        error_count = 0
        
        print(f"\n📊 Traitement de {len(calls)} appels...")
        
        for call in calls:
            call_id = call.get('id', '')
            call_direction = call.get('direction', '')
            call_status = call.get('status', '')
            raw_digits = call.get('raw_digits', '')
            
            # Vérification si l'appel existe déjà
            aircall_id = f"aircall_{call_id}"
            if aircall_id in existing_calls:
                skipped_count += 1
                print(f"🔄 Appel {call_id} déjà dans Monday.com - Ignoré")
                continue
            
            print(f"\n📞 Traitement de l'appel {call_id}")
            print(f"   Direction: {call_direction}")
            print(f"   Statut: {call_status}")
            print(f"   Numéro: {PhoneNumberFormatter.format_phone_number(raw_digits)}")
            
            try:
                # Récupération des données IA
                ai_data = self.process_call_ai_data(call_id)
                
                # Création de l'item dans Monday.com
                if self.monday_client.create_aircall_item(call, ai_data):
                    success_count += 1
                    print(f"✅ Appel {call_id} ajouté avec succès")
                else:
                    error_count += 1
                    print(f"❌ Erreur lors de l'ajout de l'appel {call_id}")
                
                # Pause entre les appels
                time.sleep(1)
                
            except Exception as e:
                error_count += 1
                print(f"❌ Erreur traitement appel {call_id}: {str(e)}")
        
        print(f"\n✅ Intégration terminée!")
        print(f"📊 Résultats: {success_count} appels ajoutés")
        print(f"🔄 Appels ignorés (déjà présents): {skipped_count}")
        print(f"❌ Erreurs: {error_count}")

def main():
    """Fonction principale"""
    if MONDAY_BOARD_ID == "NEW_BOARD_ID":
        print("❌ Veuillez configurer MONDAY_BOARD_ID")
        return
    
    integration = AircallMondayIntegration(MONDAY_BOARD_ID)
    integration.run_integration(hours_back=24)

if __name__ == "__main__":
    main()
