#!/usr/bin/env python3
"""
Interface web complète pour Taskimmo
Combine gestion des automatisations, horaires et logs
"""

from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify
from datetime import datetime
import json
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'taskimmo_secret_key_2024'

# État du système
system_state = {
    'logs': [
        f"{datetime.now().strftime('%H:%M:%S')} - INFO - Interface complète initialisée"
    ]
}

# Configuration des automatisations
automations_config = {
    'sync_aircall': {
        'name': 'Synchronisation Aircall',
        'description': 'Synchronise les appels Aircall vers Monday.com',
        'enabled': True,
        'icon': 'fas fa-phone',
        'cadence': 'Toutes les heures',
        'cron': '0 * * * *',
        'last_execution': 'Jamais',
        'success_rate': 95
    },
    'create_tasks': {
        'name': 'Création de Tâches',
        'description': 'Crée des tâches à partir des actions IA',
        'enabled': True,
        'icon': 'fas fa-tasks',
        'cadence': 'Toutes les 2h',
        'cron': '0 */2 * * *',
        'last_execution': 'Jamais',
        'success_rate': 90
    },
    'link_contacts': {
        'name': 'Liaison des Contacts',
        'description': 'Lie les appels aux contacts existants',
        'enabled': True,
        'icon': 'fas fa-link',
        'cadence': 'Toutes les 4h',
        'cron': '0 */4 * * *',
        'last_execution': 'Jamais',
        'success_rate': 85
    }
}

# Template principal - Interface complète
COMPLETE_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Taskimmo - Interface Complète</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .hero-section { background: linear-gradient(135deg, #007bff 0%, #0056b3 100%); color: white; }
        .automation-card { border-left: 4px solid #28a745; }
        .schedule-card { border-left: 4px solid #007bff; }
        .logs-card { border-left: 4px solid #ffc107; }
        .cron-display { font-family: monospace; background: #f8f9fa; padding: 10px; border-radius: 5px; }
        .log-entry { font-family: monospace; font-size: 0.9em; }
        .status-running { color: #28a745; }
        .status-stopped { color: #dc3545; }
        .section-title { border-bottom: 2px solid #dee2e6; padding-bottom: 10px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-cogs"></i> Taskimmo - Interface Complète
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/api/status" target="_blank">
                    <i class="fas fa-info-circle"></i> API Status
                </a>
            </div>
        </div>
    </nav>

    <div class="hero-section py-4">
        <div class="container text-center">
            <h1 class="display-5 mb-3">
                <i class="fas fa-cogs"></i> Interface Complète Taskimmo
            </h1>
            <p class="lead">Gestion des automatisations, horaires et logs en un seul endroit</p>
        </div>
    </div>

    <div class="container mt-4">
        <!-- Section Automatisations -->
        <div class="row mb-4">
            <div class="col-12">
                <h2 class="section-title"><i class="fas fa-robot"></i> Gestion des Automatisations</h2>
            </div>
        </div>
        
        <div class="row mb-5">
            {% for automation_id, automation in automations_config.items() %}
            <div class="col-md-6 mb-4">
                <div class="card automation-card">
                    <div class="card-header">
                        <h5><i class="{{ automation.icon }}"></i> {{ automation.name }}</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-6">
                                <p><strong>Statut:</strong> <span class="badge bg-{{ 'success' if automation.enabled else 'danger' }}">{{ 'Actif' if automation.enabled else 'Inactif' }}</span></p>
                                <p><strong>Description:</strong> {{ automation.description }}</p>
                            </div>
                            <div class="col-6">
                                <p><strong>Fréquence:</strong> {{ automation.cadence }}</p>
                                <p><strong>Dernière exécution:</strong> {{ automation.last_execution }}</p>
                            </div>
                        </div>
                        <div class="btn-group w-100">
                            <a href="/run/{{ automation_id }}" class="btn btn-warning btn-sm">
                                <i class="fas fa-play"></i> Exécuter
                            </a>
                            <a href="/toggle/{{ automation_id }}" class="btn btn-{{ 'danger' if automation.enabled else 'success' }} btn-sm">
                                <i class="fas fa-power-off"></i> {{ 'Désactiver' if automation.enabled else 'Activer' }}
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <!-- Section Horaires -->
        <div class="row mb-4">
            <div class="col-12">
                <h2 class="section-title"><i class="fas fa-clock"></i> Gestion des Horaires</h2>
            </div>
        </div>
        
        <div class="row mb-5">
            {% for automation_id, automation in automations_config.items() %}
            <div class="col-md-6 mb-4">
                <div class="card schedule-card">
                    <div class="card-header">
                        <h5><i class="{{ automation.icon }}"></i> {{ automation.name }} - Horaires</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label class="form-label"><strong>Horaires actuels :</strong></label>
                            <div class="cron-display">{{ automation.cron or 'Non configuré' }}</div>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label"><strong>Préconfigurations :</strong></label>
                            <select class="form-select" id="preset_{{ automation_id }}">
                                <option value="">Sélectionner un horaire</option>
                                <option value="0 * * * *">Toutes les heures</option>
                                <option value="0 */2 * * *">Toutes les 2h</option>
                                <option value="0 */4 * * *">Toutes les 4h</option>
                                <option value="0 9-18 * * 1-5">Heures ouvrables</option>
                                <option value="0 9,12,15,18 * * 1-5">4 fois/jour en semaine</option>
                            </select>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label"><strong>Horaires personnalisés :</strong></label>
                            <input type="text" class="form-control" id="custom_{{ automation_id }}" 
                                   placeholder="Ex: 0 9-18 * * 1-5" 
                                   value="{{ automation.cron or '' }}">
                            <div class="form-text">Format cron : minute heure jour mois jour_semaine</div>
                        </div>
                        
                        <div class="btn-group w-100">
                            <button onclick="updateSchedule('{{ automation_id }}')" class="btn btn-primary btn-sm">
                                <i class="fas fa-save"></i> Mettre à jour
                            </button>
                            <button onclick="testSchedule('{{ automation_id }}')" class="btn btn-info btn-sm">
                                <i class="fas fa-play"></i> Tester
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <!-- Section Logs -->
        <div class="row mb-4">
            <div class="col-12">
                <h2 class="section-title"><i class="fas fa-list"></i> Logs en Temps Réel</h2>
            </div>
        </div>
        
        <div class="row">
            <div class="col-12">
                <div class="card logs-card">
                    <div class="card-header">
                        <h5><i class="fas fa-list"></i> Logs Récents</h5>
                    </div>
                    <div class="card-body">
                        <div class="logs-container" id="logsContainer" style="max-height: 400px; overflow-y: auto; background: #f8f9fa; padding: 15px; border-radius: 5px;">
                            {% for log in system_state.logs[-20:] %}
                            <div class="log-entry mb-2">
                                <small class="text-muted">{{ log }}</small>
                            </div>
                            {% endfor %}
                        </div>
                        <div class="mt-3">
                            <button onclick="clearLogs()" class="btn btn-warning btn-sm">
                                <i class="fas fa-trash"></i> Effacer les logs
                            </button>
                            <button onclick="refreshLogs()" class="btn btn-primary btn-sm">
                                <i class="fas fa-sync"></i> Actualiser
                            </button>
                            <a href="/logs" class="btn btn-info btn-sm">
                                <i class="fas fa-download"></i> Télécharger logs
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Guide des Horaires -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-info-circle"></i> Guide des Horaires Cron</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Exemples d'horaires :</h6>
                                <ul>
                                    <li><code>0 9 * * 1-5</code> - Tous les jours ouvrables à 9h</li>
                                    <li><code>0 */2 * * *</code> - Toutes les 2 heures</li>
                                    <li><code>0 9,12,15,18 * * 1-5</code> - 4 fois par jour en semaine</li>
                                    <li><code>0 0 * * 0</code> - Tous les dimanches à minuit</li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h6>Format cron :</h6>
                                <ul>
                                    <li><strong>Minute :</strong> 0-59</li>
                                    <li><strong>Heure :</strong> 0-23</li>
                                    <li><strong>Jour :</strong> 1-31</li>
                                    <li><strong>Mois :</strong> 1-12</li>
                                    <li><strong>Jour semaine :</strong> 0-7 (0 et 7 = dimanche)</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function updateSchedule(automationId) {
            const customCron = document.getElementById('custom_' + automationId).value;
            const presetCron = document.getElementById('preset_' + automationId).value;
            const cronValue = presetCron || customCron;
            
            if (!cronValue) {
                alert('Veuillez sélectionner un horaire ou saisir une valeur personnalisée');
                return;
            }
            
            fetch('/api/schedule/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    automation: automationId,
                    schedule: cronValue
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('Horaires mis à jour avec succès !');
                    location.reload();
                } else {
                    alert('Erreur : ' + data.message);
                }
            })
            .catch(error => {
                alert('Erreur lors de la mise à jour : ' + error);
            });
        }
        
        function testSchedule(automationId) {
            alert('Test de l\\'automatisation ' + automationId + ' - Cette fonctionnalité sera disponible prochainement');
        }
        
        function clearLogs() {
            if (confirm('Êtes-vous sûr de vouloir effacer tous les logs ?')) {
                window.location.href = '/clear_logs';
            }
        }
        
        function refreshLogs() {
            fetch('/logs')
                .then(response => response.json())
                .then(data => {
                    const logsContainer = document.getElementById('logsContainer');
                    logsContainer.innerHTML = data.logs.slice(-20).map(log => 
                        `<div class="log-entry mb-2"><small class="text-muted">${log}</small></div>`
                    ).join('');
                })
                .catch(error => console.error('Erreur lors du rafraîchissement des logs:', error));
        }
        
        // Auto-fill custom field when preset is selected
        document.querySelectorAll('select[id^="preset_"]').forEach(select => {
            select.addEventListener('change', function() {
                const automationId = this.id.replace('preset_', '');
                const customInput = document.getElementById('custom_' + automationId);
                if (this.value) {
                    customInput.value = this.value;
                }
            });
        });
        
        // Auto-refresh des logs toutes les 30 secondes
        setInterval(function() {
            refreshLogs();
        }, 30000);
    </script>
</body>
</html>
"""

# Routes
@app.route('/')
def index():
    """Page d'accueil - Interface complète"""
    return render_template_string(COMPLETE_TEMPLATE, 
                                system_state=system_state,
                                automations_config=automations_config)

@app.route('/run/<automation_id>')
def run_automation(automation_id):
    """Exécute une automatisation"""
    try:
        add_log(f"Exécution de l'automatisation {automation_id}")
        flash(f'Automatisation {automation_id} exécutée', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        add_log(f"Erreur lors de l'exécution de {automation_id}: {str(e)}")
        flash(f'Erreur: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/toggle/<automation_id>')
def toggle_automation(automation_id):
    """Active/désactive une automatisation"""
    try:
        if automation_id in automations_config:
            automations_config[automation_id]['enabled'] = not automations_config[automation_id]['enabled']
            status = "activée" if automations_config[automation_id]['enabled'] else "désactivée"
            add_log(f"Automatisation {automation_id} {status}")
            flash(f'Automatisation {status}', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        add_log(f"Erreur toggle automatisation: {str(e)}")
        flash(f'Erreur: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/clear_logs')
def clear_logs():
    """Efface les logs"""
    system_state['logs'] = [f"{datetime.now().strftime('%H:%M:%S')} - INFO - Logs effacés"]
    flash('Logs effacés', 'info')
    return redirect(url_for('index'))

@app.route('/logs')
def get_logs():
    """Retourne les logs en JSON"""
    return jsonify({'logs': system_state['logs']})

@app.route('/api/status')
def api_status():
    """Statut de l'API"""
    return jsonify({
        'status': 'active',
        'timestamp': datetime.now().isoformat(),
        'automations': len(automations_config),
        'logs_count': len(system_state['logs'])
    })

@app.route('/api/schedule/update', methods=['POST'])
def update_schedule():
    """Met à jour les horaires d'une automatisation"""
    try:
        data = request.get_json()
        automation_id = data.get('automation')
        schedule = data.get('schedule')
        
        if automation_id in automations_config:
            automations_config[automation_id]['cron'] = schedule
            add_log(f"Horaires mis à jour pour {automation_id}: {schedule}")
            return jsonify({'status': 'success', 'message': 'Horaires mis à jour'})
        else:
            return jsonify({'status': 'error', 'message': 'Automatisation non trouvée'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

def add_log(message):
    """Ajoute un log"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"{timestamp} - INFO - {message}"
    system_state['logs'].append(log_entry)
    
    # Garder seulement les 50 derniers logs
    if len(system_state['logs']) > 50:
        system_state['logs'] = system_state['logs'][-50:]

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
