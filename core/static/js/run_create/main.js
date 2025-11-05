// Main orchestration for run creation form
document.addEventListener('DOMContentLoaded', function() {
    (function() {
        console.log('Run Create Form - Initializing...');
        
        // Define variables in outer scope
        let form, sourcesContainer, addSourceBtn, sourcesField;
        
        try {
            form = document.getElementById('run-form');
            sourcesContainer = document.getElementById('sources-container');
            addSourceBtn = document.getElementById('add-source-btn');
            sourcesField = document.querySelector('input[name="sources"]');
            
            console.log('Form elements found successfully');
        } catch (error) {
            console.error('Error finding form elements:', error);
            return;
        }
        
        // Initialize managers
        const sourceManager = new SourceManager();
        const formValidator = new FormValidator(sourceManager);
        const extractionHandler = new ExtractionHandler();
        
        // Initialize source manager
        sourceManager.initialize('sources-container', 'sources-field');
        
        // Initialize extraction handler
        const extractionCheckboxId = '{{ form.enable_extraction.id_for_label|lower }}';
        extractionHandler.initialize(extractionCheckboxId, 'extraction-prompt-container');
        
        // Expose to global scope for form validation
        window.sourceManager = sourceManager;
        window.formValidator = formValidator;
        window.extractionHandler = extractionHandler;
        window.sources = sourceManager.getSources();
        window.sourceCount = sourceManager.getSourceCount();

        // Add source button handler
        if (addSourceBtn) {
            addSourceBtn.addEventListener('click', () => {
                sourceManager.addSource();
            });
        }

        // Setup form validation
        if (form) {
            formValidator.setupFormValidation(form, (formData) => {
                console.log('Form submitted with data:', formData);
                // Form will submit normally
            });
        }

        // Add event listeners for dynamic content updates
        if (sourcesContainer) {
            sourcesContainer.addEventListener('input', function(e) {
                if (e.target.matches('.profiles-textarea, .search-input, .channels-textarea, .search-queries-textarea, .post-urls-textarea, .hashtags-textarea')) {
                    sourceManager.updateSourcesField();
                }
            });
        }
        
        // Expose functions to global scope for backward compatibility
        window.addSource = () => sourceManager.addSource();
        window.removeSource = (sourceId) => sourceManager.removeSource(sourceId);
        window.updateSourcesField = () => sourceManager.updateSourcesField();
        window.toggleExtractionPrompt = () => extractionHandler.toggleExtractionPrompt();
        
        // Add one source by default
        setTimeout(() => {
            if (typeof sourceManager.addSource === 'function') {
                sourceManager.addSource();
            }
        }, 100);
        
        console.log('Run Create Form - Initialization complete');
    })();
});