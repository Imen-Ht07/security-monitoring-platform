let currentPage = 1;
let currentResults = [];
let currentFilters = {};
let chart = null;

document.addEventListener('DOMContentLoaded', async () => {
    // Suppression du paramétrage automatique des dates pour éviter de filtrer inutilement
    // Les inputs restent vides par défaut (envoyant null au backend)
    await loadStats();
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
            return;
        }

        if (Array.isArray(response.logs) && response.logs.length > 0) {
            currentResults = response.logs;
            displayResults(currentResults);
        } else {
            showNoResults();
        }

        updateResultCount(response.total || 0);
        updatePagination(response.total || 0);

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
        page: currentPage - 1,        // ✅ IMPORTANT
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