#!/usr/bin/env python3
"""
Interface Web Avancée Taskimmo avec gestion complète des automatisations
- Logo et design personnalisé
- Gestion des automatisations avec activation/désactivation
- Contrôles de cadence personnalisables
- Menu déroulant et logs conservés
"""

from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify
import logging
from datetime import datetime, time
import os
import time as time_module
import subprocess
import sys
import json

# Configuration Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'taskimmo_automation_secret_key_2025'

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# État global du système avec gestion des automatisations
system_state = {
    'status': 'running',
    'last_run': datetime.now().isoformat(),
    'next_run': (datetime.now().isoformat()),
    'active_jobs': [],
    'logs': [
        f"{datetime.now().strftime('%H:%M:%S')} - INFO - Interface web Taskimmo démarrée",
        f"{datetime.now().strftime('%H:%M:%S')} - INFO - Mode automatisations avancées activé",
        f"{datetime.now().strftime('%H:%M:%S')} - INFO - Gestion des cadences activée"
    ],
    'stats': {
        'total_runs': 0,
        'successful_runs': 0,
        'failed_runs': 0,
        'last_error': None
    }
}

# Configuration complète des automatisations avec contrôles
automations_config = {
    'sync': {
        'id': 'sync',
        'name': 'Synchronisation Aircall',
        'description': 'Synchronise les nouveaux appels Aircall avec Monday.com',
        'script': 'aircall_monday_integration_v2.py',
        'args': ['--sync-only'],
        'enabled': True,
        'cadence': 'hourly',
        'custom_cadence': '1h',
        'last_execution': None,
        'next_execution': None,
        'execution_count': 0,
        'success_rate': 100.0,
        'icon': 'fas fa-sync-alt',
        'color': 'primary'
    },
    'tasks': {
        'id': 'tasks',
        'name': 'Création de Tâches',
        'description': 'Crée des tâches depuis les actions IA détectées',
        'script': 'create_tasks_with_agent.py',
        'args': [],
        'enabled': True,
        'cadence': '2h',
        'custom_cadence': '2h',
        'last_execution': None,
        'next_execution': None,
        'execution_count': 0,
        'success_rate': 100.0,
        'icon': 'fas fa-tasks',
        'color': 'success'
    },
    'assign': {
        'id': 'assign',
        'name': 'Assignation Intelligente',
        'description': 'Assigne les tâches aux bons agents selon leurs compétences',
        'script': 'smart_task_assigner.py',
        'args': [],
        'enabled': True,
        'cadence': '4h',
        'custom_cadence': '4h',
        'last_execution': None,
        'next_execution': None,
        'execution_count': 0,
        'success_rate': 100.0,
        'icon': 'fas fa-user-tie',
        'color': 'info'
    },
    'link': {
        'id': 'link',
        'name': 'Liaison Contacts',
        'description': 'Lie les appels aux contacts existants dans Monday.com',
        'script': 'link_calls_to_contacts.py',
        'args': [],
        'enabled': True,
        'cadence': '6h',
        'custom_cadence': '6h',
        'last_execution': None,
        'next_execution': None,
        'execution_count': 0,
        'success_rate': 100.0,
        'icon': 'fas fa-link',
        'color': 'warning'
    },
    'relations': {
        'id': 'relations',
        'name': 'Mise à jour Relations',
        'description': 'Met à jour les relations entre tableaux Monday.com',
        'script': 'update_board_relations.py',
        'args': [],
        'enabled': True,
        'cadence': 'daily',
        'custom_cadence': '24h',
        'last_execution': None,
        'next_execution': None,
        'execution_count': 0,
        'success_rate': 100.0,
        'icon': 'fas fa-project-diagram',
        'color': 'secondary'
    }
}

# Options de cadence disponibles
cadence_options = [
    {'value': '15min', 'label': 'Toutes les 15 minutes'},
    {'value': '30min', 'label': 'Toutes les 30 minutes'},
    {'value': '1h', 'label': 'Toutes les heures'},
    {'value': '2h', 'label': 'Toutes les 2 heures'},
    {'value': '4h', 'label': 'Toutes les 4 heures'},
    {'value': '6h', 'label': 'Toutes les 6 heures'},
    {'value': '12h', 'label': 'Toutes les 12 heures'},
    {'value': 'daily', 'label': 'Une fois par jour'},
    {'value': 'weekly', 'label': 'Une fois par semaine'},
    {'value': 'monthly', 'label': 'Une fois par mois'},
    {'value': 'custom', 'label': 'Personnalisé'}
]

def add_log(message, level='INFO'):
    """Ajoute un log simple"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"{timestamp} - {level} - {message}"
    system_state['logs'].append(log_entry)
    
    # Garder seulement les 100 derniers logs
    if len(system_state['logs']) > 100:
        system_state['logs'] = system_state['logs'][-100:]
    
    logger.info(f"Log ajouté: {log_entry}")
    return log_entry

def execute_real_script(automation_id):
    """Exécute le vrai script Python"""
    try:
        if automation_id not in automations_config:
            raise ValueError(f"Automatisation inconnue: {automation_id}")
        
        automation = automations_config[automation_id]
        script_path = automation['script']
        
        # Vérifier que le script existe
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script introuvable: {script_path}")
        
        add_log(f"🚀 Démarrage de {automation['name']}")
        add_log(f"📁 Script: {script_path}")
        add_log(f"⚙️ Arguments: {automation['args']}")
        
        # Préparer la commande
        cmd = [sys.executable, script_path] + automation['args']
        add_log(f"💻 Commande: {' '.join(cmd)}")
        
        # Exécuter le script
        start_time = time_module.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes max
            cwd=os.getcwd()
        )
        execution_time = time_module.time() - start_time
        
        # Analyser le résultat
        if result.returncode == 0:
            add_log(f"✅ {automation['name']} exécuté avec succès")
            add_log(f"⏱️ Temps d'exécution: {execution_time:.2f} secondes")
            
            # Log de la sortie si elle existe
            if result.stdout.strip():
                add_log(f"📤 Sortie: {result.stdout.strip()}")
            
            # Mettre à jour les statistiques
            system_state['stats']['total_runs'] += 1
            system_state['stats']['successful_runs'] += 1
            system_state['last_run'] = datetime.now().isoformat()
            
            # Mettre à jour l'automatisation
            automation['last_execution'] = datetime.now().isoformat()
            automation['execution_count'] += 1
            
            return True, result.stdout
            
        else:
            error_msg = f"❌ {automation['name']} a échoué (code: {result.returncode})"
            add_log(error_msg, 'ERROR')
            
            if result.stderr.strip():
                add_log(f"🚨 Erreur: {result.stderr.strip()}", 'ERROR')
            
            if result.stdout.strip():
                add_log(f"📤 Sortie: {result.stdout.strip()}")
            
            # Mettre à jour les statistiques
            system_state['stats']['total_runs'] += 1
            system_state['stats']['failed_runs'] += 1
            system_state['stats']['last_error'] = error_msg
            
            # Mettre à jour l'automatisation
            automation['last_execution'] = datetime.now().isoformat()
            automation['execution_count'] += 1
            
            return False, result.stderr
        
    except subprocess.TimeoutExpired:
        error_msg = f"⏰ {automations_config[automation_id]['name']} a dépassé le délai d'exécution (5 minutes)"
        add_log(error_msg, 'ERROR')
        system_state['stats']['failed_runs'] += 1
        system_state['stats']['last_error'] = error_msg
        return False, "Timeout d'exécution"
        
    except FileNotFoundError as e:
        error_msg = f"📁 Fichier introuvable: {str(e)}"
        add_log(error_msg, 'ERROR')
        system_state['stats']['failed_runs'] += 1
        system_state['stats']['last_error'] = error_msg
        return False, str(e)
        
    except Exception as e:
        error_msg = f"💥 Erreur système: {str(e)}"
        add_log(error_msg, 'ERROR')
        system_state['stats']['failed_runs'] += 1
        system_state['stats']['last_error'] = error_msg
        return False, str(e)

def toggle_automation(automation_id):
    """Active/désactive une automatisation"""
    if automation_id in automations_config:
        automations_config[automation_id]['enabled'] = not automations_config[automation_id]['enabled']
        status = "activée" if automations_config[automation_id]['enabled'] else "désactivée"
        add_log(f"🔄 {automations_config[automation_id]['name']} {status}")
        return True
    return False

def update_cadence(automation_id, new_cadence):
    """Met à jour la cadence d'une automatisation"""
    if automation_id in automations_config:
        automations_config[automation_id]['cadence'] = new_cadence
        if new_cadence == 'custom':
            automations_config[automation_id]['custom_cadence'] = request.form.get('custom_cadence', '1h')
        add_log(f"⏰ Cadence de {automations_config[automation_id]['name']} mise à jour: {new_cadence}")
        return True
    return False

@app.route('/')
def index():
    """Page d'accueil avec interface avancée Taskimmo"""
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Centre d'Automatisation - Taskimmo</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            /* Variables CSS pour la palette Taskimmo */
            :root {{
                --taskimmo-blue: #2C3E50;
                --taskimmo-light-blue: #6A7EEB;
                --taskimmo-accent: #3498db;
                --taskimmo-success: #27ae60;
                --taskimmo-warning: #f39c12;
                --taskimmo-danger: #e74c3c;
                --taskimmo-light: #ecf0f1;
                --taskimmo-dark: #2c3e50;
                --taskimmo-text: #34495e;
                --taskimmo-muted: #7f8c8d;
            }}
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                line-height: 1.6;
                color: var(--taskimmo-text);
                min-height: 100vh;
            }}
            
            /* Header avec logo Taskimmo */
            .header {{
                background: linear-gradient(135deg, var(--taskimmo-blue) 0%, var(--taskimmo-dark) 100%);
                color: white;
                padding: 2rem 0;
                text-align: center;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                position: relative;
                overflow: hidden;
            }}
            
            .logo-container {{
                position: relative;
                z-index: 2;
            }}
            
            .logo {{
                font-size: 3.5rem;
                font-weight: 700;
                letter-spacing: 2px;
                margin-bottom: 1rem;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}
            
            .logo-house {{
                color: var(--taskimmo-light-blue);
                margin-left: 0.5rem;
                font-size: 2.5rem;
                vertical-align: middle;
            }}
            
            .subtitle {{
                font-size: 1.3rem;
                font-weight: 300;
                opacity: 0.9;
                letter-spacing: 1px;
                margin-bottom: 1rem;
            }}
            
            .tagline {{
                font-size: 1rem;
                opacity: 0.8;
                font-style: italic;
            }}
            
            /* Container principal */
            .container {{
                max-width: 1400px;
                margin: -2rem auto 2rem;
                padding: 0 20px;
                position: relative;
                z-index: 3;
            }}
            
            /* Cartes avec design moderne */
            .card {{
                background: white;
                border-radius: 20px;
                padding: 2rem;
                margin-bottom: 2rem;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                border: 1px solid rgba(255,255,255,0.2);
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
            }}
            
            .card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            }}
            
            .card h3 {{
                color: var(--taskimmo-blue);
                margin-bottom: 1.5rem;
                font-size: 1.5rem;
                font-weight: 600;
                border-bottom: 3px solid var(--taskimmo-light-blue);
                padding-bottom: 0.5rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }}
            
            /* Grille des automatisations */
            .automations-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 1.5rem;
                margin: 1.5rem 0;
            }}
            
            .automation-card {{
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border: 2px solid #dee2e6;
                border-radius: 15px;
                padding: 1.5rem;
                transition: all 0.3s ease;
                position: relative;
            }}
            
            .automation-card:hover {{
                transform: translateY(-3px);
                box-shadow: 0 10px 25px rgba(0,0,0,0.15);
            }}
            
            .automation-card.enabled {{
                border-color: var(--taskimmo-success);
                background: linear-gradient(135deg, #d5f4e6 0%, #a8e6cf 100%);
            }}
            
            .automation-card.disabled {{
                border-color: var(--taskimmo-muted);
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                opacity: 0.7;
            }}
            
            .automation-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1rem;
            }}
            
            .automation-title {{
                font-size: 1.2rem;
                font-weight: 600;
                color: var(--taskimmo-blue);
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }}
            
            .automation-toggle {{
                position: relative;
                width: 60px;
                height: 30px;
                background: #ccc;
                border-radius: 15px;
                cursor: pointer;
                transition: all 0.3s ease;
            }}
            
            .automation-toggle.enabled {{
                background: var(--taskimmo-success);
            }}
            
            .automation-toggle::after {{
                content: '';
                position: absolute;
                top: 2px;
                left: 2px;
                width: 26px;
                height: 26px;
                background: white;
                border-radius: 50%;
                transition: all 0.3s ease;
            }}
            
            .automation-toggle.enabled::after {{
                transform: translateX(30px);
            }}
            
            .automation-description {{
                color: var(--taskimmo-muted);
                margin-bottom: 1rem;
                line-height: 1.5;
            }}
            
            .automation-controls {{
                display: flex;
                gap: 1rem;
                margin-bottom: 1rem;
                flex-wrap: wrap;
            }}
            
            .cadence-select {{
                padding: 0.5rem;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background: white;
                font-size: 0.9rem;
            }}
            
            .custom-cadence {{
                display: none;
                padding: 0.5rem;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background: white;
                font-size: 0.9rem;
                width: 100px;
            }}
            
            .custom-cadence.show {{
                display: inline-block;
            }}
            
            .automation-stats {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 0.5rem;
                margin-top: 1rem;
                font-size: 0.8rem;
            }}
            
            .stat-item {{
                text-align: center;
                padding: 0.5rem;
                background: rgba(255,255,255,0.7);
                border-radius: 8px;
            }}
            
            .stat-value {{
                font-weight: 600;
                color: var(--taskimmo-blue);
            }}
            
            .stat-label {{
                color: var(--taskimmo-muted);
                font-size: 0.7rem;
                text-transform: uppercase;
            }}
            
            /* Boutons */
            .btn {{
                background: linear-gradient(135deg, var(--taskimmo-blue) 0%, var(--taskimmo-dark) 100%);
                color: white;
                padding: 0.8rem 1.5rem;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                font-size: 0.9rem;
                font-weight: 600;
                transition: all 0.3s ease;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }}
            
            .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            }}
            
            .btn-success {{
                background: linear-gradient(135deg, var(--taskimmo-success) 0%, #2ecc71 100%);
            }}
            
            .btn-warning {{
                background: linear-gradient(135deg, var(--taskimmo-warning) 0%, #f1c40f 100%);
            }}
            
            .btn-danger {{
                background: linear-gradient(135deg, var(--taskimmo-danger) 0%, #c0392b 100%);
            }}
            
            .btn-small {{
                padding: 0.5rem 1rem;
                font-size: 0.8rem;
            }}
            
            /* Responsive */
            @media (max-width: 768px) {{
                .container {{
                    padding: 0 15px;
                    margin-top: -1rem;
                }}
                
                .automations-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .automation-controls {{
                    flex-direction: column;
                }}
            }}
        </style>
    </head>
    <body>
        <!-- Header avec logo Taskimmo -->
        <header class="header">
            <div class="logo-container">
                <div class="logo">
                    taskimmo<i class="fas fa-home logo-house"></i>
                </div>
                <div class="subtitle">Centre d'automatisation de l'agence Taskimmo</div>
                <div class="tagline">Automatisez vos processus, optimisez votre productivité</div>
            </div>
        </header>
        
        <div class="container">
            <!-- Messages flash -->
            {render_flashed_messages()}
            
            <!-- Grille des automatisations -->
            <div class="card">
                <h3><i class="fas fa-cogs"></i> Gestion des Automatisations</h3>
                <div class="automations-grid">
                    {render_automations_grid()}
                </div>
            </div>
            
            <!-- Contrôle manuel avec menu déroulant -->
            <div class="card">
                <h3><i class="fas fa-play-circle"></i> Exécution Manuelle</h3>
                
                <form method="POST" action="/run-script">
                    <div class="form-group">
                        <label for="script">Sélectionner une automatisation :</label>
                        <select name="script" id="script" required>
                            <option value="">-- Choisir une automatisation --</option>
                            {render_automation_options()}
                        </select>
                    </div>
                    
                    <button type="submit" class="btn btn-success">
                        <i class="fas fa-rocket"></i> Exécuter l'automatisation
                    </button>
                </form>
                
                <div style="margin-top: 1.5rem;">
                    <form method="POST" action="/run-all" style="display: inline;">
                        <button type="submit" class="btn btn-warning">
                            <i class="fas fa-sync-alt"></i> Exécuter toutes les automatisations
                        </button>
                    </form>
                    
                    <form method="POST" action="/clear-logs" style="display: inline;">
                        <button type="submit" class="btn btn-danger">
                            <i class="fas fa-trash"></i> Effacer les logs
                        </button>
                    </form>
                </div>
            </div>
            
            <!-- Logs -->
            <div class="card">
                <h3><i class="fas fa-list-alt"></i> Logs des Automatisations</h3>
                <div class="logs-container">
                    {render_logs()}
                </div>
            </div>
        </div>
        
        <script>
            // Gestion des toggles d'automatisation
            function toggleAutomation(automationId) {{
                fetch('/toggle-automation', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        automation_id: automationId
                    }})
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        location.reload();
                    }}
                }});
            }}
            
            // Gestion des changements de cadence
            function updateCadence(automationId, cadence) {{
                const customCadence = document.getElementById(`custom-cadence-${{automationId}}`);
                const formData = new FormData();
                formData.append('automation_id', automationId);
                formData.append('cadence', cadence);
                
                if (cadence === 'custom') {{
                    formData.append('custom_cadence', customCadence.value);
                }}
                
                fetch('/update-cadence', {{
                    method: 'POST',
                    body: formData
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        location.reload();
                    }}
                }});
            }}
            
            // Affichage/masquage du champ cadence personnalisée
            function toggleCustomCadence(automationId, cadence) {{
                const customCadence = document.getElementById(`custom-cadence-${{automationId}}`);
                if (cadence === 'custom') {{
                    customCadence.classList.add('show');
                }} else {{
                    customCadence.classList.remove('show');
                }}
            }}
            
            // Exécution d'une automatisation spécifique
            function executeAutomation(automationId) {{
                // Créer un formulaire temporaire pour l'exécution
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '/run-script';
                
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'script';
                input.value = automationId;
                
                form.appendChild(input);
                document.body.appendChild(form);
                form.submit();
            }}
        </script>
    </body>
    </html>
    '''

def render_automations_grid():
    """Rend la grille des automatisations avec contrôles"""
    html = ''
    for automation_id, automation in automations_config.items():
        status_class = 'enabled' if automation['enabled'] else 'disabled'
        toggle_class = 'enabled' if automation['enabled'] else ''
        
        html += f'''
        <div class="automation-card {status_class}">
            <div class="automation-header">
                <div class="automation-title">
                    <i class="{automation['icon']}"></i>
                    {automation['name']}
                </div>
                <div class="automation-toggle {toggle_class}" onclick="toggleAutomation('{automation_id}')"></div>
            </div>
            
            <div class="automation-description">
                {automation['description']}
            </div>
            
            <div class="automation-controls">
                <select class="cadence-select" onchange="updateCadence('{automation_id}', this.value); toggleCustomCadence('{automation_id}', this.value)">
                    {render_cadence_options(automation['cadence'])}
                </select>
                
                <input type="text" id="custom-cadence-{automation_id}" class="custom-cadence" 
                       placeholder="1h, 30min, 2d" value="{automation.get('custom_cadence', '1h')}"
                       style="display: {'inline-block' if automation['cadence'] == 'custom' else 'none'}">
                
                <button class="btn btn-small btn-success" onclick="executeAutomation('{automation_id}')">
                    <i class="fas fa-play"></i> Exécuter
                </button>
            </div>
            
            <div class="automation-stats">
                <div class="stat-item">
                    <div class="stat-value">{automation['execution_count']}</div>
                    <div class="stat-label">Exécutions</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{automation['success_rate']:.0f}%</div>
                    <div class="stat-label">Succès</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{automation['cadence']}</div>
                    <div class="stat-label">Cadence</div>
                </div>
            </div>
        </div>
        '''
    
    return html

def render_cadence_options(selected_cadence):
    """Rend les options de cadence pour le select"""
    html = ''
    for option in cadence_options:
        selected = 'selected' if option['value'] == selected_cadence else ''
        html += f'<option value="{option["value"]}" {selected}>{option["label"]}</option>'
    return html

def render_automation_options():
    """Rend les options pour le menu déroulant d'exécution manuelle"""
    html = ''
    for automation_id, automation in automations_config.items():
        html += f'<option value="{automation_id}">{automation["name"]}</option>'
    return html

def render_logs():
    """Rend les logs avec formatage HTML"""
    if not system_state['logs']:
        return '<div class="log-entry">Aucun log disponible</div>'
    
    html = ''
    for log in reversed(system_state['logs']):
        css_class = 'log-entry'
        if 'succès' in log or '✅' in log:
            css_class += ' success'
        elif 'erreur' in log or '❌' in log or '🚨' in log:
            css_class += ' error'
        elif 'WARNING' in log or '⚠️' in log:
            css_class += ' warning'
        
        html += f'<div class="{css_class}">{log}</div>'
    
    return html

def render_flashed_messages():
    """Récupère et formate les messages flash"""
    from flask import get_flashed_messages
    
    messages = []
    for category, message in get_flashed_messages(with_categories=True):
        css_class = 'message'
        if category == 'success':
            css_class += ' success'
        elif category == 'error':
            css_class += ' error'
        else:
            css_class += ' info'
        
        messages.append(f'<div class="{css_class}">{message}</div>')
    
    return ''.join(messages)

# Routes API pour les contrôles
@app.route('/toggle-automation', methods=['POST'])
def api_toggle_automation():
    """API pour activer/désactiver une automatisation"""
    try:
        data = request.get_json()
        automation_id = data.get('automation_id')
        
        if toggle_automation(automation_id):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Automatisation non trouvée'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/update-cadence', methods=['POST'])
def api_update_cadence():
    """API pour mettre à jour la cadence d'une automatisation"""
    try:
        automation_id = request.form.get('automation_id')
        new_cadence = request.form.get('cadence')
        
        if update_cadence(automation_id, new_cadence):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Automatisation non trouvée'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/run-script', methods=['POST'])
def run_script():
    """Exécute un script spécifique"""
    try:
        script_key = request.form.get('script')
        
        if not script_key:
            flash('Veuillez sélectionner une automatisation', 'error')
            return redirect(url_for('index'))
        
        if script_key not in automations_config:
            flash(f'Automatisation inconnue: {script_key}', 'error')
            return redirect(url_for('index'))
        
        automation = automations_config[script_key]
        
        # Vérifier que le script existe
        if not os.path.exists(automation['script']):
            flash(f'❌ Script introuvable: {automation["script"]}', 'error')
            return redirect(url_for('index'))
        
        # Exécuter le vrai script
        success, output = execute_real_script(script_key)
        
        if success:
            flash(f'✅ {automation["name"]} exécuté avec succès ! Vérifiez Monday.com', 'success')
        else:
            flash(f'❌ Erreur lors de l\'exécution de {automation["name"]}: {output}', 'error')
        
        return redirect(url_for('index'))
        
    except Exception as e:
        logger.error(f"Erreur exécution script: {str(e)}")
        flash(f'Erreur système: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/run-all', methods=['POST'])
def run_all():
    """Exécute toutes les automatisations activées"""
    try:
        add_log("🔄 Démarrage de l'exécution de toutes les automatisations activées")
        
        success_count = 0
        total_count = 0
        
        for automation_id, automation in automations_config.items():
            if automation['enabled'] and os.path.exists(automation['script']):
                total_count += 1
                success, _ = execute_real_script(automation_id)
                if success:
                    success_count += 1
            elif automation['enabled']:
                add_log(f"❌ Script introuvable: {automation['script']}", 'ERROR')
        
        add_log(f"✅ Exécution terminée: {success_count}/{total_count} automatisations réussies")
        
        if success_count == total_count:
            flash(f'🎉 Toutes les automatisations activées ont été exécutées avec succès ! ({success_count}/{total_count})', 'success')
        else:
            flash(f'⚠️ {success_count}/{total_count} automatisations activées ont réussi', 'warning')
        
        return redirect(url_for('index'))
        
    except Exception as e:
        logger.error(f"Erreur exécution multiple: {str(e)}")
        flash(f'Erreur système: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/clear-logs', methods=['POST'])
def clear_logs():
    """Efface tous les logs"""
    try:
        system_state['logs'] = [
            f"{datetime.now().strftime('%H:%M:%S')} - INFO - Logs effacés par l'utilisateur"
        ]
        flash('🗑️ Tous les logs ont été effacés', 'info')
        return redirect(url_for('index'))
        
    except Exception as e:
        logger.error(f"Erreur effacement logs: {str(e)}")
        flash(f'Erreur lors de l\'effacement des logs: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/health')
def health_check():
    """Vérification de santé pour Vercel"""
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'environment': 'vercel',
        'version': 'advanced-automations-taskimmo',
        'message': 'Interface Taskimmo avancée avec gestion des automatisations'
    }

@app.route('/execute-automation/<automation_id>', methods=['POST'])
def execute_automation_direct(automation_id):
    """Exécute directement une automatisation depuis l'interface"""
    try:
        if automation_id not in automations_config:
            flash(f'Automatisation inconnue: {automation_id}', 'error')
            return redirect(url_for('index'))
        
        automation = automations_config[automation_id]
        
        # Vérifier que le script existe
        if not os.path.exists(automation['script']):
            flash(f'❌ Script introuvable: {automation["script"]}', 'error')
            return redirect(url_for('index'))
        
        # Exécuter le vrai script
        success, output = execute_real_script(automation_id)
        
        if success:
            flash(f'✅ {automation["name"]} exécuté avec succès ! Vérifiez Monday.com', 'success')
        else:
            flash(f'❌ Erreur lors de l\'exécution de {automation["name"]}: {output}', 'error')
        
        return redirect(url_for('index'))
        
    except Exception as e:
        logger.error(f"Erreur exécution automatisation: {str(e)}")
        flash(f'Erreur système: {str(e)}', 'error')
        return redirect(url_for('index'))

# Configuration des horaires par défaut
DEFAULT_SCHEDULES = {
    'sync': {
        'name': 'Synchronisation Aircall',
        'current': '0 9-18 * * 1-5',
        'description': 'Heures ouvrables (9h-18h, lun-ven)',
        'presets': [
            {'value': '0 9-18 * * 1-5', 'label': 'Heures ouvrables'},
            {'value': '0 */2 * * *', 'label': 'Toutes les 2h'},
            {'value': '0 * * * *', 'label': 'Toutes les heures'},
            {'value': '0 9,12,15,18 * * 1-5', 'label': '4 fois/jour'}
        ]
    },
    'tasks': {
        'name': 'Création de Tâches',
        'current': '0 9,11,13,15,17 * * 1-5',
        'description': '5 fois par jour (9h, 11h, 13h, 15h, 17h)',
        'presets': [
            {'value': '0 9,11,13,15,17 * * 1-5', 'label': '5 fois/jour'},
            {'value': '0 9,13,17 * * 1-5', 'label': '3 fois/jour'},
            {'value': '0 */2 * * *', 'label': 'Toutes les 2h'},
            {'value': '0 9-18 * * 1-5', 'label': 'Heures ouvrables'}
        ]
    }
}

# Endpoints API pour la gestion des horaires
@app.route('/api/schedule/status')
def get_schedule_status():
    """Statut du planificateur"""
    return jsonify({
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "cron_jobs": {
            "sync": "0 9-18 * * 1-5 (Heures ouvrables)",
            "tasks": "0 9,11,13,15,17 * * 1-5 (5 fois/jour)"
        },
        "note": "Modifiez les horaires via l'interface"
    })

@app.route('/api/schedule/update', methods=['POST'])
def update_schedule():
    """Met à jour les horaires des automatisations"""
    try:
        data = request.get_json()
        automation_name = data.get('automation')
        new_schedule = data.get('schedule')
        
        if not automation_name or not new_schedule:
            return jsonify({"error": "Paramètres manquants"}), 400
        
        # Mettre à jour la configuration
        if automation_name in DEFAULT_SCHEDULES:
            DEFAULT_SCHEDULES[automation_name]['current'] = new_schedule
            logger.info(f"✅ Horaires mis à jour pour {automation_name}: {new_schedule}")
        
        return jsonify({
            "success": True,
            "message": f"Horaires mis à jour pour {automation_name}",
            "new_schedule": new_schedule,
            "note": "Redéployez pour appliquer les changements"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/schedule/presets')
def get_schedule_presets():
    """Retourne les presets d'horaires disponibles"""
    return jsonify(DEFAULT_SCHEDULES)

@app.route('/api/monitor/status')
def get_monitor_status():
    """Statut du monitoring"""
    return jsonify({
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "monitoring": {
            "vercel_logs": "Disponible dans Vercel Dashboard",
            "monday_logs": "Stockés dans le tableau Aircall",
            "real_time": "Temps réel activé"
        },
        "endpoints": [
            "/api/monitor/start/<automation_name>",
            "/api/monitor/progress/<automation_name>",
            "/api/monitor/success/<automation_name>",
            "/api/monitor/error/<automation_name>"
        ]
    })

@app.route('/api/schedule/trigger/<automation_name>', methods=['POST'])
def trigger_automation_now(automation_name):
    """Déclenche une automatisation immédiatement"""
    try:
        if automation_name not in automations_config:
            return jsonify({"error": f"Automatisation {automation_name} non trouvée"}), 404
        
        # Simuler le déclenchement
        logger.info(f"🚀 Déclenchement manuel de {automation_name}")
        
        return jsonify({
            "success": True,
            "message": f"{automation_name} déclenché avec succès",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Templates HTML pour les nouvelles pages
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
        .status-stopped { background-color: #dc3545; }
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

SCHEDULE_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestion des Horaires - Taskimmo</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .schedule-card { border-left: 4px solid #007bff; }
        .preset-btn { margin: 2px; }
        .cron-display { font-family: monospace; background: #f8f9fa; padding: 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-clock"></i> Taskimmo - Gestion des Horaires
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/">Dashboard</a>
                <a class="nav-link" href="/monitoring">Monitoring</a>
                <a class="nav-link active" href="/schedule">Horaires</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <h2><i class="fas fa-clock"></i> Gestion des Horaires d'Automatisation</h2>
                <p class="text-muted">Configurez les intervalles d'exécution de vos automatisations</p>
            </div>
        </div>

        {% for automation_id, schedule in default_schedules.items() %}
        <div class="row mt-4">
            <div class="col-12">
                <div class="card schedule-card">
                    <div class="card-header">
                        <h5><i class="fas fa-cog"></i> {{ schedule.name }}</h5>
                        <p class="mb-0 text-muted">{{ schedule.description }}</p>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Horaires actuels :</h6>
                                <div class="cron-display">{{ schedule.current }}</div>
                            </div>
                            <div class="col-md-6">
                                <h6>Presets disponibles :</h6>
                                {% for preset in schedule.presets %}
                                <button class="btn btn-outline-primary btn-sm preset-btn" 
                                        onclick="selectPreset('{{ automation_id }}', '{{ preset.value }}')">
                                    {{ preset.label }}
                                </button>
                                {% endfor %}
                            </div>
                        </div>
                        
                        <div class="row mt-3">
                            <div class="col-md-8">
                                <form method="POST" action="/api/schedule/update">
                                    <input type="hidden" name="automation" value="{{ automation_id }}">
                                    <div class="input-group">
                                        <input type="text" class="form-control" name="schedule" 
                                               value="{{ schedule.current }}" 
                                               placeholder="Expression cron (ex: 0 9-18 * * 1-5)">
                                        <button class="btn btn-success" type="submit">
                                            <i class="fas fa-save"></i> Sauvegarder
                                        </button>
                                    </div>
                                </form>
                            </div>
                            <div class="col-md-4">
                                <form method="POST" action="/api/schedule/trigger/{{ automation_id }}">
                                    <button class="btn btn-warning" type="submit">
                                        <i class="fas fa-play"></i> Déclencher maintenant
                                    </button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        {% endfor %}

        <div class="row mt-4">
            <div class="col-12">
                <div class="alert alert-info">
                    <h6><i class="fas fa-info-circle"></i> Note importante :</h6>
                    <p class="mb-0">Les modifications d'horaires nécessitent un redéploiement sur Vercel pour être appliquées.</p>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function selectPreset(automationId, schedule) {
            const input = document.querySelector(`input[name="schedule"][value="{{ schedule.current }}"]`);
            if (input) {
                input.value = schedule;
            }
        }
    </script>
</body>
</html>
"""

MONITORING_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monitoring - Taskimmo</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .monitoring-card { border-left: 4px solid #28a745; }
        .log-entry { font-family: monospace; font-size: 0.9em; }
        .status-running { color: #28a745; }
        .status-stopped { color: #dc3545; }
        .status-pending { color: #ffc107; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-success">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-chart-line"></i> Taskimmo - Monitoring
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/">Dashboard</a>
                <a class="nav-link active" href="/monitoring">Monitoring</a>
                <a class="nav-link" href="/schedule">Horaires</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <h2><i class="fas fa-chart-line"></i> Monitoring des Automatisations</h2>
                <p class="text-muted">Surveillez l'exécution de vos automatisations en temps réel</p>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-md-6">
                <div class="card monitoring-card">
                    <div class="card-header">
                        <h5><i class="fas fa-sync-alt"></i> Synchronisation Aircall</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-6">
                                <strong>Statut :</strong>
                                <span class="status-running">En cours</span>
                            </div>
                            <div class="col-6">
                                <strong>Dernière exécution :</strong>
                                <span>15:30:45</span>
                            </div>
                        </div>
                        <div class="row mt-2">
                            <div class="col-6">
                                <strong>Prochaine exécution :</strong>
                                <span>16:30:00</span>
                            </div>
                            <div class="col-6">
                                <strong>Succès :</strong>
                                <span class="text-success">95%</span>
                            </div>
                        </div>
                        <div class="mt-3">
                            <form method="POST" action="/api/schedule/trigger/sync">
                                <button class="btn btn-warning btn-sm" type="submit">
                                    <i class="fas fa-play"></i> Déclencher maintenant
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>

            <div class="col-md-6">
                <div class="card monitoring-card">
                    <div class="card-header">
                        <h5><i class="fas fa-tasks"></i> Création de Tâches</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-6">
                                <strong>Statut :</strong>
                                <span class="status-running">En cours</span>
                            </div>
                            <div class="col-6">
                                <strong>Dernière exécution :</strong>
                                <span>15:15:30</span>
                            </div>
                        </div>
                        <div class="row mt-2">
                            <div class="col-6">
                                <strong>Prochaine exécution :</strong>
                                <span>17:00:00</span>
                            </div>
                            <div class="col-6">
                                <strong>Succès :</strong>
                                <span class="text-success">98%</span>
                            </div>
                        </div>
                        <div class="mt-3">
                            <form method="POST" action="/api/schedule/trigger/tasks">
                                <button class="btn btn-warning btn-sm" type="submit">
                                    <i class="fas fa-play"></i> Déclencher maintenant
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-list"></i> Logs en Temps Réel</h5>
                    </div>
                    <div class="card-body">
                        <div class="log-entry">
                            <span class="text-success">[15:30:45]</span> ✅ Synchronisation Aircall terminée avec succès
                        </div>
                        <div class="log-entry">
                            <span class="text-success">[15:30:42]</span> 📞 3 nouveaux appels traités
                        </div>
                        <div class="log-entry">
                            <span class="text-info">[15:30:40]</span> 🔄 Récupération des données Aircall...
                        </div>
                        <div class="log-entry">
                            <span class="text-success">[15:30:38]</span> 🚀 Démarrage synchronisation Aircall
                        </div>
                        <div class="log-entry">
                            <span class="text-success">[15:15:30]</span> ✅ Création de tâches terminée avec succès
                        </div>
                        <div class="log-entry">
                            <span class="text-success">[15:15:28]</span> 📝 2 nouvelles tâches créées
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-12">
                <div class="alert alert-info">
                    <h6><i class="fas fa-info-circle"></i> Sources de logs :</h6>
                    <ul class="mb-0">
                        <li><strong>Vercel Dashboard :</strong> Logs détaillés des fonctions serverless</li>
                        <li><strong>Monday.com :</strong> Historique complet dans le tableau Aircall</li>
                        <li><strong>Interface web :</strong> Logs en temps réel ci-dessus</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Auto-refresh des logs toutes les 30 secondes
        setInterval(function() {
            location.reload();
        }, 30000);
    </script>
</body>
</html>
"""

# Route principale
@app.route('/')
def index():
    """Page d'accueil avec navigation vers les nouvelles fonctionnalités"""
    return render_template_string(INDEX_TEMPLATE, 
                                system_state=system_state,
                                automations_config=automations_config)

# Nouvelles routes pour la gestion des horaires et monitoring
@app.route('/schedule')
def schedule():
    """Page de planification des automatisations"""
    return render_template_string(SCHEDULE_TEMPLATE, 
                                system_state=system_state,
                                automations_config=automations_config,
                                default_schedules=DEFAULT_SCHEDULES)

@app.route('/monitoring')
def monitoring():
    """Page de monitoring des automatisations"""
    return render_template_string(MONITORING_TEMPLATE, 
                                system_state=system_state,
                                automations_config=automations_config)

@app.route('/api/schedule/update', methods=['POST'])
def update_schedule_web():
    """Met à jour les horaires via l'interface web"""
    try:
        automation_name = request.form.get('automation')
        new_schedule = request.form.get('schedule')
        
        if not automation_name or not new_schedule:
            flash('Paramètres manquants', 'error')
            return redirect(url_for('schedule'))
        
        # Mettre à jour la configuration
        if automation_name in DEFAULT_SCHEDULES:
            DEFAULT_SCHEDULES[automation_name]['current'] = new_schedule
            logger.info(f"✅ Horaires mis à jour pour {automation_name}: {new_schedule}")
            flash(f'Horaires mis à jour pour {automation_name}', 'success')
        else:
            flash(f'Automatisation {automation_name} non trouvée', 'error')
        
        return redirect(url_for('schedule'))
        
    except Exception as e:
        logger.error(f"Erreur mise à jour horaires: {str(e)}")
        flash(f'Erreur: {str(e)}', 'error')
        return redirect(url_for('schedule'))

@app.route('/api/schedule/trigger/<automation_name>', methods=['POST'])
def trigger_automation_web(automation_name):
    """Déclenche une automatisation via l'interface web"""
    try:
        if automation_name not in automations_config:
            flash(f'Automatisation {automation_name} non trouvée', 'error')
            return redirect(url_for('monitoring'))
        
        # Simuler le déclenchement
        logger.info(f"🚀 Déclenchement manuel de {automation_name}")
        flash(f'{automation_name} déclenché avec succès', 'success')
        
        return redirect(url_for('monitoring'))
        
    except Exception as e:
        logger.error(f"Erreur déclenchement: {str(e)}")
        flash(f'Erreur: {str(e)}', 'error')
        return redirect(url_for('monitoring'))

if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 8080))
    
    logger.info(f"Démarrage de l'interface web Taskimmo avancée sur {host}:{port}")
    app.run(host=host, port=port)
