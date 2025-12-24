// /static/js/ui.js
// Fonctions UI réutilisables

function showAlert(message, type = 'info') {
    const alertId = 'alert-' + Date.now();
    const alertHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert" id="${alertId}">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const container = document.querySelector('.container-fluid') || document.body;
    const alertDiv = document.createElement('div');
    alertDiv.innerHTML = alertHTML;
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = document.getElementById(alertId);
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

function showSuccess(message) {
    showAlert(message, 'success');
}

function showError(message) {
    showAlert(message, 'danger');
}

function showWarning(message) {
    showAlert(message, 'warning');
}

function showInfo(message) {
    showAlert(message, 'info');
}

function showLoading(element) {
    if (element) {
        element.style.display = 'block';
    }
}

function hideLoading(element) {
    if (element) {
        element.style.display = 'none';
    }
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function formatDate(dateString) {
    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

function getSeverityBadgeClass(severity) {
    const severityMap = {
        'CRITICAL': 'danger',
        'ERROR': 'danger',
        'WARNING': 'warning',
        'INFO': 'info',
        'DEBUG': 'secondary'
    };
    return severityMap[severity] || 'secondary';
}

function createSeverityBadge(severity) {
    const badgeClass = getSeverityBadgeClass(severity);
    return `<span class="badge bg-${badgeClass}">${severity}</span>`;
}

function createStatusBadge(status) {
    const statusMap = {
        'success': { class: 'success', icon: '✓' },
        'pending': { class: 'warning', icon: '⏳' },
        'error': { class: 'danger', icon: '✗' },
        'processing': { class: 'info', icon: '⚙️' }
    };
    
    const config = statusMap[status] || statusMap['pending'];
    return `<span class="badge bg-${config.class}">${config.icon} ${status}</span>`;
}

function showModal(modalId) {
    const modal = new bootstrap.Modal(document.getElementById(modalId));
    modal.show();
}

function hideModal(modalId) {
    const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
    if (modal) {
        modal.hide();
    }
}

function enableButton(buttonId) {
    const btn = document.getElementById(buttonId);
    if (btn) {
        btn.disabled = false;
        btn.style.opacity = '1';
    }
}

function disableButton(buttonId) {
    const btn = document.getElementById(buttonId);
    if (btn) {
        btn.disabled = true;
        btn.style.opacity = '0.5';
    }
}

function updateProgressBar(percentage, elementId = 'progressBar') {
    const bar = document.getElementById(elementId);
    if (bar) {
        bar.style.width = percentage + '%';
        bar.textContent = percentage + '%';
    }
}

function clearElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '';
    }
}

function showElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = 'block';
    }
}

function hideElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = 'none';
    }
}

function toggleElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = element.style.display === 'none' ? 'block' : 'none';
    }
}
