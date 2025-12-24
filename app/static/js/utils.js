// /static/js/utils.js
// Fonctions utilitaires

function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

function setQueryParam(param, value) {
    const url = new URL(window.location);
    url.searchParams.set(param, value);
    window.history.pushState({}, '', url);
}

function localStorage_set(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
}

function localStorage_get(key) {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : null;
}

function localStorage_remove(key) {
    localStorage.removeItem(key);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

function parseCSV(csvText) {
    const lines = csvText.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.trim());
    const data = [];
    
    for (let i = 1; i < lines.length; i++) {
        const obj = {};
        const currentLine = lines[i].split(',');
        
        for (let j = 0; j < headers.length; j++) {
            obj[headers[j]] = currentLine[j] ? currentLine[j].trim() : '';
        }
        data.push(obj);
    }
    
    return data;
}

function downloadFile(data, filename, type = 'application/json') {
    const blob = new Blob([typeof data === 'string' ? data : JSON.stringify(data, null, 2)], { type });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showSuccess('Copied to clipboard');
    }).catch(() => {
        showError('Failed to copy');
    });
}

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function getRandomColor() {
    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];
    return colors[Math.floor(Math.random() * colors.length)];
}

function truncate(str, length = 50) {
    return str.length > length ? str.substring(0, length) + '...' : str;
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function isValidIP(ip) {
    const re = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    return re.test(ip);
}

// Chart Colors
const CHART_COLORS = {
    primary: 'rgba(59, 130, 246, 1)',
    success: 'rgba(16, 185, 129, 1)',
    danger: 'rgba(239, 68, 68, 1)',
    warning: 'rgba(245, 158, 11, 1)',
    info: 'rgba(14, 165, 233, 1)'
};

const CHART_COLORS_BG = {
    primary: 'rgba(59, 130, 246, 0.1)',
    success: 'rgba(16, 185, 129, 0.1)',
    danger: 'rgba(239, 68, 68, 0.1)',
    warning: 'rgba(245, 158, 11, 0.1)',
    info: 'rgba(14, 165, 233, 0.1)'
};
