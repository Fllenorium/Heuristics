// Dashboard JavaScript for Heuristics AI Simulation Interface
console.log('Dashboard JS Loaded');

// Dashboard state management
const DashboardState = {
    currentStep: 1,
    populationData: null,
    decisionAnalysis: null,
    simulationResults: null,
    
    // Step management
    steps: {
        1: { id: 'population-step', name: 'Population Setup' },
        2: { id: 'decision-step', name: 'Decision Input' },
        3: { id: 'simulation-step', name: 'Run Simulation' },
        4: { id: 'results-step', name: 'Results' }
    },
    
    // Move to next step
    nextStep: function() {
        if (this.currentStep < 4) {
            this.currentStep++;
            this.updateUI();
        }
    },
    
    // Update UI based on current step
    updateUI: function() {
        // Update step indicators
        for (let i = 1; i <= 4; i++) {
            const stepEl = document.getElementById(`step-${i}`);
            const stepContainer = document.getElementById(this.steps[i].id);
            
            if (i < this.currentStep) {
                stepEl.className = 'step-completed w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold mr-4';
            } else if (i === this.currentStep) {
                stepEl.className = 'step-active w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold mr-4';
            } else {
                stepEl.className = 'step-pending w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold mr-4';
            }
            
            // Show/hide step containers
            if (stepContainer) {
                if (i <= this.currentStep) {
                    stepContainer.classList.remove('hidden');
                } else {
                    stepContainer.classList.add('hidden');
                }
            }
        }
    }
};

// Population generation functionality
const PopulationManager = {
    async generatePopulation() {
        try {
            HeuristicsAI.utils.showLoading();
            
            // Collect form data
            const size = parseInt(document.getElementById('population-size').value);
            const parameters = {
                age_min: parseInt(document.getElementById('age-min').value),
                age_max: parseInt(document.getElementById('age-max').value),
                income_level: document.getElementById('income-level').value,
                region: document.getElementById('region').value,
                tech_savvy: document.getElementById('tech-savvy').value,
                price_sensitive: document.getElementById('price-sensitive').value,
                innovation: document.getElementById('innovation').value
            };
            
            // Validate inputs
            if (size < 100 || size > 10000) {
                throw new Error('Population size must be between 100 and 10,000');
            }
            
            if (parameters.age_min >= parameters.age_max) {
                throw new Error('Minimum age must be less than maximum age');
            }
            
            // Call API
            const response = await HeuristicsAI.api.generatePopulation(size, parameters);
            
            if (response.success) {
                DashboardState.populationData = response.population;
                
                // Update status
                document.getElementById('population-status').innerHTML = 
                    `✅ Successfully generated ${response.size} people`;
                
                // Enable next step
                setTimeout(() => {
                    DashboardState.nextStep();
                }, 1000);
                
                HeuristicsAI.utils.showNotification('Population generated successfully!', 'success');
            } else {
                throw new Error(response.error || 'Failed to generate population');
            }
            
        } catch (error) {
            console.error('Population generation error:', error);
            document.getElementById('population-status').innerHTML = 
                `❌ Error: ${error.message}`;
            HeuristicsAI.utils.showNotification(error.message, 'error');
        } finally {
            HeuristicsAI.utils.hideLoading();
        }
    }
};

// Decision analysis functionality
const DecisionManager = {
    async analyzeDecision() {
        try {
            HeuristicsAI.utils.showLoading();
            
            // Collect form data
            const decisionText = document.getElementById('decision-text').value.trim();
            const decisionType = document.getElementById('decision-type').value;
            const timeline = document.getElementById('timeline').value;
            const scope = document.getElementById('scope').value;
            
            // Validate inputs
            if (!decisionText) {
                throw new Error('Please describe your business decision');
            }
            
            if (decisionText.length < 10) {
                throw new Error('Please provide a more detailed description of your decision');
            }
            
            const decisionParams = {
                type: decisionType,
                timeline: timeline,
                scope: scope
            };
            
            // Call API
            const response = await HeuristicsAI.api.analyzeDecision(decisionText, decisionParams);
            
            if (response.success) {
                DashboardState.decisionAnalysis = response.analysis;
                
                // Update status
                document.getElementById('analysis-status').innerHTML = 
                    `✅ Decision analyzed: ${response.analysis.decision_type} (${Math.round(response.analysis.confidence_score * 100)}% confidence)`;
                
                // Update preview in next step
                this.updateSimulationPreview();
                
                // Enable next step
                setTimeout(() => {
                    DashboardState.nextStep();
                }, 1000);
                
                HeuristicsAI.utils.showNotification('Decision analyzed successfully!', 'success');
            } else {
                throw new Error(response.error || 'Failed to analyze decision');
            }
            
        } catch (error) {
            console.error('Decision analysis error:', error);
            document.getElementById('analysis-status').innerHTML = 
                `❌ Error: ${error.message}`;
            HeuristicsAI.utils.showNotification(error.message, 'error');
        } finally {
            HeuristicsAI.utils.hideLoading();
        }
    },
    
    updateSimulationPreview() {
        if (DashboardState.populationData && DashboardState.decisionAnalysis) {
            document.getElementById('preview-population-size').textContent = 
                HeuristicsAI.utils.formatNumber(DashboardState.populationData.length);
            document.getElementById('preview-decision-type').textContent = 
                DashboardState.decisionAnalysis.decision_type;
        }
    }
};

// Simulation functionality
const SimulationManager = {
    async runSimulation() {
        try {
            // Validate we have all required data
            if (!DashboardState.populationData) {
                throw new Error('Population data is missing. Please go back and generate a population.');
            }
            
            if (!DashboardState.decisionAnalysis) {
                throw new Error('Decision analysis is missing. Please go back and analyze your decision.');
            }
            
            // Show progress
            this.showProgress();
            
            // Get decision text from step 2
            const decisionText = document.getElementById('decision-text').value;
            
            // Simulate progress updates
            this.updateProgress(10, 'Initializing simulation...');
            
            await new Promise(resolve => setTimeout(resolve, 1000));
            this.updateProgress(25, 'Processing population data...');
            
            // Call API
            const response = await HeuristicsAI.api.runSimulation(decisionText, DashboardState.populationData);
            
            this.updateProgress(75, 'Analyzing reactions...');
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            if (response.success) {
                DashboardState.simulationResults = response.simulation_results;
                
                this.updateProgress(100, 'Simulation complete!');
                
                // Show results
                setTimeout(() => {
                    this.hideProgress();
                    this.displayResults();
                    DashboardState.nextStep();
                }, 1500);
                
                HeuristicsAI.utils.showNotification('Simulation completed successfully!', 'success');
            } else {
                throw new Error(response.error || 'Simulation failed');
            }
            
        } catch (error) {
            console.error('Simulation error:', error);
            this.hideProgress();
            HeuristicsAI.utils.showNotification(error.message, 'error');
        }
    },
    
    showProgress() {
        document.getElementById('simulation-progress').classList.remove('hidden');
    },
    
    hideProgress() {
        document.getElementById('simulation-progress').classList.add('hidden');
    },
    
    updateProgress(percentage, text) {
        document.getElementById('progress-bar').style.width = `${percentage}%`;
        document.getElementById('progress-text').textContent = `${percentage}%`;
        
        if (text) {
            document.getElementById('progress-text').textContent = `${percentage}% - ${text}`;
        }
    },
    
    displayResults() {
        const results = DashboardState.simulationResults;
        const resultsContainer = document.getElementById('results-content');
        
        if (!results) {
            resultsContainer.innerHTML = '<p class="text-red-600">No results to display.</p>';
            return;
        }
        
        // Build results HTML
        const html = `
            <div class="grid md:grid-cols-2 gap-8 mb-8">
                <!-- Overall Sentiment -->
                <div class="bg-gray-50 rounded-lg p-6">
                    <h3 class="text-lg font-semibold text-gray-900 mb-4">Overall Reaction</h3>
                    <div class="space-y-3">
                        <div class="flex justify-between">
                            <span class="text-green-600">Positive:</span>
                            <span class="font-medium">${results.reactions_summary.positive} people (${Math.round(results.reactions_summary.positive / results.total_population * 100)}%)</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-red-600">Negative:</span>
                            <span class="font-medium">${results.reactions_summary.negative} people (${Math.round(results.reactions_summary.negative / results.total_population * 100)}%)</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Neutral:</span>
                            <span class="font-medium">${results.reactions_summary.neutral} people (${Math.round(results.reactions_summary.neutral / results.total_population * 100)}%)</span>
                        </div>
                    </div>
                    <div class="mt-4 pt-4 border-t border-gray-300">
                        <div class="flex justify-between">
                            <span class="font-medium">Average Reaction Strength:</span>
                            <span class="font-bold">${results.average_reaction_strength}/1.0</span>
                        </div>
                    </div>
                </div>
                
                <!-- Behavioral Segments -->
                <div class="bg-gray-50 rounded-lg p-6">
                    <h3 class="text-lg font-semibold text-gray-900 mb-4">Behavioral Segments</h3>
                    <div class="space-y-3">
                        <div class="flex justify-between">
                            <span class="text-green-700">Strong Supporters:</span>
                            <span class="font-medium">${results.behavioral_segments.strong_supporters}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-green-500">Moderate Supporters:</span>
                            <span class="font-medium">${results.behavioral_segments.moderate_supporters}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-red-700">Strong Opponents:</span>
                            <span class="font-medium">${results.behavioral_segments.strong_opponents}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-red-500">Moderate Opponents:</span>
                            <span class="font-medium">${results.behavioral_segments.moderate_opponents}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Indifferent:</span>
                            <span class="font-medium">${results.behavioral_segments.indifferent}</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Key Insights -->
            <div class="bg-blue-50 rounded-lg p-6 mb-8">
                <h3 class="text-lg font-semibold text-gray-900 mb-4">Key Insights</h3>
                <ul class="space-y-2">
                    ${results.key_insights.map(insight => `<li class="flex items-start"><span class="text-blue-600 mr-2">•</span>${insight}</li>`).join('')}
                </ul>
            </div>
            
            <!-- Predicted Outcomes -->
            <div class="bg-yellow-50 rounded-lg p-6">
                <h3 class="text-lg font-semibold text-gray-900 mb-4">Predicted Outcomes</h3>
                <div class="grid md:grid-cols-2 gap-4">
                    <div>
                        <div class="font-medium text-gray-700">Net Sentiment Score:</div>
                        <div class="text-2xl font-bold ${results.predicted_outcomes.net_sentiment_score > 0 ? 'text-green-600' : results.predicted_outcomes.net_sentiment_score < 0 ? 'text-red-600' : 'text-gray-600'}">${results.predicted_outcomes.net_sentiment_score}</div>
                    </div>
                    <div>
                        <div class="font-medium text-gray-700">Predicted Adoption Rate:</div>
                        <div class="text-2xl font-bold text-blue-600">${Math.round(results.predicted_outcomes.predicted_adoption_rate)}%</div>
                    </div>
                    <div>
                        <div class="font-medium text-gray-700">Churn Risk:</div>
                        <div class="text-2xl font-bold ${results.predicted_outcomes.churn_risk > 30 ? 'text-red-600' : 'text-yellow-600'}">${Math.round(results.predicted_outcomes.churn_risk)}%</div>
                    </div>
                    <div>
                        <div class="font-medium text-gray-700">Revenue Impact:</div>
                        <div class="text-2xl font-bold ${results.predicted_outcomes.revenue_impact_estimate === 'positive' ? 'text-green-600' : results.predicted_outcomes.revenue_impact_estimate === 'negative' ? 'text-red-600' : 'text-gray-600'}">${results.predicted_outcomes.revenue_impact_estimate}</div>
                    </div>
                </div>
            </div>
            
            <!-- Action Buttons -->
            <div class="mt-8 flex space-x-4">
                <button onclick="window.print()" class="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
                    📄 Export Results
                </button>
                <button onclick="location.reload()" class="bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 transition-colors">
                    🔄 New Simulation
                </button>
            </div>
        `;
        
        resultsContainer.innerHTML = html;
    }
};

// Initialize dashboard on DOM load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initialized');
    
    // Initial UI update
    DashboardState.updateUI();
    
    // Bind event handlers
    
    // Population generation
    const generatePopulationBtn = document.getElementById('generate-population');
    if (generatePopulationBtn) {
        generatePopulationBtn.addEventListener('click', () => {
            PopulationManager.generatePopulation();
        });
    }
    
    // Decision analysis
    const analyzeDecisionBtn = document.getElementById('analyze-decision');
    if (analyzeDecisionBtn) {
        analyzeDecisionBtn.addEventListener('click', () => {
            DecisionManager.analyzeDecision();
        });
    }
    
    // Run simulation
    const runSimulationBtn = document.getElementById('run-simulation');
    if (runSimulationBtn) {
        runSimulationBtn.addEventListener('click', () => {
            SimulationManager.runSimulation();
        });
    }
    
    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });
});

// Export for global access
window.DashboardState = DashboardState;
window.PopulationManager = PopulationManager;
window.DecisionManager = DecisionManager;
window.SimulationManager = SimulationManager;