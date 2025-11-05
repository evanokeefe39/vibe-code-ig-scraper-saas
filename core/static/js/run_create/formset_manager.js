document.addEventListener('DOMContentLoaded', function() {
    const addSourceBtn = document.getElementById('add-source-btn');
    const sourcesContainer = document.getElementById('sources-container');
    
    // Store the empty form template for cloning
    let emptyFormTemplate = null;
    
    // Load empty form template
    function loadEmptyFormTemplate() {
        if (emptyFormTemplate) return Promise.resolve(emptyFormTemplate);
        
        return fetch('/runs/create/empty-form/')
            .then(response => response.text())
            .then(html => {
                emptyFormTemplate = html;
                return emptyFormTemplate;
            })
            .catch(error => {
                console.error('Error loading empty form template:', error);
                return '';
            });
    }
    
    // Show/hide platform configs based on source type selection
    function updatePlatformConfig(sourceTypeSelect) {
        const sourceCard = sourceTypeSelect.closest('.source-card');
        if (!sourceCard) return;
        
        const container = sourceCard.querySelector('.platform-config-container');
        if (!container) return;
        
        // Clear existing configs
        container.innerHTML = '';
        
        const selectedType = sourceTypeSelect.value;
        if (!selectedType) return;
        
        // Load platform config via AJAX
        fetch(`/runs/create/platform-config/${selectedType}/`)
            .then(response => response.text())
            .then(html => {
                container.innerHTML = html;
            })
            .catch(error => {
                console.error('Error loading platform config:', error);
                container.innerHTML = '<div class="text-red-600">Error loading configuration</div>';
            });
    }
    
    // Add source functionality
    if (addSourceBtn) {
        addSourceBtn.addEventListener('click', async function() {
            const template = await loadEmptyFormTemplate();
            if (!template) {
                console.error('Could not load empty form template');
                return;
            }
            
            const formCount = document.querySelectorAll('.source-card').length;
            const totalFormsInput = document.querySelector('#id_form-TOTAL_FORMS');
            
            // Replace __prefix__ with the actual form index
            let newFormHtml = template.replace(/__prefix__/g, formCount);
            
            // Create temporary container
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = newFormHtml;
            const newForm = tempDiv.firstElementChild;
            
            sourcesContainer.appendChild(newForm);
            
            // Update formset management form
            if (totalFormsInput) {
                totalFormsInput.value = formCount + 1;
            }
            
            // Update management form fields
            updateManagementForm();
            
            // Initialize the new form's platform config
            const newSelect = newForm.querySelector('[name$="-source_type"]');
            if (newSelect) {
                updatePlatformConfig(newSelect);
            }
        });
    }
    
    // Handle source type changes for all forms (existing and dynamic)
    document.addEventListener('change', function(e) {
        if (e.target.matches('[name$="-source_type"]')) {
            updatePlatformConfig(e.target);
        }
    });
    
    // Handle remove source buttons
    document.addEventListener('click', function(e) {
        if (e.target.closest('.remove-source')) {
            e.preventDefault();
            const sourceCard = e.target.closest('.source-card');
            if (!sourceCard) return;
            
            // Find the DELETE checkbox and check it
            const deleteCheckbox = sourceCard.querySelector('[name$="-DELETE"]');
            if (deleteCheckbox) {
                deleteCheckbox.checked = true;
                sourceCard.style.display = 'none';
            } else {
                // If no DELETE checkbox, just remove it
                sourceCard.remove();
            }
            
            // Update form count and management form
            updateManagementForm();
            
            // Renumber visible sources
            const visibleCards = document.querySelectorAll('.source-card:not([style*="display: none"])');
            visibleCards.forEach((card, index) => {
                const title = card.querySelector('h3');
                if (title) {
                    title.textContent = `Source ${index + 1}`;
                }
            });
        }
    });
    
    // Update Django formset management form
    function updateManagementForm() {
        const totalFormsInput = document.querySelector('#id_form-TOTAL_FORMS');
        const visibleCards = document.querySelectorAll('.source-card:not([style*="display: none"])');
        
        if (totalFormsInput) {
            totalFormsInput.value = visibleCards.length;
        }
        
        // Update INITIAL_FORMS if needed (usually stays the same)
        // Update MAX_NUM_FORMS if needed (usually stays the same)
    }
    
    // Initialize existing forms
    document.querySelectorAll('[name$="-source_type"]').forEach(select => {
        updatePlatformConfig(select);
    });
});