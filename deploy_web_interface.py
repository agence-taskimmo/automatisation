#!/usr/bin/env python3
"""
Script de déploiement pour l'interface web d'automatisation
Configure et déploie l'interface web sur un serveur
"""

import os
import sys
import subprocess
import argparse
import json
import time
from pathlib import Path
import shutil

def check_python_version():
    """Vérifie la version de Python"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ requis")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} détecté")

def check_dependencies():
    """Vérifie et installe les dépendances"""
    print("🔍 Vérification des dépendances...")
    
    try:
        import flask
        print("✅ Flask installé")
    except ImportError:
        print("📦 Installation de Flask...")
        subprocess.run([sys.executable, "-m", "pip", "install", "flask"], check=True)
    
    try:
        import flask_socketio
        print("✅ Flask-SocketIO installé")
    except ImportError:
        print("📦 Installation de Flask-SocketIO...")
        subprocess.run([sys.executable, "-m", "pip", "install", "flask-socketio"], check=True)
    
    try:
        import schedule
        print("✅ Schedule installé")
    except ImportError:
        print("📦 Installation de Schedule...")
        subprocess.run([sys.executable, "-m", "pip", "install", "schedule"], check=True)

def create_directories():
    """Crée les répertoires nécessaires"""
    print("📁 Création des répertoires...")
    
    directories = [
        'logs',
        'templates',
        'static/css',
        'static/js',
        'backups'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Répertoire {directory} créé")

def check_files():
    """Vérifie la présence des fichiers essentiels"""
    print("🔍 Vérification des fichiers...")
    
    required_files = [
        'web_interface.py',
        'templates/base.html',
        'templates/dashboard.html',
        'templates/index.html',
        'static/css/style.css',
        'static/js/app.js',
        'config.py',
        'scheduler.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Fichiers manquants:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print("✅ Tous les fichiers sont présents")
    return True

def create_nginx_config(domain=None, port=5000):
    """Crée une configuration Nginx"""
    if not domain:
        return None
    
    config = f"""
server {{
    listen 80;
    server_name {domain};
    
    location / {{
        proxy_pass http://127.0.0.1:{port};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    location /socket.io {{
        proxy_pass http://127.0.0.1:{port};
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
    
    config_path = f"nginx_{domain}.conf"
    with open(config_path, 'w') as f:
        f.write(config)
    
    print(f"✅ Configuration Nginx créée: {config_path}")
    return config_path

def create_systemd_service(user=None, working_dir=None, port=5000):
    """Crée un service systemd"""
    if not user or not working_dir:
        return None
    
    service_content = f"""[Unit]
Description=Interface Web Automatisation Aircall
After=network.target
Wants=network.target

[Service]
Type=simple
User={user}
Group={user}
WorkingDirectory={working_dir}
ExecStart={sys.executable} {working_dir}/web_interface.py
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=aircall-web-interface
Environment=PYTHONPATH={working_dir}
Environment=PYTHONUNBUFFERED=1
Environment=PORT={port}
Environment=HOST=127.0.0.1
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths={working_dir}/logs

[Install]
WantedBy=multi-user.target
"""
    
    service_path = "aircall-web-interface.service"
    with open(service_path, 'w') as f:
        f.write(service_content)
    
    print(f"✅ Service systemd créé: {service_path}")
    return service_path

def create_docker_compose(port=5000):
    """Crée un fichier docker-compose.yml"""
    compose_content = f"""version: '3.8'

services:
  aircall-web-interface:
    build: .
    ports:
      - "{port}:5000"
    volumes:
      - ./logs:/app/logs
      - ./config.py:/app/config.py
    environment:
      - HOST=0.0.0.0
      - PORT=5000
      - DEBUG=False
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/status"]
      interval: 30s
      timeout: 10s
      retries: 3
"""
    
    with open("docker-compose.yml", 'w') as f:
        f.write(compose_content)
    
    print("✅ Docker Compose créé")

def create_dockerfile():
    """Crée un Dockerfile"""
    dockerfile_content = """FROM python:3.9-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers de dépendances
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Création des répertoires nécessaires
RUN mkdir -p logs

# Exposition du port
EXPOSE 5000

# Commande de démarrage
CMD ["python", "web_interface.py"]
"""
    
    with open("Dockerfile", 'w') as f:
        f.write(dockerfile_content)
    
    print("✅ Dockerfile créé")

def create_environment_file(port=5000, debug=False):
    """Crée un fichier .env"""
    env_content = f"""# Configuration de l'interface web
HOST=0.0.0.0
PORT={port}
DEBUG={str(debug).lower()}

# Configuration de la base de données (si applicable)
# DATABASE_URL=sqlite:///automation.db

# Configuration de sécurité
SECRET_KEY=your_secret_key_here_change_in_production
"""
    
    with open(".env", 'w') as f:
        f.write(env_content)
    
    print("✅ Fichier .env créé")

def create_startup_script():
    """Crée un script de démarrage"""
    script_content = """#!/bin/bash

# Script de démarrage de l'interface web d'automatisation
# Usage: ./start_web_interface.sh [--port PORT] [--host HOST] [--debug]

set -e

# Variables par défaut
PORT=${PORT:-5000}
HOST=${HOST:-0.0.0.0}
DEBUG=${DEBUG:-false}

# Parsing des arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --debug)
            DEBUG="true"
            shift
            ;;
        *)
            echo "Usage: $0 [--port PORT] [--host HOST] [--debug]"
            exit 1
            ;;
    esac
done

echo "🚀 Démarrage de l'interface web d'automatisation..."
echo "📍 Port: $PORT"
echo "🌐 Host: $HOST"
echo "🐛 Debug: $DEBUG"

# Vérification de Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 non trouvé"
    exit 1
fi

# Vérification des dépendances
echo "📦 Vérification des dépendances..."
python3 -c "import flask, flask_socketio, schedule" 2>/dev/null || {
    echo "📦 Installation des dépendances..."
    pip3 install -r requirements.txt
}

# Démarrage de l'interface
export PORT=$PORT
export HOST=$HOST
export DEBUG=$DEBUG

echo "✅ Démarrage sur http://$HOST:$PORT"
python3 web_interface.py
"""
    
    with open("start_web_interface.sh", 'w') as f:
        f.write(script_content)
    
    # Rendre le script exécutable
    os.chmod("start_web_interface.sh", 0o755)
    
    print("✅ Script de démarrage créé")

def create_health_check():
    """Crée un script de vérification de santé"""
    health_content = '''#!/usr/bin/env python3
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
'''
    
    with open("health_check.py", 'w') as f:
        f.write(health_content)
    
    print("✅ Script de vérification de santé créé")

def create_backup():
    """Crée une sauvegarde de la configuration actuelle"""
    print("💾 Création d'une sauvegarde...")
    
    backup_dir = Path("backups") / f"backup_{int(time.time())}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Fichiers à sauvegarder
    files_to_backup = [
        'config.py',
        'web_interface.py',
        'scheduler.py',
        'requirements.txt'
    ]
    
    for file_path in files_to_backup:
        if Path(file_path).exists():
            shutil.copy2(file_path, backup_dir)
    
    print(f"✅ Sauvegarde créée dans {backup_dir}")

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Déploiement de l'interface web d'automatisation")
    parser.add_argument("--port", type=int, default=5000, help="Port de l'interface web")
    parser.add_argument("--host", default="0.0.0.0", help="Host de l'interface web")
    parser.add_argument("--domain", help="Nom de domaine pour Nginx")
    parser.add_argument("--user", help="Utilisateur pour systemd")
    parser.add_argument("--docker", action="store_true", help="Créer les fichiers Docker")
    parser.add_argument("--nginx", action="store_true", help="Créer la configuration Nginx")
    parser.add_argument("--systemd", action="store_true", help="Créer le service systemd")
    parser.add_argument("--backup", action="store_true", help="Créer une sauvegarde")
    
    args = parser.parse_args()
    
    print("🚀 Déploiement de l'interface web d'automatisation")
    print("=" * 50)
    
    # Vérifications préliminaires
    check_python_version()
    check_dependencies()
    
    # Création des répertoires
    create_directories()
    
    # Vérification des fichiers
    if not check_files():
        print("❌ Déploiement interrompu - fichiers manquants")
        sys.exit(1)
    
    # Création des fichiers de configuration
    create_environment_file(args.port, debug=False)
    create_startup_script()
    create_health_check()
    
    # Création des fichiers optionnels
    if args.docker:
        create_dockerfile()
        create_docker_compose(args.port)
    
    if args.nginx and args.domain:
        create_nginx_config(args.domain, args.port)
    
    if args.systemd and args.user:
        working_dir = os.getcwd()
        create_systemd_service(args.user, working_dir, args.port)
    
    if args.backup:
        create_backup()
    
    print("\n" + "=" * 50)
    print("✅ Déploiement terminé avec succès !")
    print("\n📋 Prochaines étapes:")
    print("1. Vérifiez la configuration dans le fichier .env")
    print("2. Testez l'interface: python3 web_interface.py")
    print("3. Accédez à l'interface: http://localhost:" + str(args.port))
    
    if args.docker:
        print("4. Pour Docker: docker-compose up -d")
    
    if args.systemd and args.user:
        print("5. Pour systemd: sudo systemctl enable aircall-web-interface.service")
    
    print("\n🔧 Commandes utiles:")
    print(f"   Démarrage: ./start_web_interface.sh --port {args.port}")
    print("   Vérification: python3 health_check.py")
    print("   Logs: tail -f logs/web_interface.log")

if __name__ == "__main__":
    main()
