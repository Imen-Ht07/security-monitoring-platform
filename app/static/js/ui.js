// frontend/js/ui.js
/**
 * Service UI centralisé
 * Gère les notifications, modales, loaders, etc
 */

class UIService {
    constructor() {
        this.createToastContainer();
        this.logger = new Logger('UIService');
    }

    // ===== TOASTS =====

    createToastContainer() {
        if (!document.getElementById('toast-container')) {
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                width: 350px;
                max-width: 90vw;
            `;
            document.body.appendChild(container);
        }
    }

    toast(message, type = 'info', duration = CONFIG.UI.TOAST_DURATION) {
        const container = document.getElementById('toast-container');
        
        const toast = document.createElement('div');
        toast.className = `alert alert-${type}`;
        toast.style.cssText = `
            margin-bottom: 10px;
            border-radius: 8px;
            padding: 15px;
            border: 1px solid;
            animation: slideIn 0.3s ease-out;
        `;

        const colors = {
            success: { bg: 'rgba(16, 185, 129, 0.1)', border: '#10b981', text: '#10b981' },
            danger: { bg: 'rgba(239, 68, 68, 0.1)', border: '#ef4444', text: '#ef4444' },
            warning: { bg: 'rgba(245, 158, 11, 0.1)', border: '#f59e0b', text: '#f59e0b' },
            info: { bg: 'rgba(59, 130, 246, 0.1)', border: '#3b82f6', text: '#3b82f6' }
        };

        const color = colors[type] || colors.info;
        toast.style.backgroundColor = color.bg;
        toast.style.borderColor = color.border;
        toast.style.color = color.text;
        toast.innerHTML = `
            <strong>${type.toUpperCase()}:</strong> ${message}
        `;

        container.appendChild(toast);

        if (duration > 0) {
            setTimeout(() => {
                toast.style.animation = 'slideOut 0.3s ease-in';
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }

        return toast;
    }

    success(message) { this.toast(message, 'success'); }
    error(message) { this.toast(message, 'danger'); }
    warning(message) { this.toast(message, 'warning'); }
    info(message) { this.toast(message, 'info'); }

    // ===== LOADING =====

    showLoader(target = 'body') {
        const loader = document.createElement('div');
        loader.className = 'loader';
        loader.id = 'global-loader';
        loader.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9998;
        `;
        loader.innerHTML = `
            <div style="text-align: center;">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p style="color: #e2e8f0; margin-top: 15px;">Chargement...</p>
            </div>
        `;
        document.body.appendChild(loader);
        return loader;
    }

    hideLoader() {
        const loader = document.getElementById('global-loader');
        if (loader) loader.remove();
    }

    // ===== PROGRESS BAR =====

    createProgressBar(container, initialValue = 0) {
        const wrapper = document.createElement('div');
        wrapper.style.cssText = `
            margin-top: 20px;
            display: none;
        `;
        wrapper.id = 'progress-wrapper';

        wrapper.innerHTML = `
            <p style="color: #94a3b8; margin-bottom: 8px;">Upload en cours...</p>
            <div style="background: #0f172a; border: 1px solid #475569; border-radius: 6px; height: 30px; overflow: hidden;">
                <div id="progress-bar" style="width: ${initialValue}%; background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%); height: 100%; transition: width 0.3s ease; display: flex; align-items: center; justify-content: center;">
                    <span id="progress-text" style="color: white; font-weight: bold; font-size: 12px;">0%</span>
                </div>
            </div>
        `;

        container.appendChild(wrapper);

        return {
            show: () => { wrapper.style.display = 'block'; },
            hide: () => { wrapper.style.display = 'none'; },
            update: (percent) => {
                const bar = document.getElementById('progress-bar');
                const text = document.getElementById('progress-text');
                if (bar && text) {
                    bar.style.width = percent + '%';
                    text.textContent = percent + '%';
                }
            }
        };
    }

    // ===== MODALS =====

    createModal(title, content, buttons = []) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.setAttribute('tabindex', '-1');
        modal.style.cssText = 'display: none;';

        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content" style="background: var(--secondary); border: 1px solid #475569;">
                    <div class="modal-header" style="border-bottom: 1px solid #475569;">
                        <h5 class="modal-title">${title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body" id="modal-content">
                        ${content}
                    </div>
                    <div class="modal-footer" style="border-top: 1px solid #475569;">
                        ${buttons.map(btn => `
                            <button type="button" class="btn btn-${btn.type || 'secondary'}" 
                                    onclick="${btn.onclick || 'null'}">
                                ${btn.label}
                            </button>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        return { modal, show: () => bsModal.show(), hide: () => bsModal.hide() };
    }

    // ===== ALERTS =====

    alert(message, type = 'danger') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.style.cssText = `
            margin-top: 20px;
            border-radius: 8px;
        `;
        alert.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
        return alert;
    }

    // ===== DOM HELPERS =====

    show(element) {
        if (typeof element === 'string') element = document.getElementById(element);
        if (element) element.style.display = 'block';
    }

    hide(element) {
        if (typeof element === 'string') element = document.getElementById(element);
        if (element) element.style.display = 'none';
    }

    enable(element) {
        if (typeof element === 'string') element = document.getElementById(element);
        if (element) element.disabled = false;
    }

    disable(element) {
        if (typeof element === 'string') element = document.getElementById(element);
        if (element) element.disabled = true;
    }

    addClass(element, className) {
        if (typeof element === 'string') element = document.getElementById(element);
        if (element) element.classList.add(className);
    }

    removeClass(element, className) {
        if (typeof element === 'string') element = document.getElementById(element);
        if (element) element.classList.remove(className);
    }

    toggleClass(element, className) {
        if (typeof element === 'string') element = document.getElementById(element);
        if (element) element.classList.toggle(className);
    }

    // ===== TABLES =====

    createTable(headers, rows) {
        const table = document.createElement('table');
        table.className = 'table';

        // Header
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        headers.forEach(header => {
            const th = document.createElement('th');
            th.textContent = header;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Body
        const tbody = document.createElement('tbody');
        rows.forEach(row => {
            const tr = document.createElement('tr');
            row.forEach(cell => {
                const td = document.createElement('td');
                td.innerHTML = cell;
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);

        return table;
    }

    // ===== FORMS =====

    getFormData(formId) {
        const form = document.getElementById(formId);
        if (!form) return null;

        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });
        return data;
    }

    resetForm(formId) {
        const form = document.getElementById(formId);
        if (form) form.reset();
    }

    setFormData(formId, data) {
        const form = document.getElementById(formId);
        if (!form) return;

        Object.keys(data).forEach(key => {
            const input = form.querySelector(`[name="${key}"]`);
            if (input) {
                if (input.type === 'checkbox') {
                    input.checked = data[key];
                } else {
                    input.value = data[key];
                }
            }
        });
    }
}

// Créer une instance globale
const ui = new UIService();

// Ajouter les animations CSS
const style = document.createElement('style');
style.innerHTML = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }

    .alert {
        color: #e2e8f0;
    }

    .alert-success {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid #10b981;
        color: #10b981;
    }

    .alert-danger {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid #ef4444;
        color: #ef4444;
    }

    .alert-warning {
        background: rgba(245, 158, 11, 0.1);
        border: 1px solid #f59e0b;
        color: #f59e0b;
    }

    .alert-info {
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid #3b82f6;
        color: #3b82f6;
    }
`;
document.head.appendChild(style);
