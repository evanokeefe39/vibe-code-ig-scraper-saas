# Table Editor Requirements - AG-Grid Implementation
**Version:** 2.0  
**Date:** 2025-11-07  
**Status:** Active  
**Technology:** AG-Grid (JavaScript Data Grid)

---

## Overview
This document outlines requirements for migrating from the custom HTMX/Alpine.js table editor to AG-Grid. The new implementation focuses on read-first functionality with enterprise-grade features while maintaining simplicity and performance.

**Previous Implementation:** `docs/table_editor_spec.md` (Version 1.0) - **DEPRECATED**

---

## Core Requirements

### 1. Data Display & Interaction
- **Read-first approach** - Table is read-only by default
- **Resizable columns** - Users can drag column borders to resize
- **Reorderable columns** - Drag and drop column headers to reorder
- **Sortable columns** - Click headers to sort (ascending/descending)
- **Filterable columns** - Each column has individual filter capability
- **Global search** - Search bar above table searches all columns

### 2. Data Type Handling
- **Automatic type detection** - Detect data types on load:
  - Text (default)
  - Numbers
  - Dates
  - URLs
  - Boolean values
- **Smart formatting** - Apply appropriate formatting based on detected type:
  - URLs become clickable links
  - Numbers get proper formatting
  - Dates get locale-appropriate formatting
  - Boolean values show as checkboxes/toggles

### 3. Row Management
- **Checkbox selection column** - First column for row selection
- **Bulk operations** - Delete selected rows with confirmation
- **Pagination options** - User can choose: 10, 20, 50, or all records
- **Infinite scroll** - When "all" is selected, switch to infinite scroll mode

### 4. Column Management
- **Editable column names** - Inline editing in column headers (if simple to implement)
- **Add columns** - Button to add new columns with default settings
- **Delete columns** - Remove columns with confirmation dialog

---

## Technical Implementation

### AG-Grid Features Mapping

| Requirement | AG-Grid Feature | Configuration |
|-------------|------------------|---------------|
| Resizable columns | `resizable: true` | Column definition |
| Reorderable columns | `draggableColumns: true` | Grid option |
| Sortable columns | `sortable: true` | Column definition |
| Filterable columns | `filter: 'agTextColumnFilter'` | Column definition |
| Global search | `quickFilterText` | Grid option |
| Checkbox selection | `rowSelection: 'multiple'` | Grid option |
| Pagination | `pagination: true` | Grid option |
| Infinite scroll | `rowModelType: 'infinite'` | Grid option |
| Type detection | Custom logic | JavaScript module |

### File Structure

```
core/templates/core/partials/
├── _table_editor.html (DEPRECATED - keep as fallback)
├── _ag_grid_table.html (NEW - AG-Grid implementation)
└── _ag_grid_config.html (NEW - grid configuration)

core/static/js/
├── ag-grid-manager.js (NEW - AG-Grid initialization)
├── type-detector.js (NEW - automatic type detection)
└── table-editor.js (EXISTING - may be deprecated)

docs/
├── table_editor_spec.md (DEPRECATED)
└── table_editor_requirements.md (THIS FILE - ACTIVE)
```

---

## Data Flow

### Django Backend Integration
1. **Data Format Conversion** - Convert Django queryset to AG-Grid format
2. **Column Definitions** - Generate from ListColumn model
3. **Row Data** - Generate from CuratedItem model  
4. **Bulk Operations** - Django views for delete selected rows
5. **Column Management** - Django views for add/delete columns

### Frontend Data Flow
1. **Initial Load** - Django renders initial data into JavaScript
2. **AG-Grid Initialization** - Grid loads with column definitions and row data
3. **Type Detection** - JavaScript analyzes data and applies formatting
4. **User Interactions** - AG-Grid handles sorting, filtering, pagination
5. **Backend Operations** - AJAX calls for bulk operations (delete, column changes)

---

## Performance Requirements

### Target Performance
- **Initial Load:** ≤ 2 seconds for up to 1,000 rows
- **Sorting:** ≤ 500ms for any column
- **Filtering:** ≤ 300ms response time
- **Pagination:** ≤ 200ms between pages
- **Infinite Scroll:** Smooth loading for large datasets

### Scalability
- **Small datasets:** < 100 rows - client-side pagination
- **Medium datasets:** 100-1,000 rows - client-side with virtualization
- **Large datasets:** > 1,000 rows - server-side operations

---

## User Experience Requirements

### Responsive Design
- **Desktop:** Full functionality with hover states and tooltips
- **Tablet:** Touch-friendly controls, adjusted column widths
- **Mobile:** Horizontal scroll, simplified controls

### Accessibility
- **Keyboard navigation:** Full keyboard support
- **Screen reader:** ARIA labels and announcements
- **Focus management:** Logical tab order and focus indicators

### Visual Design
- **Consistent styling:** Match existing TailwindCSS design
- **Hover states:** Clear visual feedback
- **Loading states:** Indicators for async operations
- **Error states:** Clear error messages and recovery options

---

## Migration Strategy

### Phase 1: Basic Implementation
1. Create new AG-Grid template alongside existing one
2. Implement basic read-only table with core features
3. Add search, sort, filter, resize, reorder
4. Test with existing data

### Phase 2: Row & Column Management
1. Add checkbox selection and bulk delete
2. Implement pagination with size options
3. Add infinite scroll for "all" option
4. Add column add/delete functionality

### Phase 3: Advanced Features
1. Implement automatic type detection
2. Add smart formatting (URLs, dates, numbers)
3. Add inline column name editing
4. Performance optimization and testing

### Rollback Plan
- **Keep old implementation** as fallback
- **Feature flag** to switch between implementations
- **Gradual rollout** - test with small datasets first
- **Monitoring** - track performance and user feedback

---

## Success Criteria

### Functional Success
- ✅ All current features work with AG-Grid
- ✅ Performance meets or exceeds current implementation
- ✅ User experience is improved
- ✅ Code is maintainable and extensible

### Technical Success
- ✅ 90% reduction in custom code
- ✅ Better performance with large datasets
- ✅ Easier to add new features
- ✅ Robust error handling and validation

---

**Author:** Evan O'Keefe  
**Previous Version:** table_editor_spec.md v1.0 (DEPRECATED)  
**Next Steps:** Phase 1 implementation