import random
import uuid
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class IncomeLevel(Enum):
    LOW = "low"
    MIDDLE = "middle"
    HIGH = "high"
    MIXED = "mixed"

class TechSavviness(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MIXED = "mixed"

class PriceSensitivity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MIXED = "mixed"

class InnovationAdoption(Enum):
    EARLY = "early"
    MAINSTREAM = "mainstream"
    LATE = "late"
    MIXED = "mixed"

@dataclass
class PersonProfile:
    """Individual person profile with demographics and traits"""
    id: str
    age: int
    income: int
    location: str
    occupation: str
    education: str
    tech_savviness: str
    price_sensitivity: str
    innovation_adoption: str
    personality_traits: Dict[str, float]
    values: List[str]
    lifestyle: str

class PopulationGenerator:
    """
    Generates realistic synthetic populations with diverse demographics and behavioral traits.
    """
    
    def __init__(self):
        self.occupations = [
            "Software Developer", "Teacher", "Healthcare Worker", "Manager", "Sales Representative",
            "Engineer", "Consultant", "Student", "Entrepreneur", "Retail Worker", "Administrative Assistant",
            "Marketing Professional", "Financial Analyst", "Designer", "Researcher", "Service Worker",
            "Manufacturing Worker", "Government Employee", "Non-profit Worker", "Freelancer"
        ]
        
        self.education_levels = [
            "High School", "Some College", "Bachelor's Degree", "Master's Degree", "PhD", "Trade School"
        ]
        
        self.personality_traits = [
            "openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"
        ]
        
        self.core_values = [
            "security", "achievement", "convenience", "quality", "status", "family", 
            "environment", "innovation", "tradition", "independence", "community", "health"
        ]
        
        self.lifestyle_categories = [
            "urban_professional", "suburban_family", "rural_traditional", "student", 
            "retiree", "entrepreneur", "budget_conscious", "luxury_oriented"
        ]
        
        self.regions = {
            "us": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", 
                   "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville"],
            "europe": ["London", "Paris", "Berlin", "Madrid", "Rome", "Amsterdam", 
                      "Vienna", "Stockholm", "Copenhagen", "Dublin", "Brussels", "Zurich"],
            "asia": ["Tokyo", "Shanghai", "Mumbai", "Seoul", "Singapore", "Hong Kong", 
                    "Bangkok", "Jakarta", "Manila", "Kuala Lumpur", "Taipei", "Osaka"],
            "global": ["New York", "London", "Tokyo", "Shanghai", "Los Angeles", "Paris", 
                      "Berlin", "Mumbai", "São Paulo", "Sydney", "Toronto", "Dubai"]
        }
    
    def generate_population(self, size: int, parameters: Optional[Dict] = None) -> List[Dict]:
        """
        Generate a synthetic population with specified parameters.
        
        Args:
            size: Number of people to generate
            parameters: Optional dict with population parameters
            
        Returns:
            List of person profile dictionaries
        """
        if parameters is None:
            parameters = {}
        
        logger.info(f"Generating population of {size} people with parameters: {parameters}")
        
        population = []
        
        for _ in range(size):
            person = self._generate_person(parameters)
            population.append(person.dict() if hasattr(person, 'dict') else person)
        
        logger.info(f"Successfully generated population of {len(population)} people")
        return population
    
    def _generate_person(self, parameters: Dict) -> Dict:
        """Generate a single person profile"""
        person_id = str(uuid.uuid4())
        
        # Age distribution
        age_min = parameters.get('age_min', 18)
        age_max = parameters.get('age_max', 65)
        age = self._generate_realistic_age(age_min, age_max)
        
        # Income based on age and parameters
        income_level = parameters.get('income_level', 'mixed')
        income = self._generate_income(age, income_level)
        
        # Location
        region = parameters.get('region', 'us')
        location = random.choice(self.regions.get(region, self.regions['us']))
        
        # Occupation based on age and income
        occupation = self._generate_occupation(age, income)
        
        # Education correlated with income and occupation
        education = self._generate_education(income, occupation)
        
        # Behavioral traits
        tech_savviness = self._generate_trait_value(parameters.get('tech_savvy', 'mixed'), age)
        price_sensitivity = self._generate_price_sensitivity(income, parameters.get('price_sensitive', 'mixed'))
        innovation_adoption = self._generate_innovation_adoption(age, tech_savviness, parameters.get('innovation', 'mixed'))
        
        # Personality traits (Big Five)
        personality_traits = self._generate_personality_traits()
        
        # Values based on demographics and personality
        values = self._generate_values(age, income, personality_traits)
        
        # Lifestyle
        lifestyle = self._generate_lifestyle(age, income, location, personality_traits)
        
        return {
            'id': person_id,
            'age': age,
            'income': income,
            'location': location,
            'occupation': occupation,
            'education': education,
            'tech_savviness': tech_savviness,
            'price_sensitivity': price_sensitivity,
            'innovation_adoption': innovation_adoption,
            'personality_traits': personality_traits,
            'values': values,
            'lifestyle': lifestyle
        }
    
    def _generate_realistic_age(self, min_age: int, max_age: int) -> int:
        """Generate age with realistic distribution (weighted toward middle ages)"""
        # Create a weighted distribution that favors middle ages
        ages = list(range(min_age, max_age + 1))
        weights = []
        
        for age in ages:
            if 25 <= age <= 45:
                weight = 3  # Higher weight for prime working age
            elif 18 <= age <= 24 or 46 <= age <= 55:
                weight = 2  # Medium weight for young adults and middle-aged
            else:
                weight = 1  # Lower weight for very young or older
            weights.append(weight)
        
        return random.choices(ages, weights=weights)[0]
    
    def _generate_income(self, age: int, income_level: str) -> int:
        """Generate income based on age and specified level"""
        base_income = 30000
        
        # Age-based income adjustment
        if age < 25:
            age_multiplier = 0.7
        elif age < 35:
            age_multiplier = 1.0
        elif age < 45:
            age_multiplier = 1.3
        elif age < 55:
            age_multiplier = 1.4
        else:
            age_multiplier = 1.2  # Often lower due to retirement
        
        if income_level == 'low':
            income_range = (20000, 40000)
        elif income_level == 'middle':
            income_range = (40000, 80000)
        elif income_level == 'high':
            income_range = (80000, 200000)
        else:  # mixed
            income_range = (20000, 150000)
        
        base = random.randint(income_range[0], income_range[1])
        final_income = int(base * age_multiplier)
        
        return final_income
    
    def _generate_occupation(self, age: int, income: int) -> str:
        """Generate occupation that correlates with age and income"""
        if age < 25:
            # Younger people more likely to be students or entry-level
            young_occupations = ["Student", "Retail Worker", "Service Worker", "Administrative Assistant"]
            if random.random() < 0.3:
                return random.choice(young_occupations)
        
        if income > 80000:
            # Higher income occupations
            high_income_occupations = ["Software Developer", "Manager", "Engineer", "Consultant", 
                                     "Financial Analyst", "Marketing Professional", "Entrepreneur"]
            return random.choice(high_income_occupations)
        elif income > 40000:
            # Middle income occupations
            middle_income_occupations = ["Teacher", "Healthcare Worker", "Sales Representative", 
                                       "Administrative Assistant", "Designer", "Government Employee"]
            return random.choice(middle_income_occupations)
        else:
            # Lower income occupations
            lower_income_occupations = ["Retail Worker", "Service Worker", "Manufacturing Worker", 
                                      "Administrative Assistant", "Student"]
            return random.choice(lower_income_occupations)
    
    def _generate_education(self, income: int, occupation: str) -> str:
        """Generate education level correlated with income and occupation"""
        if "Student" in occupation:
            return random.choice(["High School", "Some College"])
        
        if income > 80000:
            return random.choice(["Bachelor's Degree", "Master's Degree", "PhD"])
        elif income > 40000:
            return random.choice(["High School", "Some College", "Bachelor's Degree", "Trade School"])
        else:
            return random.choice(["High School", "Some College", "Trade School"])
    
    def _generate_trait_value(self, param_value: str, age: int) -> str:
        """Generate trait value based on parameter and age"""
        if param_value in ['low', 'medium', 'high']:
            return param_value
        
        # For 'mixed', generate based on age and randomness
        if age < 30:
            # Younger people tend to be more tech-savvy
            options = ['medium', 'high', 'high']
        elif age > 50:
            # Older people tend to be less tech-savvy
            options = ['low', 'low', 'medium']
        else:
            options = ['low', 'medium', 'high']
        
        return random.choice(options)
    
    def _generate_price_sensitivity(self, income: int, param_value: str) -> str:
        """Generate price sensitivity based on income"""
        if param_value in ['low', 'medium', 'high']:
            return param_value
        
        # Higher income = lower price sensitivity
        if income > 80000:
            return random.choice(['low', 'low', 'medium'])
        elif income > 40000:
            return random.choice(['low', 'medium', 'high'])
        else:
            return random.choice(['medium', 'high', 'high'])
    
    def _generate_innovation_adoption(self, age: int, tech_savviness: str, param_value: str) -> str:
        """Generate innovation adoption pattern"""
        if param_value in ['early', 'mainstream', 'late']:
            return param_value
        
        # Younger + tech-savvy = early adopter
        if age < 35 and tech_savviness in ['medium', 'high']:
            return random.choice(['early', 'early', 'mainstream'])
        elif age > 50:
            return random.choice(['mainstream', 'late', 'late'])
        else:
            return random.choice(['early', 'mainstream', 'late'])
    
    def _generate_personality_traits(self) -> Dict[str, float]:
        """Generate Big Five personality traits"""
        traits = {}
        for trait in self.personality_traits:
            # Generate values between 0.0 and 1.0 with normal distribution
            value = max(0.0, min(1.0, random.gauss(0.5, 0.2)))
            traits[trait] = round(value, 2)
        return traits
    
    def _generate_values(self, age: int, income: int, personality_traits: Dict[str, float]) -> List[str]:
        """Generate core values based on demographics and personality"""
        selected_values = []
        
        # Age-based value tendencies
        if age < 30:
            age_values = ['innovation', 'independence', 'achievement', 'convenience']
        elif age < 50:
            age_values = ['family', 'security', 'quality', 'achievement']
        else:
            age_values = ['security', 'tradition', 'health', 'quality']
        
        # Income-based value tendencies
        if income > 80000:
            income_values = ['quality', 'status', 'convenience']
        else:
            income_values = ['security', 'family', 'community']
        
        # Personality-based values
        if personality_traits.get('openness', 0.5) > 0.7:
            selected_values.extend(['innovation', 'independence'])
        if personality_traits.get('conscientiousness', 0.5) > 0.7:
            selected_values.extend(['quality', 'achievement'])
        if personality_traits.get('agreeableness', 0.5) > 0.7:
            selected_values.extend(['family', 'community'])
        
        # Combine and randomize
        all_possible = age_values + income_values + selected_values
        final_values = list(set(random.choices(all_possible, k=random.randint(3, 6))))
        
        return final_values[:5]  # Limit to 5 values
    
    def _generate_lifestyle(self, age: int, income: int, location: str, personality_traits: Dict[str, float]) -> str:
        """Generate lifestyle category"""
        if age < 25:
            return 'student'
        elif age > 60:
            return 'retiree'
        elif income > 100000:
            return 'luxury_oriented'
        elif income < 35000:
            return 'budget_conscious'
        elif personality_traits.get('extraversion', 0.5) > 0.7 and 'New York' in location or 'London' in location:
            return 'urban_professional'
        elif personality_traits.get('openness', 0.5) > 0.7:
            return 'entrepreneur'
        else:
            return random.choice(['suburban_family', 'urban_professional', 'rural_traditional'])