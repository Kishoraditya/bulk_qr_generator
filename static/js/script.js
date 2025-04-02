document.addEventListener('DOMContentLoaded', function() {
    const qrForm = document.getElementById('qrForm');
    const generateBtn = document.getElementById('generateBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const resultsCard = document.getElementById('resultsCard');
    const errorCard = document.getElementById('errorCard');
    const errorMessage = document.getElementById('errorMessage');
    const resultStats = document.getElementById('resultStats');
    const downloadLinks = document.getElementById('downloadLinks');
    
    qrForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Hide previous results/errors
        resultsCard.style.display = 'none';
        errorCard.style.display = 'none';
        
        // Show loading spinner
        loadingSpinner.style.display = 'block';
        generateBtn.disabled = true;
        
        // Get form data
        const formData = new FormData(qrForm);
        
        // Handle checkbox values
        formData.set('include_text', document.getElementById('include_text').checked ? 'true' : 'false');
        formData.set('include_page_numbers', document.getElementById('include_page_numbers').checked ? 'true' : 'false');
        
        // Send request to server
        fetch('/generate', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading spinner
            loadingSpinner.style.display = 'none';
            generateBtn.disabled = false;
            
            if (data.error) {
                // Show error
                errorMessage.textContent = data.error;
                errorCard.style.display = 'block';
            } else {
                // Show success and download links
                displayResults(data);
                resultsCard.style.display = 'block';
                
                // Scroll to results
                resultsCard.scrollIntoView({ behavior: 'smooth' });
            }
        })
        .catch(error => {
            // Hide loading spinner
            loadingSpinner.style.display = 'none';
            generateBtn.disabled = false;
            
            // Show error
            errorMessage.textContent = 'An error occurred while processing your request. Please try again.';
            errorCard.style.display = 'block';
            console.error('Error:', error);
        });
    });
    
    function displayResults(data) {
        // Display statistics
        let statsHtml = '<div class="alert alert-info">';
        statsHtml += `<p class="stats-item"><strong>Total QR Codes:</strong> ${data.stats.total_qr_codes}</p>`;
        
        if (data.stats.qr_per_page) {
            statsHtml += `<p class="stats-item"><strong>QR Codes per Page:</strong> ${data.stats.qr_per_page}</p>`;
            statsHtml += `<p class="stats-item"><strong>Total Pages:</strong> ${data.stats.total_pages}</p>`;
        }
        
        statsHtml += '</div>';
        resultStats.innerHTML = statsHtml;
        
        // Display download links
        let linksHtml = '';
        
        if (data.download_urls.pdf) {
            linksHtml += `<a href="${data.download_urls.pdf}" class="btn btn-success download-btn">
                            <i class="bi bi-file-pdf"></i> Download PDF
                          </a>`;
        }
        
        if (data.download_urls.zip) {
            linksHtml += `<a href="${data.download_urls.zip}" class="btn btn-primary download-btn">
                            <i class="bi bi-file-zip"></i> Download ZIP (Individual QR Codes)
                          </a>`;
        }
        
        downloadLinks.innerHTML = linksHtml;
    }
    
    // Form validation and preview functionality
    const qrSizeInput = document.getElementById('qr_size');
    qrSizeInput.addEventListener('change', function() {
        if (parseInt(this.value) < 50) {
            this.value = 50;
            alert('QR code size must be at least 50px for reliable scanning.');
        }
    });
});
