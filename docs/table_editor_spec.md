# Table Editor (HTMX + Alpine.js) – MVP Functional Specification
**Version:** 0.1  
**Date:** 2025-11-01  
**Status:** **DEPRECATED** - See table_editor_requirements.md v2.0 for AG-Grid implementation

---

## 1. Overview
This document outlines the functional and non-functional requirements for the MVP version of a web-based table editor built using **HTMX** and **Alpine.js**. The goal is to provide a lightweight, responsive, and extensible in-browser editor with batch save functionality, dynamic columns, and modern table management UX.

---

## 2. Functional Requirements

### 2.1 Data Display
- Display data in a tabular format with rows as records and columns as fields.
- Column headers show field names and a dropdown for actions.
- A dummy “+” column appears at the rightmost edge for adding new columns dynamically.

### 2.2 Inline Cell Editing
- Clicking a cell replaces its content with an editable input (text, number, date, or select).
- HTMX requests (`hx-get`, `hx-post`) load and save editable fragments.
- Enter confirms, Escape cancels edits.
- Saved cells re-render with updated display values.

### 2.3 Column Management
Each column header dropdown provides:
- **Edit Column Name**
- **Edit Column Type** (text, number, date, select, checkbox)
- **Insert Column Left / Right**
- **Delete Column** (confirmation required)

#### Submenu Behavior
- Submenus expand outward depending on available viewport space.
- On mobile, dropdowns appear as modal sheets.

#### Add New Column
- Clicking the dummy “+” column adds a new column with default settings:
  - Name: “New Column”
  - Type: `text`
  - Empty values for all rows

### 2.4 Row Management
- Add and delete rows dynamically.
- New rows appear at the bottom.
- Deletion prompts confirmation before removing.

### 2.5 Batch Save
- Edits are stored in Alpine.js state until committed.
- A **Save Changes** button appears when unsaved edits exist.
- A single HTMX POST request saves all modified data in batch.
- Table re-renders after success with confirmation feedback.

### 2.6 Sorting, Filtering, and Search
- Column header click toggles sort order.
- Each column supports filters (text search, numeric range, date, or select).
- Global search bar filters across all visible columns.
- HTMX used for asynchronous reloads on sort/filter changes.

### 2.7 Field Types
Supported column types:
- Text
- Number
- Date
- Select
- Checkbox

Each has its own editing UI and validation rules.

### 2.8 Validation
- Alpine.js handles basic client-side validation (required, numeric, date).
- Django backend performs full validation on save.
- Invalid cells are visually highlighted.

### 2.9 Permissions
- Only authenticated users may edit.
- Permissions control access to column and row management actions.

---

## 3. Non-Functional Requirements

### 3.1 Performance
- Table render time ≤ 2 seconds for ≤ 1,000 rows.
- Inline edits ≤ 500 ms latency.
- Batch save completes ≤ 1 second.

### 3.2 Scalability
- Server supports server-side pagination, filtering, sorting.
- Handle 100+ columns with horizontal scroll.

### 3.3 Responsiveness
- Desktop: dropdowns/submenus positioned contextually.
- Mobile: column menus open as modal sheets; horizontal scroll enabled.

### 3.4 Reliability
- Unsaved edits persist in Alpine.js state.
- Failed saves retain unsaved edits with retry option.

### 3.5 Maintainability
- Clear separation of concerns:
  - Django: persistence and validation
  - HTMX: partial rendering and async swaps
  - Alpine.js: local state and UI logic
- Modular Django partials for `_table.html`, `_row.html`, `_cell.html`, etc.

### 3.6 Security
- CSRF protection for all write actions.
- Server-side input validation and sanitization.
- Strict permission enforcement.

### 3.7 Accessibility
- Full keyboard navigation (Tab, Enter, Esc).
- ARIA roles for table, headers, and modals.
- Accessible focus states and error feedback.

### 3.8 Visual Design
- Notion/Airtable-inspired clean minimal UI.
- TailwindCSS styling.
- Subtle hover and active highlights for cells and headers.

---

## 4. Deferred / Backlog Features
- Edit history / Undo
- Collaborative editing
- Import/export (CSV, Excel)
- Formula fields
- Saved views (filters/sorts)

---

## 5. Architecture Summary

| Layer | Role | Technology |
|-------|------|-------------|
| **Backend** | Validation, persistence, CSRF protection | Django |
| **Frontend** | Table rendering, partials | Django templates |
| **Dynamic Behaviour** | Inline edits, async updates | HTMX |
| **Client Logic** | Local state, validation, undo | Alpine.js |
| **Styling** | Responsive layout | TailwindCSS |

---

**Author:** Evan O’Keefe  
**Reviewed by:** _TBD_  
**Next Steps:** Implementation planning, UI wireframes, and API design.
