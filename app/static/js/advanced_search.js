
let currentPage = 1;
let currentResults = [];
let currentFilters = {};
let chart = null;

document.addEventListener('DOMContentLoaded', async () => {
    // Set today's date as default
    const today = new Date().toISOString().split('T')[0];
    const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];
    
    const dateFromInput = document.getElementById('dateFrom');
    const dateToInput = document.getElementById('dateTo');
    
    if (dateFromInput) dateFromInput.value = yesterday;
    if (dateToInput) dateToInput.value = today;
    
    // Load initial stats
    await loadStats();
});

async function performSearch() {
    currentPage = 1;
    const filters = buildFilters();
    currentFilters = filters;
    
    const loadingEl = document.getElementById('loading');
    if (loadingEl) showElement('loading');
    
    try {
        const response = await advancedSearch(filters);
        
        if (loadingEl) hideElement('loading');
        
        if (response && response.hits && Array.isArray(response.hits) && response.hits.length > 0) {
            currentResults = response.hits;
            displayResults(currentResults);
            updateResultCount(response.total || response.hits.length);
        } else {
            const resultsBody = document.getElementById('resultsBody');
            if (resultsBody) {
                resultsBody.innerHTML = `
                    <tr>
                        <td colspan="7" class="text-center text-muted py-4">
                            No results found. Try adjusting your filters.
                        </td>
                    </tr>
                `;
            }
        }
    } catch (error) {
        console.error('Search error:', error);
        if (loadingEl) hideElement('loading');
        showError(`Search failed: ${error.message}`);
    }
}

function buildFilters() {
    return {
        query: document.getElementById('queryText')?.value || '*',
        filters: {
            date_from: document.getElementById('dateFrom')?.value,
            date_to: document.getElementById('dateTo')?.value,
            severity: Array.from(document.getElementById('severity')?.selectedOptions || []).map(o => o.value),
            event_type: Array.from(document.getElementById('eventType')?.selectedOptions || []).map(o => o.value),
            country: Array.from(document.getElementById('country')?.selectedOptions || []).map(o => o.value),
            source_ip: document.getElementById('sourceIp')?.value,
            username: document.getElementById('username')?.value
        },
        size: CONFIG.PAGE_SIZE,
        from: (currentPage - 1) * CONFIG.PAGE_SIZE
    };
}

function displayResults(results) {
    const tbody = document.getElementById('resultsBody');
    if (!tbody) return;

    tbody.innerHTML = '';

    if (!Array.isArray(results)) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Invalid results format</td></tr>';
        return;
    }

    results.forEach(result => {
        const source = result._source || result;
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${formatDate(source.timestamp || new Date())}</td>
            <td>${truncate(source.event_type || 'N/A', 20)}</td>
            <td>${source.username || 'N/A'}</td>
            <td>${source.source_ip || 'N/A'}</td>
            <td>${source.country || 'N/A'}</td>
            <td>${createSeverityBadge(source.severity || 'INFO')}</td>
            <td>${truncate(source.description || source.message || '', 40)}</td>
        `;
        tbody.appendChild(row);
    });
}

function updateResultCount(count) {
    const resultCount = document.getElementById('resultCount');
    if (resultCount) {
        resultCount.textContent = `${count} results`;
    }
}

function resetFilters() {
    const queryText = document.getElementById('queryText');
    const severity = document.getElementById('severity');
    const eventType = document.getElementById('eventType');
    const country = document.getElementById('country');
    const sourceIp = document.getElementById('sourceIp');
    const username = document.getElementById('username');
    
    if (queryText) queryText.value = '';
    if (severity) severity.value = '';
    if (eventType) eventType.value = '';
    if (country) country.value = '';
    if (sourceIp) sourceIp.value = '';
    if (username) username.value = '';
    
    const resultsBody = document.getElementById('resultsBody');
    if (resultsBody) {
        resultsBody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-muted py-4">
                    Use filters above to perform a search
                </td>
            </tr>
        `;
    }
}

function nextPage() {
    currentPage++;
    performSearch();
}

function previousPage() {
    if (currentPage > 1) {
        currentPage--;
        performSearch();
    }
}

async function loadStats() {
    try {
        const stats = await getStats();
        displayStats(stats);
    } catch (error) {
        console.error('Error loading stats:', error);
        // Show default stats if API fails
        const container = document.getElementById('statsContainer');
        if (container) {
            container.innerHTML = `
                <div class="stat-card">
                    <h5>Total Logs</h5>
                    <div class="number">-</div>
                </div>
                <div class="stat-card">
                    <h5>Critical Events</h5>
                    <div class="number" style="color: #ef4444;">-</div>
                </div>
                <div class="stat-card">
                    <h5>Today's Events</h5>
                    <div class="number" style="color: #3b82f6;">-</div>
                </div>
                <div class="stat-card">
                    <h5>Unique IPs</h5>
                    <div class="number" style="color: #10b981;">-</div>
                </div>
            `;
        }
    }
}

function displayStats(stats) {
    const container = document.getElementById('statsContainer');
    if (!container) return;

    const statsHTML = `
        <div class="stat-card">
            <h5>Total Logs</h5>
            <div class="number">${(stats.total_logs || 0).toLocaleString()}</div>
        </div>
        <div class="stat-card">
            <h5>Critical Events</h5>
            <div class="number" style="color: #ef4444;">${(stats.critical_count || 0).toLocaleString()}</div>
        </div>
        <div class="stat-card">
            <h5>Today's Events</h5>
            <div class="number" style="color: #3b82f6;">${(stats.today_count || 0).toLocaleString()}</div>
        </div>
        <div class="stat-card">
            <h5>Unique IPs</h5>
            <div class="number" style="color: #10b981;">${(stats.unique_ips || 0).toLocaleString()}</div>
        </div>
    `;

    container.innerHTML = statsHTML;
}

function saveCurrentSearch() {
    const searchName = document.getElementById('searchName')?.value;
    const searchDescription = document.getElementById('searchDescription')?.value;

    if (!searchName) {
        showError('Please enter a search name');
        return;
    }

    const savedSearch = {
        id: generateUUID(),
        name: searchName,
        description: searchDescription,
        filters: currentFilters,
        timestamp: new Date().toISOString()
    };

    let savedSearches = localStorage_get('saved_searches') || [];
    savedSearches.push(savedSearch);
    localStorage_set('saved_searches', savedSearches);

    showSuccess('Search saved successfully');
    hideModal('saveSearchModal');
    
    const searchNameEl = document.getElementById('searchName');
    const searchDescEl = document.getElementById('searchDescription');
    if (searchNameEl) searchNameEl.value = '';
    if (searchDescEl) searchDescEl.value = '';
}

function loadSavedSearch(searchId) {
    const savedSearches = localStorage_get('saved_searches') || [];
    const search = savedSearches.find(s => s.id === searchId);

    if (search) {
        currentFilters = search.filters;
        
        // Apply filters to form
        const queryTextEl = document.getElementById('queryText');
        if (queryTextEl) queryTextEl.value = search.filters.query || '';
        
        hideModal('savedSearchesModal');
        performSearch();
    }
}

// Search shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl+F to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        const queryTextEl = document.getElementById('queryText');
        if (queryTextEl) queryTextEl.focus();
    }
    
    // Enter to search
    const queryTextEl = document.getElementById('queryText');
    if (e.key === 'Enter' && queryTextEl && document.activeElement === queryTextEl) {
        performSearch();
    }
});
