#!/usr/bin/env python3
"""
Script de démarrage rapide pour les automatisations Aircall → Monday.com
"""

import sys
import subprocess
import os

def show_quick_menu():
    """Affiche le menu de démarrage rapide"""
    print("🚀 DÉMARRAGE RAPIDE - AUTOMATISATIONS AIRCALL → MONDAY.COM")
    print("=" * 70)
    print()
    
    print("🎯 ACTIONS RAPIDES:")
    print("1. 🎮 Interface complète (recommandé)")
    print("2. ⏰ Planificateur automatique")
    print("3. 📝 Créer des tâches maintenant")
    print("4. 🔄 Synchronisation complète")
    print("5. 🔍 Vérifier le système")
    print("6. 📋 Afficher l'aide")
    print("7. ❌ Quitter")
    print()

def run_command(command, description):
    """Exécute une commande avec description"""
    print(f"🚀 {description}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, check=True)
        print("✅ Commande exécutée avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        return False
    except KeyboardInterrupt:
        print("⏹️ Commande interrompue par l'utilisateur")
        return False

def main():
    """Fonction principale"""
    while True:
        show_quick_menu()
        
        choice = input("🎯 Votre choix: ").strip()
        
        if choice == "1":
            # Interface complète
            print("\n🎮 Lancement de l'interface complète...")
            run_command("python automation_manager.py", "Interface complète")
            
        elif choice == "2":
            # Planificateur automatique
            print("\n⏰ Lancement du planificateur...")
            print("Le planificateur va s'exécuter en continu.")
            print("Appuyez sur Ctrl+C pour l'arrêter.")
            run_command("python scheduler.py --start", "Planificateur automatique")
            
        elif choice == "3":
            # Créer des tâches
            print("\n📝 Création de tâches...")
            run_command("python create_tasks_with_agent.py", "Création de tâches")
            
        elif choice == "4":
            # Synchronisation complète
            print("\n🔄 Synchronisation complète...")
            run_command("python scheduler.py --once full", "Synchronisation complète")
            
        elif choice == "5":
            # Vérifier le système
            print("\n🔍 Vérification du système...")
            run_command("python automation_manager.py", "Vérification système")
            
        elif choice == "6":
            # Afficher l'aide
            show_help()
            
        elif choice == "7":
            # Quitter
            print("👋 Au revoir !")
            break
            
        else:
            print("❌ Choix invalide")
        
        if choice in ["1", "2", "3", "4", "5"]:
            input("\n⏸️ Appuyez sur Entrée pour continuer...")
            os.system('clear' if os.name == 'posix' else 'cls')

def show_help():
    """Affiche l'aide"""
    print("\n📋 AIDE - AUTOMATISATIONS AIRCALL → MONDAY.COM")
    print("=" * 60)
    print()
    
    print("🎯 QU'EST-CE QUE CE SYSTÈME ?")
    print("Ce système automatise la synchronisation entre Aircall et Monday.com")
    print("et crée automatiquement des tâches à partir des appels téléphoniques.")
    print()
    
    print("🚀 COMMENT UTILISER :")
    print("1. Choisissez 'Interface complète' pour un contrôle total")
    print("2. Choisissez 'Planificateur automatique' pour l'automatisation")
    print("3. Choisissez 'Créer des tâches' pour une exécution manuelle")
    print()
    
    print("📞 FONCTIONNALITÉS :")
    print("✅ Synchronisation des appels Aircall")
    print("✅ Création automatique de tâches")
    print("✅ Assignation intelligente des agents")
    print("✅ Liaison automatique des contacts")
    print("✅ Gestion des relations entre tableaux")
    print()
    
    print("⚙️ CONFIGURATION :")
    print("Tous les paramètres sont dans le fichier 'config.py'")
    print("Vous pouvez modifier les tokens API et les IDs des tableaux.")
    print()
    
    print("🛠️ DÉPANNAGE :")
    print("En cas de problème, utilisez 'Vérifier le système'")
    print("ou consultez les logs dans 'automation.log'")
    print()
    
    input("⏸️ Appuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    main()

