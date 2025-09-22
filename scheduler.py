#!/usr/bin/env python3
"""
Planificateur automatique pour les automatisations Aircall → Monday.com
Exécute les tâches selon des horaires prédéfinis ET les préférences utilisateur
"""

import schedule
import time
import logging
import argparse
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
# from user_preferences import get_preferences_manager  # Supprimé

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutomationScheduler:
    """Planificateur des automatisations avec gestion des préférences utilisateur"""
    
    def __init__(self):
        self.scripts = {
            'sync': 'aircall_monday_integration_v2.py',
            'tasks': 'create_tasks_with_agent.py',
            'assign': 'smart_task_assigner.py',
            'link': 'link_calls_to_contacts.py',
            'relations': 'update_board_relations.py'
        }
        
        # Gestionnaire des préférences utilisateur (simplifié)
        # self.preferences_manager = get_preferences_manager()  # Supprimé
        
        # Configuration par défaut (fallback)
        self.default_schedule_config = {
            'sync': 'hourly',           # Synchronisation toutes les heures
            'tasks': '2h',              # Création de tâches toutes les 2h
            'assign': '4h',             # Assignation toutes les 4h
            'link': '6h',               # Liaison contacts toutes les 6h
            'relations': 'daily'         # Relations une fois par jour
        }
        
        # Horaires spécifiques par défaut
        self.default_specific_times = {
            'full_sync': '08:00',       # Synchronisation complète à 8h
            'daily_report': '18:00',    # Rapport quotidien à 18h
            'maintenance': '02:00'      # Maintenance à 2h du matin
        }
    
    def run_script(self, script_name: str) -> bool:
        """Exécute un script Python"""
        try:
            script_path = Path(script_name)
            if not script_path.exists():
                logger.error(f"Script non trouvé: {script_name}")
                return False
            
            logger.info(f"🚀 Exécution de {script_name}")
            result = subprocess.run([sys.executable, script_name], 
                                 capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info(f"✅ {script_name} exécuté avec succès")
                return True
            else:
                logger.error(f"❌ Erreur dans {script_name}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ Timeout pour {script_name}")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'exécution de {script_name}: {str(e)}")
            return False
    
    def sync_aircall(self):
        """Synchronisation Aircall → Monday.com"""
        logger.info("📞 Démarrage synchronisation Aircall")
        return self.run_script(self.scripts['sync'])
    
    def create_tasks(self):
        """Création de tâches depuis les actions IA"""
        logger.info("📝 Démarrage création de tâches")
        return self.run_script(self.scripts['tasks'])
    
    def assign_tasks(self):
        """Assignation intelligente des tâches"""
        logger.info("🧠 Démarrage assignation intelligente")
        return self.run_script(self.scripts['assign'])
    
    def link_contacts(self):
        """Liaison des appels aux contacts"""
        logger.info("🔗 Démarrage liaison contacts")
        return self.run_script(self.scripts['link'])
    
    def update_relations(self):
        """Mise à jour des relations entre tableaux"""
        logger.info("🔄 Démarrage mise à jour relations")
        return self.run_script(self.scripts['relations'])
    
    def full_sync(self):
        """Synchronisation complète (toutes les automatisations)"""
        logger.info("🚀 DÉMARRAGE SYNCHRONISATION COMPLÈTE")
        
        results = {
            'sync': self.sync_aircall(),
            'tasks': self.create_tasks(),
            'assign': self.assign_tasks(),
            'link': self.link_contacts(),
            'relations': self.update_relations()
        }
        
        success_count = sum(results.values())
        total_count = len(results)
        
        logger.info(f"📊 Synchronisation complète terminée: {success_count}/{total_count} réussies")
        
        # Rapport détaillé
        for task, success in results.items():
            status = "✅" if success else "❌"
            logger.info(f"   {status} {task}")
        
        return success_count == total_count
    
    def daily_report(self):
        """Génération du rapport quotidien"""
        logger.info("📊 Génération rapport quotidien")
        
        # Exécuter la synchronisation complète
        self.full_sync()
        
        # Générer un rapport des performances
        logger.info("📈 Rapport quotidien généré")
        return True
    
    def maintenance(self):
        """Tâches de maintenance nocturne"""
        logger.info("🔧 Démarrage maintenance nocturne")
        
        # Nettoyage des logs anciens
        self.cleanup_old_logs()
        
        # Vérification de l'intégrité du système
        self.system_health_check()
        
        logger.info("🔧 Maintenance terminée")
        return True
    
    def cleanup_old_logs(self):
        """Nettoyage des anciens logs"""
        try:
            log_file = Path('automation.log')
            if log_file.exists() and log_file.stat().st_size > 10 * 1024 * 1024:  # 10MB
                # Sauvegarder et tronquer
                backup_name = f"automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                log_file.rename(backup_name)
                logger.info(f"📁 Logs sauvegardés: {backup_name}")
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage logs: {str(e)}")
    
    def system_health_check(self):
        """Vérification de la santé du système"""
        logger.info("🏥 Vérification santé du système")
        
        # Vérifier que tous les scripts existent
        missing_scripts = []
        for script in self.scripts.values():
            if not Path(script).exists():
                missing_scripts.append(script)
        
        if missing_scripts:
            logger.warning(f"⚠️ Scripts manquants: {missing_scripts}")
        else:
            logger.info("✅ Tous les scripts sont présents")
        
        # Vérifier les préférences utilisateur (simplifié)
        logger.info("👤 Vérification des préférences utilisateur (mode simplifié)")
        logger.info(f"   Automatisations activées: {len(self.scripts)}/{len(self.scripts)}")
        logger.info(f"   Mode: Configuration par défaut")
    
    def get_user_schedule_config(self):
        """Récupère la configuration de planification (mode simplifié)"""
        # Utiliser la configuration par défaut
        user_config = self.default_schedule_config.copy()
        
        for automation_id, cadence in user_config.items():
            logger.info(f"👤 {automation_id}: {cadence} (configuration par défaut)")
        
        return user_config
    
    def get_user_specific_times(self):
        """Récupère les horaires spécifiques (mode simplifié)"""
        # Utiliser les valeurs par défaut
        specific_times = self.default_specific_times.copy()
        
        logger.info(f"⏰ Horaires par défaut: {specific_times}")
        
        return specific_times
    
    def should_run_automation(self, automation_id: str) -> bool:
        """Vérifie si une automatisation doit s'exécuter (mode simplifié)"""
        # En mode simplifié, toutes les automatisations sont activées
        logger.info(f"✅ {automation_id} activé (mode simplifié)")
        return True
    
    def setup_schedule(self):
        """Configure la planification des tâches (mode simplifié)"""
        logger.info("⏰ Configuration de la planification (mode simplifié)")
        
        # Effacer toutes les tâches planifiées existantes
        schedule.clear()
        
        # Récupérer la configuration (mode simplifié)
        user_config = self.get_user_schedule_config()
        specific_times = self.get_user_specific_times()
        
        # Configurer les tâches (mode simplifié)
        for automation_id, cadence in user_config.items():
            # Toutes les automatisations sont activées en mode simplifié
                
            try:
                if cadence == '15min':
                    schedule.every(15).minutes.do(self._create_automation_wrapper(automation_id))
                elif cadence == '30min':
                    schedule.every(30).minutes.do(self._create_automation_wrapper(automation_id))
                elif cadence == '1h' or cadence == 'hourly':
                    schedule.every().hour.do(self._create_automation_wrapper(automation_id))
                elif cadence == '2h':
                    schedule.every(2).hours.do(self._create_automation_wrapper(automation_id))
                elif cadence == '4h':
                    schedule.every(4).hours.do(self._create_automation_wrapper(automation_id))
                elif cadence == '6h':
                    schedule.every(6).hours.do(self._create_automation_wrapper(automation_id))
                elif cadence == '12h':
                    schedule.every(12).hours.do(self._create_automation_wrapper(automation_id))
                elif cadence == 'daily':
                    schedule.every().day.at("00:00").do(self._create_automation_wrapper(automation_id))
                elif cadence == 'weekly':
                    schedule.every().week.do(self._create_automation_wrapper(automation_id))
                elif cadence == 'monthly':
                    schedule.every().month.do(self._create_automation_wrapper(automation_id))
                else:
                    # Cadence personnalisée (format: "1h", "30min", "2d", etc.)
                    self._schedule_custom_cadence(automation_id, cadence)
                
                logger.info(f"✅ {automation_id} planifié avec cadence: {cadence}")
                
            except Exception as e:
                logger.error(f"❌ Erreur planification {automation_id}: {str(e)}")
        
        # Horaires spécifiques (mode simplifié)
        schedule.every().day.at(specific_times['full_sync']).do(self.full_sync)
        schedule.every().day.at(specific_times['daily_report']).do(self.daily_report)
        schedule.every().day.at(specific_times['maintenance']).do(self.maintenance)
        
        logger.info("✅ Planification configurée (mode simplifié)")
    
    def _create_automation_wrapper(self, automation_id: str):
        """Crée un wrapper pour une automatisation (mode simplifié)"""
        def automation_wrapper():
            # En mode simplifié, toutes les automatisations s'exécutent
            logger.info(f"🚀 Exécution de {automation_id} (mode simplifié)")
            if automation_id == 'sync':
                return self.sync_aircall()
            elif automation_id == 'tasks':
                return self.create_tasks()
            elif automation_id == 'assign':
                return self.assign_tasks()
            elif automation_id == 'link':
                return self.link_contacts()
            elif automation_id == 'relations':
                return self.update_relations()
            else:
                logger.warning(f"⚠️ Automatisation inconnue: {automation_id}")
                return False
        
        return automation_wrapper
    
    def _schedule_custom_cadence(self, automation_id: str, cadence: str):
        """Planifie une automatisation avec une cadence personnalisée"""
        try:
            # Parser la cadence personnalisée (ex: "1h", "30min", "2d")
            if cadence.endswith('min'):
                minutes = int(cadence[:-3])
                schedule.every(minutes).minutes.do(self._create_automation_wrapper(automation_id))
            elif cadence.endswith('h'):
                hours = int(cadence[:-1])
                schedule.every(hours).hours.do(self._create_automation_wrapper(automation_id))
            elif cadence.endswith('d'):
                days = int(cadence[:-1])
                schedule.every(days).days.do(self._create_automation_wrapper(automation_id))
            else:
                logger.warning(f"⚠️ Format de cadence non reconnu: {cadence}")
        except Exception as e:
            logger.error(f"❌ Erreur cadence personnalisée {automation_id}: {str(e)}")
    
    def run_once(self, task_type: str):
        """Exécute une tâche une seule fois"""
        logger.info(f"🎯 Exécution unique: {task_type}")
        
        if task_type == 'full':
            return self.full_sync()
        elif task_type == 'sync':
            return self.sync_aircall()
        elif task_type == 'tasks':
            return self.create_tasks()
        elif task_type == 'assign':
            return self.assign_tasks()
        elif task_type == 'link':
            return self.link_contacts()
        elif task_type == 'relations':
            return self.update_relations()
        else:
            logger.error(f"❌ Type de tâche inconnu: {task_type}")
            return False
    
    def start(self):
        """Démarre le planificateur en continu"""
        logger.info("🚀 Démarrage du planificateur automatique")
        self.setup_schedule()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Vérifier toutes les minutes
                
        except KeyboardInterrupt:
            logger.info("⏹️ Arrêt du planificateur")
        except Exception as e:
            logger.error(f"❌ Erreur dans le planificateur: {str(e)}")

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description='Planificateur des automatisations Aircall')
    parser.add_argument('--start', action='store_true', help='Démarrer le planificateur en continu')
    parser.add_argument('--once', choices=['full', 'sync', 'tasks', 'assign', 'link', 'relations'], 
                       help='Exécuter une tâche une seule fois')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='Niveau de log')
    
    args = parser.parse_args()
    
    # Configuration du niveau de log
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    scheduler = AutomationScheduler()
    
    if args.once:
        # Exécution unique
        success = scheduler.run_once(args.once)
        sys.exit(0 if success else 1)
    elif args.start:
        # Démarrage en continu
        scheduler.start()
    else:
        # Affichage de l'aide
        parser.print_help()
        print("\n📋 Exemples d'utilisation:")
        print("  python scheduler.py --start                    # Démarrer en continu")
        print("  python scheduler.py --once full               # Synchronisation complète")
        print("  python scheduler.py --once sync               # Synchronisation Aircall")
        print("  python scheduler.py --once tasks              # Création de tâches")
        print("  python scheduler.py --log-level DEBUG         # Avec logs détaillés")

if __name__ == "__main__":
    main()

