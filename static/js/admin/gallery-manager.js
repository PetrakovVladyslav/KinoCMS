// Gallery Manager Component
class GalleryManager {
    constructor(options = {}) {
        this.formsetPrefix = options.formsetPrefix || 'images';
        this.maxImages = options.maxImages || 10;
        this.validator = null;
        this.form = null;
        this.init();
    }

    init() {
        this.setupValidator();
        this.setupGalleryImages();
        this.setupAddImageButton();
        this.setupFormValidation();
    }

    setupValidator() {
        // Создаем скрытое поле для HTML5 валидации, если его нет
        this.validator = document.getElementById('gallery-validator');
        if (!this.validator) {
            this.validator = document.createElement('input');
            this.validator.type = 'hidden';
            this.validator.id = 'gallery-validator';
            this.validator.required = true;

            const galleryContainer = document.querySelector('.gallery-container');
            if (galleryContainer) {
                galleryContainer.parentNode.insertBefore(this.validator, galleryContainer);
            }
        }

        this.form = document.querySelector('form');
    }

    setupFormValidation() {
        if (!this.form || !this.validator) return;

        // Проверяем при загрузке страницы (для режима редактирования)
        if (this.hasImages()) {
            this.validator.removeAttribute('required');
        }

        // Валидация при отправке формы
        this.form.addEventListener('submit', (e) => {
            if (!this.validateGallery(e)) {
                e.preventDefault();
            }
        });
    }

    validateGallery(e) {
        const hasImages = this.hasImages();

        if (hasImages) {
            this.validator.removeAttribute('required');
            this.validator.setCustomValidity('');
            return true;
        } else {
            this.validator.setAttribute('required', '');
            this.validator.setCustomValidity('Загрузите хотя бы одно изображение в галерею');

            // Показываем браузерное сообщение
            if (!this.validator.reportValidity()) {
                // Скроллим к галерее
                const gallerySection = document.querySelector('.gallery-container');
                if (gallerySection) {
                    gallerySection.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
                return false;
            }
        }
        return true;
    }

    hasImages() {
        const galleryItems = document.querySelectorAll('.gallery-item');
        let hasImage = false;

        galleryItems.forEach((item) => {
            // Пропускаем скрытые элементы
            if (item.style.display === 'none') return;

            const deleteCheckbox = item.querySelector('input[name$="-DELETE"]');
            const isMarkedForDeletion = deleteCheckbox && deleteCheckbox.checked;

            if (!isMarkedForDeletion) {
                // Проверяем есть ли превью (существующее изображение)
                const imagePreview = item.querySelector('.gallery-image-preview');
                // Или новый файл
                const fileInput = item.querySelector('input[type="file"]');
                const hasNewFile = fileInput && fileInput.files && fileInput.files.length > 0;

                if (imagePreview || hasNewFile) {
                    hasImage = true;
                }
            }
        });

        return hasImage;
    }

    setupGalleryImages() {
        // Handle image upload preview
        document.querySelectorAll('.gallery-item input[type="file"]').forEach(input => {
            input.addEventListener('change', (e) => {
                const galleryItem = e.target.closest('.gallery-item');
                this.handleImagePreview(e, galleryItem);
                // Обновляем валидацию после загрузки файла
                this.updateValidation();
            });
        });

        // Handle click on empty placeholder
        document.querySelectorAll('.empty-image-placeholder').forEach(placeholder => {
            placeholder.addEventListener('click', function() {
                const fileInput = this.closest('.gallery-item').querySelector('input[type="file"]');
                if (fileInput) fileInput.click();
            });
        });

        // Handle delete buttons for existing images
        document.querySelectorAll('.delete-image').forEach(button => {
            button.addEventListener('click', () => {
                const galleryItem = button.closest('.gallery-item');
                this.markForDeletion(galleryItem);
                // Обновляем валидацию после удаления
                this.updateValidation();
            });
        });
    }

    updateValidation() {
        if (!this.validator) return;

        if (this.hasImages()) {
            this.validator.removeAttribute('required');
            this.validator.setCustomValidity('');
        } else {
            this.validator.setAttribute('required', '');
        }
    }

    handleImagePreview(e, galleryItem) {
        const file = e.target.files[0];
        if (!file || !file.type.startsWith('image/')) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            const placeholder = galleryItem.querySelector('.empty-image-placeholder');
            let previewContainer = galleryItem.querySelector('.image-preview-container');

            // Hide placeholder
            if (placeholder) placeholder.style.display = 'none';

            // Create or get preview container
            if (!previewContainer) {
                previewContainer = this.createPreviewContainer(e.target, placeholder, galleryItem);
                const itemContent = galleryItem.querySelector('.gallery-item-content');
                itemContent.insertBefore(previewContainer, itemContent.firstChild);
            }

            // Update image source
            const img = previewContainer.querySelector('.gallery-image-preview');
            if (img) img.src = event.target.result;
        };
        reader.readAsDataURL(file);
    }

    createPreviewContainer(fileInput, placeholder, galleryItem) {
        const previewContainer = document.createElement('div');
        previewContainer.className = 'image-preview-container';

        const img = document.createElement('img');
        img.className = 'gallery-image-preview';
        img.alt = 'Превью изображения';

        const deleteButton = document.createElement('button');
        deleteButton.type = 'button';
        deleteButton.className = 'btn btn-sm btn-danger delete-image';
        deleteButton.innerHTML = '<i class="fas fa-times"></i>';

        // Clear new image preview
        deleteButton.addEventListener('click', () => {
            previewContainer.remove();
            fileInput.value = '';
            if (placeholder) placeholder.style.display = 'flex';
            // Обновляем валидацию после удаления превью
            this.updateValidation();
        });

        previewContainer.appendChild(img);
        previewContainer.appendChild(deleteButton);

        return previewContainer;
    }

    setupAddImageButton() {
        const addButton = document.getElementById('add-gallery-image');
        if (!addButton) return;

        addButton.addEventListener('click', () => {
            this.addNewGalleryItem();
        });
    }

    addNewGalleryItem() {
        const galleryForms = document.querySelector('.gallery-forms');
        const totalForms = document.querySelector(`#id_${this.formsetPrefix}-TOTAL_FORMS`);
        const maxForms = document.querySelector(`#id_${this.formsetPrefix}-MAX_NUM_FORMS`);

        if (!totalForms || !maxForms) {
            alert('Ошибка: не найдены поля управления формсетом');
            return;
        }

        const currentCount = parseInt(totalForms.value) || 0;
        const maxCount = parseInt(maxForms.value) || this.maxImages;

        if (currentCount >= maxCount) {
            alert(`Максимальное количество изображений: ${maxCount}`);
            return;
        }

        // Create new gallery item
        const newItem = this.createGalleryItem(currentCount);
        galleryForms.appendChild(newItem);
        totalForms.value = currentCount + 1;

        // Attach handlers to new elements
        this.attachHandlersToNewItem(newItem);
    }

    createGalleryItem(index) {
        const newItem = document.createElement('div');
        newItem.className = 'gallery-item';
        newItem.setAttribute('data-form-index', index);
        newItem.innerHTML = `
            <input type="hidden" name="${this.formsetPrefix}-${index}-id" 
                   id="id_${this.formsetPrefix}-${index}-id" value="">
            <div class="gallery-item-content">
                <div class="empty-image-placeholder">
                    <i class="fas fa-plus-circle"></i>
                    <p>Добавить изображение</p>
                </div>
                <div class="image-upload-field">
                    <div class="file-input-wrapper">
                        <input type="file" name="${this.formsetPrefix}-${index}-image" 
                               accept="image/*" class="form-control-file" 
                               id="id_${this.formsetPrefix}-${index}-image">
                        <button type="button" class="btn btn-sm btn-primary custom-file-button">
                            <i class="fas fa-folder-open"></i> Добавить
                        </button>
                    </div>
                </div>
            </div>
        `;
        return newItem;
    }

    attachHandlersToNewItem(newItem) {
        const newFileInput = newItem.querySelector('input[type="file"]');
        const newPlaceholder = newItem.querySelector('.empty-image-placeholder');

        if (newFileInput) {
            newFileInput.addEventListener('change', (e) => {
                this.handleImagePreview(e, newItem);
                // Обновляем валидацию после загрузки файла
                this.updateValidation();
            });
        }

        if (newPlaceholder) {
            newPlaceholder.addEventListener('click', () => {
                if (newFileInput) newFileInput.click();
            });
        }
    }

    markForDeletion(galleryItem) {
        const deleteCheckbox = galleryItem.querySelector('input[type="checkbox"][name$="-DELETE"]');
        if (deleteCheckbox) {
            deleteCheckbox.checked = !deleteCheckbox.checked;
            galleryItem.classList.toggle('marked-for-deletion', deleteCheckbox.checked);
        } else {
            // For new items without delete checkbox, just hide/remove
            galleryItem.style.display = 'none';
        }
    }
}

// Make available globally
window.GalleryManager = GalleryManager;