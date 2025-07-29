import google.generativeai as genai
import json
import logging
from typing import Dict, List, Optional
from cachetools import TTLCache
import hashlib
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class DecisionAnalysis(BaseModel):
    """Structure for decision analysis results"""
    decision_type: str
    key_factors: List[str]
    target_demographics: List[str]
    psychological_triggers: List[str]
    potential_reactions: Dict[str, str]
    decision_parameters: Dict[str, any]
    risk_level: str
    confidence_score: float
    reasoning: str

class DecisionAnalyzer:
    """
    AI-powered decision analysis using Google Gemini API.
    Analyzes business decisions through the lens of behavioral economics.
    """
    
    def __init__(self, api_key: str, cache_ttl: int = 3600):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.cache = TTLCache(maxsize=1000, ttl=cache_ttl)
        
    def _get_cache_key(self, decision_text: str, decision_params: Optional[Dict] = None) -> str:
        """Generate cache key for decision analysis"""
        key_string = f"{decision_text}_{decision_params}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def analyze_decision(self, decision_text: str, decision_params: Optional[Dict] = None) -> Dict:
        """
        Analyze a business decision using Gemini with behavioral economics perspective.
        
        Args:
            decision_text: Plain English description of the business decision
            decision_params: Optional additional parameters about the decision
            
        Returns:
            Dictionary containing structured analysis of the decision
        """
        cache_key = self._get_cache_key(decision_text, decision_params)
        
        # Check cache first
        if cache_key in self.cache:
            logger.info("Returning cached decision analysis")
            return self.cache[cache_key]
        
        try:
            prompt = self._build_analysis_prompt(decision_text, decision_params)
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=2000,
                )
            )
            
            analysis_text = response.text
            analysis = self._parse_analysis_response(analysis_text)
            
            # Cache the result
            self.cache[cache_key] = analysis
            
            logger.info(f"Successfully analyzed decision: {decision_text[:50]}...")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing decision: {str(e)}")
            raise Exception(f"Failed to analyze decision: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        """System prompt that makes Gemini think like a behavioral economist"""
        return """You are an expert behavioral economist and decision analyst specializing in predicting human reactions to business decisions. Your role is to analyze business decisions through the lens of psychology, economics, and human behavior.

When analyzing a decision, consider:
1. Cognitive biases that might influence reactions (loss aversion, anchoring, etc.)
2. Different demographic segments and their varying motivations
3. Psychological triggers (fear, status, convenience, social proof)
4. Economic factors (price sensitivity, value perception)
5. Temporal aspects (immediate vs. long-term reactions)
6. Social and cultural factors

Always structure your analysis as JSON with these fields:
- decision_type: Category of decision (pricing, product, marketing, ux, business_model)
- key_factors: List of main factors that will influence reactions
- target_demographics: List of demographic segments most affected
- psychological_triggers: List of psychological factors at play
- potential_reactions: Object with positive, negative, and neutral reaction scenarios
- decision_parameters: Object extracting specific measurable changes
- risk_level: "low", "medium", or "high"
- confidence_score: Float between 0.0 and 1.0
- reasoning: Detailed explanation of your analysis

Be thorough, nuanced, and consider both intended and unintended consequences."""

    def _build_analysis_prompt(self, decision_text: str, decision_params: Optional[Dict] = None) -> str:
        """Build the analysis prompt for the specific decision"""
        base_prompt = f"""{self._get_system_prompt()}

Analyze this business decision:

DECISION: {decision_text}

"""
        
        if decision_params:
            base_prompt += f"ADDITIONAL CONTEXT: {json.dumps(decision_params, indent=2)}\n\n"
        
        base_prompt += """Please provide a comprehensive behavioral economic analysis. Consider:

1. What type of decision is this and what are the key variables?
2. Which demographic segments will be most affected?
3. What psychological principles apply (loss aversion, anchoring, social proof, etc.)?
4. How might different personality types react differently?
5. What are the short-term vs. long-term behavioral impacts?
6. What measurable parameters can we extract from this decision?

Provide your analysis in the specified JSON format."""

        return base_prompt
    
    def _parse_analysis_response(self, response_text: str) -> Dict:
        """Parse and validate the GPT-4 analysis response"""
        try:
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_text = response_text[json_start:json_end]
            analysis_data = json.loads(json_text)
            
            # Validate required fields
            required_fields = [
                'decision_type', 'key_factors', 'target_demographics',
                'psychological_triggers', 'potential_reactions', 
                'decision_parameters', 'risk_level', 'confidence_score', 'reasoning'
            ]
            
            for field in required_fields:
                if field not in analysis_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate data types
            if not isinstance(analysis_data['confidence_score'], (int, float)):
                analysis_data['confidence_score'] = 0.5
            
            if analysis_data['confidence_score'] > 1.0:
                analysis_data['confidence_score'] = analysis_data['confidence_score'] / 100
            
            return analysis_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            # Return fallback analysis
            return self._get_fallback_analysis(response_text)
        except Exception as e:
            logger.error(f"Error parsing analysis response: {str(e)}")
            return self._get_fallback_analysis(response_text)
    
    def _get_fallback_analysis(self, response_text: str) -> Dict:
        """Provide a fallback analysis structure when parsing fails"""
        return {
            "decision_type": "unknown",
            "key_factors": ["Unable to parse detailed analysis"],
            "target_demographics": ["General population"],
            "psychological_triggers": ["Various behavioral factors"],
            "potential_reactions": {
                "positive": "Some positive reactions expected",
                "negative": "Some negative reactions expected",
                "neutral": "Mixed reactions likely"
            },
            "decision_parameters": {},
            "risk_level": "medium",
            "confidence_score": 0.3,
            "reasoning": f"Analysis parsing failed. Raw response: {response_text[:200]}..."
        }
    
    def get_decision_categories(self) -> List[str]:
        """Get available decision categories"""
        return [
            "pricing", "product", "marketing", "ux", 
            "business_model", "operations", "strategy"
        ]