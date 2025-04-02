document.addEventListener('DOMContentLoaded', function() {
    // Form submission handlers
    setupExcelForm();
    setupUrlForm();
    setupVcardForm();
    setupImageForm();
    
    // Tab change handler to reset forms
    const tabs = document.querySelectorAll('button[data-bs-toggle="tab"]');
    tabs.forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(event) {
            resetForms();
            hideResultsSection();
        });
    });
    
    // Handle hash in URL for direct tab access
    const hash = window.location.hash;
    if (hash) {
        const tabId = hash.replace('#', '') + '-tab';
        const tab = document.getElementById(tabId);
        if (tab) {
            const bsTab = new bootstrap.Tab(tab);
            bsTab.show();
        }
    }
});

function setupExcelForm() {
    const form = document.getElementById('excelForm');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validate form
        const fileInput = document.getElementById('file');
        if (!fileInput.files.length) {
            showError('Please select a file to upload.');
            return;
        }
        
        // Show loading overlay
        showLoading();
        
        // Submit form data
        const formData = new FormData(form);
        
        fetch('/generate', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            
            if (data.error) {
                showError(data.error);
                return;
            }
            
            // Prepare download links based on download type
            const downloadLinks = [];
            
            if (data.pdf_url) {
                downloadLinks.push({
                    url: data.pdf_url,
                    label: 'Download PDF'
                });
            }
            
            if (data.zip_url) {
                downloadLinks.push({
                    url: data.zip_url,
                    label: 'Download ZIP'
                });
            }
            
            // Show results with download links
            showResults({
                message: data.message,
                download_links: downloadLinks,
                stats: data.stats
            });
        })
        .catch(error => {
            hideLoading();
            showError('An error occurred while generating QR codes. Please try again.');
            console.error('Error:', error);
        });
    });
}


function setupUrlForm() {
    const form = document.getElementById('urlForm');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validate form
        const urlInput = document.getElementById('url');
        if (!urlInput.value.trim()) {
            showError('Please enter a URL.');
            return;
        }
        
        // Show loading overlay
        showLoading();
        
        // Submit form data
        const formData = new FormData(form);
        
        fetch('/generate', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            
            if (data.error) {
                showError(data.error);
                return;
            }
            
            // Update preview
            const previewDiv = document.getElementById('urlPreview');
            previewDiv.innerHTML = `<img src="${data.preview}" class="img-fluid" alt="URL QR Code">`;
            
            // Show download button
            const downloadDiv = document.getElementById('urlDownload');
            downloadDiv.style.display = 'block';
            
            const downloadBtn = document.getElementById('urlDownloadBtn');
            downloadBtn.href = data.download_url;
            // Show success message
            showResults({
                message: data.message,
                download_links: [
                    { url: data.download_url, label: 'Download QR Code' }
                ]
            });
        })
        .catch(error => {
            hideLoading();
            showError('An error occurred while generating the QR code. Please try again.');
            console.error('Error:', error);
        });
    });
}

function setupVcardForm() {
    const form = document.getElementById('vcardForm');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validate form - at least one of name, email, or phone should be provided
        const nameInput = document.getElementById('name');
        const emailInput = document.getElementById('email');
        const phoneInput = document.getElementById('phone');
        
        if (!nameInput.value.trim() && !emailInput.value.trim() && !phoneInput.value.trim()) {
            showError('Please provide at least a name, email, or phone number.');
            return;
        }
        
        // Show loading overlay
        showLoading();
        
        // Submit form data
        const formData = new FormData(form);
        
        fetch('/generate', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            
            if (data.error) {
                showError(data.error);
                return;
            }
            
            // Update preview
            const previewDiv = document.getElementById('vcardPreview');
            previewDiv.innerHTML = `<img src="${data.preview}" class="img-fluid" alt="vCard QR Code">`;
            
            // Show download button
            const downloadDiv = document.getElementById('vcardDownload');
            downloadDiv.style.display = 'block';
            
            const downloadBtn = document.getElementById('vcardDownloadBtn');
            downloadBtn.href = data.download_url;
            
            // Show success message
            showResults({
                message: data.message,
                download_links: [
                    { url: data.download_url, label: 'Download vCard QR Code' }
                ]
            });
        })
        .catch(error => {
            hideLoading();
            showError('An error occurred while generating the vCard QR code. Please try again.');
            console.error('Error:', error);
        });
    });
}

function setupImageForm() {
    const form = document.getElementById('imageForm');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validate form
        const dataInput = document.getElementById('qr_data');
        const fileInput = document.getElementById('image_file');
        
        if (!dataInput.value.trim()) {
            showError('Please enter content for the QR code.');
            return;
        }
        
        if (!fileInput.files.length) {
            showError('Please select an image to upload.');
            return;
        }
        
        // Show loading overlay
        showLoading();
        
        // Submit form data
        const formData = new FormData(form);
        
        fetch('/generate', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            
            if (data.error) {
                showError(data.error);
                return;
            }
            
            // Update preview
            const previewDiv = document.getElementById('imagePreview');
            previewDiv.innerHTML = `<img src="${data.preview}" class="img-fluid" alt="Image QR Code">`;
            
            // Show download button
            const downloadDiv = document.getElementById('imageDownload');
            downloadDiv.style.display = 'block';
            
            const downloadBtn = document.getElementById('imageDownloadBtn');
            downloadBtn.href = data.download_url;
            
            // Show success message
            showResults({
                message: data.message,
                download_links: [
                    { url: data.download_url, label: 'Download Image QR Code' }
                ]
            });
        })
        .catch(error => {
            hideLoading();
            showError('An error occurred while generating the image QR code. Please try again.');
            console.error('Error:', error);
        });
    });
}

function showLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    loadingOverlay.style.display = 'flex';
}

function hideLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    loadingOverlay.style.display = 'none';
}

function showError(message) {
    const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
    const errorModalBody = document.getElementById('errorModalBody');
    errorModalBody.textContent = message;
    errorModal.show();
}

function showResults(data) {
    const resultsSection = document.getElementById('resultsSection');
    const resultsMessage = document.getElementById('resultsMessage');
    const downloadLinks = document.getElementById('downloadLinks');
    const statsInfo = document.getElementById('statsInfo');
    
    // Update message
    resultsMessage.textContent = data.message || 'QR codes generated successfully!';
    
    // Clear previous download links
    downloadLinks.innerHTML = '';
    
    // Add download links
    if (data.download_links && data.download_links.length > 0) {
        data.download_links.forEach(link => {
            const btn = document.createElement('a');
            btn.href = link.url;
            btn.className = 'btn btn-success';
            btn.innerHTML = `<i class="bi bi-download"></i> ${link.label}`;
            downloadLinks.appendChild(btn);
        });
    }
    
    // Add stats if available
    statsInfo.innerHTML = '';
    if (data.stats) {
        const statsList = document.createElement('ul');
        statsList.className = 'list-group';
        
        for (const [key, value] of Object.entries(data.stats)) {
            const item = document.createElement('li');
            item.className = 'list-group-item d-flex justify-content-between align-items-center';
            
            // Format the key for display (convert snake_case to Title Case)
            const formattedKey = key
                .split('_')
                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                .join(' ');
            
            item.innerHTML = `
                <span>${formattedKey}</span>
                <span class="badge bg-primary rounded-pill">${value}</span>
            `;
            statsList.appendChild(item);
        }
        
        statsInfo.appendChild(statsList);
    }
    
    // Show the results section
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function hideResultsSection() {
    const resultsSection = document.getElementById('resultsSection');
    resultsSection.style.display = 'none';
}

function resetForms() {
    // Reset all forms
    document.getElementById('excelForm')?.reset();
    document.getElementById('urlForm')?.reset();
    document.getElementById('vcardForm')?.reset();
    document.getElementById('imageForm')?.reset();
    
    // Reset previews
    document.getElementById('urlPreview').innerHTML = '<img src="/static/img/url-qr-placeholder.png" class="img-fluid" alt="URL QR Code Preview">';
    document.getElementById('vcardPreview').innerHTML = '<img src="/static/img/vcard-qr-placeholder.png" class="img-fluid" alt="vCard QR Code Preview">';
    document.getElementById('imagePreview').innerHTML = '<img src="/static/img/image-qr-placeholder.png" class="img-fluid" alt="Image QR Code Preview">';
    
    // Hide download buttons
    document.getElementById('urlDownload').style.display = 'none';
    document.getElementById('vcardDownload').style.display = 'none';
    document.getElementById('imageDownload').style.display = 'none';
}
