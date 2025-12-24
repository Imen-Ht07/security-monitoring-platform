// static/js/advanced_search.js
// frontend/js/advanced-search.js
const API_BASE = '/api';
let currentPage = 0;
const pageSize = 50;
let totalResults = 0;
let timelineChart = null;

// Initialisation au chargement
document.addEventListener('DOMContentLoaded', () => {
    loadFilterOptions();
    loadSavedSearches();
    setDefaultDates();
});

// ===== INITIALISATION =====
function setDefaultDates() {
    const today = new Date();
    const sevenDaysAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
    
    document.getElementById('dateTo').valueAsDate = today;
    document.getElementById('dateFrom').valueAsDate = sevenDaysAgo;
}

async function loadFilterOptions() {
    try {
        const response = await fetch(`${API_BASE}/filters/options`);
        const data = await response.json();
        
        if (data.success) {
            // Populate event type dropdown
            const eventTypeSelect = document.getElementById('eventType');
            data.data.event_types.forEach(type => {
                const option = document.createElement('option');
                option.value = type;
                option.textContent = type;
                eventTypeSelect.appendChild(option);
            });
            
            // Populate country dropdown
            const countrySelect = document.getElementById('country');
            data.data.countries.forEach(country => {
                const option = document.createElement('option');
                option.value = country;
                option.textContent = country;
                countrySelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading filter options:', error);
    }
}

// ===== SEARCH OPERATIONS =====
async function performSearch() {
    currentPage = 0;
    await executeSearch();
}

async function executeSearch() {
    showLoading(true);
    
    try {
        const filters = getFiltersFromUI();
        filters.page = currentPage;
        filters.size = pageSize;
        
        // 1. Effectuer la recherche
        const searchResponse = await fetch(`${API_BASE}/search/advanced`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(filters)
        });
        const searchData = await searchResponse.json();
        
        if (!searchData.success) {
            alert('Search error: ' + (searchData.error || 'Unknown error'));
            showLoading(false);
            return;
        }
        
        totalResults = searchData.total;
        displayResults(searchData.hits);
        updatePagination();
        
        // 2. Charger les stats en parallèle
        await Promise.all([
            loadTimeline(filters),
            loadTopIPs(filters),
            loadTopEvents(filters),
            loadStatistics(filters)
        ]);
        
    } catch (error) {
        console.error('Search error:', error);
        alert('Search failed: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// ===== GET FILTERS FROM UI =====
function getFiltersFromUI() {
    const severity = Array.from(document.getElementById('severity').selectedOptions).map(o => o.value);
    const eventType = Array.from(document.getElementById('eventType').selectedOptions).map(o => o.value);
    const country = Array.from(document.getElementById('country').selectedOptions).map(o => o.value);
    
    return {
        query_text: document.getElementById('queryText').value || null,
        severity: severity.length > 0 ? severity : null,
        event_type: eventType.length > 0 ? eventType : null,
        country: country.length > 0 ? country : null,
        username: document.getElementById('username').value || null,
        source_ip: document.getElementById('sourceIp').value || null,
        date_from: document.getElementById('dateFrom').value || null,
        date_to: document.getElementById('dateTo').value || null
    };
}

// ===== DISPLAY RESULTS =====
function displayResults(hits) {
    const tbody = document.getElementById('resultsBody');
    tbody.innerHTML = '';
    
    if (hits.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-4">No results found</td></tr>';
        document.getElementById('resultCount').textContent = '0 results';
        return;
    }
    
    document.getElementById('resultCount').textContent = `${totalResults} results`;
    
    hits.forEach(hit => {
        const row = document.createElement('tr');
        
        const timestamp = new Date(hit['@timestamp']).toLocaleString();
        const severity = hit.severity || 'UNKNOWN';
        const severityBadge = `<span class="badge badge-${severity.toLowerCase()}">${severity}</span>`;
        
        row.innerHTML = `
            <td><small>${timestamp}</small></td>
            <td><strong>${hit.event_type || 'N/A'}</strong></td>
            <td>${hit.username || 'N/A'}</td>
            <td><code>${hit.source_ip || 'N/A'}</code></td>
            <td>${hit.country || 'N/A'}</td>
            <td>${severityBadge}</td>
            <td><small>${(hit.description || 'N/A').substring(0, 50)}...</small></td>
        `;
        tbody.appendChild(row);
    });
}

// ===== AGGREGATIONS - TIMELINE =====
async function loadTimeline(filters) {
    try {
        const response = await fetch(`${API_BASE}/stats/timeline`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ...filters,
                interval: 'day'
            })
        });
        
        const data = await response.json();
        if (!data.success) return;
        
        const timeline = data.data;
        const labels = timeline.map(t => new Date(t.timestamp).toLocaleDateString());
        const counts = timeline.map(t => t.count);
        
        // Créer ou mettre à jour le chart
        const ctx = document.getElementById('timelineChart').getContext('2d');
        
        if (timelineChart) {
            timelineChart.destroy();
        }
        
        timelineChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Events per Day',
                    data: counts,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#3b82f6',
                    pointBorderColor: '#fff',
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#e2e8f0' }
                    }
                },
                scales: {
                    y: {
                        ticks: { color: '#e2e8f0' },
                        grid: { color: '#475569' }
                    },
                    x: {
                        ticks: { color: '#e2e8f0' },
                        grid: { color: '#475569' }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Timeline error:', error);
    }
}

// ===== AGGREGATIONS - TOP IPs =====
async function loadTopIPs(filters) {
    try {
        const response = await fetch(`${API_BASE}/stats/top-ips`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ...filters,
                limit: 10
            })
        });
        
        const data = await response.json();
        if (!data.success) return;
        
        const container = document.getElementById('topIpsContainer');
        container.innerHTML = '';
        
        data.data.forEach(item => {
            const div = document.createElement('div');
            div.className = 'd-flex justify-content-between align-items-center py-2 border-bottom';
            div.innerHTML = `
                <span><code>${item.ip}</code></span>
                <span class="badge bg-primary">${item.count}</span>
            `;
            container.appendChild(div);
        });
    } catch (error) {
        console.error('Top IPs error:', error);
    }
}

// ===== AGGREGATIONS - TOP EVENT TYPES =====
async function loadTopEvents(filters) {
    try {
        const response = await fetch(`${API_BASE}/stats/top-events`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ...filters,
                limit: 10
            })
        });
        
        const data = await response.json();
        if (!data.success) return;
        
        const container = document.getElementById('topEventsContainer');
        container.innerHTML = '';
        
        data.data.forEach(item => {
            const div = document.createElement('div');
            div.className = 'd-flex justify-content-between align-items-center py-2 border-bottom';
            div.innerHTML = `
                <span>${item.event_type}</span>
                <span class="badge bg-info">${item.count}</span>
            `;
            container.appendChild(div);
        });
    } catch (error) {
        console.error('Top events error:', error);
    }
}

// ===== STATISTICS CARDS =====
async function loadStatistics(filters) {
    try {
        const response = await fetch(`${API_BASE}/stats/severity-distribution`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(filters)
        });
        
        const data = await response.json();
        if (!data.success) return;
        
        const container = document.getElementById('statsContainer');
        container.innerHTML = '';
        
        data.data.forEach(item => {
            const div = document.createElement('div');
            div.className = 'stat-card';
            const color = item.severity === 'CRITICAL' ? '#ef4444' : 
                         item.severity === 'ERROR' ? '#f97316' : 
                         item.severity === 'WARNING' ? '#eab308' : '#0ea5e9';
            div.style.borderLeftColor = color;
            div.innerHTML = `
                <h5>${item.severity}</h5>
                <div class="number" style="color: ${color};">${item.count}</div>
            `;
            container.appendChild(div);
        });
    } catch (error) {
        console.error('Statistics error:', error);
    }
}

// ===== PAGINATION =====
function nextPage() {
    if ((currentPage + 1) * pageSize < totalResults) {
        currentPage++;
        executeSearch();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

function previousPage() {
    if (currentPage > 0) {
        currentPage--;
        executeSearch();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

function updatePagination() {
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    prevBtn.disabled = currentPage === 0;
    nextBtn.disabled = (currentPage + 1) * pageSize >= totalResults;
    
    const start = currentPage * pageSize + 1;
    const end = Math.min((currentPage + 1) * pageSize, totalResults);
    document.getElementById('pageInfo').textContent = `Results ${start}-${end} of ${totalResults}`;
}

// ===== SAVED SEARCHES =====
async function saveCurrentSearch() {
    const name = document.getElementById('searchName').value;
    
    if (!name) {
        alert('Please enter a search name');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/searches`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
                description: document.getElementById('searchDescription').value,
                filters: getFiltersFromUI()
            })
        });
        
        const data = await response.json();
        if (data.success) {
            alert('Search saved successfully!');
            document.getElementById('searchName').value = '';
            document.getElementById('searchDescription').value = '';
            bootstrap.Modal.getInstance(document.getElementById('saveSearchModal')).hide();
            loadSavedSearches();
        }
    } catch (error) {
        console.error('Save search error:', error);
        alert('Failed to save search');
    }
}

async function loadSavedSearches() {
    try {
        const response = await fetch(`${API_BASE}/searches`);
        const data = await response.json();
        
        if (!data.success) return;
        
        const container = document.getElementById('savedSearchesList');
        container.innerHTML = '';
        
        if (data.data.length === 0) {
            container.innerHTML = '<p class="text-muted">No saved searches yet</p>';
            return;
        }
        
        data.data.forEach(search => {
            const div = document.createElement('div');
            div.className = 'd-flex justify-content-between align-items-center p-3 border-bottom';
            div.innerHTML = `
                <div>
                    <h6 class="mb-0">${search.name}</h6>
                    <small class="text-muted">${new Date(search.created_at).toLocaleString()}</small>
                </div>
                <div>
                    <button class="btn btn-sm btn-primary" onclick="loadSavedSearch('${search.id}')">Load</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteSavedSearch('${search.id}')">Delete</button>
                </div>
            `;
            container.appendChild(div);
        });
    } catch (error) {
        console.error('Load saved searches error:', error);
    }
}

async function loadSavedSearch(searchId) {
    try {
        const response = await fetch(`${API_BASE}/searches/${searchId}`);
        const data = await response.json();
        
        if (!data.success) return;
        
        const filters = data.data.filters;
        
        // Populate filters from saved search
        if (filters.query_text) document.getElementById('queryText').value = filters.query_text;
        if (filters.source_ip) document.getElementById('sourceIp').value = filters.source_ip;
        if (filters.username) document.getElementById('username').value = filters.username;
        if (filters.date_from) document.getElementById('dateFrom').value = filters.date_from;
        if (filters.date_to) document.getElementById('dateTo').value = filters.date_to;
        
        // Set multi-selects
        if (filters.severity) {
            const severitySelect = document.getElementById('severity');
            Array.from(severitySelect.options).forEach(opt => {
                opt.selected = filters.severity.includes(opt.value);
            });
        }
        
        if (filters.event_type) {
            const eventSelect = document.getElementById('eventType');
            Array.from(eventSelect.options).forEach(opt => {
                opt.selected = filters.event_type.includes(opt.value);
            });
        }
        
        if (filters.country) {
            const countrySelect = document.getElementById('country');
            Array.from(countrySelect.options).forEach(opt => {
                opt.selected = filters.country.includes(opt.value);
            });
        }
        
        // Close modal and search
        bootstrap.Modal.getInstance(document.getElementById('savedSearchesModal')).hide();
        performSearch();
        
    } catch (error) {
        console.error('Load saved search error:', error);
    }
}

async function deleteSavedSearch(searchId) {
    if (!confirm('Delete this saved search?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/searches/${searchId}`, { method: 'DELETE' });
        const data = await response.json();
        
        if (data.success) {
            loadSavedSearches();
        }
    } catch (error) {
        console.error('Delete saved search error:', error);
    }
}

// ===== UTILITIES =====
function resetFilters() {
    document.getElementById('queryText').value = '';
    document.getElementById('sourceIp').value = '';
    document.getElementById('username').value = '';
    document.getElementById('severity').selectedIndex = -1;
    document.getElementById('eventType').selectedIndex = -1;
    document.getElementById('country').selectedIndex = -1;
    setDefaultDates();
}

function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'block' : 'none';
}
