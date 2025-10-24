# Data Structure Refactoring Plan: Separating Scraped and Extracted Data

## Overview
This plan outlines the refactoring of the Instagram scraper data pipeline to properly separate raw scraped data from processed extracted entities. The goal is to improve data organization, enable better rendering of extracted data in the curation UI, and provide clearer separation of concerns between scraping and entity extraction.

## Current State Analysis

### Existing Data Structure
- **Run.output**: Currently stores an array of post objects directly
- **No separation** between raw scraped data and extracted entities
- **Curation UI** displays raw post data, making it difficult to work with extracted insights

### Problems with Current Approach
- Mixed raw and processed data in single field
- Difficult to render extracted entities effectively
- No clear distinction between scraping output and LLM processing results
- Hard to debug extraction quality or compare raw vs processed data

## Proposed Solution

### 1. Database Schema Changes

#### Update `core/models.py` - Run Model
```python
class Run(models.Model):
    user_id = models.BigIntegerField(null=True)
    n8n_execution_id = models.BigIntegerField(blank=True, null=True, db_index=True)
    input = models.JSONField(null=True)  # Scraping parameters
    scraped = models.JSONField(null=True, help_text="Raw scraped data from Instagram posts")
    extracted = models.JSONField(null=True, help_text="Processed entities extracted from scraped data")
    # Keep output temporarily for backward compatibility
    output = models.JSONField(null=True)  # DEPRECATED: Will be removed after migration
    created_at = models.DateTimeField(auto_now_add=True)
```

**Data Structure:**
- Both `scraped` and `extracted` fields use: `{"result": <data>}` for consistency
- `scraped.result`: Array of raw Instagram post objects
- `extracted.result`: Array of processed entity objects

#### Migration Strategy
1. Add `scraped` and `extracted` fields via Django migration
2. Populate new fields from existing `output` data during migration
3. Keep `output` field temporarily for backward compatibility
4. Remove `output` field in future cleanup phase

### 2. N8N Pipeline Refactoring

#### Current Pipeline Output
```json
[
  {
    "id": "3569152364791366671",
    "type": "Video",
    "caption": "🤩Nouveau bar à flans...",
    "hashtags": ["flan", "patisserie"],
    "locationName": "Paris, France"
  }
]
```

#### New Pipeline Output Structure
```json
{
  "scraped": {
    "result": [
      {
        "id": "3569152364791366671",
        "type": "Video",
        "caption": "🤩Nouveau bar à flans...",
        "hashtags": ["flan", "patisserie"],
        "locationName": "Paris, France",
        "timestamp": "2025-02-16T08:56:26.000Z"
      }
    ]
  },
  "extracted": {
    "result": [
      {
        "type": "business",
        "name": "Paris & Co",
        "category": "bakery",
        "address": "4 rue de la Convention, 75015 Paris",
        "price_range": "€€",
        "specialties": ["flans", "pastries"],
        "confidence": 0.95
      },
      {
        "type": "location",
        "name": "Paris, France",
        "coordinates": {"lat": 48.8566, "lng": 2.3522},
        "venue_type": "city"
      }
    ]
  }
}
```

#### Pipeline Node Changes
1. **Scraping Node**: Outputs raw post data to `scraped.result`
2. **LLM Processing Node**: Takes `scraped.result`, extracts entities to `extracted.result`
3. **Final Output Node**: Combines both under top-level keys

### 3. Backend Code Updates

#### View Changes (`core/views.py`)
- Update `run_detail` to access `run.extracted['result']` instead of `run.output`
- Modify `entity_list` to iterate through `run.extracted['result']`
- Add backward compatibility for existing `output` data during transition

#### New Data Access Pattern
```python
# In entity_list view
for run in runs:
    if run.extracted and 'result' in run.extracted:
        for entity in run.extracted['result']:
            entities.append({
                'data': entity,
                'run_id': run.pk,
                'run_created': run.created_at
            })
    # Fallback to old output format during transition
    elif run.output and isinstance(run.output, list):
        for entity in run.output:
            entities.append({
                'data': entity,
                'run_id': run.pk,
                'run_created': run.created_at
            })
```

### 4. Frontend Template Updates

#### Enhanced Entity Display (`core/templates/core/entity_list.html`)
- **Entity Type Icons**: Different icons for businesses, locations, contacts
- **Rich Metadata Display**: Show confidence scores, categories, extracted fields
- **Collapsible Details**: Expandable sections for full entity data
- **Type-based Filtering**: Filter entities by type (business, location, etc.)

#### Entity Rendering Examples
- **Business Entity**: Name, category, address, price range, specialties
- **Location Entity**: Name, coordinates, venue type, address
- **Contact Entity**: Name, role, contact information
- **Generic Entity**: Fallback display with key-value pairs

### 5. Curation UI Improvements

#### Entity Selection Logic
- Source entities from `run.extracted['result']` for cleaner data
- Maintain traceability to source run
- Add entity type filtering and sorting

#### Collection Management
- Show entity type breakdowns in collection summaries
- Enhanced detail views with categorized entity lists
- Export functionality that respects entity types

### 6. Migration and Deployment Phases

#### Phase 1: Database & Model Changes ✅ COMPLETED
- [x] Deploy model changes and migrations
- [x] Test database schema updates
- [x] Verify backward compatibility

#### Phase 2: Pipeline Updates
- [ ] Modify n8n workflow to output new structure
- [ ] Test pipeline with sample data
- [ ] Validate extracted data quality

#### Phase 3: Backend Updates ✅ COMPLETED
- [x] Update views to use new data structure
- [x] Test curation workflow
- [x] Update export functionality

#### Phase 4: Frontend Updates ✅ COMPLETED
- [x] Deploy template changes
- [x] Test entity rendering
- [x] Validate user experience

#### Phase 5: Cleanup
- [ ] Remove deprecated `output` field
- [ ] Update documentation
- [ ] Archive old sample data

## Benefits

### Data Organization
- **Clear Separation**: Raw scraped data vs. processed extracted entities
- **Better Debugging**: Compare raw input with extraction results
- **Scalability**: Easy to add new entity types without pipeline changes

### User Experience
- **Rich Entity Display**: Extracted entities shown with proper metadata and formatting
- **Improved Curation**: Work with clean, structured entity data
- **Better Filtering**: Filter and sort by entity types and properties

### Development Benefits
- **Maintainability**: Clear separation of scraping vs. processing logic
- **Testing**: Easier to test extraction quality independently
- **Extensibility**: New extraction types can be added without breaking existing code

## Risks and Mitigations

### Data Migration Risk
- **Risk**: Existing data in `output` field may be lost or corrupted
- **Mitigation**: Keep `output` field during transition, thorough testing of migration

### Pipeline Compatibility
- **Risk**: New pipeline structure breaks existing integrations
- **Mitigation**: Phased deployment, backward compatibility in views

### User Experience Disruption
- **Risk**: Changes to data display confuse users
- **Mitigation**: Gradual rollout, user testing, clear communication

## Success Criteria

- [ ] Extracted entities display properly in curation UI with rich metadata
- [ ] Users can filter and sort entities by type and properties
- [ ] Export functionality works with new entity structure
- [ ] Pipeline produces clean separation of scraped vs. extracted data
- [ ] No data loss during migration
- [ ] Backward compatibility maintained during transition

## Timeline Estimate

- **Phase 1**: 1-2 days (database changes)
- **Phase 2**: 2-3 days (pipeline updates)
- **Phase 3**: 1-2 days (backend updates)
- **Phase 4**: 1-2 days (frontend updates)
- **Phase 5**: 0.5 days (cleanup)

**Total**: 5-10 days depending on testing and validation needs.