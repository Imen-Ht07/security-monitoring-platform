// /static/js/api.js
// Fonctions API réutilisables

class APIClient {
    constructor(baseUrl = CONFIG.API_BASE_URL) {
        this.baseUrl = baseUrl;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // GET request
    get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    // POST request
    post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // PUT request
    put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    // DELETE request
    delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    // Upload file
    async uploadFile(endpoint, file, description = '') {
        const formData = new FormData();
        formData.append('file', file);
        if (description) {
            formData.append('description', description);
        }

        const url = `${this.baseUrl}${endpoint}`;
        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Upload Error: ${response.status}`);
        }

        return await response.json();
    }
}

// Instance globale
const api = new APIClient();

// Fonctions de recherche
async function searchLogs(query) {
    return api.get(`${CONFIG.ENDPOINTS.SEARCH}?q=${encodeURIComponent(query)}`);
}

async function advancedSearch(filters) {
    return api.post(CONFIG.ENDPOINTS.SEARCH_ADVANCED, filters);
}

// Fonctions de stats
async function getStats() {
    return api.get(CONFIG.ENDPOINTS.STATS);
}

async function getTopIPs() {
    return api.post(CONFIG.ENDPOINTS.STATS_TOP_IPS, {});
}

async function getSeverityStats() {
    return api.get(CONFIG.ENDPOINTS.STATS_SEVERITY);
}

// Fonctions d'upload
async function uploadLogFile(file, description = '') {
    return api.uploadFile(CONFIG.ENDPOINTS.UPLOAD, file, description);
}

async function getUploadHistory() {
    return api.get(CONFIG.ENDPOINTS.UPLOAD_HISTORY);
}

// Health check
async function checkHealth() {
    return api.get(CONFIG.ENDPOINTS.HEALTH);
}
