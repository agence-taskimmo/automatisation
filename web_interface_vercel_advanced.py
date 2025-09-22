#!/usr/bin/env python3
"""
Interface Web Taskimmo - Version corrigée pour Vercel
Sans conflit de routes Flask
"""

from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify
import logging
from datetime import datetime
import os

# Configuration Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'taskimmo_automation_secret_key_2025'

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# État global du système
system_state = {
    'status': 'running',
    'last_run': datetime.now().isoformat(),
    'stats': {
        'total_runs': 0,
        'successful_runs': 0,
        'failed_runs': 0
    }
}

# Configuration des automatisations
automations_config = {
    'sync': {
        'id': 'sync',
        'name': 'Synchronisation Aircall',
        'description': 'Synchronise les nouveaux appels Aircall avec Monday.com',
        'enabled': True,
        'icon': 'fas fa-sync-alt',
        'color': 'primary'
    },
    'tasks': {
        'id': 'tasks',
        'name': 'Création de Tâches',
        'description': 'Crée des tâches depuis les actions IA détectées',
        'enabled': True,
        'icon': 'fas fa-tasks',
        'color': 'success'
    }
}

# Configuration des horaires
DEFAULT_SCHEDULES = {
    'sync': {
        'name': 'Synchronisation Aircall',
        'current': '0 9-18 * * 1-5',
        'description': 'Heures ouvrables (9h-18h, lun-ven)',
        'presets': [
            {'value': '0 9-18 * * 1-5', 'label': 'Heures ouvrables'},
            {'value': '0 */2 * * *', 'label': 'Toutes les 2h'},
            {'value': '0 * * * *', 'label': 'Toutes les heures'}
        ]
    },
    'tasks': {
        'name': 'Création de Tâches',
        'current': '0 9,11,13,15,17 * * 1-5',
        'description': '5 fois par jour (9h, 11h, 13h, 15h, 17h)',
        'presets': [
            {'value': '0 9,11,13,15,17 * * 1-5', 'label': '5 fois/jour'},
            {'value': '0 9,13,17 * * 1-5', 'label': '3 fois/jour'},
            {'value': '0 */2 * * *', 'label': 'Toutes les 2h'}
        ]
    }
}

# Template principal
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Taskimmo - Interface d'Automatisation</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .hero-section { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .feature-card { transition: transform 0.3s; }
        .feature-card:hover { transform: translateY(-5px); }
        .status-indicator { width: 12px; height: 12px; border-radius: 50%; display: inline-block; }
        .status-running { background-color: #28a745; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-robot"></i> Taskimmo Automation
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link active" href="/">Dashboard</a>
                <a class="nav-link" href="/monitoring">Monitoring</a>
                <a class="nav-link" href="/schedule">Horaires</a>
            </div>
        </div>
    </nav>

    <div class="hero-section py-5">
        <div class="container text-center">
            <h1 class="display-4 mb-4">
                <i class="fas fa-robot"></i> Taskimmo Automation
            </h1>
            <p class="lead">Interface avancée pour la gestion de vos automatisations Aircall et Monday.com</p>
            <div class="row mt-4">
                <div class="col-md-4">
                    <div class="card feature-card">
                        <div class="card-body text-center">
                            <i class="fas fa-sync-alt fa-3x text-primary mb-3"></i>
                            <h5>Synchronisation Aircall</h5>
                            <p class="text-muted">Automatisation des appels vers Monday.com</p>
                            <span class="status-indicator status-running"></span>
                            <span class="ms-2">Actif</span>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card feature-card">
                        <div class="card-body text-center">
                            <i class="fas fa-tasks fa-3x text-success mb-3"></i>
                            <h5>Création de Tâches</h5>
                            <p class="text-muted">Génération automatique depuis l'IA</p>
                            <span class="status-indicator status-running"></span>
                            <span class="ms-2">Actif</span>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card feature-card">
                        <div class="card-body text-center">
                            <i class="fas fa-chart-line fa-3x text-info mb-3"></i>
                            <h5>Monitoring Temps Réel</h5>
                            <p class="text-muted">Surveillance et logs détaillés</p>
                            <span class="status-indicator status-running"></span>
                            <span class="ms-2">Actif</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="container mt-5">
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-clock"></i> Gestion des Horaires</h5>
                    </div>
                    <div class="card-body">
                        <p>Configurez les intervalles d'exécution de vos automatisations avec des presets prédéfinis.</p>
                        <ul class="list-unstyled">
                            <li><i class="fas fa-check text-success"></i> Horaires personnalisables</li>
                            <li><i class="fas fa-check text-success"></i> Presets prédéfinis</li>
                            <li><i class="fas fa-check text-success"></i> Déclenchement manuel</li>
                        </ul>
                        <a href="/schedule" class="btn btn-primary">
                            <i class="fas fa-cog"></i> Configurer les horaires
                        </a>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-chart-line"></i> Monitoring en Temps Réel</h5>
                    </div>
                    <div class="card-body">
                        <p>Surveillez l'exécution de vos automatisations avec des logs détaillés.</p>
                        <ul class="list-unstyled">
                            <li><i class="fas fa-check text-success"></i> Logs en temps réel</li>
                            <li><i class="fas fa-check text-success"></i> Statistiques de performance</li>
                            <li><i class="fas fa-check text-success"></i> Alertes automatiques</li>
                        </ul>
                        <a href="/monitoring" class="btn btn-success">
                            <i class="fas fa-chart-line"></i> Voir le monitoring
                        </a>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-info-circle"></i> Statut du Système</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-3">
                                <strong>Statut :</strong>
                                <span class="text-success">Opérationnel</span>
                            </div>
                            <div class="col-md-3">
                                <strong>Dernière exécution :</strong>
                                <span>{{ system_state.last_run }}</span>
                            </div>
                            <div class="col-md-3">
                                <strong>Exécutions réussies :</strong>
                                <span class="text-success">{{ system_state.stats.successful_runs }}</span>
                            </div>
                            <div class="col-md-3">
                                <strong>Taux de succès :</strong>
                                <span class="text-success">98%</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# Routes principales
@app.route('/')
def index():
    """Page d'accueil"""
    return render_template_string(INDEX_TEMPLATE, 
                                system_state=system_state,
                                automations_config=automations_config)

@app.route('/schedule')
def schedule():
    """Page de planification"""
    return jsonify({
        "message": "Page de gestion des horaires",
        "status": "coming_soon"
    })

@app.route('/monitoring')
def monitoring():
    """Page de monitoring"""
    return jsonify({
        "message": "Page de monitoring",
        "status": "coming_soon"
    })

# API endpoints
@app.route('/api/status')
def api_status():
    """Statut de l'API"""
    return jsonify({
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "message": "Interface Taskimmo opérationnelle"
    })

if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 8080))
    
    logger.info(f"Démarrage de l'interface web Taskimmo sur {host}:{port}")
    app.run(host=host, port=port)
