# 🚀 Centre d'Automatisation Taskimmo

**Automatisez vos processus, optimisez votre productivité**

## 📋 Description

Centre d'automatisation complet pour l'agence Taskimmo, intégrant Aircall et Monday.com avec une interface web moderne et des automatisations intelligentes.

## 🏗️ Architecture

### **Scripts d'Automatisation**
- **`aircall_monday_integration_v2.py`** - Synchronisation Aircall → Monday.com
- **`create_tasks_with_agent.py`** - Création de tâches depuis les actions IA
- **`smart_task_assigner.py`** - Assignation intelligente des tâches
- **`link_calls_to_contacts.py`** - Liaison des appels aux contacts
- **`update_board_relations.py`** - Mise à jour des relations entre tableaux

### **Gestion et Configuration**
- **`config.py`** - Configuration centralisée (APIs, colonnes, agents)
- **`scheduler.py`** - Planificateur automatique des tâches
- **`start_automation.py`** - Démarrage des automatisations
- **`automation_manager.py`** - Gestionnaire d'automatisations
- **`test_automation.py`** - Tests du système

### **Déploiement**
- **`requirements.txt`** - Dépendances Python

## 🚀 Déploiement Rapide

### **Serveur Local**
```bash
# Installation des dépendances
pip install -r requirements.txt

# Démarrage des automatisations
python start_automation.py --start

# Ou utiliser le gestionnaire
python automation_manager.py
```

## ⚙️ Configuration

### **APIs**
- **Monday.com** : Token API configuré dans `config.py`
- **Aircall** : ID et Token API configurés dans `config.py`

### **Automatisations**
- **Synchronisation Aircall** : Toutes les heures
- **Création de tâches** : Toutes les 2 heures
- **Assignation intelligente** : Toutes les 4 heures
- **Liaison contacts** : Toutes les 6 heures
- **Relations** : Une fois par jour

## 🎯 Fonctionnalités

### **Automatisations**
- ✅ **Synchronisation Aircall** avec détection de doublons
- ✅ **Création de tâches** depuis les actions IA
- ✅ **Assignation intelligente** selon les compétences
- ✅ **Liaison automatique** des contacts
- ✅ **Gestion des relations** entre tableaux

### **Sécurité et Robustesse**
- ✅ **Vérification des doublons** robuste
- ✅ **Gestion d'erreurs** complète
- ✅ **Logs détaillés** avec structuration
- ✅ **Timeout et retry** automatiques

## 📱 Utilisation

### **1. Gestionnaire d'automatisations**
- Utilisez `python automation_manager.py` pour l'interface interactive
- Exécution manuelle des automatisations
- Vérification de l'état du système

### **2. Planificateur automatique**
- Utilisez `python start_automation.py --scheduled` pour l'automatisation continue
- Planification configurable des tâches
- Logs automatiques

### **3. Tests et maintenance**
- Utilisez `python test_automation.py` pour vérifier le système
- Logs détaillés de toutes les actions
- Surveillance des performances

## 🔧 Maintenance

### **Logs**
- **Rotation automatique** des fichiers de log
- **Nettoyage** des anciens logs
- **Sauvegarde** des logs importants

### **Tests**
- **`test_automation.py`** pour vérifier le système
- **Tests automatiques** des connexions API
- **Validation** de la configuration

## 📚 Documentation

- **`README.md`** - Documentation principale

## 🆘 Support

### **Problèmes courants**
1. **Connexion API** : Vérifiez les tokens dans `config.py`
2. **Doublons** : Le système détecte automatiquement les appels existants
3. **Logs** : Consultez l'interface web pour les détails

### **Contact**
- **Agence Taskimmo** - Support technique
- **Documentation** : Consultez les guides inclus

## 📈 Évolutions Futures

- **Notifications** par email/Slack
- **Tableau de bord** avancé
- **Intégrations** supplémentaires
- **IA avancée** pour l'assignation

---

**Développé pour Taskimmo - Automatisez l'avenir ! 🏠✨**
