#!/usr/bin/env python3
"""
Analyse de la structure complète des données Aircall
"""

import requests
import base64
import json
from datetime import datetime, timedelta

# Configuration Aircall
AIRCALL_API_ID = "cc1c0e0e08b34c3394245889a4377872"
AIRCALL_API_TOKEN = "3e5d6de7ef4d4bd1ebbca9c590e2e981"

class AircallDataAnalyzer:
    """Analyseur de la structure des données Aircall"""
    
    def __init__(self):
        self.base_url = "https://api.aircall.io/v1"
        
        # Encodage Basic Auth
        credentials = f"{AIRCALL_API_ID}:{AIRCALL_API_TOKEN}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        self.headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json"
        }
    
    def get_sample_call(self):
        """Récupère un appel exemple pour analyser sa structure"""
        try:
            # Récupération des appels récents
            params = {
                "per_page": 1,
                "order": "desc"
            }
            
            response = requests.get(
                f"{self.base_url}/calls",
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                calls = data.get('calls', [])
                if calls:
                    return calls[0]
            
            return None
            
        except Exception as e:
            print(f"❌ Erreur récupération appel exemple: {str(e)}")
            return None
    
    def analyze_call_structure(self, call_data):
        """Analyse la structure complète d'un appel"""
        print("🔍 ANALYSE DE LA STRUCTURE D'UN APPEL AIRCALL")
        print("=" * 60)
        
        if not call_data:
            print("❌ Aucune donnée d'appel disponible")
            return
        
        print(f"📞 ID de l'appel: {call_data.get('id', 'N/A')}")
        print(f"📅 Date: {datetime.fromtimestamp(call_data.get('started_at', 0)).strftime('%d/%m/%Y %H:%M:%S')}")
        print()
        
        # Analyse des champs principaux
        print("📋 CHAMPS PRINCIPAUX:")
        print("-" * 30)
        
        main_fields = [
            'id', 'direction', 'status', 'duration', 'started_at', 'ended_at',
            'raw_digits', 'number', 'name', 'answered_at', 'voicemail',
            'recording', 'missed_call_reason', 'cost', 'currency'
        ]
        
        for field in main_fields:
            value = call_data.get(field)
            if value is not None:
                if field in ['started_at', 'ended_at', 'answered_at']:
                    formatted_value = datetime.fromtimestamp(value).strftime('%d/%m/%Y %H:%M:%S') if value else 'N/A'
                else:
                    formatted_value = str(value)
                print(f"  {field}: {formatted_value}")
        
        # Analyse des objets imbriqués
        print("\n🔗 OBJETS IMBRIQUÉS:")
        print("-" * 30)
        
        # User (agent)
        user = call_data.get('user', {})
        if user:
            print("👤 USER (Agent):")
            for key, value in user.items():
                print(f"    {key}: {value}")
        
        # Team
        team = call_data.get('team', {})
        if team:
            print("👥 TEAM:")
            for key, value in team.items():
                print(f"    {key}: {value}")
        
        # Contact
        contact = call_data.get('contact', {})
        if contact:
            print("📇 CONTACT:")
            for key, value in contact.items():
                print(f"    {key}: {value}")
        
        # Tags
        tags = call_data.get('tags', [])
        if tags:
            print("🏷️ TAGS:")
            for tag in tags:
                print(f"    - {tag}")
        
        # Comments
        comments = call_data.get('comments', [])
        if comments:
            print("💬 COMMENTS:")
            for comment in comments:
                print(f"    - {comment}")
        
        # Events
        events = call_data.get('events', [])
        if events:
            print("📅 EVENTS:")
            for event in events:
                print(f"    - {event}")
        
        # Files
        files = call_data.get('files', [])
        if files:
            print("📁 FILES:")
            for file in files:
                print(f"    - {file}")
        
        # Numbers
        numbers = call_data.get('numbers', [])
        if numbers:
            print("📞 NUMBERS:")
            for number in numbers:
                print(f"    - {number}")
        
        # Suggestions
        suggestions = call_data.get('suggestions', [])
        if suggestions:
            print("💡 SUGGESTIONS:")
            for suggestion in suggestions:
                print(f"    - {suggestion}")
        
        # Analytics
        analytics = call_data.get('analytics', {})
        if analytics:
            print("📊 ANALYTICS:")
            for key, value in analytics.items():
                print(f"    {key}: {value}")
        
        # Custom fields
        custom_fields = call_data.get('custom_fields', {})
        if custom_fields:
            print("🔧 CUSTOM FIELDS:")
            for key, value in custom_fields.items():
                print(f"    {key}: {value}")
        
        # Metadata
        metadata = call_data.get('metadata', {})
        if metadata:
            print("📋 METADATA:")
            for key, value in metadata.items():
                print(f"    {key}: {value}")
    
    def check_ai_endpoints(self, call_id):
        """Vérifie tous les endpoints IA disponibles"""
        print(f"\n🤖 ENDPOINTS IA DISPONIBLES POUR L'APPEL {call_id}:")
        print("-" * 50)
        
        ai_endpoints = [
            ('transcription', f'/calls/{call_id}/transcription'),
            ('summary', f'/calls/{call_id}/summary'),
            ('sentiments', f'/calls/{call_id}/sentiments'),
            ('topics', f'/calls/{call_id}/topics'),
            ('action_items', f'/calls/{call_id}/action_items'),
            ('keywords', f'/calls/{call_id}/keywords'),
            ('entities', f'/calls/{call_id}/entities'),
            ('intent', f'/calls/{call_id}/intent'),
            ('language', f'/calls/{call_id}/language'),
            ('quality_score', f'/calls/{call_id}/quality_score')
        ]
        
        for endpoint_name, endpoint_path in ai_endpoints:
            try:
                response = requests.get(
                    f"{self.base_url}{endpoint_path}",
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {endpoint_name}: Disponible")
                    if data:
                        print(f"    Structure: {list(data.keys())}")
                elif response.status_code == 404:
                    print(f"❌ {endpoint_name}: Non disponible")
                else:
                    print(f"⚠️ {endpoint_name}: Erreur {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {endpoint_name}: Erreur - {str(e)}")
    
    def suggest_columns(self, call_data):
        """Suggère les colonnes à ajouter au tableau Monday.com"""
        print(f"\n💡 SUGGESTIONS DE COLONNES POUR MONDAY.COM:")
        print("-" * 50)
        
        suggested_columns = []
        
        # Colonnes de base (déjà présentes)
        base_columns = [
            ('ID_Aircall', 'text', 'ID unique de l\'appel'),
            ('Direction_Appel', 'status', 'Entrant/Sortant'),
            ('Statut_Appel', 'status', 'Statut de l\'appel'),
            ('Duree_Appel', 'numbers', 'Durée en secondes'),
            ('Date_Debut', 'date', 'Date de début'),
            ('Date_Fin', 'date', 'Date de fin'),
            ('Numero_Telephone', 'text', 'Numéro de téléphone'),
            ('Agent_Responsable', 'text', 'Nom de l\'agent'),
            ('Date_Import', 'date', 'Date d\'import')
        ]
        
        # Colonnes IA (déjà présentes)
        ai_columns = [
            ('Transcription_IA', 'long_text', 'Transcription complète'),
            ('Resume_IA', 'long_text', 'Résumé IA'),
            ('Sentiment_IA', 'status', 'Sentiment détecté'),
            ('Sujets_IA', 'text', 'Sujets identifiés'),
            ('Actions_IA', 'long_text', 'Actions à suivre')
        ]
        
        # Nouvelles colonnes suggérées
        new_columns = []
        
        # Coût de l'appel
        if call_data.get('cost') is not None:
            new_columns.append(('Cout_Appel', 'numbers', 'Coût de l\'appel'))
        
        # Devise
        if call_data.get('currency'):
            new_columns.append(('Devise', 'text', 'Devise du coût'))
        
        # Raison de l'appel manqué
        if call_data.get('missed_call_reason'):
            new_columns.append(('Raison_Manque', 'text', 'Raison de l\'appel manqué'))
        
        # Enregistrement disponible
        if call_data.get('recording'):
            new_columns.append(('Enregistrement', 'link', 'Lien vers l\'enregistrement'))
        
        # Répondeur
        if call_data.get('voicemail'):
            new_columns.append(('Repondeur', 'status', 'Message laissé sur répondeur'))
        
        # Nom du contact
        if call_data.get('name'):
            new_columns.append(('Nom_Contact', 'text', 'Nom du contact'))
        
        # Équipe
        if call_data.get('team'):
            new_columns.append(('Equipe', 'text', 'Équipe responsable'))
        
        # Tags
        if call_data.get('tags'):
            new_columns.append(('Tags', 'text', 'Tags associés'))
        
        # Commentaires
        if call_data.get('comments'):
            new_columns.append(('Commentaires', 'long_text', 'Commentaires internes'))
        
        # Score de qualité (si disponible)
        new_columns.append(('Score_Qualite', 'numbers', 'Score de qualité IA'))
        
        # Langue détectée
        new_columns.append(('Langue', 'text', 'Langue détectée'))
        
        # Intent détecté
        new_columns.append(('Intent', 'text', 'Intention détectée'))
        
        # Entités nommées
        new_columns.append(('Entites', 'text', 'Entités nommées détectées'))
        
        # Mots-clés
        new_columns.append(('Mots_Cles', 'text', 'Mots-clés extraits'))
        
        print("📋 COLONNES ACTUELLES:")
        for col_name, col_type, description in base_columns + ai_columns:
            print(f"  ✅ {col_name} ({col_type}): {description}")
        
        print("\n🆕 NOUVELLES COLONNES SUGGÉRÉES:")
        for col_name, col_type, description in new_columns:
            print(f"  ➕ {col_name} ({col_type}): {description}")
        
        return new_columns

def main():
    """Fonction principale"""
    analyzer = AircallDataAnalyzer()
    
    # Récupération d'un appel exemple
    print("🔍 Récupération d'un appel exemple...")
    sample_call = analyzer.get_sample_call()
    
    if sample_call:
        # Analyse de la structure
        analyzer.analyze_call_structure(sample_call)
        
        # Vérification des endpoints IA
        call_id = sample_call.get('id')
        if call_id:
            analyzer.check_ai_endpoints(call_id)
        
        # Suggestions de colonnes
        analyzer.suggest_columns(sample_call)
    else:
        print("❌ Impossible de récupérer un appel exemple")

if __name__ == "__main__":
    main()


