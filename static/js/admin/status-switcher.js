// Status Switcher Component
class StatusSwitcher {
    constructor(options = {}) {
        this.switchSelector = options.switchSelector || '.custom-switch input[type="checkbox"]';
        this.labelId = options.labelId || 'status-label';
        this.enabledText = options.enabledText || 'Включена';
        this.disabledText = options.disabledText || 'Выключена';
        this.init();
    }

    init() {
        this.statusSwitch = document.querySelector(this.switchSelector);
        this.statusLabel = document.getElementById(this.labelId);

        if (!this.statusSwitch || !this.statusLabel) return;

        this.setupEventListener();
        this.updateLabel(); // Set initial state
    }

    setupEventListener() {
        this.statusSwitch.addEventListener('change', () => {
            this.updateLabel();
        });
    }

    updateLabel() {
        this.statusLabel.textContent = this.statusSwitch.checked
            ? this.enabledText
            : this.disabledText;
    }
}

// Make available globally
window.StatusSwitcher = StatusSwitcher;