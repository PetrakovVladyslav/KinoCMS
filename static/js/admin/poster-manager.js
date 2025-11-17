// Poster Manager Component
class PosterManager {
    constructor(options = {}) {
        this.posterInputSelector = options.posterInputSelector || 'input[type="file"][name="poster"]';
        this.init();
    }

    init() {
        this.setupPosterPreview();
        this.setupExistingPosterDelete();
    }

    setupPosterPreview() {
        const posterInput = document.querySelector(this.posterInputSelector);
        if (!posterInput) return;

        posterInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    this.displayPosterPreview(event.target.result, file.name, posterInput);
                };
                reader.readAsDataURL(file);
            }
        });
    }

    displayPosterPreview(imageSrc, fileName, posterInput) {
        let previewContainer = document.querySelector('.current-logo-preview');
        const posterUploadContainer = document.querySelector('.logo-upload-container');

        if (!previewContainer) {
            previewContainer = document.createElement('div');
            previewContainer.className = 'current-logo-preview mt-3';
            posterUploadContainer.appendChild(previewContainer);
        }

        previewContainer.innerHTML = `
            <label class="form-label">Новый постер:</label>
            <div class="logo-preview-wrapper">
                <img src="${imageSrc}" alt="Новый постер" class="logo-preview">
                <button type="button" class="btn btn-sm btn-danger delete-logo">
                    <i class="fas fa-times"></i>
                </button>
                <div class="logo-overlay">
                    <small class="text-white">${fileName}</small>
                </div>
            </div>
        `;

        // Add delete functionality
        this.attachDeleteHandler(previewContainer, posterInput);
    }

    setupExistingPosterDelete() {
        const existingPosterPreview = document.querySelector('.current-logo-preview');
        if (!existingPosterPreview) return;

        const posterInput = document.querySelector(this.posterInputSelector);
        this.attachDeleteHandler(existingPosterPreview, posterInput);
    }

    attachDeleteHandler(previewContainer, posterInput) {
        const deleteBtn = previewContainer.querySelector('.delete-logo');
        if (deleteBtn && !deleteBtn.dataset.listenerAttached) {
            deleteBtn.dataset.listenerAttached = 'true';
            deleteBtn.addEventListener('click', () => {
                previewContainer.remove();
                if (posterInput) posterInput.value = '';
            });
        }
    }
}

// Make available globally
window.PosterManager = PosterManager;