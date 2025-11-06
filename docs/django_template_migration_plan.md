# Django Template Migration Plan

## Overview

Replace the current JavaScript-heavy frontend with a Django template-based approach using formsets and standard Django patterns. This maintains all rich configuration options while dramatically reducing complexity.

## Current Architecture Problems

### Issues with Current Approach
- **Over-engineered UI:** 150+ lines of template per platform for simple configuration
- **Complex JavaScript:** Multiple modules (platform_configs, source_manager, form_validator, etc.)
- **Maintenance nightmare:** Each platform change requires template + JS updates
- **Poor UX:** Users overwhelmed with options rendered via JavaScript
- **Fighting Django:** Using `<template>` tags and DOM manipulation instead of Django's template system

### Current Data Flow
1. **Frontend:** JavaScript creates `{"sourceType": "youtube-search", "config": {...}}`
2. **Django View:** `trigger_run()` converts to platform format and posts to n8n
3. **n8n Workflow:** Expects `{"sources": [{"platform": "youtube", "sourceType": "...", "configuration": {...}}]}`

## Proposed Django Template Architecture

### Core Components

#### 1. Django Formset
```python
# forms.py
class SourceForm(forms.Form):
    source_type = forms.ChoiceField(choices=[
        ('youtube-search', 'YouTube Search'),
        ('youtube-channel', 'YouTube Channel'),
        ('youtube-playlist', 'YouTube Playlist'),
        ('youtube-hashtag', 'YouTube Hashtag'),
        ('youtube-video', 'YouTube Video'),
        ('instagram-profile', 'Instagram Profile'),
        ('instagram-post', 'Instagram Post'),
        ('instagram-hashtag', 'Instagram Hashtag'),
        ('instagram-search', 'Instagram Search'),
        ('tiktok-profile', 'TikTok Profile'),
        ('tiktok-hashtag', 'TikTok Hashtag'),
        ('tiktok-search', 'TikTok Search'),
        ('tiktok-video', 'TikTok Video'),
    ])
    
    # Common fields
    max_results = forms.IntegerField(initial=50, min_value=1, max_value=1000)
    
    # Platform-specific fields (all present, validation based on source_type)
    search_queries = forms.CharField(required=False, widget=forms.Textarea)
    profile_urls = forms.CharField(required=False, widget=forms.Textarea)
    hashtags = forms.CharField(required=False, widget=forms.Textarea)
    channels = forms.CharField(required=False, widget=forms.Textarea)
    
    # YouTube-specific fields
    sorting_order = forms.ChoiceField(required=False, choices=[
        ('relevance', 'Relevance'),
        ('rating', 'Rating'),
        ('date', 'Date'),
        ('views', 'Views'),
    ])
    date_filter = forms.ChoiceField(required=False, choices=[
        ('', 'Any time'),
        ('hour', 'Last hour'),
        ('today', 'Today'),
        ('week', 'This week'),
        ('month', 'This month'),
        ('year', 'This year'),
    ])
    video_type = forms.ChoiceField(required=False, choices=[
        ('video', 'Video'),
        ('movie', 'Movie'),
    ])
    length_filter = forms.ChoiceField(required=False, choices=[
        ('', 'Any length'),
        ('under4', 'Under 4 minutes'),
        ('between420', '4-20 minutes'),
        ('plus20', 'Over 20 minutes'),
    ])
    
    # Quality filters
    is_hd = forms.BooleanField(required=False)
    has_subtitles = forms.BooleanField(required=False)
    is_3d = forms.BooleanField(required=False)
    is_live = forms.BooleanField(required=False)
    is_4k = forms.BooleanField(required=False)
    
    # Subtitle options
    subtitles_language = forms.ChoiceField(required=False, choices=[
        ('any', 'Any'),
        ('en', 'English'),
        ('de', 'German'),
        ('es', 'Spanish'),
        ('fr', 'French'),
    ])
    download_subtitles = forms.BooleanField(required=False)
    
    # Instagram-specific fields
    feed_type = forms.ChoiceField(required=False, choices=[
        ('posts', 'Posts only'),
        ('tagged', 'Tagged posts'),
        ('reels', 'Reels only'),
    ])
    oldest_post_date = forms.DateField(required=False)
    relative_date_filter = forms.ChoiceField(required=False, choices=[
        ('', 'No filter'),
        ('1 minute', 'Last minute'),
        ('1 hour', 'Last hour'),
        ('1 day', 'Last 24 hours'),
        ('3 days', 'Last 3 days'),
        ('7 days', 'Last 7 days'),
        ('30 days', 'Last 30 days'),
    ])
    results_type = forms.ChoiceField(required=False, choices=[
        ('posts', 'Posts'),
        ('comments', 'Comments'),
        ('mentions', 'Mentions'),
    ])

SourceFormSet = formset_factory(SourceForm, extra=1, can_delete=True)
```

#### 2. Template Structure
```html
<!-- run_create.html -->
{% extends "base.html" %}
{% load static %}

{% block content %}
<div class="max-w-6xl mx-auto px-4 py-8">
    <h1>Create New Scraping Run</h1>
    
    <form method="post" id="run-form">
        {% csrf_token %}
        
        <!-- Global Settings -->
        <div class="mb-8">
            <h2>Global Settings</h2>
            {{ form.enable_extraction }}
            {{ form.extraction_prompt }}
            {{ form.auto_infer_columns }}
        </div>
        
        <!-- Sources Configuration -->
        <div class="mb-8">
            <h2>Sources Configuration</h2>
            <div id="sources-container">
                {% for form in source_formset %}
                    {% include "core/run_create/partials/source_card.html" %}
                {% endfor %}
            </div>
            
            <button type="button" id="add-source-btn">Add Source</button>
            {{ source_formset.management_form }}
        </div>
        
        <!-- Form Actions -->
        <button type="submit">Start Scraping Run</button>
    </form>
</div>

<!-- Platform Configuration Templates -->
{% include "core/run_create/platforms/youtube_search.html" %}
{% include "core/run_create/platforms/instagram_profile.html" %}
{% include "core/run_create/platforms/tiktok_profile.html" %}
<!-- ... other platforms -->

<!-- Minimal JavaScript for formset management -->
<script src="{% static 'js/run_create/formset_manager.js' %}"></script>
{% endblock %}
```

#### 3. Platform-Specific Templates
```html
<!-- core/run_create/platforms/youtube_search.html -->
<div class="platform-config" data-platform="youtube-search" style="display: none;">
    <div class="bg-red-50 border border-red-200 rounded-lg p-3">
        <span class="text-sm font-medium text-red-800">💰 Cost: $5.00 per 1000 results</span>
    </div>
    
    <div class="space-y-4">
        <div>
            <label>Search Queries *</label>
            {{ form.search_queries }}
            <p class="text-xs text-gray-500">Search terms like typing in YouTube's search bar</p>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
            <div>
                <label>Sorting Order</label>
                {{ form.sorting_order }}
            </div>
            <div>
                <label>Date Filter</label>
                {{ form.date_filter }}
            </div>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
            <div>
                <label>Video Type</label>
                {{ form.video_type }}
            </div>
            <div>
                <label>Length Filter</label>
                {{ form.length_filter }}
            </div>
        </div>
        
        <div>
            <label>Max Videos</label>
            {{ form.max_results }}
        </div>
        
        <!-- Quality Filters -->
        <div class="border border-gray-200 rounded-lg p-4">
            <h5 class="text-sm font-medium text-gray-900 mb-3">⭐ Quality Filters</h5>
            <div class="grid grid-cols-3 gap-3">
                <label>{{ form.is_hd }} HD</label>
                <label>{{ form.has_subtitles }} Has Subtitles</label>
                <label>{{ form.is_3d }} 3D</label>
                <label>{{ form.is_live }} Live</label>
                <label>{{ form.is_4k }} 4K</label>
            </div>
        </div>
        
        <!-- Subtitle Options -->
        <div class="border border-gray-200 rounded-lg p-4">
            <h5 class="text-sm font-medium text-gray-900 mb-3">💬 Subtitle Options</h5>
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label>Subtitle Language</label>
                    {{ form.subtitles_language }}
                </div>
                <div class="flex items-center space-x-4">
                    <label>{{ form.download_subtitles }} Download Subtitles</label>
                    <label>{{ form.prefer_auto_generated_subtitles }} Prefer Auto-Generated</label>
                </div>
            </div>
        </div>
    </div>
</div>
```

#### 4. Source Card Template
```html
<!-- core/run_create/partials/source_card.html -->
<div class="source-card border rounded-lg p-4 mb-4">
    <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold">Source {{ forloop.counter }}</h3>
        {% if source_formset.can_delete %}
            <button type="button" class="remove-source" data-form-prefix="{{ form.prefix }}">Remove</button>
        {% endif %}
    </div>
    
    <div class="mb-4">
        {{ form.source_type }}
    </div>
    
    <!-- Platform-specific configuration will be shown/hidden based on selection -->
    <div class="platform-config-container">
        <!-- All platform configs are included in the page, hidden by default -->
        <!-- JavaScript shows the relevant one based on source_type selection -->
    </div>
</div>
```

#### 5. Minimal JavaScript
```javascript
// formset_manager.js - Only for formset management, no complex DOM manipulation
document.addEventListener('DOMContentLoaded', function() {
    const addSourceBtn = document.getElementById('add-source-btn');
    const sourcesContainer = document.getElementById('sources-container');
    
    // Show/hide platform configs based on source type selection
    function updatePlatformConfig(sourceTypeSelect) {
        const sourceCard = sourceTypeSelect.closest('.source-card');
        const container = sourceCard.querySelector('.platform-config-container');
        
        // Hide all platform configs
        container.querySelectorAll('.platform-config').forEach(config => {
            config.style.display = 'none';
        });
        
        // Show relevant config
        const selectedType = sourceTypeSelect.value;
        const relevantConfig = document.querySelector(`.platform-config[data-platform="${selectedType}"]`);
        if (relevantConfig) {
            // Clone the config template into this source card
            const clonedConfig = relevantConfig.cloneNode(true);
            clonedConfig.style.display = 'block';
            container.innerHTML = '';
            container.appendChild(clonedConfig);
        }
    }
    
    // Add source functionality
    if (addSourceBtn) {
        addSourceBtn.addEventListener('click', function() {
            // Use Django's formset management to add new form
            const formCount = document.querySelectorAll('.source-card').length;
            const newFormHtml = `{% include "core/run_create/partials/empty_source_card.html" %}`.replace(/__prefix__/g, formCount);
            
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = newFormHtml;
            const newForm = tempDiv.firstElementChild;
            
            sourcesContainer.appendChild(newForm);
            
            // Update formset management form
            const totalFormsInput = document.querySelector('#id_form-TOTAL_FORMS');
            totalFormsInput.value = formCount + 1;
        });
    }
    
    // Handle source type changes for existing forms
    document.addEventListener('change', function(e) {
        if (e.target.matches('[name$="-source_type"]')) {
            updatePlatformConfig(e.target);
        }
    });
    
    // Initialize existing forms
    document.querySelectorAll('[name$="-source_type"]').forEach(select => {
        updatePlatformConfig(select);
    });
});
```

#### 6. Updated View
```python
# views.py
def run_create(request):
    if request.method == 'POST':
        source_formset = SourceFormSet(request.POST, prefix='form')
        form = RunForm(request.POST)
        
        if source_formset.is_valid() and form.is_valid():
            # Process sources from formset
            sources = []
            for source_form in source_formset:
                if source_form.is_valid() and source_form.cleaned_data.get('source_type'):
                    source_config = build_source_config(source_form.cleaned_data)
                    sources.append({
                        "sourceType": source_form.cleaned_data['source_type'],
                        "config": source_config
                    })
            
            # Create run with processed sources
            run = form.save(commit=False)
            run.user_id = 1  # Dummy user_id for development
            run.input = json.dumps({
                'sources': sources,
                'days_since': form.cleaned_data['days_since'],
                'max_results': form.cleaned_data['max_results'],
                'auto_infer_columns': form.cleaned_data['auto_infer_columns'],
                'custom_columns': form.cleaned_data['custom_columns'],
                'extraction_prompt': form.cleaned_data['extraction_prompt']
            })
            run.save()
            trigger_run(run)
            messages.success(request, 'Run started successfully!')
            return redirect('run_detail', pk=run.pk)
    else:
        source_formset = SourceFormSet(prefix='form')
        form = RunForm()
    
    return render(request, 'core/run_create.html', {
        'form': form,
        'source_formset': source_formset
    })

def build_source_config(cleaned_data):
    """Convert Django form data to n8n configuration format"""
    source_type = cleaned_data['source_type']
    config = {}
    
    if source_type.startswith('youtube-'):
        if source_type == 'youtube-search':
            config['searchQueries'] = cleaned_data.get('search_queries', '').splitlines()
            config['maxResults'] = cleaned_data.get('max_results', 50)
            config['sortingOrder'] = cleaned_data.get('sorting_order', 'relevance')
            config['dateFilter'] = cleaned_data.get('date_filter', '')
            config['videoType'] = cleaned_data.get('video_type', 'video')
            config['lengthFilter'] = cleaned_data.get('length_filter', '')
            
            # Quality filters
            config['qualityFilters'] = {
                'isHD': cleaned_data.get('is_hd', False),
                'hasSubtitles': cleaned_data.get('has_subtitles', False),
                'is3D': cleaned_data.get('is_3d', False),
                'isLive': cleaned_data.get('is_live', False),
                'is4K': cleaned_data.get('is_4k', False),
            }
            
            # Subtitle options
            config['subtitleOptions'] = {
                'language': cleaned_data.get('subtitles_language', 'any'),
                'downloadSubtitles': cleaned_data.get('download_subtitles', False),
            }
        else:
            # YouTube channel, playlist, hashtag, video
            config['startUrls'] = cleaned_data.get('profile_urls', '').splitlines()
            config['maxResults'] = cleaned_data.get('max_results', 50)
    
    elif source_type.startswith('instagram-'):
        if source_type == 'instagram-search':
            config['search'] = cleaned_data.get('search_queries', '').splitlines()
        else:
            config['directUrls'] = cleaned_data.get('profile_urls', '').splitlines()
        
        config['resultsType'] = cleaned_data.get('results_type', 'posts')
        config['resultsLimit'] = cleaned_data.get('max_results', 100)
        config['oldestPostDate'] = cleaned_data.get('oldest_post_date', '')
        config['relativeDateFilter'] = cleaned_data.get('relative_date_filter', '')
        config['feedType'] = cleaned_data.get('feed_type', 'posts')
    
    elif source_type.startswith('tiktok-'):
        if source_type == 'tiktok-profile':
            config['profiles'] = cleaned_data.get('profile_urls', '').splitlines()
        elif source_type == 'tiktok-hashtag':
            config['hashtags'] = cleaned_data.get('hashtags', '').splitlines()
        elif source_type == 'tiktok-search':
            config['searchQueries'] = cleaned_data.get('search_queries', '').splitlines()
        elif source_type == 'tiktok-video':
            config['postURLs'] = cleaned_data.get('profile_urls', '').splitlines()
        
        config['resultsPerPage'] = cleaned_data.get('max_results', 50)
    
    return config
```

## Implementation Strategy

### Phase 1: Foundation (Week 1)
1. Create `SourceForm` with all platform fields
2. Create `SourceFormSet` 
3. Update `run_create` view to handle formset
4. Create basic template structure

### Phase 2: Platform Templates (Week 2)
1. Create platform-specific templates
2. Implement source card template
3. Add minimal JavaScript for formset management
4. Test with YouTube Search only

### Phase 3: Expand Platforms (Week 3)
1. Add all Instagram platform templates
2. Add all TikTok platform templates
3. Add remaining YouTube platform templates
4. Comprehensive testing

### Phase 4: Cleanup (Week 4)
1. Remove old JavaScript modules
2. Remove old template files
3. Update documentation
4. Performance testing

## Benefits

### Technical Benefits
- **90% less JavaScript:** From 5+ modules to 1 small file
- **Standard Django patterns:** Formsets, validation, error handling
- **Better caching:** Templates compiled server-side
- **SEO friendly:** Content in HTML, not generated by JS
- **Progressive enhancement:** Works without JavaScript

### Maintenance Benefits
- **Easier testing:** Standard Django form testing
- **Single source of truth:** Form validation in Python
- **Better error handling:** Django's built-in form validation
- **Simpler debugging:** No complex JavaScript state management

### User Experience Benefits
- **Faster loading:** No JavaScript compilation on page load
- **Better accessibility:** Standard HTML form patterns
- **Mobile friendly:** Responsive without JavaScript complexity
- **Form persistence:** Browser's native form state management

## Files to Remove

### JavaScript Files
- `core/static/js/run_create/platform_configs.js`
- `core/static/js/run_create/source_manager.js`
- `core/static/js/run_create/form_validator.js`
- `core/static/js/run_create/extraction_handler.js`
- `core/static/js/run_create/utils.js`
- `core/static/js/run_create/main.js`

### Template Files
- `core/templates/core/run_create/platform_templates/youtube_search.html`
- `core/templates/core/run_create/platform_templates/instagram_profile.html`
- `core/templates/core/run_create/platform_templates/tiktok_profile.html`
- `core/templates/core/run_create/platform_templates/additional_platforms.html`
- `core/templates/core/run_create/partials/source_card.html`
- `core/templates/core/run_create/partials/form_actions.html`

### Files to Create

### New Template Structure
```
core/templates/core/run_create/
├── run_create.html (main form)
├── partials/
│   ├── source_card.html
│   └── empty_source_card.html
└── platforms/
    ├── youtube_search.html
    ├── youtube_channel.html
    ├── youtube_playlist.html
    ├── youtube_hashtag.html
    ├── youtube_video.html
    ├── instagram_profile.html
    ├── instagram_post.html
    ├── instagram_hashtag.html
    ├── instagram_search.html
    ├── tiktok_profile.html
    ├── tiktok_hashtag.html
    ├── tiktok_search.html
    └── tiktok_video.html
```

### New JavaScript
```
core/static/js/run_create/
└── formset_manager.js (single small file)
```

## Risk Assessment

### Low Risk
- **Backward compatibility:** n8n workflow unchanged
- **Data format:** Same JSON structure as current
- **Validation:** Django forms provide better validation

### Medium Risk
- **Template complexity:** Many platform-specific templates to maintain
- **Form size:** Large form with many fields

### Mitigation
- **Incremental migration:** Phase-by-phase approach
- **Comprehensive testing:** Each platform tested individually
- **Fallback plan:** Keep old code in separate branch during migration

## Success Criteria

### Functional Requirements
- [ ] All 14 platform types supported
- [ ] All configuration options available
- [ ] Form validation working correctly
- [ ] n8n integration unchanged
- [ ] Multi-source runs working

### Non-Functional Requirements
- [ ] Page load time < 2 seconds
- [ ] Works without JavaScript
- [ ] Mobile responsive
- [ ] Accessibility compliant
- [ ] 90% reduction in JavaScript code

### Code Quality
- [ ] All old JavaScript files removed
- [ ] All old template files removed
- [ ] Test coverage > 80%
- [ ] Documentation updated
- [ ] No JavaScript errors in browser console

## Timeline

| Week | Tasks | Deliverables |
|------|--------|--------------|
| 1 | Form foundation, basic template | Working YouTube Search |
| 2 | Platform templates, formset JS | All platforms working |
| 3 | Testing, refinement, edge cases | Production-ready implementation |
| 4 | Cleanup, documentation, deployment | Complete migration |

## Conclusion

This migration plan transforms the current JavaScript-heavy frontend into a clean, maintainable Django template-based implementation while preserving all functionality. The approach leverages Django's strengths (formsets, validation, template system) and eliminates unnecessary complexity.

The result will be a more maintainable, testable, and user-friendly interface that follows Django best practices.