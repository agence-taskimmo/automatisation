/**
 * Application JavaScript principale pour l'interface web d'automatisation
 * Gère les WebSockets, les notifications et les fonctionnalités communes
 */

// Configuration globale
const APP_CONFIG = {
    // URLs de l'API
    API_BASE: '',
    WEBSOCKET_URL: window.location.origin,
    
    // Intervalles de mise à jour (en millisecondes)
    STATUS_UPDATE_INTERVAL: 10000,    // 10 secondes
    LOGS_UPDATE_INTERVAL: 15000,      // 15 secondes
    
    // Timeouts
    REQUEST_TIMEOUT: 30000,           // 30 secondes
    
    // Configuration des notifications
    NOTIFICATION_DURATION: 5000,      // 5 secondes
    MAX_NOTIFICATIONS: 5
};

// État global de l'application
let appState = {
    connected: false,
    systemStatus: 'unknown',
    lastUpdate: null,
    notifications: [],
    websocket: null
};

// Initialisation de l'application
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initialisation de l\'interface web d\'automatisation');
    
    // Initialiser les composants
    initializeWebSocket();
    initializeNotifications();
    initializeGlobalEvents();
    
    // Mise à jour périodique
    startPeriodicUpdates();
    
    console.log('✅ Interface web initialisée');
});

/**
 * Initialise la connexion WebSocket
 */
function initializeWebSocket() {
    try {
        // Créer la connexion Socket.IO
        appState.websocket = io(APP_CONFIG.WEBSOCKET_URL);
        
        // Gestion des événements de connexion
        appState.websocket.on('connect', function() {
            console.log('🔌 WebSocket connecté');
            appState.connected = true;
            updateConnectionStatus(true);
        });
        
        appState.websocket.on('disconnect', function() {
            console.log('🔌 WebSocket déconnecté');
            appState.connected = false;
            updateConnectionStatus(false);
        });
        
        // Gestion des mises à jour de statut
        appState.websocket.on('status_update', function(data) {
            console.log('📊 Mise à jour du statut reçue:', data);
            appState.systemStatus = data.status;
            appState.lastUpdate = new Date();
            
            // Mettre à jour l'interface si nécessaire
            if (typeof updateSystemStatus === 'function') {
                updateSystemStatus(data);
            }
        });
        
        // Gestion des résultats de scripts
        appState.websocket.on('script_result', function(data) {
            console.log('📝 Résultat de script reçu:', data);
            showNotification(
                `${data.script} - ${data.success ? 'Succès' : 'Échec'}`,
                data.success ? 'success' : 'error'
            );
        });
        
        // Gestion des résultats de synchronisation complète
        appState.websocket.on('full_sync_result', function(data) {
            console.log('🔄 Résultat de synchronisation complète reçu:', data);
            showNotification(
                `Synchronisation complète - ${data.successful_scripts}/${data.total_scripts} réussies`,
                data.success ? 'success' : 'warning'
            );
        });
        
        // Gestion des erreurs WebSocket
        appState.websocket.on('error', function(error) {
            console.error('❌ Erreur WebSocket:', error);
            showNotification('Erreur de connexion WebSocket', 'error');
        });
        
    } catch (error) {
        console.error('❌ Erreur lors de l\'initialisation WebSocket:', error);
        showNotification('Impossible de se connecter au serveur', 'error');
    }
}

/**
 * Met à jour l'indicateur de statut de connexion
 */
function updateConnectionStatus(connected) {
    const statusIndicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    
    if (statusIndicator && statusText) {
        if (connected) {
            statusIndicator.className = 'fas fa-circle text-success me-1';
            statusText.textContent = 'Connecté';
        } else {
            statusIndicator.className = 'fas fa-circle text-danger me-1';
            statusText.textContent = 'Déconnecté';
        }
    }
}

/**
 * Initialise le système de notifications
 */
function initializeNotifications() {
    // Créer le conteneur de notifications s'il n'existe pas
    if (!document.getElementById('notification-container')) {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1055';
        document.body.appendChild(container);
    }
}

/**
 * Affiche une notification
 * @param {string} message - Message à afficher
 * @param {string} type - Type de notification (success, error, warning, info)
 * @param {number} duration - Durée d'affichage en millisecondes
 */
function showNotification(message, type = 'info', duration = APP_CONFIG.NOTIFICATION_DURATION) {
    // Limiter le nombre de notifications
    if (appState.notifications.length >= APP_CONFIG.MAX_NOTIFICATIONS) {
        const oldestNotification = appState.notifications.shift();
        if (oldestNotification && oldestNotification.element) {
            oldestNotification.element.remove();
        }
    }
    
    // Créer l'élément de notification
    const notification = document.createElement('div');
    notification.className = `toast align-items-center text-white bg-${type} border-0`;
    notification.setAttribute('role', 'alert');
    notification.setAttribute('aria-live', 'assertive');
    notification.setAttribute('aria-atomic', 'true');
    
    // Déterminer l'icône selon le type
    let icon = 'info-circle';
    switch (type) {
        case 'success':
            icon = 'check-circle';
            break;
        case 'error':
            icon = 'exclamation-triangle';
            break;
        case 'warning':
            icon = 'exclamation-circle';
            break;
    }
    
    notification.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-${icon} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    // Ajouter au conteneur
    const container = document.getElementById('notification-container');
    container.appendChild(notification);
    
    // Créer et afficher le toast Bootstrap
    const toast = new bootstrap.Toast(notification, {
        autohide: true,
        delay: duration
    });
    
    toast.show();
    
    // Stocker la référence
    const notificationRef = {
        element: notification,
        toast: toast,
        timestamp: Date.now()
    };
    
    appState.notifications.push(notificationRef);
    
    // Nettoyer après fermeture
    notification.addEventListener('hidden.bs.toast', () => {
        const index = appState.notifications.findIndex(n => n.element === notification);
        if (index > -1) {
            appState.notifications.splice(index, 1);
        }
        notification.remove();
    });
    
    // Retourner la référence pour manipulation externe
    return notificationRef;
}

/**
 * Initialise les événements globaux
 */
function initializeGlobalEvents() {
    // Gestion des erreurs globales
    window.addEventListener('error', function(event) {
        console.error('❌ Erreur JavaScript globale:', event.error);
        showNotification('Erreur JavaScript détectée', 'error');
    });
    
    // Gestion des promesses rejetées
    window.addEventListener('unhandledrejection', function(event) {
        console.error('❌ Promesse rejetée non gérée:', event.reason);
        showNotification('Erreur de promesse détectée', 'error');
    });
    
    // Gestion de la visibilité de la page
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            console.log('📱 Page masquée - Pause des mises à jour');
        } else {
            console.log('📱 Page visible - Reprise des mises à jour');
        }
    });
}

/**
 * Démarre les mises à jour périodiques
 */
function startPeriodicUpdates() {
    // Mise à jour du statut
    setInterval(() => {
        if (!document.hidden && appState.connected) {
            updateSystemStatus();
        }
    }, APP_CONFIG.STATUS_UPDATE_INTERVAL);
    
    // Mise à jour des logs
    setInterval(() => {
        if (!document.hidden && appState.connected) {
            updateLogs();
        }
    }, APP_CONFIG.LOGS_UPDATE_INTERVAL);
}

/**
 * Met à jour le statut du système
 */
function updateSystemStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            appState.systemStatus = data.status;
            appState.lastUpdate = new Date();
            
            // Mettre à jour l'interface si la fonction existe
            if (typeof updateSystemStatus === 'function') {
                updateSystemStatus(data);
            }
        })
        .catch(error => {
            console.error('❌ Erreur mise à jour statut:', error);
            if (appState.connected) {
                showNotification('Erreur lors de la mise à jour du statut', 'warning');
            }
        });
}

/**
 * Met à jour les logs
 */
function updateLogs() {
    fetch('/api/logs')
        .then(response => response.json())
        .then(data => {
            // Mettre à jour l'interface si la fonction existe
            if (typeof updateLogs === 'function') {
                updateLogs(data);
            }
        })
        .catch(error => {
            console.error('❌ Erreur mise à jour logs:', error);
        });
}

/**
 * Effectue une requête API avec gestion d'erreur
 * @param {string} url - URL de l'API
 * @param {Object} options - Options de la requête
 * @returns {Promise} - Promesse de la requête
 */
function apiRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
        timeout: APP_CONFIG.REQUEST_TIMEOUT
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    // Ajouter un timeout à la requête
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), finalOptions.timeout);
    
    return fetch(url, {
        ...finalOptions,
        signal: controller.signal
    })
    .then(response => {
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return response.json();
    })
    .catch(error => {
        clearTimeout(timeoutId);
        
        if (error.name === 'AbortError') {
            throw new Error('Requête expirée');
        }
        
        throw error;
    });
}

/**
 * Formate une date pour l'affichage
 * @param {string|Date} date - Date à formater
 * @param {string} format - Format de sortie (short, long, relative)
 * @returns {string} - Date formatée
 */
function formatDate(date, format = 'short') {
    const dateObj = new Date(date);
    const now = new Date();
    const diffMs = now - dateObj;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    switch (format) {
        case 'relative':
            if (diffMins < 1) return 'À l\'instant';
            if (diffMins < 60) return `Il y a ${diffMins} min`;
            if (diffHours < 24) return `Il y a ${diffHours}h`;
            if (diffDays < 7) return `Il y a ${diffDays}j`;
            return dateObj.toLocaleDateString('fr-FR');
            
        case 'long':
            return dateObj.toLocaleString('fr-FR', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
            
        case 'short':
        default:
            return dateObj.toLocaleString('fr-FR');
    }
}

/**
 * Formate un nombre avec des unités
 * @param {number} number - Nombre à formater
 * @param {string} unit - Unité (B, KB, MB, etc.)
 * @returns {string} - Nombre formaté
 */
function formatNumber(number, unit = '') {
    if (number >= 1000000) {
        return (number / 1000000).toFixed(1) + 'M' + unit;
    } else if (number >= 1000) {
        return (number / 1000).toFixed(1) + 'K' + unit;
    } else {
        return number.toString() + unit;
    }
}

/**
 * Vérifie si l'utilisateur est sur mobile
 * @returns {boolean} - True si sur mobile
 */
function isMobile() {
    return window.innerWidth <= 768;
}

/**
 * Affiche un modal de confirmation
 * @param {string} title - Titre du modal
 * @param {string} message - Message de confirmation
 * @param {string} confirmText - Texte du bouton de confirmation
 * @param {string} cancelText - Texte du bouton d'annulation
 * @returns {Promise<boolean>} - True si confirmé, False si annulé
 */
function showConfirmModal(title, message, confirmText = 'Confirmer', cancelText = 'Annuler') {
    return new Promise((resolve) => {
        // Créer le modal
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">${cancelText}</button>
                        <button type="button" class="btn btn-primary" id="confirm-btn">${confirmText}</button>
                    </div>
                </div>
            </div>
        `;
        
        // Ajouter au DOM
        document.body.appendChild(modal);
        
        // Créer l'instance Bootstrap
        const bsModal = new bootstrap.Modal(modal);
        
        // Gérer les événements
        modal.querySelector('#confirm-btn').addEventListener('click', () => {
            bsModal.hide();
            resolve(true);
        });
        
        modal.addEventListener('hidden.bs.modal', () => {
            resolve(false);
            modal.remove();
        });
        
        // Afficher le modal
        bsModal.show();
    });
}

/**
 * Affiche un indicateur de chargement
 * @param {string} message - Message à afficher
 * @returns {Object} - Objet avec les méthodes show() et hide()
 */
function showLoadingIndicator(message = 'Chargement...') {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div class="loading-content">
            <div class="spinner-border text-primary mb-3" role="status">
                <span class="visually-hidden">Chargement...</span>
            </div>
            <p class="text-muted">${message}</p>
        </div>
    `;
    
    // Styles CSS
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
    `;
    
    const content = overlay.querySelector('.loading-content');
    content.style.cssText = `
        background: white;
        padding: 2rem;
        border-radius: 0.5rem;
        text-align: center;
        box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
    `;
    
    return {
        show: () => {
            document.body.appendChild(overlay);
        },
        hide: () => {
            if (overlay.parentNode) {
                overlay.remove();
            }
        }
    };
}

// Export des fonctions pour utilisation globale
window.AppUtils = {
    showNotification,
    formatDate,
    formatNumber,
    isMobile,
    showConfirmModal,
    showLoadingIndicator,
    apiRequest
};

// Log de fin d'initialisation
console.log('🎯 Utilitaires de l\'application disponibles via window.AppUtils');
