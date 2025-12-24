// frontend/js/config.js
/**
 * Configuration centralisée du frontend
 * Source unique de vérité pour toutes les config
 */

const CONFIG = {
    // API Configuration
    API: {
        BASE_URL: window.location.origin + '/api',
        TIMEOUT: 30000, // 30 secondes
        RETRY_ATTEMPTS: 3,
        RETRY_DELAY: 1000 // ms
    },

    // Upload Configuration
    UPLOAD: {
        MAX_SIZE: 50 * 1024 * 1024, // 50MB
        ALLOWED_TYPES: ['csv', 'json'],
        CHUNK_SIZE: 10000,
        TIMEOUT: 60000 // 60 secondes
    },

    // Search Configuration
    SEARCH: {
        PAGE_SIZE: 50,
        MAX_PAGE_SIZE: 100,
        DEFAULT_DATE_RANGE: 7 // jours
    },

    // UI Configuration
    UI: {
        THEME: 'dark',
        TOAST_DURATION: 3000, // ms
        DEBOUNCE_DELAY: 300 // ms
    },

    // Chart Configuration
    CHARTS: {
        ANIMATION_DURATION: 300,
        COLORS: {
            primary: '#3b82f6',
            success: '#10b981',
            danger: '#ef4444',
            warning: '#f59e0b',
            info: '#0ea5e9'
        },
        THEME: {
            textColor: '#e2e8f0',
            gridColor: '#475569',
            bgColor: '#1e293b'
        }
    },

    // Logging Configuration
    LOG: {
        LEVEL: 'info', // 'debug', 'info', 'warn', 'error'
        STORAGE: true // Stocker les logs localement
    }
};

// Export pour modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}
