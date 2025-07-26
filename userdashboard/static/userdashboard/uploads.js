function setupDropArea(dropAreaId, fileInputId) {
    const dropArea = document.getElementById(dropAreaId);
    const fileInput = document.getElementById(fileInputId);
    if (!dropArea || !fileInput) return;

    // Click to upload
    dropArea.addEventListener('click', function(e) {
        if (e.target.classList.contains('drop-click') || e.target.classList.contains('drop-area') || e.target.classList.contains('drop-text')) {
            fileInput.click();
        }
    });

    // Drag and drop
    dropArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        dropArea.classList.add('dragover');
    });
    dropArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        dropArea.classList.remove('dragover');
    });
    dropArea.addEventListener('drop', function(e) {
        e.preventDefault();
        dropArea.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            fileInput.dispatchEvent(new Event('change'));
        }
    });

    // Show selected file name
    fileInput.addEventListener('change', function() {
        let label = dropArea.querySelector('.file-selected');
        if (!label) {
            label = document.createElement('div');
            label.className = 'file-selected';
            dropArea.appendChild(label);
        }
        label.textContent = fileInput.files.length ? fileInput.files[0].name : '';
    });
}

setupDropArea('kmlDropArea', 'kmlFile');
setupDropArea('csvDropArea', 'csvFile');
setupDropArea('shpDropArea', 'shpFile');

document.querySelectorAll('.upload-card form').forEach(form => {
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        alert('File upload functionality coming soon!');
    });
}); 