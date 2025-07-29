import google.generativeai as genai
import json
import logging
import asyncio
import time
from typing import Dict, List, Optional, Tuple
from cachetools import TTLCache
import hashlib
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class PersonReaction(BaseModel):
    """Structure for individual person reaction"""
    person_id: str
    reaction_type: str  # positive, negative, neutral
    reaction_strength: float  # 0.0 to 1.0
    reasoning: str
    behavioral_change: Dict[str, any]
    likelihood_to_act: float

class PopulationResults(BaseModel):
    """Structure for population-level simulation results"""
    total_population: int
    reactions_summary: Dict[str, int]
    average_reaction_strength: float
    demographic_breakdown: Dict[str, Dict]
    key_insights: List[str]
    behavioral_segments: Dict[str, Dict]
    predicted_outcomes: Dict[str, any]

class BehaviorEngine:
    """
    AI-powered behavior prediction engine using Google Gemini.
    Simulates how individuals and populations react to business decisions.
    """
    
    def __init__(self, api_key: str, cache_ttl: int = 3600, max_workers: int = 5):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.cache = TTLCache(maxsize=5000, ttl=cache_ttl)
        self.max_workers = max_workers
        self.rate_limit_delay = 0.2  # Delay between API calls to respect rate limits
        
    def _get_cache_key(self, person_profile: Dict, decision_analysis: Dict) -> str:
        """Generate cache key for person+decision combination"""
        key_string = f"{json.dumps(person_profile, sort_keys=True)}_{json.dumps(decision_analysis, sort_keys=True)}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def simulate_person_reaction(self, person_profile: Dict, decision_analysis: Dict) -> Dict:
        """
        Simulate how a specific person would react to a business decision.
        
        Args:
            person_profile: Dictionary containing person's demographics and traits
            decision_analysis: Analysis from DecisionAnalyzer
            
        Returns:
            Dictionary containing the person's predicted reaction
        """
        cache_key = self._get_cache_key(person_profile, decision_analysis)
        
        # Check cache first
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            prompt = self._build_person_reaction_prompt(person_profile, decision_analysis)
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": self._get_person_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.4,
                max_tokens=800
            )
            
            reaction_text = response.choices[0].message.content
            reaction = self._parse_person_reaction(reaction_text, person_profile['id'])
            
            # Cache the result
            self.cache[cache_key] = reaction
            
            # Rate limiting
            time.sleep(self.rate_limit_delay)
            
            return reaction
            
        except Exception as e:
            logger.error(f"Error simulating person reaction: {str(e)}")
            return self._get_fallback_person_reaction(person_profile['id'])
    
    def simulate_population_behavior(self, population: List[Dict], decision_analysis: Dict, 
                                   batch_size: int = 50) -> Dict:
        """
        Simulate how an entire population would react to a business decision.
        
        Args:
            population: List of person profiles
            decision_analysis: Analysis from DecisionAnalyzer
            batch_size: Number of people to process in each batch
            
        Returns:
            Dictionary containing population-level results
        """
        logger.info(f"Starting population simulation for {len(population)} people")
        
        all_reactions = []
        total_batches = (len(population) + batch_size - 1) // batch_size
        
        # Process population in batches to manage API rate limits
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(population))
            batch = population[start_idx:end_idx]
            
            logger.info(f"Processing batch {batch_num + 1}/{total_batches} ({len(batch)} people)")
            
            # Process batch with ThreadPoolExecutor for concurrent API calls
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                batch_reactions = list(executor.map(
                    lambda person: self.simulate_person_reaction(person, decision_analysis),
                    batch
                ))
            
            all_reactions.extend(batch_reactions)
            
            # Brief pause between batches
            if batch_num < total_batches - 1:
                time.sleep(1)
        
        # Aggregate results
        results = self._aggregate_population_results(all_reactions, decision_analysis)
        
        logger.info("Population simulation completed")
        return results
    
    def _get_person_system_prompt(self) -> str:
        """System prompt for individual person behavior simulation"""
        return """You are a behavioral psychology expert who can accurately predict how specific individuals react to business decisions based on their personality, demographics, and psychological traits.

Your task is to roleplay as the given person and predict their authentic reaction to a business decision. Consider:

1. Their demographic profile (age, income, location, etc.)
2. Their personality traits and values
3. Their past experiences and current life situation
4. Relevant cognitive biases and psychological patterns
5. Their relationship with the company/brand
6. Social and cultural influences

Always respond as JSON with these fields:
- reaction_type: "positive", "negative", or "neutral"
- reaction_strength: Float from 0.0 to 1.0 (how strong the reaction is)
- reasoning: Detailed explanation of why this person would react this way
- behavioral_change: Object describing specific actions they might take
- likelihood_to_act: Float from 0.0 to 1.0 (probability they'll actually act on their reaction)

Be realistic and nuanced. People often have complex, mixed reactions. Consider both emotional and rational responses."""

    def _build_person_reaction_prompt(self, person_profile: Dict, decision_analysis: Dict) -> str:
        """Build prompt for simulating individual person reaction"""
        return f"""You are roleplaying as this person:

PERSON PROFILE:
{json.dumps(person_profile, indent=2)}

BUSINESS DECISION TO REACT TO:
Decision Type: {decision_analysis.get('decision_type', 'Unknown')}
Key Factors: {decision_analysis.get('key_factors', [])}
Decision Parameters: {decision_analysis.get('decision_parameters', {})}

CONTEXT:
The decision involves these psychological triggers: {decision_analysis.get('psychological_triggers', [])}
Risk level assessed as: {decision_analysis.get('risk_level', 'medium')}

Please predict how this specific person would react to this business decision. Put yourself in their shoes and consider:

1. How does this decision align with their values and priorities?
2. How might their demographic characteristics influence their reaction?
3. What cognitive biases might be at play?
4. How would their personality traits shape their response?
5. What specific actions (if any) would they likely take?

Respond with your analysis in JSON format."""

    def _parse_person_reaction(self, response_text: str, person_id: str) -> Dict:
        """Parse and validate person reaction response"""
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_text = response_text[json_start:json_end]
            reaction_data = json.loads(json_text)
            
            # Add person ID
            reaction_data['person_id'] = person_id
            
            # Validate and normalize fields
            reaction_data['reaction_type'] = reaction_data.get('reaction_type', 'neutral')
            reaction_data['reaction_strength'] = float(reaction_data.get('reaction_strength', 0.5))
            reaction_data['likelihood_to_act'] = float(reaction_data.get('likelihood_to_act', 0.5))
            reaction_data['reasoning'] = reaction_data.get('reasoning', 'No reasoning provided')
            reaction_data['behavioral_change'] = reaction_data.get('behavioral_change', {})
            
            # Ensure values are in valid ranges
            reaction_data['reaction_strength'] = max(0.0, min(1.0, reaction_data['reaction_strength']))
            reaction_data['likelihood_to_act'] = max(0.0, min(1.0, reaction_data['likelihood_to_act']))
            
            return reaction_data
            
        except Exception as e:
            logger.error(f"Error parsing person reaction: {str(e)}")
            return self._get_fallback_person_reaction(person_id)
    
    def _get_fallback_person_reaction(self, person_id: str) -> Dict:
        """Fallback reaction when parsing fails"""
        return {
            'person_id': person_id,
            'reaction_type': 'neutral',
            'reaction_strength': 0.5,
            'reasoning': 'Unable to determine specific reaction',
            'behavioral_change': {},
            'likelihood_to_act': 0.3
        }
    
    def _aggregate_population_results(self, reactions: List[Dict], decision_analysis: Dict) -> Dict:
        """Aggregate individual reactions into population-level insights"""
        total_population = len(reactions)
        
        # Count reactions by type
        reactions_summary = {
            'positive': len([r for r in reactions if r['reaction_type'] == 'positive']),
            'negative': len([r for r in reactions if r['reaction_type'] == 'negative']),
            'neutral': len([r for r in reactions if r['reaction_type'] == 'neutral'])
        }
        
        # Calculate average reaction strength
        avg_reaction_strength = sum(r['reaction_strength'] for r in reactions) / total_population
        
        # Segment by reaction type and strength
        behavioral_segments = {
            'strong_supporters': len([r for r in reactions if r['reaction_type'] == 'positive' and r['reaction_strength'] > 0.7]),
            'moderate_supporters': len([r for r in reactions if r['reaction_type'] == 'positive' and 0.3 <= r['reaction_strength'] <= 0.7]),
            'strong_opponents': len([r for r in reactions if r['reaction_type'] == 'negative' and r['reaction_strength'] > 0.7]),
            'moderate_opponents': len([r for r in reactions if r['reaction_type'] == 'negative' and 0.3 <= r['reaction_strength'] <= 0.7]),
            'indifferent': len([r for r in reactions if r['reaction_type'] == 'neutral'])
        }
        
        # Generate key insights
        key_insights = self._generate_insights(reactions, decision_analysis)
        
        # Predict outcomes
        predicted_outcomes = self._predict_outcomes(reactions, decision_analysis)
        
        return {
            'total_population': total_population,
            'reactions_summary': reactions_summary,
            'average_reaction_strength': round(avg_reaction_strength, 3),
            'demographic_breakdown': {},  # Could be expanded with more analysis
            'key_insights': key_insights,
            'behavioral_segments': behavioral_segments,
            'predicted_outcomes': predicted_outcomes
        }
    
    def _generate_insights(self, reactions: List[Dict], decision_analysis: Dict) -> List[str]:
        """Generate key insights from population reactions"""
        insights = []
        total = len(reactions)
        
        positive_pct = len([r for r in reactions if r['reaction_type'] == 'positive']) / total * 100
        negative_pct = len([r for r in reactions if r['reaction_type'] == 'negative']) / total * 100
        
        # Overall sentiment
        if positive_pct > 60:
            insights.append(f"Strong overall support ({positive_pct:.1f}% positive reactions)")
        elif negative_pct > 60:
            insights.append(f"Strong overall opposition ({negative_pct:.1f}% negative reactions)")
        else:
            insights.append("Mixed reactions with no clear consensus")
        
        # Action likelihood
        high_action_likelihood = len([r for r in reactions if r['likelihood_to_act'] > 0.7]) / total * 100
        if high_action_likelihood > 30:
            insights.append(f"High action potential: {high_action_likelihood:.1f}% likely to act on their reaction")
        
        # Risk assessment
        risk_level = decision_analysis.get('risk_level', 'medium')
        if risk_level == 'high' and negative_pct > 40:
            insights.append("⚠️ High-risk decision with significant negative sentiment")
        
        return insights
    
    def _predict_outcomes(self, reactions: List[Dict], decision_analysis: Dict) -> Dict:
        """Predict business outcomes based on population reactions"""
        total = len(reactions)
        
        # Calculate net sentiment score
        positive_score = sum(r['reaction_strength'] for r in reactions if r['reaction_type'] == 'positive')
        negative_score = sum(r['reaction_strength'] for r in reactions if r['reaction_type'] == 'negative')
        net_sentiment = (positive_score - negative_score) / total
        
        # Predict key metrics
        outcomes = {
            'net_sentiment_score': round(net_sentiment, 3),
            'predicted_adoption_rate': max(0, min(100, 50 + net_sentiment * 50)),
            'churn_risk': max(0, min(100, abs(net_sentiment) * 30 if net_sentiment < 0 else 0)),
            'revenue_impact_estimate': 'positive' if net_sentiment > 0.2 else 'negative' if net_sentiment < -0.2 else 'neutral'
        }
        
        return outcomes