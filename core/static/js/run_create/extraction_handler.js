// Extraction prompt handling for run creation form
class ExtractionHandler {
    constructor() {
        this.enableExtractionCheckbox = null;
        this.extractionPromptContainer = null;
    }

    initialize(checkboxId, containerId) {
        this.enableExtractionCheckbox = document.getElementById(checkboxId);
        this.extractionPromptContainer = document.getElementById(containerId);
        
        if (this.enableExtractionCheckbox) {
            this.enableExtractionCheckbox.addEventListener('change', () => {
                this.toggleExtractionPrompt();
            });
        }
        
        // Initialize state
        this.toggleExtractionPrompt();
    }

    toggleExtractionPrompt() {
        if (!this.enableExtractionCheckbox || !this.extractionPromptContainer) return;
        
        if (this.enableExtractionCheckbox.checked) {
            this.extractionPromptContainer.style.display = 'block';
        } else {
            this.extractionPromptContainer.style.display = 'none';
        }
    }

    isExtractionEnabled() {
        return this.enableExtractionCheckbox ? this.enableExtractionCheckbox.checked : false;
    }

    getExtractionPrompt() {
        const promptTextarea = this.extractionPromptContainer?.querySelector('textarea');
        return promptTextarea ? promptTextarea.value : '';
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ExtractionHandler };
} else {
    window.ExtractionHandler = ExtractionHandler;
}