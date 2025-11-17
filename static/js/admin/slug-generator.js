// Slug Generator Component with Transliteration
class SlugGenerator {
    constructor(options = {}) {
        this.nameInputSelector = options.nameInputSelector || 'input[name="name_ru"]';
        this.slugInputSelector = options.slugInputSelector || 'input[name="slug"]';
        this.translitMap = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh',
            'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
            'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts',
            'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu',
            'я': 'ya', 'і': 'i', 'ї': 'yi', 'є': 'ye', 'ґ': 'g',
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo', 'Ж': 'Zh',
            'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O',
            'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'H', 'Ц': 'Ts',
            'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch', 'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu',
            'Я': 'Ya', 'І': 'I', 'Ї': 'Yi', 'Є': 'Ye', 'Ґ': 'G'
        };
        this.init();
    }

    init() {
        this.nameInput = document.querySelector(this.nameInputSelector);
        this.slugInput = document.querySelector(this.slugInputSelector);

        if (!this.nameInput || !this.slugInput) return;

        // Only auto-generate if slug is empty (for new pages)
        this.slugWasEmpty = !this.slugInput.value;

        this.setupEventListeners();
    }

    setupEventListeners() {
        // Auto-generate slug from name input
        this.nameInput.addEventListener('input', () => {
            // Only auto-generate if user hasn't manually edited the slug
            if (this.slugWasEmpty || !this.slugInput.value) {
                const generatedSlug = this.generateSlug(this.nameInput.value);
                this.slugInput.value = generatedSlug;
            }
        });

        // If user manually edits slug, stop auto-generation
        this.slugInput.addEventListener('input', () => {
            if (this.slugInput.value) {
                this.slugWasEmpty = false;
            }
        });
    }

    transliterate(text) {
        return text.split('').map(char => this.translitMap[char] || char).join('');
    }

    generateSlug(text) {
        if (!text) return '';

        // Transliterate
        let slug = this.transliterate(text);

        // Convert to lowercase, replace spaces and special chars with hyphens
        slug = slug.toLowerCase()
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/^-+|-+$/g, '');

        return slug;
    }
}

// Make available globally
window.SlugGenerator = SlugGenerator;