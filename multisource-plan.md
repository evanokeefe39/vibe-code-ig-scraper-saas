# Multi-Source Scraper Implementation Plan

## Overview
This document outlines the plan to extend the current Instagram-only scraper SaaS to support multiple social media platforms (TikTok, YouTube) using Apify actors while maintaining the existing MVP functionality.

## Current State
- **Base**: MVP branch with Instagram scraper fully functional
- **Infrastructure**: Django backend with n8n workflow orchestration
- **Database**: PostgreSQL with existing Run model (scraped/extracted JSON fields)
- **V2 Interfaces**: Already defined OpenAPI specs for Instagram, TikTok, and YouTube Apify actors
- **Data Flow**: `scraped` (raw JSON array) → `extracted` (structured data) → UserList export

## Architecture Understanding

### Apify Actor Integration
- **Instagram Actor**: `apify/instagram-scraper` - profiles, posts, reels
- **TikTok Actor**: `apify/tiktok-scraper` - profiles, videos, search
- **YouTube Actor**: `apify/youtube-scraper` - channel videos, search results
- **Unified Data Model**: All platforms produce "post" data (videos, images, text)

### Key Insight
Instagram posts/reels ≈ TikTok videos ≈ YouTube videos/shorts
All can be treated as unified "posts" with platform-specific metadata.

## Implementation Phases

## Phase 1: Enhanced Run Creation Interface

### 1.1 Multi-Source Form Enhancement
**Files to modify**: `core/forms.py`

#### Enhanced RunForm:
```python
class RunForm(forms.ModelForm):
    # Dynamic source management
    sources = forms.JSONField(initial=[])
    
    # Platform-specific configurations
    instagram_profiles = forms.CharField(required=False)
    instagram_search = forms.CharField(required=False)
    tiktok_profiles = forms.CharField(required=False)
    tiktok_search = forms.CharField(required=False)
    youtube_search = forms.CharField(required=False)
    
    # Column inference
    auto_infer_columns = forms.BooleanField(initial=True)
    custom_columns = forms.JSONField(required=False)
```

### 1.2 Dynamic Column Creation
**Files to modify**: `core/views.py`

#### Key Features:
- Analyze scraped data structure to infer columns
- Allow users to customize inferred columns
- Support platform-specific field mapping
- Handle schema drift gracefully

### 1.3 Multi-Step UI
**Files to modify**: `templates/core/run_create.html`

#### UI Flow:
1. **Source Selection**: Add multiple sources with platform-specific inputs
2. **Column Preview**: Show inferred columns from sample data
3. **Customization**: Allow column editing and type selection
4. **Execution**: Run multi-source scraping

### 1.4 Enhanced n8n Workflow
**Files to modify**: `n8n/v2/`

#### Workflow Features:
- Multiple Apify actor nodes (one per platform)
- Dynamic source routing
- Unified data aggregation
- Enhanced LLM extraction with platform awareness

## Phase 2: Data Structure & Extraction Enhancement

### 2.1 Extraction Service
**Files to create**: `core/services/extraction_service.py`

#### Service Features:
- Platform-aware extraction prompts
- Field coercion and type conversion
- Re-runnable extraction with different prompts
- Quality scoring and validation

### 2.2 Column Inference Logic
**Files to create**: `core/services/data_population.py`

#### Inference Strategy:
- Analyze first 10 items from each platform
- Identify common patterns (caption, likes, comments, etc.)
- Map platform-specific fields to unified columns
- Handle missing data gracefully

### 2.3 Enhanced Extraction Prompts
**Files to modify**: `n8n/v2/prompts/`

#### Prompt Strategy:
- Platform-specific field mapping
- Unified output schema
- Error handling for missing data
- Type conversion instructions

## Phase 3: Multi-Source UI Development

### 3.1 Dynamic Source Management
**Files to modify**: `templates/core/run_create.html`

#### UI Components:
- Add/remove source buttons
- Platform-specific input forms
- Real-time validation
- Source preview cards

### 3.2 Column Preview Interface
**Files to create**: `templates/core/column_preview.html`

#### Features:
- Live column inference from sample data
- Column type selection (text, number, date, etc.)
- Field mapping preview
- Validation feedback

### 3.3 Enhanced Run Detail View
**Files to modify**: `templates/core/run_detail.html`

#### Features:
- Multi-source execution status
- Platform-specific error reporting
- Extraction re-run functionality
- Data quality metrics

## Phase 4: Re-runnable Extraction

### 4.1 Extraction Re-run Interface
**Files to modify**: `core/views.py`, `templates/core/run_detail.html`

#### Features:
- Edit extraction prompt
- Preview extraction results
- Apply to existing scraped data
- Compare extraction versions

### 4.2 Enhanced Prompt Templates
**Files to create**: `n8n/v2/prompts/multi_platform_extraction.md`

#### Template Features:
- Platform-specific field handling
- Unified output schema
- Error recovery instructions
- Quality validation rules

### 4.3 Seamless List Population
**Files to modify**: `core/views.py`

#### Flow:
- scraped → extracted → UserList (direct)
- No manual column setup required
- Automatic type conversion
- Validation and error handling

## Phase 5: Testing & Deployment

### 5.1 Multi-Source Testing
**Files to create**: `core/tests/test_multi_source.py`

#### Test Scenarios:
- Multi-source run creation
- Column inference accuracy
- Cross-platform data extraction
- Error handling and recovery

### 5.2 Data Validation
**Files to create**: `core/services/validation_service.py`

#### Validation Features:
- Data type checking
- Quality scoring
- Anomaly detection
- Platform-specific validation

### 5.3 Production Deployment
**Files to modify**: `docker-compose.yml`, environment configs

#### Requirements:
- Apify actor credentials
- Enhanced error monitoring
- Performance optimization
- User feedback collection

## Key Implementation Files

### Core Files to Modify:
- `core/forms.py` - Enhanced multi-source form
- `core/views.py` - Dynamic column creation and extraction logic
- `templates/core/run_create.html` - Multi-step interface
- `templates/core/run_detail.html` - Enhanced run management

### New Files to Create:
- `core/services/extraction_service.py` - Enhanced LLM extraction
- `core/services/data_population.py` - Column inference and data population
- `core/services/validation_service.py` - Data validation and quality
- `templates/core/column_preview.html` - Column preview interface

### n8n Workflow Updates:
- Multi-actor workflow with dynamic routing
- Enhanced extraction prompts
- Platform-specific error handling
- Unified data aggregation

## Success Criteria

### Functional Requirements:
- ✅ Users can add multiple sources in single run
- ✅ System automatically infers columns from scraped data
- ✅ Users can customize inferred columns before extraction
- ✅ Extraction can be re-run with different prompts
- ✅ Seamless flow from scraped → extracted → UserList

### Technical Requirements:
- ✅ Maintains existing scraped/extracted data flow
- ✅ Handles schema drift through dynamic column creation
- ✅ Supports platform-specific field mapping
- ✅ Provides re-runnable extraction with quality feedback
- ✅ Eliminates manual column setup requirement

## Implementation Dependencies

### Critical Path Items:
1. ✅ V2 Interface Specifications (already complete)
2. 🔄 Multi-source form enhancement
3. 🔄 Dynamic column inference logic
4. 🔄 Enhanced extraction service
5. 🔄 Multi-step UI development
6. 🔄 Re-runnable extraction interface

### External Dependencies:
- Apify actor credentials and rate limits
- LLM API for enhanced extraction
- Platform-specific data format monitoring

## Risk Mitigation

### Technical Risks:
- **Schema Drift**: Dynamic column creation handles this automatically
- **Platform Data Changes**: Flexible inference logic adapts to new fields
- **Extraction Quality**: Re-runnable extraction allows prompt optimization

### Business Risks:
- **User Experience**: Multi-step UI guides users through complex process
- **Data Quality**: Validation service ensures high-quality extracted data
- **Performance**: Efficient column inference minimizes processing time

---

*This plan reflects the Apify-based architecture and focuses on immediate implementation.*