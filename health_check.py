#!/usr/bin/env python3
# Script de vérification de santé pour l'interface web
import requests
import sys
import time

def check_health(url, timeout=30):
    """Vérifie la santé de l'interface web"""
    try:
        response = requests.get(f"{url}/api/status", timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Interface web opérationnelle")
            print(f"   Statut: {data.get('status', 'inconnu')}")
            print(f"   Total exécutions: {data.get('stats', {}).get('total_runs', 0)}")
            return True
        else:
            print(f"❌ Interface web répond avec le code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    print(f"🔍 Vérification de la santé de l'interface web sur {url}")
    
    if check_health(url):
        sys.exit(0)
    else:
        sys.exit(1)
