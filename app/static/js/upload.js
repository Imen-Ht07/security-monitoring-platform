// frontend/js/upload.js
const API_BASE = '/api/upload';
let selectedFile = null;

// Initialisation au chargement
document.addEventListener('DOMContentLoaded', () => {
    setupDragAndDrop();
    loadUploads();
});

// ===== DRAG & DROP =====
function setupDragAndDrop() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    
    // Click to select file
    dropZone.addEventListener('click', () => fileInput.click());
    
    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            selectFile(e.target.files[0]);
        }
    });
    
    // Drag over
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });
    
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });
    
    // Drop
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        
        if (e.dataTransfer.files.length > 0) {
            selectFile(e.dataTransfer.files[0]);
        }
    });
}

function selectFile(file) {
    selectedFile = file;
    
    // Valider
    const ext = file.name.split('.').pop().toLowerCase();
    if (!['csv', 'json'].includes(ext)) {
        showError('Invalid file type. Only CSV and JSON are allowed.');
        selectedFile = null;
        return;
    }
    
    if (file.size > 50 * 1024 * 1024) {
        showError('File too large. Maximum 50MB allowed.');
        selectedFile = null;
        return;
    }
    
    // Afficher le preview
    const preview = document.getElementById('filePreview');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const fileType = document.getElementById('fileType');
    
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    fileType.textContent = ext.toUpperCase() + ' File';
    
    preview.style.display = 'block';
    preview.classList.remove('error');
    preview.classList.add('selected');
    
    // Afficher le form
    document.getElementById('uploadForm').style.display = 'block';
    document.getElementById('uploadStatus').style.display = 'none';
    
    // Reset description
    document.getElementById('description').value = '';
}

function clearFile() {
    selectedFile = null;
    document.getElementById('fileInput').value = '';
    document.getElementById('filePreview').style.display = 'none';
    document.getElementById('uploadForm').style.display = 'none';
    document.getElementById('progressContainer').style.display = 'none';
    document.getElementById('uploadStatus').style.display = 'none';
}

// ===== UPLOAD =====
async function uploadFile() {
    if (!selectedFile) {
        showError('No file selected');
        return;
    }
    
    const uploadBtn = document.getElementById('uploadBtn');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const uploadStatus = document.getElementById('uploadStatus');
    
    uploadBtn.disabled = true;
    progressContainer.style.display = 'block';
    
    try {
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('description', document.getElementById('description').value);
        
        // Utiliser XMLHttpRequest pour le progress
        const xhr = new XMLHttpRequest();
        
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percentComplete = Math.round((e.loaded / e.total) * 100);
                progressBar.style.width = percentComplete + '%';
                progressText.textContent = percentComplete + '%';
            }
        });
        
        xhr.addEventListener('load', () => {
            if (xhr.status === 201 || xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                
                uploadStatus.className = 'alert alert-success';
                uploadStatus.innerHTML = `
                    <i class="fas fa-check-circle"></i> <strong>Upload successful!</strong><br>
                    Uploaded: <strong>${response.filename}</strong><br>
                    Documents: <strong>${response.documents_count}</strong><br>
                    Indexed: <strong>${response.indexed_count}</strong>
                `;
                uploadStatus.style.display = 'block';
                
                // Reset après 2s
                setTimeout(() => {
                    clearFile();
                    loadUploads();
                }, 2000);
            } else {
                const response = JSON.parse(xhr.responseText);
                showErrorInForm(response.error || 'Upload failed');
                uploadBtn.disabled = false;
            }
        });
        
        xhr.addEventListener('error', () => {
            showErrorInForm('Network error during upload');
            uploadBtn.disabled = false;
        });
        
        xhr.open('POST', API_BASE);
        xhr.send(formData);
        
    } catch (error) {
        showErrorInForm(error.message);
        uploadBtn.disabled = false;
    }
}

// ===== UPLOAD HISTORY =====
async function loadUploads() {
    try {
        const response = await fetch(`${API_BASE}/history`);
        const data = await response.json();
        
        document.getElementById('uploadsLoading').style.display = 'none';
        
        if (!data.success || data.count === 0) {
            document.getElementById('uploadsEmpty').style.display = 'block';
            document.getElementById('uploadsTable').style.display = 'none';
            return;
        }
        
        const tbody = document.getElementById('uploadsBody');
        tbody.innerHTML = '';
        
        data.data.forEach(upload => {
            const row = document.createElement('tr');
            const uploadedDate = new Date(upload.uploaded_at).toLocaleString();
            
            const successRate = upload.document_count > 0 
                ? Math.round((upload.indexed_count / upload.document_count) * 100) 
                : 0;
            
            const statusClass = successRate === 100 ? 'status-success' : 
                               successRate > 0 ? 'status-pending' : 'status-error';
            
            row.innerHTML = `
                <td>
                    <strong>${upload.original_name}</strong>
                    <small class="d-block text-muted">${upload.filename}</small>
                </td>
                <td><code>${upload.file_type.toUpperCase()}</code></td>
                <td>${formatFileSize(upload.file_size)}</td>
                <td>${upload.document_count}</td>
                <td>
                    <span class="status-badge ${statusClass}">
                        ${upload.indexed_count}/${upload.document_count} (${successRate}%)
                    </span>
                </td>
                <td><small>${uploadedDate}</small></td>
                <td>
                    <small>${upload.description ? upload.description.substring(0, 30) + '...' : 'N/A'}</small>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-light action-btn" onclick="showUploadDetails('${upload.id}')">
                        <i class="fas fa-info-circle"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger action-btn" onclick="deleteUpload('${upload.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
        
        document.getElementById('uploadsTable').style.display = 'table';
        document.getElementById('uploadsEmpty').style.display = 'none';
        
    } catch (error) {
        console.error('Load uploads error:', error);
        document.getElementById('uploadsLoading').innerHTML = '<p class="text-danger">Failed to load uploads</p>';
    }
}

async function showUploadDetails(uploadId) {
    try {
        const response = await fetch(`${API_BASE}/${uploadId}`);
        const data = await response.json();
        
        if (!data.success) {
            alert('Failed to load upload details');
            return;
        }
        
        const upload = data.data;
        const uploadedDate = new Date(upload.uploaded_at).toLocaleString();
        const successRate = upload.document_count > 0 
            ? Math.round((upload.indexed_count / upload.document_count) * 100) 
            : 0;
        
        const content = `
            <div class="mb-3">
                <h6 class="text-muted">Filename</h6>
                <p>${upload.original_name}</p>
            </div>
            <div class="mb-3">
                <h6 class="text-muted">File Size</h6>
                <p>${formatFileSize(upload.file_size)}</p>
            </div>
            <div class="mb-3">
                <h6 class="text-muted">Type</h6>
                <p><code>${upload.file_type.toUpperCase()}</code></p>
            </div>
            <div class="mb-3">
                <h6 class="text-muted">Uploaded At</h6>
                <p>${uploadedDate}</p>
            </div>
            <div class="mb-3">
                <h6 class="text-muted">Documents</h6>
                <p>${upload.document_count} total</p>
            </div>
            <div class="mb-3">
                <h6 class="text-muted">Indexed</h6>
                <p>${upload.indexed_count}/${upload.document_count} (${successRate}%)</p>
            </div>
            <div class="mb-3">
                <h6 class="text-muted">Description</h6>
                <p>${upload.description || 'N/A'}</p>
            </div>
        `;
        
        document.getElementById('fileDetailsContent').innerHTML = content;
        
        const modal = new bootstrap.Modal(document.getElementById('fileDetailsModal'));
        modal.show();
        
    } catch (error) {
        console.error('Show details error:', error);
        alert('Failed to load upload details');
    }
}

async function deleteUpload(uploadId) {
    if (!confirm('Delete this upload? Documents will NOT be removed from the index.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/${uploadId}`, { method: 'DELETE' });
        const data = await response.json();
        
        if (data.success) {
            alert('Upload deleted');
            loadUploads();
        } else {
            alert('Failed to delete upload');
        }
    } catch (error) {
        console.error('Delete upload error:', error);
        alert('Error deleting upload');
    }
}

// ===== UTILITIES =====
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function showError(message) {
    const preview = document.getElementById('filePreview');
    preview.style.display = 'block';
    preview.classList.add('error');
    preview.classList.remove('selected');
    preview.innerHTML = `
        <div style="color: var(--danger);">
            <i class="fas fa-exclamation-circle"></i> ${message}
        </div>
    `;
}

function showErrorInForm(message) {
    const uploadStatus = document.getElementById('uploadStatus');
    uploadStatus.className = 'alert alert-danger';
    uploadStatus.innerHTML = `<i class="fas fa-times-circle"></i> ${message}`;
    uploadStatus.style.display = 'block';
    document.getElementById('progressContainer').style.display = 'none';
}
