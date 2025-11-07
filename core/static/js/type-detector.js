/**
 * Type Detection Module
 * Automatically detects and formats data types for table cells
 */

class TypeDetector {
    // Type detection constants
    static TYPES = {
        TEXT: 'text',
        NUMBER: 'number',
        DATE: 'date',
        URL: 'url',
        BOOLEAN: 'boolean',
        JSON: 'json'
    };

    // Detection patterns
    static PATTERNS = {
        URL: /^https?:\/\/.+/i,
        DATE: /^\d{4}-\d{2}-\d{2}$/,
        BOOLEAN: /^(true|false|yes|no|1|0)$/i,
        NUMBER: /^-?\d+\.?\d*$/,
        JSON: /^\s*\{.*\}\s*$|^\s*\[.*\]\s*$/
    };

    /**
     * Detect column type based on sample data
     */
    static detectColumnType(fieldName, rows) {
        if (!rows || rows.length === 0) {
            return this.TYPES.TEXT;
        }

        // Sample first 10 rows for type detection
        const sampleSize = Math.min(10, rows.length);
        const samples = rows.slice(0, sampleSize).map(row => row[fieldName]).filter(val => val != null && val !== '');

        if (samples.length === 0) {
            return this.TYPES.TEXT;
        }

        // Count type matches
        const typeCounts = {};
        
        samples.forEach(value => {
            const detectedType = this.detectValueType(value);
            typeCounts[detectedType] = (typeCounts[detectedType] || 0) + 1;
        });

        // Return the most common type (70% threshold)
        const totalSamples = samples.length;
        const threshold = totalSamples * 0.7;

        for (const [type, count] of Object.entries(typeCounts)) {
            if (count >= threshold) {
                return type;
            }
        }

        // Fallback to text if no clear majority
        return this.TYPES.TEXT;
    }

    /**
     * Detect type of a single value
     */
    static detectValueType(value) {
        if (value == null || value === '') {
            return this.TYPES.TEXT;
        }

        const stringValue = value.toString().trim();

        // Check for URL first (most specific)
        if (this.PATTERNS.URL.test(stringValue)) {
            return this.TYPES.URL;
        }

        // Check for boolean
        if (this.PATTERNS.BOOLEAN.test(stringValue)) {
            return this.TYPES.BOOLEAN;
        }

        // Check for number
        if (this.PATTERNS.NUMBER.test(stringValue)) {
            return this.TYPES.NUMBER;
        }

        // Check for date (YYYY-MM-DD format)
        if (this.PATTERNS.DATE.test(stringValue)) {
            // Validate it's actually a valid date
            const date = new Date(stringValue);
            if (!isNaN(date.getTime())) {
                return this.TYPES.DATE;
            }
        }

        // Check for JSON
        if (this.PATTERNS.JSON.test(stringValue)) {
            try {
                JSON.parse(stringValue);
                return this.TYPES.JSON;
            } catch (e) {
                // Not valid JSON, fall through to text
            }
        }

        // Default to text
        return this.TYPES.TEXT;
    }

    /**
     * Format value based on detected type
     */
    static formatValue(value, type) {
        if (value == null || value === '') {
            return '';
        }

        switch (type) {
            case this.TYPES.NUMBER:
                return this.formatNumber(value);
            
            case this.TYPES.DATE:
                return this.formatDate(value);
            
            case this.TYPES.URL:
                return this.formatUrl(value);
            
            case this.TYPES.BOOLEAN:
                return this.formatBoolean(value);
            
            case this.TYPES.JSON:
                return this.formatJson(value);
            
            default:
                return this.formatText(value);
        }
    }

    /**
     * Format number values
     */
    static formatNumber(value) {
        const num = parseFloat(value);
        if (isNaN(num)) {
            return value;
        }

        // Format with appropriate decimal places
        if (Number.isInteger(num)) {
            return num.toLocaleString();
        } else {
            return num.toLocaleString(undefined, {
                minimumFractionDigits: 0,
                maximumFractionDigits: 2
            });
        }
    }

    /**
     * Format date values
     */
    static formatDate(value) {
        try {
            const date = new Date(value);
            if (isNaN(date.getTime())) {
                return value;
            }

            // Check if it's today or yesterday
            const now = new Date();
            const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
            const yesterday = new Date(today);
            yesterday.setDate(yesterday.getDate() - 1);

            if (date >= today) {
                return 'Today';
            } else if (date >= yesterday) {
                return 'Yesterday';
            } else {
                // Format based on how old the date is
                const diffInDays = Math.floor((today - date) / (1000 * 60 * 60 * 24));
                
                if (diffInDays < 7) {
                    return date.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' });
                } else if (diffInDays < 365) {
                    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
                } else {
                    return date.toLocaleDateString();
                }
            }
        } catch (e) {
            return value;
        }
    }

    /**
     * Format URL values
     */
    static formatUrl(value) {
        if (!value || typeof value !== 'string') {
            return value;
        }

        // Extract domain for display
        try {
            const url = new URL(value);
            const domain = url.hostname.replace('www.', '');
            
            return {
                url: value,
                display: domain,
                fullDisplay: value.length > 50 ? value.substring(0, 47) + '...' : value
            };
        } catch (e) {
            return value;
        }
    }

    /**
     * Format boolean values
     */
    static formatBoolean(value) {
        const stringValue = value.toString().toLowerCase().trim();
        
        if (['true', 'yes', '1'].includes(stringValue)) {
            return true;
        } else if (['false', 'no', '0'].includes(stringValue)) {
            return false;
        }
        
        return value;
    }

    /**
     * Format JSON values
     */
    static formatJson(value) {
        try {
            const parsed = JSON.parse(value);
            
            if (typeof parsed === 'object' && parsed !== null) {
                const keys = Object.keys(parsed);
                if (keys.length <= 3) {
                    // Show as key-value pairs for small objects
                    return keys.map(key => `${key}: ${parsed[key]}`).join(', ');
                } else {
                    // Show count for larger objects
                    return `{${keys.length} properties}`;
                }
            }
            
            return value;
        } catch (e) {
            return value;
        }
    }

    /**
     * Format text values
     */
    static formatText(value) {
        if (value == null) {
            return '';
        }
        
        const stringValue = value.toString();
        
        // Truncate very long text
        if (stringValue.length > 100) {
            return stringValue.substring(0, 97) + '...';
        }
        
        return stringValue;
    }

    /**
     * Get column configuration based on type
     */
    static getColumnConfig(type) {
        const configs = {
            [this.TYPES.TEXT]: {
                filter: 'agTextColumnFilter',
                cellRenderer: 'textCellRenderer',
                comparator: this.textComparator
            },
            [this.TYPES.NUMBER]: {
                filter: 'agNumberColumnFilter',
                cellRenderer: 'numberCellRenderer',
                comparator: this.numberComparator,
                cellClass: 'text-right'
            },
            [this.TYPES.DATE]: {
                filter: 'agDateColumnFilter',
                cellRenderer: 'dateCellRenderer',
                comparator: this.dateComparator,
                cellClass: 'text-center'
            },
            [this.TYPES.URL]: {
                filter: 'agTextColumnFilter',
                cellRenderer: 'urlCellRenderer',
                comparator: this.textComparator
            },
            [this.TYPES.BOOLEAN]: {
                filter: 'agSetColumnFilter',
                cellRenderer: 'booleanCellRenderer',
                comparator: this.booleanComparator,
                cellClass: 'text-center'
            },
            [this.TYPES.JSON]: {
                filter: 'agTextColumnFilter',
                cellRenderer: 'jsonCellRenderer',
                comparator: this.textComparator
            }
        };

        return configs[type] || configs[this.TYPES.TEXT];
    }

    // Comparators for sorting
    static textComparator(a, b) {
        if (a == null && b == null) return 0;
        if (a == null) return -1;
        if (b == null) return 1;
        
        return a.toString().localeCompare(b.toString());
    }

    static numberComparator(a, b) {
        const numA = parseFloat(a);
        const numB = parseFloat(b);
        
        if (isNaN(numA) && isNaN(numB)) return 0;
        if (isNaN(numA)) return -1;
        if (isNaN(numB)) return 1;
        
        return numA - numB;
    }

    static dateComparator(a, b) {
        if (!a && !b) return 0;
        if (!a) return -1;
        if (!b) return 1;
        
        const dateA = new Date(a);
        const dateB = new Date(b);
        
        return dateA.getTime() - dateB.getTime();
    }

    static booleanComparator(a, b) {
        const boolA = Boolean(a);
        const boolB = Boolean(b);
        
        if (boolA === boolB) return 0;
        return boolA ? 1 : -1;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TypeDetector;
}