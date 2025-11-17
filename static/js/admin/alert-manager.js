// Alert Manager Component
class AlertManager {
    constructor(options = {}) {
        this.autoHideDelay = options.autoHideDelay || 5000;
        this.fadeOutDuration = options.fadeOutDuration || 500;
        this.init();
    }

    init() {
        this.setupAutoHideAlerts();
    }

    setupAutoHideAlerts() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach((alert) => {
            setTimeout(() => {
                this.hideAlert(alert);
            }, this.autoHideDelay);
        });
    }

    hideAlert(alert) {
        if (!alert || !alert.parentNode) return;

        alert.style.transition = `opacity ${this.fadeOutDuration}ms`;
        alert.style.opacity = '0';

        setTimeout(() => {
            if (alert && alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, this.fadeOutDuration);
    }
}

// Make available globally
window.AlertManager = AlertManager;