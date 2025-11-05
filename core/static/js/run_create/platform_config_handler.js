// Simple platform configuration handler for Django formsets
document.addEventListener('DOMContentLoaded', function() {
    console.log('Platform Config Handler - Initializing...');
    
    // Handle platform configuration visibility
    function handlePlatformConfigVisibility(sourceCard) {
        const sourceTypeSelect = sourceCard.querySelector('.source-type-select');
        if (!sourceTypeSelect) return;
        
        const sourceType = sourceTypeSelect.value;
        const platformConfigs = sourceCard.querySelectorAll('.platform-config');
        
        // Hide all platform configs
        platformConfigs.forEach(config => {
            config.style.display = 'none';
        });
        
        // Show the relevant platform config based on source type
        if (sourceType) {
            // Map source types to config classes
            const configMap = {
                'youtube-search': 'youtube-search-config',
                'youtube-channel': 'youtube-channel-config', 
                'youtube-playlist': 'youtube-playlist-config',
                'youtube-hashtag': 'youtube-hashtag-config',
                'youtube-video': 'youtube-video-config',
                'instagram-profile': 'instagram-profile-config',
                'instagram-post': 'instagram-post-config',
                'instagram-hashtag': 'instagram-hashtag-config',
                'instagram-search': 'instagram-search-config',
                'tiktok-profile': 'tiktok-profile-config',
                'tiktok-hashtag': 'tiktok-hashtag-config',
                'tiktok-search': 'tiktok-search-config',
                'tiktok-video': 'tiktok-video-config'
            };
            
            const configClass = configMap[sourceType];
            if (configClass) {
                const targetConfig = sourceCard.querySelector(`.${configClass}`);
                if (targetConfig) {
                    targetConfig.style.display = 'block';
                }
            }
        }
    }
    
    // Initialize all existing source cards
    function initializeSourceCards() {
        const sourceCards = document.querySelectorAll('.source-card');
        sourceCards.forEach(sourceCard => {
            const sourceTypeSelect = sourceCard.querySelector('.source-type-select');
            
            if (sourceTypeSelect) {
                // Handle initial state
                handlePlatformConfigVisibility(sourceCard);
                
                // Handle change events
                sourceTypeSelect.addEventListener('change', () => {
                    handlePlatformConfigVisibility(sourceCard);
                });
            }
        });
    }
    
    // Handle dynamically added source cards (for formset additions)
    function observeSourceCards() {
        const sourcesContainer = document.getElementById('sources-container');
        if (!sourcesContainer) return;
        
        // Mutation observer to detect new source cards
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            // Check if this is a source card or contains source cards
                            const sourceCard = node.classList?.contains('source-card') ? 
                                node : node.querySelector?.('.source-card');
                            
                            if (sourceCard) {
                                const sourceTypeSelect = sourceCard.querySelector('.source-type-select');
                                if (sourceTypeSelect) {
                                    // Initialize the new source card
                                    handlePlatformConfigVisibility(sourceCard);
                                    
                                    // Add change listener
                                    sourceTypeSelect.addEventListener('change', () => {
                                        handlePlatformConfigVisibility(sourceCard);
                                    });
                                }
                            }
                        }
                    });
                }
            });
        });
        
        observer.observe(sourcesContainer, {
            childList: true,
            subtree: true
        });
    }
    
    // Initialize
    initializeSourceCards();
    observeSourceCards();
    
    console.log('Platform Config Handler - Initialization complete');
});