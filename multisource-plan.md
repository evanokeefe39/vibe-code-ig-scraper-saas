# Multi-Source Scraper Implementation Plan (Revised)

## Overview
This document outlines the plan to extend the current Instagram-only scraper SaaS to support multiple social media platforms (TikTok, YouTube) using Apify actors and unified post-centric data processing.

## Architecture Understanding

### Current State
- **Base**: MVP branch with Instagram scraper fully functional
- **Infrastructure**: Django backend with n8n workflow orchestration
- **Data Flow**: `scraped` (raw JSON array) → `extracted` (structured data) → UserList export
- **Apify Integration**: 3 actors available (Instagram, TikTok, YouTube) with defined interfaces

### Key Architectural Insight
- **Apify Actors**: Each platform has dedicated actor with specific parameters
- **Unified Data Model**: All platforms produce posts (videos, images, text) with similar attributes
- **n8n Orchestration**: Single workflow can invoke multiple actors via Apify nodes
- **Post-Centric**: Instagram posts/reels ≈ TikTok videos ≈ YouTube videos/shorts

## Phase 1: Enhanced Run Creation Interface (Week 1-2)

### 1.1 Multi-Source Run Form
**Files to modify**: `core/forms.py`, `core/views.py`, `templates/core/run_create.html`

#### New Data Structure:
```python
# Enhanced Run.input structure
{
    "sources": [
        {
            "platform": "instagram",
            "type": "profile_scrape", 
            "config": {
                "directUrls": ["https://instagram.com/username1", "https://instagram.com/username2"],
                "resultsType": "posts",
                "resultsLimit": 50,
                "onlyPostsNewerThan": "7 days"
            }
        },
        {
            "platform": "instagram", 
            "type": "search",
            "config": {
                "search": "ai",
                "searchType": "hashtag",
                "searchLimit": 25
            }
        },
        {
            "platform": "tiktok",
            "type": "profile_scrape",
            "config": {
                "profiles": ["username1", "username2"],
                "profileScrapeSections": ["videos"],
                "resultsPerPage": 50
            }
        },
        {
            "platform": "youtube",
            "type": "search",
            "config": {
                "searchQueries": ["ai tutorials"],
                "maxResults": 25,
                "dateFilter": "month"
            }
        }
    ],
    "extraction_prompt": "Extract business information, contact details, and location data from posts",
    "enable_extraction": true
}
```

#### Form Enhancement:
- **Dynamic Source Management**: Add/remove sources dynamically
- **Platform-Specific Configs**: Show relevant fields per platform/type combination
- **Real-time Validation**: Validate URLs and parameters per platform
- **Source Preview**: Show what data will be scraped from each source

### 1.2 Enhanced n8n Workflow
**Files to create**: `n8n/v2/multi_source_workflow.json`

#### Workflow Architecture:
```
1. Receive Run Input (sources array)
2. For each source:
   - Route to appropriate Apify actor node
   - Pass platform-specific config
   - Collect results in unified format
3. Merge all results into single scraped array
4. Run LLM extraction on merged data (if enabled)
5. Store results in Run.scraped and Run.extracted
6. Return execution completion
```

#### Apify Node Configuration:
```json
{
    "nodeType": "apify_call",
    "dynamic": true,
    "actorMapping": {
        "instagram": "clockwork/instagram-scraper",
        "tiktok": "clockwork/tiktok-scraper", 
        "youtube": "streamers/youtube-scraper"
    },
    "parameterMapping": {
        "instagram": {
            "profile_scrape": ["directUrls", "resultsType", "resultsLimit"],
            "search": ["search", "searchType", "searchLimit"]
        },
        "tiktok": {
            "profile_scrape": ["profiles", "profileScrapeSections", "resultsPerPage"],
            "search": ["searchQueries", "resultsPerPage"]
        },
        "youtube": {
            "search": ["searchQueries", "maxResults", "dateFilter"]
        }
    }
}
```

## Phase 2: Data Structure & Extraction Enhancement (Week 2-3)

### 2.1 Unified Post Schema
**Files to modify**: `core/models.py` (no schema changes, just documentation)

#### Current Model Works:
- `Run.scraped`: Array of JSON objects (varying shapes)
- `Run.extracted`: Structured data from LLM extraction
- `UserList/ListColumn/ListRow`: Target structured data

#### Post Structure Understanding:
```python
# All platforms produce posts with these common elements:
COMMON_POST_FIELDS = {
    "content": "caption/text/description",
    "author": "username/channel/profile", 
    "engagement": "likes/comments/shares/views",
    "media": "images/videos/thumbnails",
    "metadata": "timestamps/duration/links",
    "platform": "instagram/tiktok/youtube"
}

# Platform-specific variations:
INSTAGRAM_POST = {
    "caption": str,
    "like_count": int,
    "comment_count": int, 
    "media_url": str,
    "timestamp": str,
    "is_video": bool,
    "location": dict
}

TIKTOK_POST = {
    "text": str,
    "diggCount": int,
    "commentCount": int,
    "videoURL": str, 
    "createTime": str,
    "author": dict
}

YOUTUBE_POST = {
    "description": str,
    "likeCount": int,
    "commentCount": int,
    "video_url": str,
    "publishedAt": str,
    "channelTitle": str
}
```

### 2.2 Enhanced Extraction System
**Files to create**: `core/services/extraction_service.py`

#### Extraction Prompt Engineering:
```python
class ExtractionService:
    def analyze_scraped_structure(self, scraped_data: list) -> dict:
        """Analyze scraped data to understand available fields"""
        
    def generate_extraction_prompt(self, base_prompt: str, scraped_sample: dict) -> str:
        """Enhance user prompt with field mapping hints"""
        
    def extract_structured_data(self, scraped_data: list, prompt: str) -> dict:
        """Run LLM extraction with field coercion"""
        
    def coerce_to_table_schema(self, extracted_data: list, target_columns: list) -> list:
        """Map extracted data to target table structure"""
```

#### Enhanced Prompt Strategy:
```python
# Base prompt enhancement
ENHANCED_PROMPT_TEMPLATE = """
Extract the following information from social media posts:

User Request: {user_prompt}

Available Data Fields: {available_fields}
Platform Types: {platforms}

Please extract and structure the data into a table format with these columns:
{target_columns}

For each post, provide:
- Content (caption, text, description)
- Author information 
- Engagement metrics (likes, comments, shares, views)
- Media information
- Timestamps
- Platform-specific metadata

Focus on: {extraction_focus}
Output format: JSON array of objects with consistent keys.
"""
```

### 2.3 Dynamic Column Creation
**Files to modify**: `core/views.py` (run_create view)

#### Column Inference Logic:
```python
def infer_columns_from_scraped(scraped_data: list, extraction_prompt: str) -> List[ColumnSuggestion]:
    """Analyze scraped data + prompt to suggest table columns"""
    
    # Sample first few posts to understand structure
    sample_posts = scraped_data[:5]
    
    # Extract all unique field paths
    available_fields = set()
    for post in sample_posts:
        available_fields.update(extract_json_paths(post))
    
    # Map to common column types
    column_suggestions = []
    for field in available_fields:
        column_type = infer_column_type(field, sample_posts)
        column_suggestions.append({
            'name': normalize_column_name(field),
            'type': column_type,
            'source_field': field,
            'platforms': get_platforms_for_field(field, sample_posts)
        })
    
    return column_suggestions
```

## Phase 3: Multi-Source Run Creation UI (Week 3)

### 3.1 Enhanced Run Creation Interface
**Files to modify**: `templates/core/run_create.html`

#### Multi-Step Interface:
1. **Source Configuration**: Add multiple sources with platform-specific forms
2. **Data Preview**: Show sample scraped data structure
3. **Column Planning**: Suggest columns based on data + extraction prompt
4. **Target Selection**: Choose existing list or create new one
5. **Confirmation**: Review complete configuration before execution

#### UI Components:
```html
<!-- Source Management -->
<div id="sources-container">
    <div class="source-item" data-platform="instagram" data-type="profile_scrape">
        <!-- Instagram profile scrape form -->
    </div>
    <div class="source-item" data-platform="tiktok" data-type="search">
        <!-- TikTok search form -->  
    </div>
</div>

<button type="button" id="add-source">+ Add Source</button>

<!-- Dynamic Source Selection Modal -->
<div id="source-modal">
    <h3>Add Data Source</h3>
    <div class="platform-options">
        <button data-platform="instagram">Instagram</button>
        <button data-platform="tiktok">TikTok</button>
        <button data-platform="youtube">YouTube</button>
    </div>
    <div class="type-options">
        <!-- Dynamic based on platform selection -->
    </div>
</div>
```

### 3.2 Real-time Column Preview
**Files to create**: `templates/core/_column_preview.html`

#### Column Suggestion Interface:
```html
<div id="column-preview">
    <h3>Suggested Table Columns</h3>
    <div class="column-suggestions">
        <div class="column-item">
            <input type="checkbox" name="selected_columns" value="content" checked>
            <label>Content (text)</label>
            <span class="type-badge">text</span>
            <span class="platform-badge">All platforms</span>
        </div>
        <div class="column-item">
            <input type="checkbox" name="selected_columns" value="author_username">
            <label>Author Username</label>
            <span class="type-badge">text</span>
            <span class="platform-badge">All platforms</span>
        </div>
    </div>
    
    <div class="custom-columns">
        <h4>Add Custom Columns</h4>
        <input type="text" placeholder="Column name">
        <select class="column-type">
            <option value="text">Text</option>
            <option value="number">Number</option>
            <option value="date">Date</option>
            <option value="url">URL</option>
        </select>
    </div>
</div>
```

## Phase 4: Extraction & Data Processing (Week 3-4)

### 4.1 Enhanced Extraction Prompts
**Files to create**: `core/prompts/`

#### Platform-Aware Extraction:
```markdown
# Multi-Platform Social Media Extraction

## Task
Extract structured information from mixed-platform social media data.

## Input Data
The data contains posts from multiple platforms:
- Instagram: Posts with captions, images, engagement metrics
- TikTok: Videos with text, author info, engagement data  
- YouTube: Videos with descriptions, channel info, statistics

## Required Fields
Based on the user's request: "{user_request}"

Focus on extracting:
1. **Content**: Main text/caption/description
2. **Author**: Creator information (username, display name)
3. **Engagement**: Likes, comments, shares, views
4. **Media**: URLs to images/videos/thumbnails
5. **Timing**: Publication dates/timestamps
6. **Metadata**: Platform-specific relevant information

## Output Format
Return JSON array with consistent field names across platforms:
```json
[
  {
    "content": "Post caption or text",
    "author_username": "creator username", 
    "author_display_name": "creator display name",
    "likes": 123,
    "comments": 45,
    "shares": 12,
    "views": 1500,
    "media_url": "https://...",
    "media_type": "image/video",
    "published_at": "2025-01-15T10:30:00Z",
    "platform": "instagram",
    "post_url": "https://...",
    "extracted_business_info": "...",
    "extracted_location": "...",
    "extracted_contact": "..."
  }
]
```

## Special Instructions
- Normalize field names across platforms (e.g., caption, text, description → content)
- Handle missing gracefully (not all platforms have all fields)
- Focus on business/contact/location extraction as requested
- Preserve platform-specific metadata in separate fields
```

### 4.2 Re-runnable Extraction
**Files to modify**: `core/views.py` (run_detail view)

#### Extraction Re-run Feature:
```python
def rerun_extraction(request, pk):
    run = get_object_or_404(Run, pk=pk)
    
    if request.method == 'POST':
        new_prompt = request.POST.get('extraction_prompt')
        target_columns = request.POST.getlist('target_columns')
        
        # Run extraction with new parameters
        extracted_data = extract_from_scraped(
            run.scraped, 
            new_prompt, 
            target_columns
        )
        
        # Update run with new extraction
        run.extracted = extracted_data
        run.save()
        
        # If target list specified, update it too
        if request.POST.get('update_target_list'):
            update_list_with_extracted_data(run, extracted_data)
        
        return JsonResponse({'success': True, 'extracted': extracted_data})
```

## Phase 5: List Integration & Export (Week 4)

### 5.1 Seamless List Population
**Files to modify**: `core/views.py` (run_create and related)

#### Auto-List Creation:
```python
def create_or_update_list_from_run(run, column_suggestions):
    """Create/update target list based on run configuration"""
    
    # Get or create target list
    if run.input.get('target_list_id'):
        user_list = UserList.objects.get(pk=run.input['target_list_id'])
    else:
        user_list = UserList.objects.create(
            user=run.user,
            name=f"Run {run.pk} - {datetime.now().strftime('%Y-%m-%d')}",
            description=f"Data from multi-source run on {run.created_at}"
        )
    
    # Create columns from suggestions
    for suggestion in column_suggestions:
        if suggestion.get('selected', False):
            ListColumn.objects.get_or_create(
                user_list=user_list,
                name=suggestion['name'],
                defaults={
                    'column_type': suggestion['type'],
                    'description': f"Extracted from {suggestion['source_field']}",
                    'order': ListColumn.objects.filter(user_list=user_list).count()
                }
            )
    
    return user_list
```

### 5.2 Data Population Service
**Files to create**: `core/services/data_population.py`

#### Extracted → List Mapping:
```python
def populate_list_from_extracted(user_list, extracted_data):
    """Populate list rows with structured extracted data"""
    
    columns = {col.name: col for col in user_list.columns.all()}
    
    for item in extracted_data:
        row_data = {}
        
        # Map extracted fields to table columns
        for column_name, column in columns.items():
            if column_name in item:
                row_data[column_name] = item[column_name]
            else:
                # Try to find nested data
                row_data[column_name] = extract_nested_value(item, column_name)
        
        # Create row
        ListRow.objects.create(
            user_list=user_list,
            data=row_data
        )
```

## Phase 6: Testing & Validation (Week 4-5)

### 6.1 Multi-Source Testing
**Files to create**: `core/tests/test_multi_source.py`

#### Test Scenarios:
```python
class MultiSourceTestCase(TestCase):
    def test_mixed_platform_run(self):
        """Test Instagram + TikTok + YouTube in single run"""
        
    def test_platform_specific_configs(self):
        """Test each platform's configuration options"""
        
    def test_extraction_prompt_enhancement(self):
        """Test prompt enhancement with field mapping"""
        
    def test_column_inference_accuracy(self):
        """Test automatic column type inference"""
        
    def test_rerun_extraction(self):
        """Test extraction re-run functionality"""
```

### 6.2 Data Quality Validation
**Files to create**: `core/services/data_validation.py`

#### Validation Rules:
```python
def validate_extracted_data(extracted_data, expected_columns):
    """Validate extracted data quality"""
    
    issues = []
    
    # Check for required columns
    for col in expected_columns:
        if not all(col.get(item) for item in extracted_data):
            issues.append(f"Missing column: {col}")
    
    # Check data type consistency
    for item in extracted_data:
        for field, value in item.items():
            if not validate_field_type(field, value):
                issues.append(f"Type mismatch in {field}: {value}")
    
    return issues
```

## Implementation Benefits

### User Experience Improvements
1. **Unified Interface**: Single form for all platforms and configurations
2. **Intelligent Suggestions**: Automatic column detection from data structure
3. **Flexible Extraction**: Re-runnable extraction with different prompts
4. **Seamless Export**: Direct scraped → extracted → list flow
5. **No Schema Drift**: Dynamic column creation handles any data structure

### Technical Advantages
1. **Apify Integration**: Leverages existing robust actors
2. **Unified Data Model**: Post-centric approach works across platforms
3. **Flexible Extraction**: LLM-based extraction handles varying schemas
4. **Scalable Architecture**: Easy to add new platforms
5. **Backward Compatible**: Doesn't break existing Instagram functionality

## Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 1 | Week 1-2 | Multi-source run form, n8n workflow |
| Phase 2 | Week 2-3 | Enhanced extraction, column inference |
| Phase 3 | Week 3 | Multi-step UI, column preview |
| Phase 4 | Week 3-4 | Re-runnable extraction, prompts |
| Phase 5 | Week 4 | List integration, data population |
| Phase 6 | Week 4-5 | Testing, validation, deployment |

**Total Estimated Timeline**: 5 weeks
**Go-Live Target**: [Date based on project start]

## Next Steps

1. **Immediate**: Start with enhanced Run form for multi-source input
2. **Week 1**: Implement n8n workflow with multiple Apify actors
3. **Week 2**: Build column inference and extraction enhancement
4. **Week 3**: Create multi-step UI with real-time preview
5. **Week 4**: Add re-runnable extraction and list integration
6. **Week 5**: Comprehensive testing and production deployment

---

*This revised plan focuses on the Apify actor architecture and unified post-centric data model, eliminating schema drift through dynamic column creation and enhanced extraction.*
