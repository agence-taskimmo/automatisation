#!/bin/bash

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
