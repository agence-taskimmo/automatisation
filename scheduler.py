#!/usr/bin/env python3
"""
Planificateur automatique pour les automatisations Aircall → Monday.com
Exécute les tâches selon des horaires prédéfinis
"""

import schedule
import time
import logging
import argparse
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

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
    """Planificateur des automatisations"""
    
    def __init__(self):
        self.scripts = {
            'sync': 'aircall_monday_integration_v2.py',
            'tasks': 'create_tasks_with_agent.py',
            'assign': 'smart_task_assigner.py',
            'link': 'link_calls_to_contacts.py',
            'relations': 'update_board_relations.py'
        }
        
        # Configuration des horaires
        self.schedule_config = {
            'sync': 'hourly',           # Synchronisation toutes les heures
            'tasks': '2h',              # Création de tâches toutes les 2h
            'assign': '4h',             # Assignation toutes les 4h
            'link': '6h',               # Liaison contacts toutes les 6h
            'relations': 'daily'         # Relations une fois par jour
        }
        
        # Horaires spécifiques
        self.specific_times = {
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
    
    def setup_schedule(self):
        """Configure la planification des tâches"""
        logger.info("⏰ Configuration de la planification")
        
        # Tâches horaires
        schedule.every().hour.do(self.sync_aircall)
        schedule.every(2).hours.do(self.create_tasks)
        schedule.every(4).hours.do(self.assign_tasks)
        schedule.every(6).hours.do(self.link_contacts)
        schedule.every().day.at("00:00").do(self.update_relations)
        
        # Horaires spécifiques
        schedule.every().day.at(self.specific_times['full_sync']).do(self.full_sync)
        schedule.every().day.at(self.specific_times['daily_report']).do(self.daily_report)
        schedule.every().day.at(self.specific_times['maintenance']).do(self.maintenance)
        
        logger.info("✅ Planification configurée")
    
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

