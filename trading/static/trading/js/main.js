// trading/static/trading/js/main.js

// Toast Notification System
const ToastManager = {
    show: function(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type} fade-in`;
        
        const icons = {
            success: '<svg class="w-5 h-5 inline mr-2 text-green-600" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>',
            error: '<svg class="w-5 h-5 inline mr-2 text-red-600" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/></svg>',
            warning: '<svg class="w-5 h-5 inline mr-2 text-yellow-600" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>',
            info: '<svg class="w-5 h-5 inline mr-2 text-blue-600" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/></svg>'
        };
        
        toast.innerHTML = `
            <div class="flex items-center">
                ${icons[type] || icons.info}
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
};

// API Helper Functions
const API = {
    baseURL: '/api',
    
    async get(endpoint) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`);
            if (!response.ok) throw new Error('API request failed');
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            ToastManager.show('Failed to fetch data', 'error');
            throw error;
        }
    },
    
    async post(endpoint, data) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error('API request failed');
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            ToastManager.show('Failed to send data', 'error');
            throw error;
        }
    },
    
    getCsrfToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
};

// Data Formatter Utilities
const Formatter = {
    currency(value) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            minimumFractionDigits: 2
        }).format(value);
    },
    
    number(value, decimals = 2) {
        return new Intl.NumberFormat('en-IN', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(value);
    },
    
    percentage(value) {
        return `${this.number(value, 2)}%`;
    },
    
    date(dateString) {
        return new Date(dateString).toLocaleDateString('en-IN', {
            day: '2-digit',
            month: 'short',
            year: 'numeric'
        });
    },
    
    datetime(dateString) {
        return new Date(dateString).toLocaleString('en-IN', {
            day: '2-digit',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    duration(seconds) {
        if (seconds < 60) return `${seconds}s`;
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${minutes}m ${secs}s`;
    }
};

// Loading Spinner
const LoadingSpinner = {
    show(element) {
        const spinner = document.createElement('div');
        spinner.className = 'spinner mx-auto';
        spinner.id = 'loadingSpinner';
        element.appendChild(spinner);
    },
    
    hide() {
        const spinner = document.getElementById('loadingSpinner');
        if (spinner) spinner.remove();
    }
};

// Table Search and Filter
class TableFilter {
    constructor(tableId, searchInputId) {
        this.table = document.getElementById(tableId);
        this.searchInput = document.getElementById(searchInputId);
        
        if (this.table && this.searchInput) {
            this.searchInput.addEventListener('keyup', () => this.filter());
        }
    }
    
    filter() {
        const searchTerm = this.searchInput.value.toLowerCase();
        const rows = this.table.getElementsByTagName('tr');
        
        for (let i = 1; i < rows.length; i++) {
            const row = rows[i];
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        }
    }
}

// Export to CSV
function exportTableToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    for (let i = 0; i < rows.length; i++) {
        const row = [];
        const cols = rows[i].querySelectorAll('td, th');
        
        for (let j = 0; j < cols.length; j++) {
            let text = cols[j].innerText.replace(/"/g, '""');
            row.push(`"${text}"`);
        }
        
        csv.push(row.join(','));
    }
    
    downloadCSV(csv.join('\n'), filename);
}

function downloadCSV(csv, filename) {
    const csvFile = new Blob([csv], { type: 'text/csv' });
    const downloadLink = document.createElement('a');
    downloadLink.download = filename;
    downloadLink.href = window.URL.createObjectURL(csvFile);
    downloadLink.style.display = 'none';
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}

// Auto-refresh functionality
class AutoRefresh {
    constructor(interval = 60000) {
        this.interval = interval;
        this.timerId = null;
        this.enabled = false;
    }
    
    start(callback) {
        if (this.enabled) return;
        this.enabled = true;
        this.timerId = setInterval(callback, this.interval);
        ToastManager.show('Auto-refresh enabled', 'info');
    }
    
    stop() {
        if (!this.enabled) return;
        this.enabled = false;
        clearInterval(this.timerId);
        ToastManager.show('Auto-refresh disabled', 'info');
    }
    
    toggle(callback) {
        if (this.enabled) {
            this.stop();
        } else {
            this.start(callback);
        }
    }
}

// Chart Utilities
const ChartUtils = {
    defaultColors: [
        'rgba(59, 130, 246, 0.8)',
        'rgba(139, 92, 246, 0.8)',
        'rgba(236, 72, 153, 0.8)',
        'rgba(34, 197, 94, 0.8)',
        'rgba(251, 146, 60, 0.8)'
    ],
    
    getGradient(ctx, color1, color2) {
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, color1);
        gradient.addColorStop(1, color2);
        return gradient;
    },
    
    defaultOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom'
            }
        }
    }
};

// Local Storage Helper
const Storage = {
    set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('Storage Error:', error);
        }
    },
    
    get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Storage Error:', error);
            return defaultValue;
        }
    },
    
    remove(key) {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('Storage Error:', error);
        }
    },
    
    clear() {
        try {
            localStorage.clear();
        } catch (error) {
            console.error('Storage Error:', error);
        }
    }
};

// Form Validation
class FormValidator {
    constructor(formId) {
        this.form = document.getElementById(formId);
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.validate(e));
        }
    }
    
    validate(event) {
        const inputs = this.form.querySelectorAll('input[required], select[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                this.showError(input, 'This field is required');
                isValid = false;
            } else {
                this.clearError(input);
            }
        });
        
        if (!isValid) {
            event.preventDefault();
            ToastManager.show('Please fill all required fields', 'error');
        }
        
        return isValid;
    }
    
    showError(input, message) {
        input.classList.add('border-red-500');
        let error = input.nextElementSibling;
        if (!error || !error.classList.contains('error-message')) {
            error = document.createElement('span');
            error.className = 'error-message text-red-500 text-sm mt-1';
            input.parentNode.insertBefore(error, input.nextSibling);
        }
        error.textContent = message;
    }
    
    clearError(input) {
        input.classList.remove('border-red-500');
        const error = input.nextElementSibling;
        if (error && error.classList.contains('error-message')) {
            error.remove();
        }
    }
}

// Initialize common features on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip-popup';
            tooltip.textContent = this.getAttribute('data-tooltip');
            document.body.appendChild(tooltip);
        });
    });
    
    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Initialize date pickers with today's date
    const datePickers = document.querySelectorAll('input[type="date"]');
    datePickers.forEach(picker => {
        if (!picker.value) {
            picker.valueAsDate = new Date();
        }
    });
    
    console.log('TradeShelf Dashboard Initialized');
});
// Function to update script status
function updateScriptStatus() {
    fetch('/api/script-status/')
        .then(response => response.json())
        .then(data => {
            // Update Camarilla status
            updateScriptUI('camarilla', data.camarilla);

            // Update Whole Number status
            updateScriptUI('whole_number', data.whole_number);
        })
        .catch(error => {
            console.error('Error fetching script status:', error);
        });
}

function updateScriptUI(scriptType, data) {
    const statusElement = document.getElementById(scriptType + 'Status');
    const messageElement = document.getElementById(scriptType + 'Message');

    if (!statusElement) return;

    let statusText = data.status;
    let statusClass = '';

    if (data.is_running) {
        statusText = 'RUNNING';
        statusClass = 'px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800 animate-pulse';
    } else if (data.status === 'SUCCESS') {
        statusClass = 'px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800';
    } else if (data.status === 'FAILED') {
        statusClass = 'px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800';
    } else {
        statusClass = 'px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800';
    }

    statusElement.textContent = statusText;
    statusElement.className = statusClass;

    // Update message if running
    if (data.is_running && messageElement) {
        messageElement.textContent = `Processing... ${data.records_processed} records`;
        messageElement.className = 'mt-2 text-sm text-blue-600';
    }
}
// Export functions for global use
window.ToastManager = ToastManager;
window.API = API;
window.Formatter = Formatter;
window.LoadingSpinner = LoadingSpinner;
window.TableFilter = TableFilter;
window.exportTableToCSV = exportTableToCSV;
window.AutoRefresh = AutoRefresh;
window.ChartUtils = ChartUtils;
window.Storage = Storage;
window.FormValidator = FormValidator;
