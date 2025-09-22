#!/usr/bin/env python3
"""
Script de démarrage automatique des automatisations
Peut être utilisé avec cron, systemd ou en tant que service Windows
"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

# Ajouter le répertoire courant au path Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import validate_config
from scheduler import AutomationScheduler

def setup_logging():
    """Configure le système de logging"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Fichier de log avec date
    log_file = log_dir / f"automation_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def check_environment():
    """Vérifie l'environnement d'exécution"""
    logger = logging.getLogger(__name__)
    
    # Vérifier Python
    logger.info(f"🐍 Version Python: {sys.version}")
    
    # Vérifier le répertoire de travail
    work_dir = Path.cwd()
    logger.info(f"📁 Répertoire de travail: {work_dir}")
    
    # Vérifier les fichiers essentiels
    essential_files = [
        'config.py',
        'scheduler.py',
        'aircall_monday_integration_v2.py',
        'create_tasks_from_actions.py',
        'smart_task_assigner.py'
    ]
    
    missing_files = []
    for file in essential_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"❌ Fichiers manquants: {missing_files}")
        return False
    
    logger.info("✅ Environnement vérifié")
    return True

def start_as_service():
    """Démarre l'automatisation en tant que service"""
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Démarrage du service d'automatisation")
    
    try:
        # Vérifier la configuration
        if not validate_config():
            logger.error("❌ Configuration invalide")
            return False
        
        # Vérifier l'environnement
        if not check_environment():
            logger.error("❌ Environnement invalide")
            return False
        
        # Démarrer le planificateur
        scheduler = AutomationScheduler()
        logger.info("✅ Planificateur démarré")
        
        # Démarrer en continu
        scheduler.start()
        
    except KeyboardInterrupt:
        logger.info("⏹️ Arrêt du service (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Erreur dans le service: {str(e)}")
        return False
    
    return True

def start_scheduled():
    """Démarre l'automatisation avec planification"""
    logger = logging.getLogger(__name__)
    
    logger.info("⏰ Démarrage de l'automatisation planifiée")
    
    try:
        # Vérifier la configuration
        if not validate_config():
            logger.error("❌ Configuration invalide")
            return False
        
        # Vérifier l'environnement
        if not check_environment():
            logger.error("❌ Environnement invalide")
            return False
        
        # Démarrer le planificateur
        scheduler = AutomationScheduler()
        logger.info("✅ Planificateur démarré")
        
        # Configurer la planification
        scheduler.setup_schedule()
        logger.info("✅ Planification configurée")
        
        # Démarrer en continu
        scheduler.start()
        
    except KeyboardInterrupt:
        logger.info("⏹️ Arrêt de l'automatisation (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Erreur dans l'automatisation: {str(e)}")
        return False
    
    return True

def run_once(task_type: str = "full"):
    """Exécute une tâche une seule fois"""
    logger = logging.getLogger(__name__)
    
    logger.info(f"🎯 Exécution unique: {task_type}")
    
    try:
        # Vérifier la configuration
        if not validate_config():
            logger.error("❌ Configuration invalide")
            return False
        
        # Vérifier l'environnement
        if not check_environment():
            logger.error("❌ Environnement invalide")
            return False
        
        # Exécuter la tâche
        scheduler = AutomationScheduler()
        success = scheduler.run_once(task_type)
        
        if success:
            logger.info("✅ Tâche exécutée avec succès")
        else:
            logger.error("❌ Tâche échouée")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'exécution: {str(e)}")
        return False

def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Démarrage automatique des automatisations')
    parser.add_argument('--service', action='store_true', 
                       help='Démarrer en tant que service (mode continu)')
    parser.add_argument('--scheduled', action='store_true',
                       help='Démarrer avec planification automatique')
    parser.add_argument('--once', choices=['full', 'sync', 'tasks', 'assign', 'link', 'relations'],
                       help='Exécuter une tâche une seule fois')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Niveau de log')
    parser.add_argument('--daemon', action='store_true',
                       help='Mode daemon (détaché du terminal)')
    
    args = parser.parse_args()
    
    # Configuration du logging
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    logger = setup_logging()
    
    # Mode daemon
    if args.daemon:
        logger.info("👻 Mode daemon activé")
        # Détacher du terminal
        try:
            pid = os.fork()
            if pid > 0:
                # Processus parent
                logger.info(f"🚀 Service démarré avec PID: {pid}")
                sys.exit(0)
        except OSError:
            logger.error("❌ Impossible de démarrer en mode daemon")
            sys.exit(1)
    
    logger.info("🤖 Démarrage du système d'automatisation")
    logger.info(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    try:
        if args.once:
            # Exécution unique
            success = run_once(args.once)
            sys.exit(0 if success else 1)
        elif args.service:
            # Mode service
            success = start_as_service()
            sys.exit(0 if success else 1)
        elif args.scheduled:
            # Mode planifié
            success = start_scheduled()
            sys.exit(0 if success else 1)
        else:
            # Mode par défaut (planifié)
            logger.info("⏰ Mode par défaut: planification automatique")
            success = start_scheduled()
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        logger.info("⏹️ Arrêt demandé par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
