/**
 * AG-Grid Manager
 * Handles AG-Grid initialization and operations for table editor
 */

class AgGridManager {
    constructor(gridId, data) {
        this.gridId = gridId;
        this.data = data;
        this.gridApi = null;
        this.columnApi = null;
        this.selectedRows = [];
        
        this.init();
    }

    init() {
        // Detect column types and format data
        const processedColumns = this.processColumns(this.data.columns);
        const processedRows = this.processRows(this.data.rows);

        // Grid options
        const gridOptions = {
            columnDefs: processedColumns,
            rowData: processedRows,
            rowSelection: {
                mode: 'multiRow',
                checkboxes: true, // Use built-in checkboxes
                headerCheckbox: true, // Add header checkbox
                enableClickSelection: true,
                enableSelectionWithoutKeys: false
            },
            enableCellTextSelection: true,
            cellSelection: false,
            pagination: true,
            paginationPageSize: 20,
            paginationPageSizeSelector: [10, 20, 50],
            domLayout: 'normal',
            animateRows: true,
            suppressDragLeaveHidesColumns: true,
            onGridReady: this.onGridReady.bind(this),
            onSelectionChanged: this.onSelectionChanged.bind(this),
            onCellValueChanged: this.onCellValueChanged.bind(this),
            onColumnMoved: this.onColumnMoved.bind(this),
            onColumnResized: this.onColumnResized.bind(this),
            onSortChanged: this.onSortChanged.bind(this),
            onFilterChanged: this.onFilterChanged.bind(this),
            components: {
                editableHeader: this.EditableHeaderComponent
            }
        };

        // Initialize grid
        const gridElement = document.getElementById(this.gridId);
        this.gridApi = agGrid.createGrid(gridElement, gridOptions);
        // columnApi will be set in onGridReady

        // Setup event listeners
        this.setupEventListeners();
        
        // Update UI
        this.updateRowCount();
        this.updateFooterInfo();
    }

    processColumns(columns) {
        return columns.map(col => {
            const detectedType = TypeDetector.detectColumnType(col.field, this.data.rows);
            const columnDef = {
                headerName: col.name,
                field: col.field,
                colId: col.id,
                sortable: true,
                resizable: true,
                filter: true,
                filterParams: {
                    buttons: ['reset', 'apply']
                },
                editable: false, // Read-only by default
                ...this.getColumnConfig(detectedType)
            };

            return columnDef;
        });
    }

    processRows(rows) {
        return rows.map(row => {
            const processedRow = { ...row };
            
            // Process each cell value based on column type
            Object.keys(processedRow).forEach(key => {
                if (key !== 'id') {
                    const detectedType = TypeDetector.detectColumnType(key, this.data.rows);
                    processedRow[key] = TypeDetector.formatValue(processedRow[key], detectedType);
                }
            });
            
            return processedRow;
        });
    }

    getColumnConfig(detectedType) {
        const self = this;
        const configs = {
            text: { filter: 'agTextColumnFilter', cellRenderer: function(params) { return self.textCellRenderer(params); } },
            number: { filter: 'agNumberColumnFilter', cellRenderer: function(params) { return self.numberCellRenderer(params); }, comparator: this.numberComparator.bind(this) },
            date: { filter: 'agDateColumnFilter', cellRenderer: function(params) { return self.dateCellRenderer(params); }, comparator: this.dateComparator.bind(this) },
            url: { filter: 'agTextColumnFilter', cellRenderer: function(params) { return self.urlCellRenderer(params); } },
            boolean: { filter: 'agSetColumnFilter', cellRenderer: function(params) { return self.booleanCellRenderer(params); }, cellEditor: 'agCheckboxCellEditor' }
        };
        return configs[detectedType] || configs.text;
    }

    // Cell Renderers
    textCellRenderer(params) {
        const value = params.value;
        if (value === null || value === undefined) return '';
        return `<span class="text-gray-900">${AgGridManager.escapeHtml(value.toString())}</span>`;
    }

    numberCellRenderer(params) {
        const value = params.value;
        if (value === null || value === undefined) return '';
        if (isNaN(value)) return params.value;
        return `<span class="text-gray-900 font-medium">${Number(value).toLocaleString()}</span>`;
    }

    dateCellRenderer(params) {
        const value = params.value;
        if (!value) return '';
        
        try {
            const date = new Date(value);
            if (isNaN(date.getTime())) return value;
            
            return `<span class="text-gray-900">${date.toLocaleDateString()}</span>`;
        } catch (e) {
            return value;
        }
    }

    urlCellRenderer(params) {
        const value = params.value;
        if (!value || !value.startsWith('http')) return AgGridManager.textCellRendererStatic(params);
        const displayText = value.length > 50 ? value.substring(0, 47) + '...' : value;
        return `<a href="${value}" target="_blank" class="text-blue-600 hover:text-blue-800 underline" title="${value}">${displayText}</a>`;
    }

    booleanCellRenderer(params) {
        const value = params.value;
        if (value === null || value === undefined) return '';
        
        const isChecked = Boolean(value);
        return `
            <div class="flex items-center justify-center">
                <input 
                    type="checkbox" 
                    ${isChecked ? 'checked' : ''} 
                    disabled
                    class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                >
            </div>
        `;
    }

    // Comparators
    numberComparator(a, b) {
        const numA = parseFloat(a);
        const numB = parseFloat(b);
        
        if (isNaN(numA) && isNaN(numB)) return 0;
        if (isNaN(numA)) return -1;
        if (isNaN(numB)) return 1;
        
        return numA - numB;
    }

    dateComparator(a, b) {
        if (!a && !b) return 0;
        if (!a) return -1;
        if (!b) return 1;
        
        const dateA = new Date(a);
        const dateB = new Date(b);
        
        return dateA.getTime() - dateB.getTime();
    }

    // Grid Event Handlers
    onGridReady(params) {
        this.gridApi = params.api;
        // In newer AG-Grid versions, columnApi is part of the main api
        this.columnApi = params.api;
        // Auto-size columns initially
        setTimeout(() => {
            try {
                this.gridApi.autoSizeAllColumns(false);
            } catch (e) {
                console.log('Auto-size columns not available:', e);
            }

        }, 100);
    }

    onSelectionChanged() {
        this.selectedRows = this.gridApi.getSelectedRows();
        this.updateSelectedCount();
        this.updateDeleteButton();
    }

    onCellValueChanged(params) {
        // Handle cell value changes if needed in future
        console.log('Cell value changed:', params);
    }

    onColumnMoved(params) {
        console.log('Column moved:', params);
    }

    onColumnResized(params) {
        if (params.finished) {
            console.log('Column resized:', params);
        }
    }

    onSortChanged(params) {
        console.log('Sort changed:', params);
    }

    onFilterChanged(params) {
        this.updateRowCount();
    }

    // Event Listeners
    setupEventListeners() {
        // Global search
        const searchInput = document.getElementById('global-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.gridApi.setGridOption('quickFilterText', e.target.value);
            });
        }





        // Delete selected button
        const deleteBtn = document.getElementById('delete-selected-btn');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', () => {
                this.deleteSelectedRows();
            });
        }

        // Export CSV button
        const exportBtn = document.getElementById('export-csv-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                this.exportToCsv();
            });
        }

        // Table Settings button
        const settingsBtn = document.getElementById('table-settings-btn');
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => {
                this.openTableSettings();
            });
        }
    }

    // UI Updates
    updateRowCount() {
        const rowCount = this.gridApi.getDisplayedRowCount();
        const totalCount = this.data.rows.length;
        const countElement = document.getElementById('row-count');
        
        if (countElement) {
            if (rowCount === totalCount) {
                countElement.textContent = `(${totalCount} rows)`;
            } else {
                countElement.textContent = `(${rowCount} of ${totalCount} rows)`;
            }
        }
    }

    updateSelectedCount() {
        // Update button title with selected count
        const deleteBtn = document.getElementById('delete-selected-btn');
        if (deleteBtn) {
            deleteBtn.title = this.selectedRows.length > 0 
                ? `Delete Selected (${this.selectedRows.length})` 
                : 'Delete Selected';
        }
    }

    updateDeleteButton() {
        const deleteBtn = document.getElementById('delete-selected-btn');
        if (deleteBtn) {
            deleteBtn.disabled = this.selectedRows.length === 0;
        }
    }

    updateFooterInfo() {
        const footerElement = document.getElementById('footer-info');
        if (footerElement) {
            const totalRows = this.data.rows.length;
            const totalCols = this.data.columns.length;
            footerElement.textContent = `${totalRows} rows × ${totalCols} columns`;
        }
    }



    showAddColumnModal() {
        const modal = document.getElementById('add-column-modal');
        if (modal) {
            modal.classList.remove('hidden');
            document.getElementById('new-column-name').focus();
        }
    }

    deleteSelectedRows() {
        if (this.selectedRows.length === 0) return;

        if (confirm(`Are you sure you want to delete ${this.selectedRows.length} selected row(s)?`)) {
            // Get IDs of selected rows
            const selectedIds = this.selectedRows.map(row => row.id);
            
            // Send delete request to Django
            fetch(`/lists/${this.data.listId}/delete-rows/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({ ids: selectedIds })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Remove rows from grid
                    this.gridApi.applyTransaction({
                        remove: this.selectedRows
                    });
                    
                    // Clear selection
                    this.selectedRows = [];
                    this.updateSelectedCount();
                    this.updateDeleteButton();
                    this.updateRowCount();
                } else {
                    alert('Error deleting rows: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error deleting rows:', error);
                alert('Error deleting rows');
            });
        }
    }

    exportToCsv() {
        // Simple CSV export with all data and headers
        const dataToExport = this.data.rows;
        const columnDefs = this.gridApi.getColumnDefs();
        
        // Build CSV content
        let csvContent = '';
        
        // Add headers
        const headers = columnDefs.map(col => col.headerName || col.field || '');
        csvContent += headers.map(header => `"${header}"`).join(',') + '\n';
        
        // Add data rows
        dataToExport.forEach(row => {
            const rowData = columnDefs.map(col => {
                const value = row[col.field] || '';
                return `"${value.toString().replace(/"/g, '""')}"`;
            });
            csvContent += rowData.join(',') + '\n';
        });
        
        // Create and download file
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `table-export-${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    openTableSettings() {
        this.loadCurrentSettings();
        document.getElementById('table-settings-modal').classList.remove('hidden');
    }

    // Utility methods
    getCsrfToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return decodeURIComponent(value);
            }
        }
        return '';
    }

    static escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    static textCellRendererStatic(params) {
        const value = params.value;
        if (value === null || value === undefined) return '';
        return `<span class="text-gray-900">${AgGridManager.escapeHtml(value.toString())}</span>`;
    }



    loadCurrentSettings() {
        // Setup delete list confirmation
        this.setupDeleteListConfirmation();
    }

    applyTableSettings() {
        closeTableSettingsModal();
    }



    setupDeleteListConfirmation() {
        const confirmationInput = document.getElementById('delete-list-confirmation');
        const confirmBtn = document.getElementById('confirm-delete-list-btn');
        
        if (!confirmationInput || !confirmBtn) return;
        
        // Get list name from page title if not in data
        const listName = this.data.listName || document.querySelector('h1')?.textContent?.trim() || '';
        
        // Remove existing listener if any
        if (this._deleteListHandler) {
            confirmationInput.removeEventListener('input', this._deleteListHandler);
        }
        
        // Create new handler
        this._deleteListHandler = (e) => {
            const isMatch = e.target.value.trim() === listName;
            confirmBtn.disabled = !isMatch;
        };
        
        // Add new listener
        confirmationInput.addEventListener('input', this._deleteListHandler);
        
        // Initial check
        const isMatch = confirmationInput.value.trim() === listName;
        confirmBtn.disabled = !isMatch;
    }

    // Editable Header Component (for future use)
    EditableHeaderComponent() {}
}

// Global functions for modal handling
function closeAddColumnModal() {
    const modal = document.getElementById('add-column-modal');
    if (modal) {
        modal.classList.add('hidden');
        document.getElementById('new-column-name').value = '';
        document.getElementById('new-column-type').value = 'text';
    }
}

function closeTableSettingsModal() {
    const modal = document.getElementById('table-settings-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
    
    // Clean up delete list listener
    if (window.agGridManager && window.agGridManager._deleteListHandler) {
        const confirmationInput = document.getElementById('delete-list-confirmation');
        if (confirmationInput) {
            confirmationInput.removeEventListener('input', window.agGridManager._deleteListHandler);
        }
        window.agGridManager._deleteListHandler = null;
    }
}

function applyTableSettings() {
    if (window.agGridManager) {
        window.agGridManager.applyTableSettings();
    }
}

function addNewColumn() {
    const name = document.getElementById('new-column-name').value.trim();
    const type = document.getElementById('new-column-type').value;
    
    if (!name) {
        alert('Please enter a column name');
        return;
    }

    // Send add column request to Django
    fetch(`/lists/${window.agGridManager.data.listId}/add-column/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': window.agGridManager.getCsrfToken()
        },
        body: JSON.stringify({ name, type })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Add column to grid
            const newColumn = {
                headerName: name,
                field: data.field,
                colId: data.id,
                ...window.agGridManager.getColumnConfig(type)
            };
            
            window.agGridManager.columnApi.applyColumnsAsync([newColumn]);
            closeAddColumnModal();
        } else {
            alert('Error adding column: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error adding column:', error);
        alert('Error adding column');
    });
}

function confirmDeleteList() {
    if (!window.agGridManager) return;
    
    // Get list name from page title if not in data
    const listName = window.agGridManager.data.listName || document.querySelector('h1')?.textContent?.trim() || '';
    const confirmationInput = document.getElementById('delete-list-confirmation');
    const enteredName = confirmationInput?.value?.trim();
    
    if (enteredName !== listName) {
        return;
    }
    
    // Create and submit form for deletion
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/lists/${window.agGridManager.data.listId}/delete/`;
    
    // Add CSRF token
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = window.agGridManager.getCsrfToken();
    form.appendChild(csrfInput);
    
    document.body.appendChild(form);
    form.submit();
}