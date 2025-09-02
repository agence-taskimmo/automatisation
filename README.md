# 🚀 Interface Web d'Automatisation Aircall → Monday.com

Interface web moderne pour gérer et surveiller vos automatisations Aircall → Monday.com à distance, sans intervention manuelle.

## ✨ Fonctionnalités

- **🌐 Interface web responsive** accessible depuis n'importe quel appareil
- **📊 Tableau de bord en temps réel** avec statistiques et statut du système
- **⚡ Contrôle des automatisations** via interface graphique intuitive
- **📝 Surveillance des logs** et notifications en temps réel
- **🔄 Gestion du planificateur** (démarrage/arrêt automatique)
- **🔌 API REST complète** pour intégration externe
- **📱 Design mobile-first** optimisé pour tous les écrans

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Navigateur    │◄──►│  Interface Web   │◄──►│  Automatisations│
│                 │    │   (Flask)        │    │   (Python)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   WebSockets     │
                       │  (Temps réel)    │
                       └──────────────────┘
```

## 🚀 Déploiement Rapide

### Option 1 : Vercel (Recommandé)

1. **Forkez ce repository**
2. **Connectez-vous sur [vercel.com](https://vercel.com)**
3. **Importez votre fork**
4. **Déployez en un clic !** 🎉

### Option 2 : Local

```bash
# Cloner le repository
git clone https://github.com/agence-taskimmo/automatisation.git
cd automatisation

# Installer les dépendances
pip install -r requirements.txt

# Démarrer l'interface
python3 web_interface.py

# Accès : http://localhost:5000
```

### Option 3 : Serveur

```bash
# Utiliser le script de déploiement
python3 deploy_web_interface.py --systemd --user $USER

# Installer le service
sudo systemctl enable aircall-web-interface.service
sudo systemctl start aircall-web-interface.service
```

## 📁 Structure du Projet

```
automatisation/
├── web_interface.py              # Interface web principale
├── web_interface_vercel.py       # Version Vercel
├── vercel.json                   # Configuration Vercel
├── requirements.txt               # Dépendances complètes
├── requirements_vercel.txt        # Dépendances Vercel
├── deploy_web_interface.py       # Script de déploiement
├── templates/                     # Templates HTML
│   ├── base.html                 # Template de base
│   ├── index.html                # Page d'accueil
│   └── dashboard.html            # Tableau de bord
├── static/                        # Fichiers statiques
│   ├── css/style.css             # Styles CSS
│   └── js/app.js                 # JavaScript principal
├── config.py                      # Configuration
├── scheduler.py                   # Planificateur automatique
├── aircall_monday_integration_v2.py  # Intégration principale
└── docs/                          # Documentation
    ├── GUIDE_DEPLOIEMENT_WEB.md
    └── GUIDE_DEPLOIEMENT_VERCEL.md
```

## 🔧 Configuration

### Variables d'environnement

Créez un fichier `.env` :

```bash
# Configuration de l'interface web
HOST=0.0.0.0
PORT=5000
DEBUG=false

# Configuration de sécurité
SECRET_KEY=votre_cle_secrete_complexe

# API Keys (optionnel)
MONDAY_API_TOKEN=votre_token_monday
AIRCALL_API_TOKEN=votre_token_aircall
```

### Configuration avancée

Modifiez `config.py` pour personnaliser :
- **Ports et adresses** d'écoute
- **Intervalles** de planification
- **Règles** d'assignation des tâches
- **Paramètres** de logging

## 🌐 API REST

### Endpoints disponibles

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/status` | Statut du système |
| POST | `/api/run/{script}` | Exécuter un script |
| POST | `/api/run/full` | Synchronisation complète |
| POST | `/api/scheduler/start` | Démarrer le planificateur |
| POST | `/api/scheduler/stop` | Arrêter le planificateur |
| GET | `/api/logs` | Récupérer les logs |
| GET | `/api/config/validate` | Valider la configuration |
| GET | `/api/health` | Vérification de santé |

### Exemple d'utilisation

```bash
# Démarrer une synchronisation
curl -X POST http://localhost:5000/api/run/sync \
  -H "Content-Type: application/json" \
  -d '{"user": "API User"}'

# Vérifier le statut
curl http://localhost:5000/api/status | jq '.status'
```

## 🔒 Sécurité

### Production

1. **Changer la clé secrète** dans la configuration
2. **Restreindre l'accès** aux IPs autorisées
3. **Utiliser HTTPS** (automatique sur Vercel)
4. **Valider toutes les entrées** utilisateur

### Firewall

```bash
# Autoriser uniquement le port de l'interface
sudo ufw allow 5000/tcp

# Ou pour Nginx
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

## 📊 Monitoring

### Vérification de santé

```bash
# Test rapide
python3 health_check.py

# Test avec URL personnalisée
python3 health_check.py http://votre-domaine.com
```

### Logs

```bash
# Logs de l'interface web
tail -f logs/web_interface.log

# Logs systemd
sudo journalctl -u aircall-web-interface.service -f

# Logs Docker
docker-compose logs -f
```

## 🚨 Dépannage

### Problèmes courants

#### 1. Port déjà utilisé

```bash
# Vérifier les processus
lsof -i :5000

# Tuer le processus
kill -9 PID

# Ou utiliser un autre port
PORT=8080 python3 web_interface.py
```

#### 2. Dépendances manquantes

```bash
# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall

# Vérifier les versions
pip list | grep -E "(flask|schedule)"
```

#### 3. Interface inaccessible

```bash
# Vérifier le firewall
sudo ufw status

# Vérifier la configuration réseau
netstat -tlnp | grep :5000

# Tester localement
curl http://127.0.0.1:5000/api/status
```

## 🔄 Mise à jour

### Processus de mise à jour

```bash
# 1. Sauvegarder la configuration
python3 deploy_web_interface.py --backup

# 2. Arrêter le service
sudo systemctl stop aircall-web-interface.service

# 3. Mettre à jour les fichiers
git pull origin main

# 4. Redémarrer le service
sudo systemctl start aircall-web-interface.service
```

### Rollback

```bash
# Restaurer depuis la sauvegarde
cp backups/backup_TIMESTAMP/* .

# Redémarrer
sudo systemctl restart aircall-web-interface.service
```

## 🌍 Déploiement multi-environnements

### Développement

```bash
DEBUG=true PORT=5000 python3 web_interface.py
```

### Staging

```bash
HOST=0.0.0.0 PORT=5001 python3 web_interface.py
```

### Production

```bash
# Via systemd
sudo systemctl start aircall-web-interface.service

# Ou via Docker
docker-compose -f docker-compose.prod.yml up -d

# Ou via Vercel (automatique)
git push origin main
```

## 📱 Utilisation mobile

L'interface est entièrement responsive et accessible depuis :

- **Smartphones** (iOS/Android)
- **Tablettes**
- **Ordinateurs** (Windows/Mac/Linux)

### Fonctionnalités mobiles

- Navigation tactile optimisée
- Interface adaptative
- Notifications push (si supportées)
- Synchronisation en temps réel

## 🤝 Contribution

### Comment contribuer

1. **Forkez le repository**
2. **Créez une branche** pour votre fonctionnalité
3. **Commitez vos changements**
4. **Poussez vers la branche**
5. **Ouvrez une Pull Request**

### Standards de code

- **Python** : PEP 8
- **JavaScript** : ESLint
- **CSS** : Prettier
- **Tests** : pytest pour Python

## 📞 Support

### Ressources utiles

- **Documentation Flask** : [flask.palletsprojects.com](https://flask.palletsprojects.com/)
- **Documentation Socket.IO** : [python-socketio.readthedocs.io](https://python-socketio.readthedocs.io/)
- **Documentation Vercel** : [vercel.com/docs](https://vercel.com/docs)

### Commandes de diagnostic

```bash
# Vérification complète
python3 test_automation.py

# Test de l'interface web
python3 health_check.py

# Vérification des ports
netstat -tlnp | grep :5000

# Vérification des processus
ps aux | grep web_interface
```

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- **Flask** pour le framework web
- **Bootstrap** pour l'interface utilisateur
- **Socket.IO** pour les communications en temps réel
- **Vercel** pour l'hébergement cloud

---

## 🎯 Prochaines étapes

1. **Tester l'interface** localement
2. **Configurer la sécurité** pour la production
3. **Mettre en place le monitoring** (logs, métriques)
4. **Configurer les sauvegardes** automatiques
5. **Former les utilisateurs** à l'interface

---

**🎉 Félicitations !** Votre interface web d'automatisation est maintenant prête pour le déploiement sur Vercel et accessible depuis n'importe où dans le monde !

**URL de votre interface :** `https://votre-projet.vercel.app`

---

**🚀 Prêt à automatiser vos processus Aircall → Monday.com depuis le cloud !**
