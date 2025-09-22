#!/usr/bin/env python3
"""
Gestionnaire principal des automatisations Aircall → Monday.com
Interface conviviale pour gérer et exécuter les automatisations
"""

import os
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path

class AutomationManager:
    """Gestionnaire principal des automatisations"""
    
    def __init__(self):
        self.scripts = {
            '1': {
                'name': 'Créer des tâches avec agent',
                'script': 'create_tasks_with_agent.py',
                'description': 'Crée des tâches depuis les Actions_IA des appels Aircall'
            },
            '2': {
                'name': 'Synchroniser les appels Aircall',
                'script': 'aircall_monday_integration_v2.py',
                'description': 'Synchronise les nouveaux appels Aircall vers Monday.com'
            },
            '3': {
                'name': 'Assigner les tâches intelligemment',
                'script': 'smart_task_assigner.py',
                'description': 'Assigne les tâches aux bons agents selon les règles'
            },
            '4': {
                'name': 'Lier les appels aux contacts',
                'script': 'link_calls_to_contacts.py',
                'description': 'Lie automatiquement les appels aux contacts existants'
            },
            '5': {
                'name': 'Mettre à jour les relations',
                'script': 'update_board_relations.py',
                'description': 'Met à jour les relations entre les différents tableaux'
            }
        }
        
        self.special_options = {
            'A': {
                'name': 'Exécuter toutes les automatisations principales',
                'description': 'Exécute les automatisations 1, 2, 3, 4, 5 dans l\'ordre'
            },
            'B': {
                'name': 'Exécuter la séquence complète recommandée',
                'description': 'Synchronisation → Liaison → Création tâches → Assignation → Relations'
            },
            'C': {
                'name': 'Vérifier l\'état du système',
                'description': 'Vérifie la présence des scripts et la configuration'
            },
            'D': {
                'name': 'Afficher les logs',
                'description': 'Affiche les derniers logs d\'automatisation'
            }
        }
    
    def clear_screen(self):
        """Nettoie l'écran"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Affiche l'en-tête du gestionnaire"""
        print("🤖 GESTIONNAIRE DES AUTOMATISATIONS AIRCALL → MONDAY.COM")
        print("=" * 70)
        print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 70)
        print()
    
    def print_menu(self):
        """Affiche le menu principal"""
        print("📋 AUTOMATISATIONS PRINCIPALES :")
        print("-" * 50)
        
        for key, info in self.scripts.items():
            print(f"{key}. {info['name']}")
            print(f"   {info['description']}")
            print()
        
        print("🎯 OPTIONS SPÉCIALES :")
        print("-" * 50)
        
        for key, info in self.special_options.items():
            print(f"{key}. {info['name']}")
            print(f"   {info['description']}")
            print()
        
        print("⏹️  Q. Quitter")
        print("-" * 50)
    
    def run_script(self, script_name: str, description: str = "") -> bool:
        """Exécute un script Python"""
        try:
            script_path = Path(script_name)
            if not script_path.exists():
                print(f"❌ Script non trouvé: {script_name}")
                return False
            
            print(f"🚀 Exécution de: {description or script_name}")
            print(f"⏰ Début: {datetime.now().strftime('%H:%M:%S')}")
            print("-" * 50)
            
            # Exécution du script
            result = subprocess.run([sys.executable, script_name], 
                                 capture_output=True, text=True, timeout=300)
            
            print("-" * 50)
            print(f"⏰ Fin: {datetime.now().strftime('%H:%M:%S')}")
            
            if result.returncode == 0:
                print(f"✅ {script_name} exécuté avec succès")
                if result.stdout:
                    # Afficher les dernières lignes de sortie
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 10:
                        print("📋 Dernières lignes de sortie:")
                        for line in lines[-10:]:
                            print(f"   {line}")
                    else:
                        print("📋 Sortie complète:")
                        for line in lines:
                            print(f"   {line}")
                return True
            else:
                print(f"❌ Erreur dans {script_name}")
                if result.stderr:
                    print("📋 Erreurs:")
                    for line in result.stderr.strip().split('\n')[-5:]:
                        print(f"   ❌ {line}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout pour {script_name} (plus de 5 minutes)")
            return False
        except Exception as e:
            print(f"❌ Erreur lors de l'exécution de {script_name}: {str(e)}")
            return False
    
    def execute_all_main(self):
        """Exécute toutes les automatisations principales"""
        print("🚀 EXÉCUTION DE TOUTES LES AUTOMATISATIONS PRINCIPALES")
        print("=" * 70)
        
        results = {}
        total_scripts = len(self.scripts)
        
        for i, (key, info) in enumerate(self.scripts.items(), 1):
            print(f"\n📋 [{i}/{total_scripts}] {info['name']}")
            print("-" * 50)
            
            success = self.run_script(info['script'], info['name'])
            results[key] = success
            
            if i < total_scripts:
                print("\n⏳ Pause de 5 secondes avant la prochaine automatisation...")
                time.sleep(5)
        
        # Résumé des résultats
        print("\n" + "=" * 70)
        print("📊 RÉSUMÉ DES EXÉCUTIONS")
        print("=" * 70)
        
        success_count = sum(results.values())
        for key, success in results.items():
            status = "✅" if success else "❌"
            script_name = self.scripts[key]['name']
            print(f"{status} {script_name}")
        
        print(f"\n🎯 Résultat global: {success_count}/{total_scripts} automatisations réussies")
        
        if success_count == total_scripts:
            print("🎉 Toutes les automatisations ont réussi !")
        else:
            print("⚠️ Certaines automatisations ont échoué. Vérifiez les logs.")
        
        return success_count == total_scripts
    
    def execute_recommended_sequence(self):
        """Exécute la séquence recommandée"""
        print("🎯 EXÉCUTION DE LA SÉQUENCE RECOMMANDÉE")
        print("=" * 70)
        
        sequence = [
            ('2', 'Synchronisation Aircall'),
            ('4', 'Liaison des appels aux contacts'),
            ('1', 'Création de tâches'),
            ('3', 'Assignation intelligente'),
            ('5', 'Mise à jour des relations')
        ]
        
        results = {}
        total_steps = len(sequence)
        
        for i, (key, description) in enumerate(sequence, 1):
            print(f"\n📋 [{i}/{total_steps}] {description}")
            print("-" * 50)
            
            script_info = self.scripts[key]
            success = self.run_script(script_info['script'], description)
            results[key] = success
            
            if i < total_steps:
                print("\n⏳ Pause de 10 secondes avant l'étape suivante...")
                time.sleep(10)
        
        # Résumé des résultats
        print("\n" + "=" * 70)
        print("📊 RÉSUMÉ DE LA SÉQUENCE RECOMMANDÉE")
        print("=" * 70)
        
        success_count = sum(results.values())
        for key, success in results.items():
            status = "✅" if success else "❌"
            script_name = self.scripts[key]['name']
            print(f"{status} {script_name}")
        
        print(f"\n🎯 Résultat de la séquence: {success_count}/{total_steps} étapes réussies")
        
        if success_count == total_steps:
            print("🎉 Séquence complète réussie !")
        else:
            print("⚠️ Certaines étapes ont échoué. Vérifiez les logs.")
        
        return success_count == total_steps
    
    def check_system_status(self):
        """Vérifie l'état du système"""
        print("🏥 VÉRIFICATION DE L'ÉTAT DU SYSTÈME")
        print("=" * 70)
        
        # Vérifier la présence des scripts
        print("📁 Vérification des scripts...")
        missing_scripts = []
        
        for key, info in self.scripts.items():
            script_path = Path(info['script'])
            if script_path.exists():
                print(f"✅ {info['script']} - Présent")
            else:
                print(f"❌ {info['script']} - MANQUANT")
                missing_scripts.append(info['script'])
        
        # Vérifier les fichiers de configuration
        print("\n⚙️ Vérification des fichiers de configuration...")
        config_files = ['requirements.txt', '.gitignore']
        
        for config_file in config_files:
            config_path = Path(config_file)
            if config_path.exists():
                print(f"✅ {config_file} - Présent")
            else:
                print(f"⚠️ {config_file} - Manquant")
        
        # Vérifier les logs
        print("\n📋 Vérification des logs...")
        log_file = Path('automation.log')
        if log_file.exists():
            size_mb = log_file.stat().st_size / (1024 * 1024)
            print(f"✅ automation.log - Présent ({size_mb:.1f} MB)")
        else:
            print("⚠️ automation.log - Aucun log trouvé")
        
        # Résumé
        print("\n" + "=" * 70)
        if missing_scripts:
            print(f"❌ {len(missing_scripts)} script(s) manquant(s):")
            for script in missing_scripts:
                print(f"   - {script}")
        else:
            print("✅ Tous les scripts sont présents")
        
        print("🏥 Vérification terminée")
    
    def show_logs(self):
        """Affiche les derniers logs"""
        print("📋 AFFICHAGE DES LOGS")
        print("=" * 70)
        
        log_file = Path('automation.log')
        if not log_file.exists():
            print("❌ Aucun fichier de log trouvé")
            return
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if not lines:
                print("📋 Le fichier de log est vide")
                return
            
            print(f"📁 Fichier: {log_file}")
            print(f"📊 Taille: {len(lines)} lignes")
            print(f"📅 Dernière modification: {datetime.fromtimestamp(log_file.stat().st_mtime).strftime('%d/%m/%Y %H:%M:%S')}")
            print("-" * 50)
            
            # Afficher les 20 dernières lignes
            print("📋 20 dernières lignes:")
            for line in lines[-20:]:
                line = line.strip()
                if line:
                    print(f"   {line}")
            
            print("-" * 50)
            print("💡 Pour voir tous les logs, ouvrez le fichier 'automation.log'")
            
        except Exception as e:
            print(f"❌ Erreur lors de la lecture des logs: {str(e)}")
    
    def run(self):
        """Exécute le gestionnaire principal"""
        while True:
            self.clear_screen()
            self.print_header()
            self.print_menu()
            
            choice = input("\n🎯 Votre choix: ").strip().upper()
            
            if choice == 'Q':
                print("\n👋 Au revoir !")
                break
            
            elif choice in self.scripts:
                script_info = self.scripts[choice]
                print(f"\n🚀 Exécution de: {script_info['name']}")
                input("Appuyez sur Entrée pour continuer...")
                
                success = self.run_script(script_info['script'], script_info['name'])
                
                if success:
                    print("\n✅ Automatisation terminée avec succès")
                else:
                    print("\n❌ Automatisation terminée avec des erreurs")
                
                input("\nAppuyez sur Entrée pour continuer...")
            
            elif choice == 'A':
                print("\n🚀 Exécution de toutes les automatisations principales")
                input("Appuyez sur Entrée pour continuer...")
                
                self.execute_all_main()
                input("\nAppuyez sur Entrée pour continuer...")
            
            elif choice == 'B':
                print("\n🎯 Exécution de la séquence recommandée")
                input("Appuyez sur Entrée pour continuer...")
                
                self.execute_recommended_sequence()
                input("\nAppuyez sur Entrée pour continuer...")
            
            elif choice == 'C':
                print("\n🏥 Vérification de l'état du système")
                input("Appuyez sur Entrée pour continuer...")
                
                self.check_system_status()
                input("\nAppuyez sur Entrée pour continuer...")
            
            elif choice == 'D':
                print("\n📋 Affichage des logs")
                input("Appuyez sur Entrée pour continuer...")
                
                self.show_logs()
                input("\nAppuyez sur Entrée pour continuer...")
            
            else:
                print(f"\n❌ Choix invalide: {choice}")
                input("Appuyez sur Entrée pour continuer...")

def main():
    """Fonction principale"""
    try:
        manager = AutomationManager()
        manager.run()
    except KeyboardInterrupt:
        print("\n\n⏹️ Arrêt du gestionnaire (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Erreur dans le gestionnaire: {str(e)}")
        input("Appuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    main()
