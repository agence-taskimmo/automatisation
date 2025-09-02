# 🚀 GUIDE DE DÉPLOIEMENT - INTERFACE WEB AUTOMATISATION

## 📋 Vue d'ensemble

Cette interface web vous permet de gérer et surveiller vos automatisations Aircall → Monday.com à distance, sans intervention manuelle. Elle offre :

- **Tableau de bord en temps réel** avec statistiques et statut du système
- **Contrôle des automatisations** via interface graphique
- **Surveillance des logs** et notifications en temps réel
- **Gestion du planificateur** (démarrage/arrêt)
- **Interface responsive** accessible depuis n'importe quel appareil

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

## 🚀 Démarrage rapide

### 1. Installation automatique

```bash
# Exécuter le script de déploiement
python3 deploy_web_interface.py --backup

# Démarrer l'interface
python3 web_interface.py
```

### 2. Accès à l'interface

- **URL locale** : http://localhost:5000
- **URL réseau** : http://VOTRE_IP:5000

## 🔧 Déploiement détaillé

### Prérequis

- Python 3.8+
- Accès Internet pour les dépendances
- Port disponible (5000 par défaut)

### Installation des dépendances

```bash
pip install -r requirements.txt
```

### Structure des fichiers

```
Recupération/
├── web_interface.py          # Serveur Flask principal
├── templates/                # Templates HTML
│   ├── base.html            # Template de base
│   ├── index.html           # Page d'accueil
│   └── dashboard.html       # Tableau de bord
├── static/                   # Fichiers statiques
│   ├── css/style.css        # Styles CSS
│   └── js/app.js            # JavaScript principal
├── config.py                 # Configuration
├── scheduler.py              # Planificateur
└── logs/                     # Fichiers de logs
```

## 🌐 Déploiement sur serveur

### Option 1 : Déploiement direct

```bash
# 1. Copier les fichiers sur le serveur
scp -r . user@server:/path/to/automation/

# 2. Se connecter au serveur
ssh user@server

# 3. Installer les dépendances
cd /path/to/automation
pip3 install -r requirements.txt

# 4. Démarrer l'interface
python3 web_interface.py
```

### Option 2 : Service systemd

```bash
# Créer le service
python3 deploy_web_interface.py --systemd --user $USER

# Installer le service
sudo cp aircall-web-interface.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable aircall-web-interface.service
sudo systemctl start aircall-web-interface.service

# Vérifier le statut
sudo systemctl status aircall-web-interface.service
```

### Option 3 : Docker

```bash
# Créer les fichiers Docker
python3 deploy_web_interface.py --docker

# Construire et démarrer
docker-compose up -d

# Vérifier les logs
docker-compose logs -f
```

### Option 4 : Nginx + Proxy

```bash
# Créer la configuration Nginx
python3 deploy_web_interface.py --nginx --domain votre-domaine.com

# Copier la configuration
sudo cp nginx_votre-domaine.com.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/votre-domaine.com /etc/nginx/sites-enabled/

# Redémarrer Nginx
sudo systemctl restart nginx
```

## ⚙️ Configuration

### Variables d'environnement

Créez un fichier `.env` :

```bash
# Configuration de l'interface web
HOST=0.0.0.0
PORT=5000
DEBUG=false

# Configuration de sécurité
SECRET_KEY=votre_cle_secrete_ici

# Configuration de la base de données (optionnel)
# DATABASE_URL=sqlite:///automation.db
```

### Configuration avancée

Modifiez `config.py` pour personnaliser :

- **Ports et adresses** d'écoute
- **Intervalles** de planification
- **Règles** d'assignation des tâches
- **Paramètres** de logging

## 🔒 Sécurité

### Production

1. **Changer la clé secrète** :
   ```python
   app.config['SECRET_KEY'] = 'nouvelle_cle_secrete_complexe'
   ```

2. **Restreindre l'accès** :
   ```python
   # Dans web_interface.py
   app.config['HOST'] = '127.0.0.1'  # Local uniquement
   ```

3. **Authentification** (optionnel) :
   ```python
   from flask_login import LoginManager, login_required
   
   @app.route('/dashboard')
   @login_required
   def dashboard():
       # ...
   ```

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

### Métriques

L'interface expose des métriques via l'API :

```bash
# Statut du système
curl http://localhost:5000/api/status

# Logs récents
curl http://localhost:5000/api/logs
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

#### 3. Erreurs de permissions

```bash
# Vérifier les permissions
ls -la logs/
chmod 755 logs/
chown $USER:$USER logs/
```

#### 4. Interface inaccessible

```bash
# Vérifier le firewall
sudo ufw status

# Vérifier la configuration réseau
netstat -tlnp | grep :5000

# Tester localement
curl http://127.0.0.1:5000/api/status
```

### Logs d'erreur

```bash
# Logs détaillés
python3 web_interface.py 2>&1 | tee debug.log

# Mode debug
DEBUG=true python3 web_interface.py
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

## 🔌 API REST

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

### Exemple d'utilisation

```bash
# Démarrer une synchronisation
curl -X POST http://localhost:5000/api/run/sync \
  -H "Content-Type: application/json" \
  -d '{"user": "API User"}'

# Vérifier le statut
curl http://localhost:5000/api/status | jq '.status'
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
```

## 📞 Support

### Ressources utiles

- **Documentation Flask** : https://flask.palletsprojects.com/
- **Documentation Socket.IO** : https://python-socketio.readthedocs.io/
- **Logs système** : `journalctl -u aircall-web-interface.service`

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

---

## 🎯 Prochaines étapes

1. **Tester l'interface** localement
2. **Configurer la sécurité** pour la production
3. **Mettre en place le monitoring** (logs, métriques)
4. **Configurer les sauvegardes** automatiques
5. **Former les utilisateurs** à l'interface

---

**🎉 Félicitations !** Votre interface web d'automatisation est maintenant opérationnelle et vous pouvez gérer vos automatisations Aircall → Monday.com à distance, sans intervention manuelle.
