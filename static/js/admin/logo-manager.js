// Logo Manager Component (для работы с логотипами/иконками)
class LogoManager {
    constructor(options = {}) {
        this.logoInputSelector = options.logoInputSelector || 'input[type="file"][name$="logo"]';
        this.init();
    }

    init() {
        this.setupLogoPreview();
        this.setupExistingLogoDelete();
    }

    setupLogoPreview() {
        const logoInput = document.querySelector(this.logoInputSelector);
        if (!logoInput) return;

        logoInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    this.displayLogoPreview(event.target.result, file.name, logoInput);
                };
                reader.readAsDataURL(file);
            }
        });
    }

    displayLogoPreview(imageSrc, fileName, logoInput) {
        let previewContainer = document.querySelector('.current-logo-preview');
        const logoUploadContainer = document.querySelector('.logo-upload-container');

        if (!previewContainer) {
            previewContainer = document.createElement('div');
            previewContainer.className = 'current-logo-preview mt-3';
            logoUploadContainer.appendChild(previewContainer);
        }

        previewContainer.innerHTML = `
            <label class="form-label">Новый логотип:</label>
            <div class="logo-preview-wrapper">
                <img src="${imageSrc}" alt="Новый логотип" class="logo-preview">
                <button type="button" class="btn btn-sm btn-danger delete-logo">
                    <i class="fas fa-times"></i>
                </button>
                <div class="logo-overlay">
                    <small class="text-white">${fileName}</small>
                </div>
            </div>
        `;

        // Add delete functionality
        this.attachDeleteHandler(previewContainer, logoInput);
    }

    setupExistingLogoDelete() {
        const existingLogoPreview = document.querySelector('.current-logo-preview');
        if (!existingLogoPreview) return;

        const logoInput = document.querySelector(this.logoInputSelector);
        this.attachDeleteHandler(existingLogoPreview, logoInput);
    }

    attachDeleteHandler(previewContainer, logoInput) {
        const deleteBtn = previewContainer.querySelector('.delete-logo');
        if (deleteBtn && !deleteBtn.dataset.listenerAttached) {
            deleteBtn.dataset.listenerAttached = 'true';
            deleteBtn.addEventListener('click', () => {
                previewContainer.remove();
                if (logoInput) logoInput.value = '';
            });
        }
    }
}

// Make available globally
window.LogoManager = LogoManager;