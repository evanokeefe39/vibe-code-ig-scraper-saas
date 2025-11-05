// Form validation for run creation form
class FormValidator {
    constructor(sourceManager) {
        this.sourceManager = sourceManager;
    }

    validateForm(formData) {
        const errors = [];
        
        // Check if at least one source exists
        if (!formData.sources || formData.sources.length === 0) {
            errors.push('Please add at least one source.');
            return { isValid: false, errors };
        }
        
        // Validate each source has required data
        for (const source of formData.sources) {
            const sourceValidation = this.validateSource(source);
            if (!sourceValidation.isValid) {
                errors.push(sourceValidation.error);
            }
        }
        
        return {
            isValid: errors.length === 0,
            errors: errors
        };
    }

    validateSource(source) {
        const config = source.config || {};
        const sourceType = source.sourceType;
        
        const hasData = window.RunCreateUtils.validateSourceData(sourceType, config);
        
        if (!hasData) {
            const sourceTypeConfig = window.sourceTypeConfigs[sourceType];
            const sourceName = sourceTypeConfig ? sourceTypeConfig.name : sourceType;
            return {
                isValid: false,
                error: `Please add URLs, search terms, or other required data for ${sourceName} source.`
            };
        }
        
        return { isValid: true };
    }

    showValidationErrors(errors) {
        if (errors.length === 1) {
            alert(errors[0]);
        } else {
            const errorMessage = 'Please fix the following issues:\n\n' + errors.map((error, index) => `${index + 1}. ${error}`).join('\n');
            alert(errorMessage);
        }
    }

    setupFormValidation(form, submitCallback) {
        form.addEventListener('submit', (e) => {
            const formData = this.getFormData();
            const validation = this.validateForm(formData);
            
            if (!validation.isValid) {
                e.preventDefault();
                this.showValidationErrors(validation.errors);
                return false;
            }
            
            // Show loading state
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = window.RunCreateUtils.showLoadingState(submitBtn, 'Creating Run...');
            
            // Re-enable after 10 seconds as fallback
            setTimeout(() => {
                window.RunCreateUtils.restoreButtonState(submitBtn, originalText);
            }, 10000);
            
            // Call submit callback if provided
            if (submitCallback) {
                submitCallback(formData);
            }
        });
    }

    getFormData() {
        const sourcesField = document.querySelector('input[name="sources"]');
        let sources = [];
        
        try {
            sources = JSON.parse(sourcesField.value || '[]');
        } catch (e) {
            console.error('Error parsing sources:', e);
            sources = [];
        }
        
        return {
            sources: sources
        };
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { FormValidator };
} else {
    window.FormValidator = FormValidator;
}