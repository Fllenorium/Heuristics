from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import os
from config import config
from src.services.decision_analyzer import DecisionAnalyzer
from src.services.behavior_engine import BehaviorEngine
from src.models.population import PopulationGenerator
from src.utils.logger import setup_logger

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    CORS(app)
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        storage_uri=app.config['RATELIMIT_STORAGE_URL']
    )
    
    # Setup logging
    setup_logger(app.config['LOG_LEVEL'])
    
    # Initialize services
    decision_analyzer = DecisionAnalyzer(app.config['GEMINI_API_KEY'])
    behavior_engine = BehaviorEngine(app.config['GEMINI_API_KEY'])
    population_generator = PopulationGenerator()
    
    @app.route('/')
    def index():
        """Homepage"""
        return render_template('index.html')
    
    @app.route('/dashboard')
    def dashboard():
        """Main dashboard for creating simulations"""
        return render_template('dashboard.html')
    
    @app.route('/api/analyze-decision', methods=['POST'])
    @limiter.limit("20 per minute")
    def analyze_decision():
        """Analyze a business decision using AI"""
        try:
            data = request.get_json()
            decision_text = data.get('decision')
            
            if not decision_text:
                return jsonify({'error': 'Decision text is required'}), 400
            
            # Analyze the decision
            analysis = decision_analyzer.analyze_decision(decision_text)
            
            return jsonify({
                'success': True,
                'analysis': analysis
            })
            
        except Exception as e:
            app.logger.error(f"Error analyzing decision: {str(e)}")
            return jsonify({'error': 'Failed to analyze decision'}), 500
    
    @app.route('/api/generate-population', methods=['POST'])
    @limiter.limit("15 per minute")
    def generate_population():
        """Generate a synthetic population"""
        try:
            data = request.get_json()
            population_params = data.get('parameters', {})
            size = min(data.get('size', 1000), app.config['MAX_POPULATION_SIZE'])
            
            # Generate population
            population = population_generator.generate_population(size, population_params)
            
            return jsonify({
                'success': True,
                'population': population,
                'size': len(population)
            })
            
        except Exception as e:
            app.logger.error(f"Error generating population: {str(e)}")
            return jsonify({'error': 'Failed to generate population'}), 500
    
    @app.route('/api/run-simulation', methods=['POST'])
    @limiter.limit("3 per minute")
    def run_simulation():
        """Run a complete simulation on a population"""
        try:
            data = request.get_json()
            decision_text = data.get('decision')
            population = data.get('population')
            
            if not decision_text or not population:
                return jsonify({'error': 'Decision and population are required'}), 400
            
            # Analyze decision first
            decision_analysis = decision_analyzer.analyze_decision(decision_text)
            
            # Run behavior simulation
            results = behavior_engine.simulate_population_behavior(
                population, 
                decision_analysis,
                batch_size=app.config['DEFAULT_BATCH_SIZE']
            )
            
            return jsonify({
                'success': True,
                'decision_analysis': decision_analysis,
                'simulation_results': results
            })
            
        except Exception as e:
            app.logger.error(f"Error running simulation: {str(e)}")
            return jsonify({'error': 'Failed to run simulation'}), 500
    
    @app.route('/api/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'version': '1.0.0',
            'gemini_configured': bool(app.config['GEMINI_API_KEY'])
        })
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({'error': 'Rate limit exceeded', 'description': str(e.description)}), 429
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)