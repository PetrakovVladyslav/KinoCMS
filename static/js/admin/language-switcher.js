// Language Switcher Component
class LanguageSwitcher {
    constructor(options = {}) {
        this.ruBtnId = options.ruBtnId || 'lang-ru';
        this.ukBtnId = options.ukBtnId || 'lang-uk';
        this.init();
    }

    init() {
        this.langRuBtn = document.getElementById(this.ruBtnId);
        this.langUkBtn = document.getElementById(this.ukBtnId);
        this.fieldGroups = document.querySelectorAll('.field-group');

        if (!this.langRuBtn || !this.langUkBtn) return;

        this.setupEventListeners();
    }

    setupEventListeners() {
        this.langRuBtn.addEventListener('click', () => this.switchLanguage('ru'));
        this.langUkBtn.addEventListener('click', () => this.switchLanguage('uk'));
    }

    switchLanguage(lang) {
        // Update button states
        if (lang === 'ru') {
            this.langRuBtn.classList.add('active');
            this.langUkBtn.classList.remove('active');
        } else {
            this.langUkBtn.classList.add('active');
            this.langRuBtn.classList.remove('active');
        }

        // Show/hide appropriate field groups
        this.fieldGroups.forEach(group => {
            if (group.dataset.lang === lang) {
                group.classList.add('active');
                group.style.display = 'block';
            } else {
                group.classList.remove('active');
                group.style.display = 'none';
            }
        });
    }
}

// Make available globally
window.LanguageSwitcher = LanguageSwitcher;