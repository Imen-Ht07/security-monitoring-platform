// /static/js/upload.js
// Upload page functionality

let selectedFile = null;

document.addEventListener('DOMContentLoaded', async () => {
    setupDragAndDrop();
    await loadUploads();
});

function setupDragAndDrop() {
    const dropZone = document.getElementById('dropZone');
    if (!dropZone) return;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('drag-over');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('drag-over');
        });
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files[0]);
    });

    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            handleFiles(e.target.files[0]);
        });
    }
}

function handleFiles(file) {
    if (!file) return;

    // Validate file
    const ext = file.name.split('.').pop().toLowerCase();
    if (!CONFIG.SUPPORTED_FORMATS.includes(ext)) {
        showError(`Invalid file format. Supported: ${CONFIG.SUPPORTED_FORMATS.join(', ')}`);
        return;
    }

    if (file.size > CONFIG.MAX_FILE_SIZE) {
        showError(`File too large. Max: ${formatBytes(CONFIG.MAX_FILE_SIZE)}`);
        return;
    }

    selectedFile = file;
    displayFilePreview(file);
    showElement('uploadForm');
}

function displayFilePreview(file) {
    const preview = document.getElementById('filePreview');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const fileType = document.getElementById('fileType');

    if (preview && fileName && fileSize && fileType) {
        fileName.textContent = file.name;
        fileSize.textContent = formatBytes(file.size);
        fileType.textContent = file.type || 'Unknown';
        showElement('filePreview');
    }
}

function clearFile() {
    selectedFile = null;
    hideElement('filePreview');
    hideElement('uploadForm');
    const fileInput = document.getElementById('fileInput');
    if (fileInput) fileInput.value = '';
}

async function uploadFile() {
    if (!selectedFile) {
        showError('No file selected');
        return;
    }

    const description = document.getElementById('description')?.value || '';
    
    disableButton('uploadBtn');
    showElement('progressContainer');

    try {
        const progressContainer = document.getElementById('progressContainer');
        if (progressContainer) {
            progressContainer.style.display = 'block';
        }

        const result = await uploadLogFile(selectedFile, description);
        
        showSuccess(`✅ File uploaded successfully! ${result.records_count || 0} records indexed.`);
        clearFile();
        await loadUploads();
    } catch (error) {
        showError(`Upload failed: ${error.message}`);
    } finally {
        enableButton('uploadBtn');
        hideElement('progressContainer');
    }
}

async function loadUploads() {
    const loadingDiv = document.getElementById('uploadsLoading');
    const tableDiv = document.getElementById('uploadsTable');
    const emptyDiv = document.getElementById('uploadsEmpty');

    if (loadingDiv) showElement('uploadsLoading');
    if (tableDiv) hideElement('uploadsTable');
    if (emptyDiv) hideElement('uploadsEmpty');

    try {
        const data = await getUploadHistory();
        
        if (loadingDiv) hideElement('uploadsLoading');

        if (!data.uploads || data.uploads.length === 0) {
            if (emptyDiv) showElement('uploadsEmpty');
            return;
        }

        displayUploads(data.uploads);
        if (tableDiv) showElement('uploadsTable');
    } catch (error) {
        console.error('Error loading uploads:', error);
        if (loadingDiv) hideElement('uploadsLoading');
        showError('Failed to load upload history');
    }
}

function displayUploads(uploads) {
    const tbody = document.getElementById('uploadsBody');
    if (!tbody) return;

    tbody.innerHTML = '';

    uploads.forEach(upload => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${upload.filename || 'N/A'}</td>
            <td>${upload.file_type || 'N/A'}</td>
            <td>${formatBytes(upload.file_size || 0)}</td>
            <td>${upload.records_count || 0}</td>
            <td>${upload.indexed_count || 0}</td>
            <td>${formatDate(upload.timestamp)}</td>
            <td>${truncate(upload.description || '', 30)}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="viewDetails('${upload.id}')">
                    <i class="fas fa-eye"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function viewDetails(uploadId) {
    // Show modal with details
    showModal('fileDetailsModal');
    // Fetch and display details
    // ... implementation
}
