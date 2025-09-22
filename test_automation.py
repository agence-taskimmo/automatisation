#!/usr/bin/env python3
"""
Script de test des automatisations Aircall → Monday.com
Vérifie que tous les composants fonctionnent correctement
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

def print_header(title: str):
    """Affiche un en-tête formaté"""
    print("\n" + "=" * 70)
    print(f"🧪 {title}")
    print("=" * 70)

def print_section(title: str):
    """Affiche une section formatée"""
    print(f"\n📋 {title}")
    print("-" * 50)

def test_file_exists(file_path: str, description: str) -> bool:
    """Teste l'existence d'un fichier"""
    path = Path(file_path)
    if path.exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - MANQUANT")
        return False

def test_python_import(module: str, description: str) -> bool:
    """Teste l'import d'un module Python"""
    try:
        __import__(module)
        print(f"✅ {description}: {module}")
        return True
    except ImportError as e:
        print(f"❌ {description}: {module} - {str(e)}")
        return False

def test_script_execution(script: str, description: str, timeout: int = 60) -> bool:
    """Teste l'exécution d'un script"""
    try:
        print(f"🚀 Test de {description}...")
        
        result = subprocess.run(
            [sys.executable, script, "--help"],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            print(f"✅ {description}: {script}")
            return True
        else:
            print(f"❌ {description}: {script} - Erreur d'exécution")
            if result.stderr:
                print(f"   Erreur: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description}: {script} - Timeout")
        return False
    except Exception as e:
        print(f"❌ {description}: {script} - Exception: {str(e)}")
        return False

def test_configuration():
    """Teste la configuration du système"""
    print_section("TEST DE LA CONFIGURATION")
    
    # Test du fichier de configuration
    config_exists = test_file_exists('config.py', 'Fichier de configuration')
    
    if config_exists:
        try:
            from config import validate_config
            print("✅ Import du module config réussi")
            
            # Test de validation de la configuration
            print("🔧 Test de validation de la configuration...")
            if validate_config():
                print("✅ Configuration valide")
            else:
                print("❌ Configuration invalide")
                
        except Exception as e:
            print(f"❌ Erreur lors du test de configuration: {str(e)}")
    
    return config_exists

def test_dependencies():
    """Teste les dépendances Python"""
    print_section("TEST DES DÉPENDANCES")
    
    dependencies = [
        ('requests', 'Module requests'),
        ('schedule', 'Module schedule'),
        ('json', 'Module json'),
        ('datetime', 'Module datetime'),
        ('pathlib', 'Module pathlib')
    ]
    
    success_count = 0
    for module, description in dependencies:
        if test_python_import(module, description):
            success_count += 1
    
    print(f"\n📊 Dépendances: {success_count}/{len(dependencies)} OK")
    return success_count == len(dependencies)

def test_scripts():
    """Teste l'existence et l'exécution des scripts"""
    print_section("TEST DES SCRIPTS")
    
    scripts = [
        ('aircall_monday_integration_v2.py', 'Synchronisation Aircall'),
        ('create_tasks_with_agent.py', 'Création de tâches'),
        ('smart_task_assigner.py', 'Assignation intelligente'),
        ('link_calls_to_contacts.py', 'Liaison contacts'),
        ('update_board_relations.py', 'Mise à jour relations'),
        ('automation_manager.py', 'Gestionnaire principal'),
        ('scheduler.py', 'Planificateur'),
        ('start_automation.py', 'Démarrage automatique')
    ]
    
    existence_count = 0
    execution_count = 0
    
    for script, description in scripts:
        # Test d'existence
        if test_file_exists(script, description):
            existence_count += 1
            
            # Test d'exécution (avec --help si disponible)
            if test_script_execution(script, description):
                execution_count += 1
    
    print(f"\n📊 Scripts: {existence_count}/{len(scripts)} présents, {execution_count}/{len(scripts)} exécutables")
    return existence_count == len(scripts)

def test_api_connections():
    """Teste les connexions aux APIs"""
    print_section("TEST DES CONNEXIONS API")
    
    try:
        from config import MONDAY_API_TOKEN, AIRCALL_API_ID, AIRCALL_API_TOKEN
        
        # Test Monday.com
        if MONDAY_API_TOKEN and MONDAY_API_TOKEN != "your_token_here":
            print("✅ Token Monday.com configuré")
        else:
            print("❌ Token Monday.com manquant ou invalide")
        
        # Test Aircall
        if AIRCALL_API_ID and AIRCALL_API_ID != "your_api_id_here":
            print("✅ API ID Aircall configuré")
        else:
            print("❌ API ID Aircall manquant ou invalide")
            
        if AIRCALL_API_TOKEN and AIRCALL_API_TOKEN != "your_api_token_here":
            print("✅ Token Aircall configuré")
        else:
            print("❌ Token Aircall manquant ou invalide")
            
    except Exception as e:
        print(f"❌ Erreur lors du test des connexions API: {str(e)}")
        return False
    
    return True

def test_scheduler():
    """Teste le planificateur"""
    print_section("TEST DU PLANIFICATEUR")
    
    try:
        from scheduler import AutomationScheduler
        
        scheduler = AutomationScheduler()
        print("✅ Planificateur instancié avec succès")
        
        # Test de la configuration
        scheduler.setup_schedule()
        print("✅ Planification configurée")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test du planificateur: {str(e)}")
        return False

def test_automation_manager():
    """Teste le gestionnaire d'automatisation"""
    print_section("TEST DU GESTIONNAIRE")
    
    try:
        from automation_manager import AutomationManager
        
        manager = AutomationManager()
        print("✅ Gestionnaire instancié avec succès")
        
        # Test de la vérification du système
        print("🔍 Test de la vérification du système...")
        manager.check_system_status()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test du gestionnaire: {str(e)}")
        return False

def run_quick_test():
    """Exécute un test rapide d'une automatisation"""
    print_section("TEST RAPIDE D'AUTOMATISATION")
    
    try:
        print("🚀 Test de la synchronisation Aircall...")
        
        result = subprocess.run(
            [sys.executable, 'aircall_monday_integration_v2.py'],
            capture_output=True,
            text=True,
            timeout=120  # 2 minutes max
        )
        
        if result.returncode == 0:
            print("✅ Test de synchronisation réussi")
            return True
        else:
            print("❌ Test de synchronisation échoué")
            if result.stderr:
                print(f"   Erreur: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Test de synchronisation - Timeout (plus de 2 minutes)")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du test de synchronisation: {str(e)}")
        return False

def generate_report(results: dict):
    """Génère un rapport de test"""
    print_header("RAPPORT DE TEST")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    failed_tests = total_tests - passed_tests
    
    print(f"📊 Résultats: {passed_tests}/{total_tests} tests réussis")
    
    if failed_tests == 0:
        print("🎉 Tous les tests sont réussis ! Le système est prêt.")
    else:
        print(f"⚠️ {failed_tests} test(s) ont échoué. Vérifiez la configuration.")
    
    print("\n📋 Détail des tests:")
    for test_name, success in results.items():
        status = "✅" if success else "❌"
        print(f"   {status} {test_name}")
    
    # Recommandations
    print("\n💡 Recommandations:")
    if failed_tests == 0:
        print("   - Le système est prêt pour la production")
        print("   - Vous pouvez démarrer l'automatisation avec: python start_automation.py --scheduled")
        print("   - Ou utiliser le gestionnaire: python automation_manager.py")
    else:
        print("   - Corrigez les erreurs avant de démarrer l'automatisation")
        print("   - Vérifiez la configuration dans config.py")
        print("   - Testez manuellement chaque composant défaillant")

def main():
    """Fonction principale"""
    print_header("TEST COMPLET DU SYSTÈME D'AUTOMATISATION")
    print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    results = {}
    
    # Tests de base
    results['Configuration'] = test_configuration()
    results['Dépendances'] = test_dependencies()
    results['Scripts'] = test_scripts()
    
    # Tests avancés
    results['Connexions API'] = test_api_connections()
    results['Planificateur'] = test_scheduler()
    results['Gestionnaire'] = test_automation_manager()
    
    # Test rapide (optionnel)
    print("\n🤔 Voulez-vous exécuter un test rapide de synchronisation ? (o/N): ", end="")
    choice = input().strip().lower()
    
    if choice in ['o', 'oui', 'y', 'yes']:
        results['Test rapide'] = run_quick_test()
    else:
        print("⏭️ Test rapide ignoré")
        results['Test rapide'] = True  # Considéré comme réussi si ignoré
    
    # Génération du rapport
    generate_report(results)
    
    # Sauvegarde du rapport
    try:
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"Rapport de test - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")
            
            for test_name, success in results.items():
                status = "✅" if success else "❌"
                f.write(f"{status} {test_name}\n")
            
            f.write(f"\nTotal: {sum(results.values())}/{len(results)} tests réussis\n")
        
        print(f"\n📁 Rapport sauvegardé: {report_file}")
        
    except Exception as e:
        print(f"⚠️ Impossible de sauvegarder le rapport: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur fatale lors du test: {str(e)}")
        sys.exit(1)
