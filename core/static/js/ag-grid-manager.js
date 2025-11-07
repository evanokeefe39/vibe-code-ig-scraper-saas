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
            rowSelection: 'multiple',
            enableCellTextSelection: true,
            suppressRowClickSelection: false,
            rowMultiSelectWithClick: true,
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
        this.columnApi = this.gridApi;

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

            // Add checkbox column as first column
            if (col.field === 'checkbox') {
                columnDef.headerCheckboxSelection = true;
                columnDef.checkboxSelection = true;
                columnDef.width = 50;
                columnDef.maxWidth = 50;
                columnDef.resizable = false;
                columnDef.sortable = false;
                columnDef.filter = false;
            }

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
        const configs = {
            text: { filter: 'agTextColumnFilter', cellRenderer: this.textCellRenderer.bind(this) },
            number: { filter: 'agNumberColumnFilter', cellRenderer: this.numberCellRenderer.bind(this), comparator: this.numberComparator.bind(this) },
            date: { filter: 'agDateColumnFilter', cellRenderer: this.dateCellRenderer.bind(this), comparator: this.dateComparator.bind(this) },
            url: { filter: 'agTextColumnFilter', cellRenderer: this.urlCellRenderer.bind(this) },
            boolean: { filter: 'agSetColumnFilter', cellRenderer: this.booleanCellRenderer.bind(this), cellEditor: 'agCheckboxCellEditor' }
        };
        return configs[detectedType] || configs.text;
    }
        };

        return configs[detectedType] || configs.text;
    }

    // Cell Renderers
    textCellRenderer(params) {
        const value = params.value;
        if (value === null || value === undefined) return '';
        return `<span class="text-gray-900">${this.escapeHtml(value.toString())}</span>`;
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
        if (!value || !value.startsWith('http')) return this.textCellRenderer.call(this, params);
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
        // Auto-size columns initially
        setTimeout(() => {
            this.gridApi.autoSizeAllColumns(false);
            // Initialize pagination controls
            this.updatePaginationControls();
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
        this.updatePaginationControls();
    }

    // Event Listeners
    setupEventListeners() {
        // Global search
        const searchInput = document.getElementById('global-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.gridApi.setQuickFilter(e.target.value);
            });
        }

        // Page size selector
        const pageSizeSelect = document.getElementById('page-size');
        if (pageSizeSelect) {
            pageSizeSelect.addEventListener('change', (e) => {
                this.changePageSize(e.target.value);
            });
        }

        // Add column button
        const addColumnBtn = document.getElementById('add-column-btn');
        if (addColumnBtn) {
            addColumnBtn.addEventListener('click', () => {
                this.showAddColumnModal();
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
    }

    // UI Updates
    updateRowCount() {
        const rowCount = this.gridApi.getDisplayedRowCount();
        const totalCount = this.gridApi.getRowCount();
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
        const countElement = document.getElementById('selected-count');
        if (countElement) {
            countElement.textContent = this.selectedRows.length;
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

    updatePaginationControls() {
        const paginationInfo = document.getElementById('pagination-info');
        const paginationButtons = document.getElementById('pagination-buttons');
        
        if (!this.gridApi || !paginationInfo || !paginationButtons) return;
        
        const currentPage = this.gridApi.getCurrentPage() + 1;
        const totalPages = this.gridApi.getTotalPages();
        const pageSize = this.gridApi.getPaginationPageSize();
        const totalRows = this.gridApi.getRowCount();
        const startRow = (currentPage - 1) * pageSize + 1;
        const endRow = Math.min(currentPage * pageSize, totalRows);
        
        // Update pagination info
        paginationInfo.innerHTML = `
            <span>Showing ${startRow} to ${endRow} of ${totalRows} rows</span>
            <span class="ml-4">Page ${currentPage} of ${totalPages}</span>
        `;
        
        // Update pagination buttons
        paginationButtons.innerHTML = `
            <button 
                class="px-3 py-1 border rounded ${currentPage === 1 ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-white hover:bg-gray-50'}"
                onclick="window.agGridManager.goToPage(1)"
                ${currentPage === 1 ? 'disabled' : ''}
            >
                First
            </button>
            <button 
                class="px-3 py-1 border rounded ${currentPage === 1 ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-white hover:bg-gray-50'}"
                onclick="window.agGridManager.goToPage(${currentPage - 1})"
                ${currentPage === 1 ? 'disabled' : ''}
            >
                Previous
            </button>
            <button 
                class="px-3 py-1 border rounded ${currentPage === totalPages ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-white hover:bg-gray-50'}"
                onclick="window.agGridManager.goToPage(${currentPage + 1})"
                ${currentPage === totalPages ? 'disabled' : ''}
            >
                Next
            </button>
            <button 
                class="px-3 py-1 border rounded ${currentPage === totalPages ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-white hover:bg-gray-50'}"
                onclick="window.agGridManager.goToPage(${totalPages})"
                ${currentPage === totalPages ? 'disabled' : ''}
            >
                Last
            </button>
        `;
    }

    goToPage(pageNumber) {
        if (this.gridApi && this.gridApi.paginationIsActive()) {
            this.gridApi.goToPage(pageNumber - 1); // AG-Grid uses 0-based indexing
        }
    }

    // Operations
    changePageSize(size) {
        const paginationControls = document.getElementById('pagination-controls');
        const paginationInfo = document.getElementById('pagination-info');
        const paginationButtons = document.getElementById('pagination-buttons');
        
        if (size === 'all') {
            // Switch to infinite scroll and hide pagination controls
            this.gridApi.setGridOption('pagination', false);
            this.gridApi.setGridOption('rowModelType', 'infinite');
            
            if (paginationControls) {
                paginationControls.style.display = 'none';
            }
        } else {
            // Use pagination and show pagination controls
            this.gridApi.setGridOption('pagination', true);
            this.gridApi.setGridOption('rowModelType', 'clientSide');
            this.gridApi.setGridOption('paginationPageSize', parseInt(size));
            
            if (paginationControls) {
                paginationControls.style.display = 'flex';
                this.updatePaginationControls();
            }
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
        this.gridApi.exportDataAsCsv({
            fileName: `table-export-${new Date().toISOString().split('T')[0]}.csv`
        });
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

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
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