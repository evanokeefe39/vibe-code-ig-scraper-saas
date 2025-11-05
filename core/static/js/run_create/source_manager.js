// Source management functionality for run creation form
class SourceManager {
    constructor() {
        this.sources = [];
        this.sourceCount = 0;
        this.sourcesContainer = null;
        this.sourcesField = null;
    }

    initialize(containerId, fieldId) {
        this.sourcesContainer = document.getElementById(containerId);
        this.sourcesField = document.getElementById(fieldId);
    }

    addSource() {
        const template = document.getElementById('source-template');
        const sourceCard = template.content.cloneNode(true);
        
        const sourceId = `source-${this.sourceCount++}`;
        sourceCard.querySelector('.source-card').id = sourceId;
        
        this.sourcesContainer.appendChild(sourceCard);
        
        const sourceCardElement = document.getElementById(sourceId);
        const sourceTypeSelect = sourceCardElement.querySelector('.source-type-select');
        const platformConfig = sourceCardElement.querySelector('.platform-config');
        const removeBtn = sourceCardElement.querySelector('.remove-source');
        
        // Handle source type selection
        sourceTypeSelect.addEventListener('change', () => {
            this.updateSourceConfig(sourceId, sourceTypeSelect.value);
        });
        
        // Handle source removal
        removeBtn.addEventListener('click', () => {
            this.removeSource(sourceId);
        });
        
        // Add to sources array
        this.sources.push({
            id: sourceId,
            sourceType: '',
            config: {}
        });
        
        this.updateSourcesField();
    }

    updateSourceConfig(sourceId, sourceType) {
        const sourceCard = document.getElementById(sourceId);
        const platformConfig = sourceCard.querySelector('.platform-config');
        const platformBadge = sourceCard.querySelector('.platform-badge');
        
        // Clear existing config
        platformConfig.innerHTML = '';
        
        if (!sourceType) {
            platformBadge.textContent = '';
            platformBadge.className = 'platform-badge';
            return;
        }
        
        const config = window.sourceTypeConfigs[sourceType];
        platformBadge.textContent = `${config.icon} ${config.name}`;
        platformBadge.className = `platform-badge inline-flex items-center px-3 py-1 rounded-full text-sm ${config.color}`;
        
        // Add source type-specific configuration
        const configTemplate = document.getElementById(config.template);
        const configContent = configTemplate.content.cloneNode(true);
        platformConfig.appendChild(configContent);
        
        // Add event listeners for dynamic updates
        platformConfig.addEventListener('input', () => {
            this.updateSourcesField();
        });
        platformConfig.addEventListener('change', () => {
            this.updateSourcesField();
        });
        
        // Update source in array
        const sourceIndex = this.sources.findIndex(s => s.id === sourceId);
        if (sourceIndex !== -1) {
            this.sources[sourceIndex].sourceType = sourceType;
            this.sources[sourceIndex].config = {};
        }
        
        this.updateSourcesField();
    }

    removeSource(sourceId) {
        const sourceCard = document.getElementById(sourceId);
        if (sourceCard) {
            sourceCard.remove();
        }
        
        this.sources = this.sources.filter(s => s.id !== sourceId);
        this.updateSourcesField();
    }

    updateSourcesField() {
        const validSources = this.sources.map(source => {
            const sourceCard = document.getElementById(source.id);
            if (!sourceCard) return null;
            
            const sourceTypeSelect = sourceCard.querySelector('.source-type-select');
            const sourceType = sourceTypeSelect ? sourceTypeSelect.value : '';
            
            if (!sourceType) return null;
            
            const config = {};
            
            // Extract universal options
            window.RunCreateUtils.extractUniversalOptions(sourceCard, config);
            
            // Extract platform-specific data
            this.extractPlatformSpecificData(sourceCard, sourceType, config);
            
            return {
                id: source.id,
                sourceType: sourceType,
                config: config
            };
        }).filter(s => s !== null);
        
        this.sourcesField.value = JSON.stringify(validSources);
    }

    extractPlatformSpecificData(sourceCard, sourceType, config) {
        // Instagram universal parameters
        if (sourceType.startsWith('instagram-')) {
            this.extractInstagramUniversalOptions(sourceCard, config);
        }
        
        // YouTube source types
        if (sourceType.startsWith('youtube-')) {
            this.extractYouTubeData(sourceCard, sourceType, config);
        } else if (sourceType.startsWith('instagram-')) {
            this.extractInstagramData(sourceCard, sourceType, config);
        } else if (sourceType.startsWith('tiktok-')) {
            this.extractTikTokData(sourceCard, sourceType, config);
        }
    }

    extractInstagramUniversalOptions(sourceCard, config) {
        const resultsLimitInput = sourceCard.querySelector('.results-limit-input');
        const relativeDateFilterSelect = sourceCard.querySelector('.relative-date-filter-select');
        const resultsTypeSelect = sourceCard.querySelector('.results-type-select');
        
        if (resultsLimitInput) {
            const value = window.RunCreateUtils.parseIntFromInput(resultsLimitInput);
            if (value !== null) config.resultsLimit = value;
        }
        
        if (relativeDateFilterSelect && relativeDateFilterSelect.value) {
            // If relative date is selected, it overrides absolute date
            config.onlyPostsNewerThan = relativeDateFilterSelect.value;
        }
        
        if (resultsTypeSelect) {
            const value = window.RunCreateUtils.getSelectValue(resultsTypeSelect);
            if (value !== null) config.resultsType = value;
        }
    }

    extractYouTubeData(sourceCard, sourceType, config) {
        if (sourceType === 'youtube-search') {
            const searchQueriesTextarea = sourceCard.querySelector('.search-queries-textarea');
            const sortingOrderSelect = sourceCard.querySelector('.sorting-order-select');
            const dateFilterSelect = sourceCard.querySelector('.date-filter-select');
            const videoTypeSelect = sourceCard.querySelector('.video-type-select');
            const lengthFilterSelect = sourceCard.querySelector('.length-filter-select');
            
            // Quality filters
            const qualityCheckboxes = {
                isHD: '.is-hd-checkbox',
                hasSubtitles: '.has-subtitles-checkbox',
                hasCC: '.has-cc-checkbox',
                is3D: '.is-3d-checkbox',
                isLive: '.is-live-checkbox',
                is4K: '.is-4k-checkbox'
            };
            
            if (searchQueriesTextarea) {
                config.searchQueries = window.RunCreateUtils.parseTextareaInput(searchQueriesTextarea);
            }
            
            config.sortingOrder = window.RunCreateUtils.getSelectValue(sortingOrderSelect);
            config.dateFilter = window.RunCreateUtils.getSelectValue(dateFilterSelect);
            config.videoType = window.RunCreateUtils.getSelectValue(videoTypeSelect);
            config.lengthFilter = window.RunCreateUtils.getSelectValue(lengthFilterSelect);
            
            // Quality filters
            Object.entries(qualityCheckboxes).forEach(([key, selector]) => {
                const checkbox = sourceCard.querySelector(selector);
                if (checkbox) {
                    config[key] = window.RunCreateUtils.getCheckboxValue(checkbox);
                }
            });
            
        } else if (sourceType === 'youtube-channel') {
            const startUrlsTextarea = sourceCard.querySelector('.start-urls-textarea');
            const sortVideosBySelect = sourceCard.querySelector('.sort-videos-by-select');
            const relativeDateFilterSelect = sourceCard.querySelector('.relative-date-filter-select');
            
            if (startUrlsTextarea) {
                config.startUrls = window.RunCreateUtils.parseUrlsFromTextarea(startUrlsTextarea);
            }
            
            config.sortVideosBy = window.RunCreateUtils.getSelectValue(sortVideosBySelect);
            config.relativeDateFilter = window.RunCreateUtils.getSelectValue(relativeDateFilterSelect);
            
        } else if (sourceType === 'youtube-playlist' || sourceType === 'youtube-hashtag' || sourceType === 'youtube-video') {
            const startUrlsTextarea = sourceCard.querySelector('.start-urls-textarea');
            
            if (startUrlsTextarea) {
                config.startUrls = window.RunCreateUtils.parseUrlsFromTextarea(startUrlsTextarea);
            }
        }
    }

    extractInstagramData(sourceCard, sourceType, config) {
        if (sourceType === 'instagram-profile') {
            const directUrlsTextarea = sourceCard.querySelector('.direct-urls-textarea');
            const feedTypeSelect = sourceCard.querySelector('.feed-type-select');
            
            if (directUrlsTextarea) {
                config.directUrls = window.RunCreateUtils.parseTextareaInput(directUrlsTextarea);
            }
            
            if (feedTypeSelect && feedTypeSelect.value) {
                // Map feed options to backend parameters
                if (feedTypeSelect.value === 'tagged') {
                    config.isUserTaggedFeedURL = true;
                } else if (feedTypeSelect.value === 'reels') {
                    config.isUserReelFeedURL = true;
                }
            }
            
            config.addParentData = true;
            
        } else if (sourceType === 'instagram-post' || sourceType === 'instagram-hashtag') {
            const directUrlsTextarea = sourceCard.querySelector('.direct-urls-textarea');
            
            if (directUrlsTextarea) {
                config.directUrls = window.RunCreateUtils.parseTextareaInput(directUrlsTextarea);
            }
            
            config.addParentData = true;
            
        } else if (sourceType === 'instagram-search') {
            const searchQueriesTextarea = sourceCard.querySelector('.search-queries-textarea');
            const searchTypeSelect = sourceCard.querySelector('.search-type-select');
            const searchLimitInput = sourceCard.querySelector('.search-limit-input');
            
            if (searchQueriesTextarea) {
                const queries = window.RunCreateUtils.parseTextareaInput(searchQueriesTextarea);
                if (queries.length > 0) {
                    config.search = queries.join(', ');
                }
            }
            
            config.searchType = window.RunCreateUtils.getSelectValue(searchTypeSelect);
            
            const limitValue = window.RunCreateUtils.parseIntFromInput(searchLimitInput);
            if (limitValue !== null) config.searchLimit = limitValue;
            
            config.addParentData = true;
        }
    }

    extractTikTokData(sourceCard, sourceType, config) {
        if (sourceType === 'tiktok-profile') {
            const profilesTextarea = sourceCard.querySelector('.profiles-textarea');
            const profileScrapeSectionsSelect = sourceCard.querySelector('.profile-scrape-sections-select');
            const profileSortingSelect = sourceCard.querySelector('.profile-sorting-select');
            const relativeDateFilterSelect = sourceCard.querySelector('.relative-date-filter-select');
            const resultsPerPageInput = sourceCard.querySelector('.results-per-page-input');
            
            if (profilesTextarea) {
                config.profiles = window.RunCreateUtils.parseTextareaInput(profilesTextarea);
            }
            
            config.profileScrapeSections = window.RunCreateUtils.getSelectValue(profileScrapeSectionsSelect)?.split(',');
            config.profileSorting = window.RunCreateUtils.getSelectValue(profileSortingSelect);
            config.oldestPostDateUnified = window.RunCreateUtils.getInputValue(sourceCard.querySelector('.oldest-post-date-input'));
            config.newestPostDate = window.RunCreateUtils.getInputValue(sourceCard.querySelector('.newest-post-date-input'));
            
            if (relativeDateFilterSelect && relativeDateFilterSelect.value) {
                config.oldestPostDateUnified = relativeDateFilterSelect.value;
            }
            
            const resultsPerPage = window.RunCreateUtils.parseIntFromInput(resultsPerPageInput);
            if (resultsPerPage !== null) config.resultsPerPage = resultsPerPage;
            
            config.excludePinnedPosts = window.RunCreateUtils.getCheckboxValue(sourceCard.querySelector('.exclude-pinned-posts-checkbox'));
            
        } else if (sourceType === 'tiktok-hashtag') {
            const hashtagsTextarea = sourceCard.querySelector('.hashtags-textarea');
            const resultsPerPageInput = sourceCard.querySelector('.results-per-page-input');
            
            if (hashtagsTextarea) {
                config.hashtags = window.RunCreateUtils.parseHashtagsFromTextarea(hashtagsTextarea);
            }
            
            const resultsPerPage = window.RunCreateUtils.parseIntFromInput(resultsPerPageInput);
            if (resultsPerPage !== null) config.resultsPerPage = resultsPerPage;
            
        } else if (sourceType === 'tiktok-search') {
            const searchQueriesTextarea = sourceCard.querySelector('.search-queries-textarea');
            const resultsPerPageInput = sourceCard.querySelector('.results-per-page-input');
            
            if (searchQueriesTextarea) {
                config.searchQueries = window.RunCreateUtils.parseTextareaInput(searchQueriesTextarea);
            }
            
            // Always use video results for TikTok search
            config.searchSection = '/video';
            
            const resultsPerPage = window.RunCreateUtils.parseIntFromInput(resultsPerPageInput);
            if (resultsPerPage !== null) config.resultsPerPage = resultsPerPage;
            
        } else if (sourceType === 'tiktok-video') {
            const postUrlsTextarea = sourceCard.querySelector('.post-urls-textarea');
            
            if (postUrlsTextarea) {
                config.postURLs = window.RunCreateUtils.parseTextareaInput(postUrlsTextarea);
            }
        }
        
        // TikTok download options (common to multiple types)
        if (['tiktok-profile', 'tiktok-hashtag', 'tiktok-search', 'tiktok-video'].includes(sourceType)) {
            config.shouldDownloadVideos = window.RunCreateUtils.getCheckboxValue(sourceCard.querySelector('.download-video-checkbox'));
            config.shouldDownloadCovers = window.RunCreateUtils.getCheckboxValue(sourceCard.querySelector('.download-covers-checkbox'));
            config.shouldDownloadSubtitles = window.RunCreateUtils.getCheckboxValue(sourceCard.querySelector('.download-subtitles-checkbox'));
            config.shouldDownloadSlideshowImages = window.RunCreateUtils.getCheckboxValue(sourceCard.querySelector('.download-slideshow-checkbox'));
        }
    }

    getSources() {
        return this.sources;
    }

    getSourceCount() {
        return this.sourceCount;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SourceManager };
} else {
    window.SourceManager = SourceManager;
}