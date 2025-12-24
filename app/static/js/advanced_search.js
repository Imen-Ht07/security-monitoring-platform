let currentPage = 1;
let currentResults = [];
let currentFilters = {};
let chart = null;

document.addEventListener('DOMContentLoaded', async () => {
    const today = new Date().toISOString().split('T')[0];
    const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];

    const dateFromInput = document.getElementById('dateFrom');
    const dateToInput = document.getElementById('dateTo');

    if (dateFromInput) dateFromInput.value = yesterday;
    if (dateToInput) dateToInput.value = today;

    await loadStats();
});

/* =======================
   SEARCH
======================= */
async function performSearch() {
    currentPage = currentPage || 1;
    const filters = buildFilters();
    currentFilters = filters;

    showElement('loading');

    try {
        const response = await advancedSearch(filters);

        console.log("Advanced search response:", response); // DEBUG

        hideElement('loading');

        if (response && Array.isArray(response.logs) && response.logs.length > 0) {
            currentResults = response.logs;
            displayResults(currentResults);
            updateResultCount(response.total || response.logs.length);
            updatePagination(response.total || 0);
        } else {
            showNoResults();
            updateResultCount(0);
            updatePagination(0);
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
    return {
        query: document.getElementById('queryText')?.value || '*',
        filters: {
            date_from: document.getElementById('dateFrom')?.value || null,
            date_to: document.getElementById('dateTo')?.value || null,
            severity: Array.from(document.getElementById('severity')?.selectedOptions || []).map(o => o.value),
            event_type: Array.from(document.getElementById('eventType')?.selectedOptions || []).map(o => o.value),
            country: Array.from(document.getElementById('country')?.selectedOptions || []).map(o => o.value),
            source_ip: document.getElementById('sourceIp')?.value || null,
            username: document.getElementById('username')?.value || null
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
            <td>${log.username || 'N/A'}</td>
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
                <td colspan="7" class="text-center text-muted py-4">
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
    ['queryText', 'sourceIp', 'username'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });

    ['severity', 'eventType', 'country'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.selectedIndex = -1;
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
