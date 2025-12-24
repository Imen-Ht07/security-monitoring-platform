// frontend/js/api.js
/**
 * Service API centralisé
 * Gère tous les appels HTTP vers le backend
 * Avec retry, error handling, logging
 */

class APIService {
    constructor(config = CONFIG) {
        this.baseURL = config.API.BASE_URL;
        this.timeout = config.API.TIMEOUT;
        this.retryAttempts = config.API.RETRY_ATTEMPTS;
        this.retryDelay = config.API.RETRY_DELAY;
        this.logger = new Logger('APIService');
    }

    /**
     * Effectue une requête HTTP avec retry et error handling
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
            ...options
        };

        let lastError;
        for (let attempt = 0; attempt <= this.retryAttempts; attempt++) {
            try {
                this.logger.debug(`Request: ${defaultOptions.method} ${url}`);
                
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), this.timeout);

                const response = await fetch(url, {
                    ...defaultOptions,
                    signal: controller.signal
                });

                clearTimeout(timeoutId);

                if (!response.ok) {
                    throw new APIError(
                        `HTTP ${response.status}: ${response.statusText}`,
                        response.status,
                        await response.json().catch(() => ({}))
                    );
                }

                const data = await response.json();
                this.logger.debug(`Response: ${response.status}`, data);
                return data;

            } catch (error) {
                lastError = error;
                this.logger.warn(`Attempt ${attempt + 1} failed:`, error.message);

                if (attempt < this.retryAttempts) {
                    await this.delay(this.retryDelay * (attempt + 1)); // Exponential backoff
                }
            }
        }

        this.logger.error(`Failed after ${this.retryAttempts + 1} attempts:`, lastError);
        throw lastError;
    }

    /**
     * GET request
     */
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    /**
     * POST request
     */
    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    /**
     * PUT request
     */
    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    /**
     * DELETE request
     */
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    /**
     * Upload fichier avec FormData
     */
    async uploadFile(endpoint, file, metadata = {}, onProgress = null) {
        const url = `${this.baseURL}${endpoint}`;
        const formData = new FormData();
        formData.append('file', file);
        Object.keys(metadata).forEach(key => {
            formData.append(key, metadata[key]);
        });

        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();

            // Progress tracking
            if (onProgress) {
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable) {
                        onProgress({
                            loaded: e.loaded,
                            total: e.total,
                            percent: Math.round((e.loaded / e.total) * 100)
                        });
                    }
                });
            }

            // Success
            xhr.addEventListener('load', () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        resolve(response);
                    } catch (e) {
                        reject(new Error('Invalid JSON response'));
                    }
                } else {
                    try {
                        const error = JSON.parse(xhr.responseText);
                        reject(new APIError(error.error, xhr.status, error));
                    } catch (e) {
                        reject(new APIError(`HTTP ${xhr.status}`, xhr.status));
                    }
                }
            });

            // Error
            xhr.addEventListener('error', () => {
                reject(new Error('Network error'));
            });

            // Abort
            xhr.addEventListener('abort', () => {
                reject(new Error('Upload cancelled'));
            });

            // Timeout
            xhr.timeout = CONFIG.UPLOAD.TIMEOUT;
            xhr.addEventListener('timeout', () => {
                reject(new Error('Upload timeout'));
            });

            xhr.open('POST', url);
            xhr.send(formData);
        });
    }

    /**
     * Delay helper pour retry
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // ===== SEARCH ENDPOINTS =====

    async searchAdvanced(filters) {
        return this.post('/search/advanced', filters);
    }

    async getFilterOptions() {
        return this.get('/filters/options');
    }

    async getTopIPs(filters = {}) {
        return this.post('/stats/top-ips', filters);
    }

    async getTopEvents(filters = {}) {
        return this.post('/stats/top-events', filters);
    }

    async getTimeline(filters = {}) {
        return this.post('/stats/timeline', filters);
    }

    async getSeverityDistribution(filters = {}) {
        return this.post('/stats/severity-distribution', filters);
    }

    // ===== SAVED SEARCHES =====

    async listSavedSearches() {
        return this.get('/searches');
    }

    async getSavedSearch(id) {
        return this.get(`/searches/${id}`);
    }

    async saveSearch(name, description, filters) {
        return this.post('/searches', {
            name,
            description,
            filters
        });
    }

    async deleteSavedSearch(id) {
        return this.delete(`/searches/${id}`);
    }

    // ===== UPLOAD ENDPOINTS =====

    async uploadFile(file, description = '', onProgress = null) {
        return this.uploadFile('/upload', file, { description }, onProgress);
    }

    async getUploadHistory() {
        return this.get('/upload/history');
    }

    async getUploadDetails(id) {
        return this.get(`/upload/${id}`);
    }

    async deleteUpload(id) {
        return this.delete(`/upload/${id}`);
    }
}

/**
 * Custom Error Class for API errors
 */
class APIError extends Error {
    constructor(message, status, data = {}) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.data = data;
    }
}

/**
 * Simple Logger
 */
class Logger {
    constructor(context = 'App', level = CONFIG.LOG.LEVEL) {
        this.context = context;
        this.level = level;
        this.levels = { debug: 0, info: 1, warn: 2, error: 3 };
        this.logs = [];
    }

    log(level, message, data = null) {
        if (this.levels[level] >= this.levels[this.level]) {
            const timestamp = new Date().toISOString();
            const entry = { timestamp, level, context: this.context, message, data };
            
            console[level](`[${this.context}] ${message}`, data || '');
            
            if (CONFIG.LOG.STORAGE) {
                this.logs.push(entry);
                this.saveLogs();
            }
        }
    }

    debug(message, data) { this.log('debug', message, data); }
    info(message, data) { this.log('info', message, data); }
    warn(message, data) { this.log('warn', message, data); }
    error(message, data) { this.log('error', message, data); }

    saveLogs() {
        try {
            localStorage.setItem(`logs_${this.context}`, JSON.stringify(this.logs.slice(-100)));
        } catch (e) {
            // Storage full or disabled
        }
    }

    getLogs() {
        try {
            return JSON.parse(localStorage.getItem(`logs_${this.context}`) || '[]');
        } catch {
            return [];
        }
    }
}

// Créer une instance globale
const api = new APIService();
const appLogger = new Logger('App');
