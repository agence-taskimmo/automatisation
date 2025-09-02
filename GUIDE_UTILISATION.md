# 🚀 GUIDE D'UTILISATION RAPIDE - AUTOMATISATION AIRCALL

## **🎯 DÉMARRAGE RAPIDE**

### **1. Test du système**
```bash
# Vérifier que tout fonctionne
python3 test_automation.py
```

### **2. Interface principale (recommandé)**
```bash
# Lancer le gestionnaire avec interface
python3 automation_manager.py
```

### **3. Planificateur automatique**
```bash
# Démarrer en continu avec planification
python3 start_automation.py --scheduled

# Ou utiliser le planificateur directement
python3 scheduler.py --start
```

## **📋 MODES D'UTILISATION**

### **Mode Manuel (Gestionnaire)**
- **Interface conviviale** avec menus numérotés
- **Exécution à la demande** des automatisations
- **Vérification de l'état** du système
- **Affichage des logs** en temps réel

### **Mode Planifié (Automatique)**
- **Synchronisation Aircall** : Toutes les heures
- **Création de tâches** : Toutes les 2 heures
- **Assignation intelligente** : Toutes les 4 heures
- **Liaison contacts** : Toutes les 6 heures
- **Mise à jour relations** : Une fois par jour

### **Mode Service (Production)**
- **Démarrage automatique** au boot du système
- **Gestion des erreurs** et redémarrage automatique
- **Logs détaillés** avec rotation automatique

## **⚙️ CONFIGURATION**

### **Fichier config.py**
Tous les paramètres sont centralisés :
- **Tokens API** (Monday.com, Aircall)
- **IDs des tableaux** Monday.com
- **Mapping des agents** et colonnes
- **Horaires** de planification
- **Règles d'assignation** intelligente

### **Variables d'environnement**
```bash
# Créer un fichier .env si nécessaire
MONDAY_API_TOKEN=your_token_here
AIRCALL_API_ID=your_api_id_here
AIRCALL_API_TOKEN=your_api_token_here
```

## **🔧 COMMANDES PRINCIPALES**

### **Gestionnaire principal**
```bash
python3 automation_manager.py
# Puis choisir dans le menu :
# 1-5 : Automatisations individuelles
# A : Toutes les automatisations
# B : Séquence recommandée
# C : Vérification système
# D : Affichage logs
```

### **Planificateur**
```bash
# Démarrer en continu
python3 scheduler.py --start

# Exécution unique
python3 scheduler.py --once full      # Synchronisation complète
python3 scheduler.py --once sync      # Synchronisation Aircall
python3 scheduler.py --once tasks     # Création de tâches
python3 scheduler.py --once assign    # Assignation intelligente
python3 scheduler.py --once link      # Liaison contacts
python3 scheduler.py --once relations # Mise à jour relations
```

### **Démarrage automatique**
```bash
# Mode planifié (recommandé)
python3 start_automation.py --scheduled

# Mode service
python3 start_automation.py --service

# Mode daemon (détaché)
python3 start_automation.py --daemon

# Exécution unique
python3 start_automation.py --once full
```

## **📊 MONITORING ET LOGS**

### **Fichiers de log**
- **`automation.log`** : Log principal
- **`logs/automation_YYYYMMDD.log`** : Logs quotidiens
- **`logs/cron_*.log`** : Logs des tâches cron

### **Vérification de l'état**
```bash
# Vérification complète
python3 test_automation.py

# Vérification rapide
python3 automation_manager.py
# Puis choisir "C"
```

### **Surveillance en temps réel**
```bash
# Suivre les logs
tail -f automation.log

# Suivre les logs cron
tail -f logs/cron_*.log
```

## **🚀 AUTOMATISATION COMPLÈTE**

### **Avec Cron (Linux/macOS)**
```bash
# Éditer le crontab
crontab -e

# Copier les lignes de cron_setup.txt
# Ajuster les chemins selon votre système
```

### **Avec Systemd (Linux)**
```bash
# Copier le service
sudo cp aircall-automation.service /etc/systemd/system/

# Activer et démarrer
sudo systemctl enable aircall-automation
sudo systemctl start aircall-automation

# Vérifier le statut
sudo systemctl status aircall-automation
```

### **Avec Task Scheduler (Windows)**
1. Ouvrir **Planificateur de tâches**
2. Créer une **tâche de base**
3. Programmer l'exécution de `start_automation.py --scheduled`
4. Configurer le **démarrage automatique**

## **🔄 WORKFLOW RECOMMANDÉ**

### **Séquence quotidienne**
1. **8h00** : Synchronisation complète
2. **9h-18h** : Synchronisation Aircall (toutes les heures)
3. **10h et 16h** : Liaison des contacts
4. **12h00** : Mise à jour des relations
5. **18h00** : Rapport quotidien
6. **2h00** : Maintenance nocturne

### **Exécution manuelle**
```bash
# Séquence complète recommandée
python3 automation_manager.py
# Puis choisir "B"
```

## **🐛 DÉPANNAGE**

### **Problèmes courants**

**"Module non trouvé"**
```bash
pip3 install -r requirements.txt
```

**"Token invalide"**
- Vérifier `config.py`
- Régénérer les tokens API

**"Script non trouvé"**
```bash
# Vérifier la structure
python3 test_automation.py
```

**"Timeout"**
- Augmenter `timeout` dans `config.py`
- Vérifier la connexion internet

### **Logs d'erreur**
```bash
# Voir les erreurs récentes
grep "ERROR" automation.log

# Voir les erreurs d'une date
grep "ERROR" logs/automation_20250902.log
```

## **📈 OPTIMISATION**

### **Performance**
- **Délais entre appels** : Ajuster dans `config.py`
- **Taille des lots** : Optimiser selon l'API
- **Fréquence des tâches** : Adapter aux besoins

### **Maintenance**
- **Rotation des logs** : Automatique
- **Nettoyage** : Tous les dimanches
- **Vérification santé** : Tous les lundis

## **🔒 SÉCURITÉ**

### **Bonnes pratiques**
- **Ne jamais commiter** les tokens API
- **Utiliser des variables d'environnement** en production
- **Restreindre les permissions** des services
- **Surveiller les logs** régulièrement

### **Audit**
```bash
# Vérifier la configuration
python3 config.py

# Tester les connexions
python3 test_automation.py
```

## **📞 SUPPORT**

### **En cas de problème**
1. **Vérifier les logs** : `tail -f automation.log`
2. **Tester le système** : `python3 test_automation.py`
3. **Vérifier la configuration** : `python3 config.py`
4. **Consulter ce guide** et le README.md

### **Informations utiles**
- **Version Python** : 3.8+
- **Dépendances** : Voir `requirements.txt`
- **Configuration** : Voir `config.py`
- **Logs** : Dossier `logs/`

---

**🎯 Objectif** : Automatiser complètement le processus de création de tâches depuis les appels Aircall, avec une gestion intelligente des agents et des clients.

**💡 Conseil** : Commencez par tester avec `python3 test_automation.py`, puis utilisez `python3 automation_manager.py` pour une utilisation manuelle, et enfin `python3 start_automation.py --scheduled` pour l'automatisation complète.
