// /static/js/config.js
// Configuration globale de l'application

const CONFIG = {
    API_BASE_URL: '/api',
    PAGE_SIZE: 20,
    MAX_FILE_SIZE: 50 * 1024 * 1024, // 50MB
    SUPPORTED_FORMATS: ['csv', 'json'],
    
    // Messages
    MESSAGES: {
        SUCCESS: '✅ Success',
        ERROR: '❌ Error',
        LOADING: '⏳ Loading...',
        NO_RESULTS: 'No results found',
        INVALID_FILE: 'Invalid file format'
    },
    
    // API Endpoints
    ENDPOINTS: {
        HEALTH: '/health',
        SEARCH: '/search',
        SEARCH_ADVANCED: '/search/advanced',
        UPLOAD: '/upload',
        UPLOAD_HISTORY: '/upload/history',
        STATS: '/stats',
        STATS_TOP_IPS: '/stats/top-ips',
        STATS_SEVERITY: '/stats/severity'
    }
};

// Logged in user (if any)
let currentUser = null;

// Theme (light/dark)
let currentTheme = localStorage.getItem('theme') || 'dark';
