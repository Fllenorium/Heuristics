// Main JavaScript file for Heuristics AI
console.log('Heuristics AI - Main JS Loaded');

// Global configuration
const HeuristicsAI = {
    baseUrl: window.location.origin,
    apiBaseUrl: window.location.origin + '/api',
    
    // Utility functions
    utils: {
        // Show loading overlay
        showLoading: function() {
            const overlay = document.getElementById('loading-overlay');
            if (overlay) {
                overlay.classList.remove('hidden');
            }
        },
        
        // Hide loading overlay
        hideLoading: function() {
            const overlay = document.getElementById('loading-overlay');
            if (overlay) {
                overlay.classList.add('hidden');
            }
        },
        
        // Show notification
        showNotification: function(message, type = 'info') {
            // Create notification element
            const notification = document.createElement('div');
            notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
                type === 'error' ? 'bg-red-500 text-white' : 
                type === 'success' ? 'bg-green-500 text-white' : 
                'bg-blue-500 text-white'
            }`;
            notification.textContent = message;
            
            document.body.appendChild(notification);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 5000);
        },
        
        // Format number with commas
        formatNumber: function(num) {
            return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        },
        
        // Validate form data
        validateRequired: function(formData, requiredFields) {
            const missing = [];
            requiredFields.forEach(field => {
                if (!formData[field] || formData[field].toString().trim() === '') {
                    missing.push(field);
                }
            });
            return missing;
        }
    },
    
    // API helper functions
    api: {
        // Generic API call function
        call: async function(endpoint, method = 'GET', data = null) {
            try {
                const options = {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json',
                    }
                };
                
                if (data && method !== 'GET') {
                    options.body = JSON.stringify(data);
                }
                
                const response = await fetch(`${HeuristicsAI.apiBaseUrl}${endpoint}`, options);
                
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.error || `HTTP ${response.status}`);
                }
                
                return await response.json();
            } catch (error) {
                console.error('API call failed:', error);
                throw error;
            }
        },
        
        // Health check
        healthCheck: async function() {
            return await this.call('/health');
        },
        
        // Analyze decision using Gemini
        analyzeDecision: async function(decisionText, decisionParams = {}) {
            return await this.call('/analyze-decision', 'POST', {
                decision: decisionText,
                parameters: decisionParams
            });
        },
        
        // Generate population
        generatePopulation: async function(size, parameters) {
            return await this.call('/generate-population', 'POST', {
                size: size,
                parameters: parameters
            });
        },
        
        // Run simulation
        runSimulation: async function(decision, population) {
            return await this.call('/run-simulation', 'POST', {
                decision: decision,
                population: population
            });
        }
    }
};

// Global error handler
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    HeuristicsAI.utils.showNotification('An unexpected error occurred', 'error');
});

// Global unhandled promise rejection handler
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    HeuristicsAI.utils.showNotification('An unexpected error occurred', 'error');
    event.preventDefault();
});

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing Heuristics AI');
    
    // Add click handlers for navigation
    const navLinks = document.querySelectorAll('nav a');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Add active state or analytics tracking here if needed
        });
    });
    
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});

// Export for use in other scripts
window.HeuristicsAI = HeuristicsAI;