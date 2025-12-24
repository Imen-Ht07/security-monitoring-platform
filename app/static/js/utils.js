// frontend/js/utils.js
/**
 * Utilitaires et helpers réutilisables
 */

class Utils {
    /**
     * Formate la taille d'un fichier
     */
    static formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    /**
     * Formate une date
     */
    static formatDate(dateString, format = 'fr-FR') {
        const date = new Date(dateString);
        return date.toLocaleString(format);
    }

    /**
     * Formate la durée
     */
    static formatDuration(ms) {
        const seconds = Math.floor(ms / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);

        if (hours > 0) return `${hours}h ${minutes % 60}m`;
        if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
        return `${seconds}s`;
    }

    /**
     * Valide une email
     */
    static isValidEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }

    /**
     * Valide une IP
     */
    static isValidIP(ip) {
        const regex = /^(\d{1,3}\.){3}\d{1,3}$/;
        return regex.test(ip);
    }

    /**
     * Copie du texte dans le clipboard
     */
    static copyToClipboard(text) {
        return navigator.clipboard.writeText(text);
    }

    /**
     * Débounce une fonction
     */
    static debounce(func, delay = CONFIG.UI.DEBOUNCE_DELAY) {
        let timeoutId;
        return (...args) => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func(...args), delay);
        };
    }

    /**
     * Throttle une fonction
     */
    static throttle(func, interval) {
        let lastTime = 0;
        return (...args) => {
            const now = Date.now();
            if (now - lastTime >= interval) {
                lastTime = now;
                func(...args);
            }
        };
    }

    /**
     * Retarde l'exécution
     */
    static delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Convertit un objet en query string
     */
    static toQueryString(obj) {
        return Object.keys(obj)
            .filter(key => obj[key] !== null && obj[key] !== undefined && obj[key] !== '')
            .map(key => {
                if (Array.isArray(obj[key])) {
                    return obj[key].map(v => `${key}=${encodeURIComponent(v)}`).join('&');
                }
                return `${key}=${encodeURIComponent(obj[key])}`;
            })
            .join('&');
    }

    /**
     * Parse query string en objet
     */
    static parseQueryString(qs) {
        const params = new URLSearchParams(qs);
        const obj = {};
        params.forEach((value, key) => {
            if (obj[key]) {
                if (!Array.isArray(obj[key])) {
                    obj[key] = [obj[key]];
                }
                obj[key].push(value);
            } else {
                obj[key] = value;
            }
        });
        return obj;
    }

    /**
     * Profondeur copie d'un objet
     */
    static deepClone(obj) {
        return JSON.parse(JSON.stringify(obj));
    }

    /**
     * Fusionne deux objets
     */
    static mergeObjects(target, source) {
        return { ...target, ...source };
    }

    /**
     * Filtre un array d'objets
     */
    static filterBy(array, predicate) {
        return array.filter(predicate);
    }

    /**
     * Trie un array d'objets
     */
    static sortBy(array, key, order = 'asc') {
        const sorted = [...array];
        sorted.sort((a, b) => {
            if (a[key] < b[key]) return order === 'asc' ? -1 : 1;
            if (a[key] > b[key]) return order === 'asc' ? 1 : -1;
            return 0;
        });
        return sorted;
    }

    /**
     * Groupe un array par clé
     */
    static groupBy(array, key) {
        return array.reduce((acc, obj) => {
            const group = obj[key];
            if (!acc[group]) acc[group] = [];
            acc[group].push(obj);
            return acc;
        }, {});
    }

    /**
     * Extrait les propriétés d'un objet
     */
    static pick(obj, keys) {
        const picked = {};
        keys.forEach(key => {
            if (key in obj) picked[key] = obj[key];
        });
        return picked;
    }

    /**
     * Crée un ID unique
     */
    static generateId(prefix = '') {
        return prefix + Date.now() + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Valide si un objet est vide
     */
    static isEmpty(obj) {
        return Object.keys(obj).length === 0;
    }

    /**
     * Obtient les dates par défaut
     */
    static getDefaultDateRange(days = CONFIG.SEARCH.DEFAULT_DATE_RANGE) {
        const today = new Date();
        const pastDate = new Date(today.getTime() - days * 24 * 60 * 60 * 1000);
        
        return {
            from: pastDate.toISOString().split('T')[0],
            to: today.toISOString().split('T')[0]
        };
    }

    /**
     * Valide une date
     */
    static isValidDate(dateString) {
        const date = new Date(dateString);
        return date instanceof Date && !isNaN(date);
    }

    /**
     * Retourne la date du jour au format ISO
     */
    static today() {
        return new Date().toISOString().split('T')[0];
    }

    /**
     * Retourne la date d'hier
     */
    static yesterday() {
        const date = new Date();
        date.setDate(date.getDate() - 1);
        return date.toISOString().split('T')[0];
    }

    /**
     * Cache les données dans localStorage
     */
    static setCache(key, value, expiry = null) {
        const data = {
            value,
            expiry: expiry ? Date.now() + expiry * 1000 : null
        };
        try {
            localStorage.setItem(key, JSON.stringify(data));
        } catch (e) {
            appLogger.warn('Cache storage full');
        }
    }

    /**
     * Récupère les données du cache
     */
    static getCache(key) {
        try {
            const data = JSON.parse(localStorage.getItem(key));
            if (!data) return null;

            if (data.expiry && Date.now() > data.expiry) {
                localStorage.removeItem(key);
                return null;
            }

            return data.value;
        } catch {
            return null;
        }
    }

    /**
     * Efface le cache
     */
    static clearCache(key) {
        try {
            localStorage.removeItem(key);
        } catch {
            // Ignore
        }
    }

    /**
     * Extrait les erreurs d'une réponse API
     */
    static getErrorMessage(error) {
        if (error instanceof APIError) {
            return error.data?.error || error.message;
        }
        return error?.message || 'Une erreur est survenue';
    }
}

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Utils;
}
