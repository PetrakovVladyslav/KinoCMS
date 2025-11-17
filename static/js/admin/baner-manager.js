// Banner Manager Component
class BannerManager {
    constructor(options = {}) {
        this.bannerInputSelector = options.bannerInputSelector || 'input[type="file"][name="banner"]';
        this.init();
    }

    init() {
        this.setupBannerPreview();
        this.setupExistingBannerDelete();
    }

    setupBannerPreview() {
        const bannerInput = document.querySelector(this.bannerInputSelector);
        if (!bannerInput) return;

        bannerInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    this.displayBannerPreview(event.target.result, file.name, bannerInput);
                };
                reader.readAsDataURL(file);
            }
        });
    }

    displayBannerPreview(imageSrc, fileName, bannerInput) {
        let previewContainer = document.querySelector('.current-banner-preview');
        const bannerUploadContainer = document.querySelector('.banner-upload-container');

        if (!previewContainer) {
            previewContainer = document.createElement('div');
            previewContainer.className = 'current-banner-preview mt-3';
            bannerUploadContainer.appendChild(previewContainer);
        }

        previewContainer.innerHTML = `
            <label class="form-label">Новый баннер:</label>
            <div class="banner-preview-wrapper">
                <img src="${imageSrc}" alt="Новый баннер" class="banner-preview">
                <button type="button" class="btn btn-sm btn-danger delete-banner">
                    <i class="fas fa-times"></i>
                </button>
                <div class="banner-overlay">
                    <small class="text-white">${fileName}</small>
                </div>
            </div>
        `;

        // Add delete functionality
        this.attachDeleteHandler(previewContainer, bannerInput);
    }

    setupExistingBannerDelete() {
        const existingBannerPreview = document.querySelector('.current-banner-preview');
        if (!existingBannerPreview) return;

        const bannerInput = document.querySelector(this.bannerInputSelector);
        this.attachDeleteHandler(existingBannerPreview, bannerInput);
    }

    attachDeleteHandler(previewContainer, bannerInput) {
        const deleteBtn = previewContainer.querySelector('.delete-banner');
        if (deleteBtn && !deleteBtn.dataset.listenerAttached) {
            deleteBtn.dataset.listenerAttached = 'true';
            deleteBtn.addEventListener('click', () => {
                previewContainer.remove();
                if (bannerInput) bannerInput.value = '';
            });
        }
    }
}

// Make available globally
window.BannerManager = BannerManager;