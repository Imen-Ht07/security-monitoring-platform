let currentPage = 1;
let currentResults = [];
let currentFilters = {};
let currentTotal = 0;
let chart = null;
document.addEventListener('DOMContentLoaded', async () => {
    // Suppression du paramétrage automatique des dates pour éviter de filtrer inutilement
    // Les inputs restent vides par défaut (envoyant null au backend)
    await loadStats();
    loadSavedSearches();
    chart = new Chart(document.getElementById('timelineChart'), {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Events per Day',
                data: [],
                borderColor: 'var(--accent)',
                tension: 0.1
            }]
        },
        options: {
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
});
/* =======================
   SEARCH
======================= */
async function performSearch() {
    const filters = buildFilters();
    currentFilters = filters;
    showElement('loading');
    try {
        const response = await advancedSearch(filters);
        console.log("Advanced search response:", response); // DEBUG
        hideElement('loading');
        if (!response.success) {
            showError(response.error || 'Unknown error');
            updateResultCount(0);
            updatePagination(0);
            showNoResults();
            clearAggs();
            return;
        }
        currentTotal = response.total || 0;
        if (Array.isArray(response.logs) && response.logs.length > 0) {
            currentResults = response.logs;
            displayResults(currentResults);
        } else {
            showNoResults();
        }
        updateResultCount(currentTotal);
        updatePagination(currentTotal);
        if (response.aggs) {
            displayTopIps(response.aggs.top_ips?.buckets || []);
            displayTopEvents(response.aggs.top_event_types?.buckets || []);
            updateTimelineChart(response.aggs.timeline?.buckets || []);
        } else {
            clearAggs();
        }
    } catch (error) {
        hideElement('loading');
        console.error('Search error:', error);
        showError(`Search failed: ${error.message}`);
    }
}
/* =======================
   BUILD FILTERS
======================= */
function buildFilters() {
    const getSplitValues = (id) => {
        const val = document.getElementById(id)?.value || '';
        return val.split(',').map(s => s.trim()).filter(s => s) || null;
    };
    return {
        query: document.getElementById('queryText')?.value || '*',
        filters: {
            date_from: document.getElementById('dateFrom')?.value || null,
            date_to: document.getElementById('dateTo')?.value || null,
            severity: document.getElementById('severity')?.value || null,
            event_type: getSplitValues('eventType') || null,
            country: getSplitValues('country') || null,
            source_ip: document.getElementById('sourceIp')?.value || null
        },
        page: currentPage - 1, // ✅ IMPORTANT
        size: CONFIG.PAGE_SIZE
    };
}
/* =======================
   DISPLAY RESULTS
======================= */
function displayResults(results) {
    const tbody = document.getElementById('resultsBody');
    if (!tbody) return;
    tbody.innerHTML = '';
    results.forEach(log => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${formatDate(log.timestamp)}</td>
            <td>${truncate(log.event_type || 'N/A', 20)}</td>
            <td>${log.source_ip || 'N/A'}</td>
            <td>${log.country || 'N/A'}</td>
            <td>${createSeverityBadge(log.severity || 'INFO')}</td>
            <td>${truncate(log.description || log.message || '', 40)}</td>
        `;
        tbody.appendChild(row);
    });
}
function showNoResults() {
    const tbody = document.getElementById('resultsBody');
    if (tbody) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted py-4">
                    No results found. Try adjusting your filters.
                </td>
            </tr>
        `;
    }
}
function updateResultCount(count) {
    const el = document.getElementById('resultCount');
    if (el) el.textContent = `${count} results`;
}
/* =======================
   PAGINATION
======================= */
function updatePagination(total) {
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const pageInfo = document.getElementById('pageInfo');
    if (pageInfo) pageInfo.textContent = `Page ${currentPage}`;
    if (prevBtn) prevBtn.disabled = currentPage === 1;
    if (nextBtn) nextBtn.disabled = currentPage * CONFIG.PAGE_SIZE >= total;
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
/* =======================
   RESET
======================= */
function resetFilters() {
    ['queryText', 'dateFrom', 'dateTo', 'severity', 'eventType', 'country', 'sourceIp'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });
    showNoResults();
    updateResultCount(0);
    clearAggs();
}
/* =======================
   STATS
======================= */
async function loadStats() {
    try {
        const stats = await getStats();
        displayStats(stats);
    } catch (err) {
        console.error(err);
    }
}
function displayStats(stats) {
    const container = document.getElementById('statsContainer');
    if (!container) return;
    container.innerHTML = `
        <div class="stat-card"><h5>Total Logs</h5><div class="number">${stats.total_logs || 0}</div></div>
        <div class="stat-card"><h5>Critical Events</h5><div class="number">${stats.critical_count || 0}</div></div>
        <div class="stat-card"><h5>Today's Events</h5><div class="number">${stats.today_count || 0}</div></div>
        <div class="stat-card"><h5>Unique IPs</h5><div class="number">${stats.unique_ips || 0}</div></div>
    `;
}
/* =======================
   SHORTCUT
======================= */
document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && document.activeElement.id === 'queryText') {
        performSearch();
    }
});
/* =======================
   SAVED SEARCHES
======================= */
function saveCurrentSearch() {
    const name = document.getElementById('searchName')?.value.trim();
    const description = document.getElementById('searchDescription')?.value.trim();
   
    if (!name) {
        showError('Please enter a search name');
        return;
    }

    // Build fresh filters from current input values
    const filters = buildFilters();

    const savedSearches = localStorage_get('savedSearches') || [];
    savedSearches.push({
        name,
        description,
        filters
    });
   
    localStorage_set('savedSearches', savedSearches);
    showSuccess('Search saved successfully');
   
    // Clear inputs
    document.getElementById('searchName').value = '';
    document.getElementById('searchDescription').value = '';

    // Blur focused element inside modal to avoid ARIA issues
    const modal = document.getElementById('saveSearchModal');
    if (modal && modal.contains(document.activeElement)) {
        document.activeElement.blur();
    }
   
    // Hide modal
    hideModal('saveSearchModal');
   
    // Refresh list
    loadSavedSearches();
}
function loadSavedSearches() {
    const listContainer = document.getElementById('savedSearchesList');
    if (!listContainer) return;
    const savedSearches = localStorage_get('savedSearches') || [];
   
    if (savedSearches.length === 0) {
        listContainer.innerHTML = '<p class="text-muted">No saved searches yet.</p>';
        return;
    }
    listContainer.innerHTML = savedSearches.map((search, index) => `
        <div class="card mb-3">
            <div class="card-body">
                <h6>${search.name}</h6>
                <p class="text-muted small">${search.description || 'No description'}</p>
                <button class="btn btn-sm btn-primary" onclick="applySavedSearch(${index})">
                    <i class="fas fa-search"></i> Load
                </button>
                <button class="btn btn-sm btn-danger ms-2" onclick="deleteSavedSearch(${index})">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </div>
        </div>
    `).join('');
}
function applySavedSearch(index) {
    const savedSearches = localStorage_get('savedSearches') || [];
    const search = savedSearches[index];
    if (!search) return;
    const filters = search.filters;
    const innerFilters = filters.filters || {};
    document.getElementById('queryText').value = filters.query || '';
    document.getElementById('dateFrom').value = innerFilters.date_from || '';
    document.getElementById('dateTo').value = innerFilters.date_to || '';
    document.getElementById('severity').value = innerFilters.severity || '';
    document.getElementById('eventType').value = Array.isArray(innerFilters.event_type) ? innerFilters.event_type.join(', ') : '';
    document.getElementById('country').value = Array.isArray(innerFilters.country) ? innerFilters.country.join(', ') : '';
    document.getElementById('sourceIp').value = innerFilters.source_ip || '';
    hideModal('savedSearchesModal');
    performSearch();
}
function deleteSavedSearch(index) {
    const savedSearches = localStorage_get('savedSearches') || [];
    savedSearches.splice(index, 1);
    localStorage_set('savedSearches', savedSearches);
    loadSavedSearches();
    showSuccess('Search deleted');
}
/* =======================
   AGGREGATIONS
======================= */
function displayTopIps(buckets) {
    const container = document.getElementById('topIpsContainer');
    if (!container) return;
    if (buckets.length === 0) {
        container.innerHTML = '<p class="text-muted">No data available</p>';
        return;
    }
    container.innerHTML = buckets.map(b => `
        <div class="d-flex justify-content-between mb-2">
            <span>${b.key}</span>
            <span class="badge bg-primary">${b.doc_count}</span>
        </div>
    `).join('');
}
function displayTopEvents(buckets) {
    const container = document.getElementById('topEventsContainer');
    if (!container) return;
    if (buckets.length === 0) {
        container.innerHTML = '<p class="text-muted">No data available</p>';
        return;
    }
    container.innerHTML = buckets.map(b => `
        <div class="d-flex justify-content-between mb-2">
            <span>${b.key}</span>
            <span class="badge bg-primary">${b.doc_count}</span>
        </div>
    `).join('');
}
function updateTimelineChart(buckets) {
    if (!chart) return;
    if (buckets.length === 0) {
        chart.data.labels = [];
        chart.data.datasets[0].data = [];
        chart.update();
        return;
    }
    const sortedBuckets = buckets.sort((a, b) => new Date(a.key_as_string) - new Date(b.key_as_string));
    chart.data.labels = sortedBuckets.map(b => b.key_as_string);
    chart.data.datasets[0].data = sortedBuckets.map(b => b.doc_count);
    chart.update();
}
function clearAggs() {
    displayTopIps([]);
    displayTopEvents([]);
    updateTimelineChart([]);
}
/* =======================
   EXPORT
======================= */
async function exportResults(format) {
    if (currentTotal === 0) {
        showError('No results to export');
        return;
    }
    showElement('loading');
    try {
        const exportFilters = { ...currentFilters, page: 0, size: currentTotal };
        const response = await advancedSearch(exportFilters);
        hideElement('loading');
        if (!response.success || !Array.isArray(response.logs)) {
            showError('Failed to fetch all results for export');
            return;
        }
        const allLogs = response.logs;
        if (format === 'json') {
            const blob = new Blob([JSON.stringify(allLogs, null, 2)], { type: 'application/json' });
            downloadBlob(blob, 'search_results.json');
        } else if (format === 'csv') {
            const csv = convertToCSV(allLogs);
            const blob = new Blob([csv], { type: 'text/csv' });
            downloadBlob(blob, 'search_results.csv');
        } else if (format === 'pdf') {
            exportToPDF(allLogs);
        }
    } catch (error) {
        hideElement('loading');
        showError('Export failed: ' + error.message);
    }
}
function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
function convertToCSV(logs) {
    const headers = ['timestamp', 'event_type', 'source_ip', 'country', 'severity', 'description'];
    const rows = logs.map(log => 
        headers.map(h => JSON.stringify((log[h] || '').toString().replace(/"/g, '""'))).join(',')
    );
    return [headers.join(','), ...rows].join('\n');
}
function exportToPDF(logs) {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    const columns = ['Timestamp', 'Event Type', 'Source IP', 'Country', 'Severity', 'Description'];
    const data = logs.map(log => [
        formatDate(log.timestamp),
        log.event_type || 'N/A',
        log.source_ip || 'N/A',
        log.country || 'N/A',
        log.severity || 'INFO',
        log.description || log.message || ''
    ]);
    doc.autoTable({
        head: [columns],
        body: data,
        theme: 'grid',
        styles: { fontSize: 8, cellPadding: 2 },
        columnStyles: { 5: { cellWidth: 50 } } // Wider description
    });
    doc.save('search_results.pdf');
}