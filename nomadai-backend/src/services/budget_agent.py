import json
import os
from typing import Dict, Any
import cohere
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BudgetAgent:
    """
    Budget Agent that analyzes travel preferences and suggests budget allocation
    using Cohere AI for intelligent budget planning.
    """
    
    def __init__(self):
        self.cohere_client = cohere.Client(os.getenv("COHERE_API_KEY"))
    
    def analyze_budget(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze travel preferences and suggest budget allocation.
        
        Args:
            form_data: Travel form data from user
            
        Returns:
            Dictionary with budget analysis and recommendations
        """
        try:
            # Extract key information
            budget = int(form_data.get('budget', 0))
            destination = form_data.get('destination', '')
            people = int(form_data.get('people', 1))
            activities = form_data.get('activities', [])
            hotel_preference = form_data.get('hotelPreference', 'mid-range')
            travel_mode = form_data.get('travelMode', 'plane')
            
            # Create prompt for Cohere
            prompt = self._create_budget_prompt(
                budget, destination, people, activities, 
                hotel_preference, travel_mode
            )
            
            # Get response from Cohere
            response = self.cohere_client.generate(
                model="command",
                prompt=prompt,
                max_tokens=500,
                temperature=0.7
            )
            
            # Parse the response
            budget_analysis = self._parse_budget_response(response.generations[0].text)
            
            return {
                "success": True,
                "budget_analysis": budget_analysis,
                "total_budget": budget,
                "per_person_budget": budget // people,
                "recommendations": budget_analysis.get("recommendations", []),
                "budget_allocation": budget_analysis.get("allocation", {}),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_allocation": self._get_fallback_allocation(budget, people)
            }
    
    def _create_budget_prompt(self, budget: int, destination: str, people: int, 
                            activities: list, hotel_preference: str, travel_mode: str) -> str:
        """Create a detailed prompt for budget analysis."""
        
        return f"""
        You are an expert travel budget planner. Analyze the following travel request and provide a detailed budget breakdown in JSON format.

        Travel Details:
        - Total Budget: ${budget}
        - Destination: {destination}
        - Number of People: {people}
        - Activities: {', '.join(activities)}
        - Hotel Preference: {hotel_preference}
        - Travel Mode: {travel_mode}

        Please provide a JSON response with the following structure:
        {{
            "allocation": {{
                "flights": {{
                    "percentage": 40,
                    "amount": 0,
                    "notes": "Estimated flight costs"
                }},
                "accommodation": {{
                    "percentage": 30,
                    "amount": 0,
                    "notes": "Hotel costs based on preference"
                }},
                "activities": {{
                    "percentage": 20,
                    "amount": 0,
                    "notes": "Sightseeing and experiences"
                }},
                "food": {{
                    "percentage": 8,
                    "amount": 0,
                    "notes": "Daily meals and dining"
                }},
                "transportation": {{
                    "percentage": 2,
                    "amount": 0,
                    "notes": "Local transportation"
                }}
            }},
            "recommendations": [
                "Consider booking flights 2-3 months in advance for better prices",
                "Look for hotel deals during off-peak seasons",
                "Mix free activities with paid experiences to balance costs"
            ],
            "budget_category": "budget/mid-range/luxury",
            "feasibility_score": 85,
            "money_saving_tips": [
                "Use public transportation instead of taxis",
                "Book activities in advance for discounts",
                "Consider alternative accommodation options"
            ]
        }}

        Focus on realistic estimates and practical advice. Ensure the total allocation equals 100%.
        """
    
    def _parse_budget_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the Cohere response and extract budget information."""
        try:
            # Try to extract JSON from the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback parsing
                return self._extract_budget_info(response_text)
                
        except json.JSONDecodeError:
            return self._extract_budget_info(response_text)
    
    def _extract_budget_info(self, text: str) -> Dict[str, Any]:
        """Extract budget information from unstructured text."""
        # Simple fallback parsing
        return {
            "allocation": {
                "flights": {"percentage": 40, "amount": 0, "notes": "Flight costs"},
                "accommodation": {"percentage": 30, "amount": 0, "notes": "Hotel costs"},
                "activities": {"percentage": 20, "amount": 0, "notes": "Activities"},
                "food": {"percentage": 8, "amount": 0, "notes": "Food costs"},
                "transportation": {"percentage": 2, "amount": 0, "notes": "Local transport"}
            },
            "recommendations": [
                "Book flights in advance for better prices",
                "Consider alternative accommodation options",
                "Mix free and paid activities"
            ],
            "budget_category": "mid-range",
            "feasibility_score": 80,
            "money_saving_tips": [
                "Use public transportation",
                "Book activities in advance",
                "Look for hotel deals"
            ]
        }
    
    def _get_fallback_allocation(self, budget: int, people: int) -> Dict[str, Any]:
        """Provide fallback budget allocation if AI analysis fails."""
        per_person = budget // people
        
        return {
            "flights": {"percentage": 40, "amount": int(per_person * 0.4), "notes": "Flight costs"},
            "accommodation": {"percentage": 30, "amount": int(per_person * 0.3), "notes": "Hotel costs"},
            "activities": {"percentage": 20, "amount": int(per_person * 0.2), "notes": "Activities"},
            "food": {"percentage": 8, "amount": int(per_person * 0.08), "notes": "Food costs"},
            "transportation": {"percentage": 2, "amount": int(per_person * 0.02), "notes": "Local transport"}
        }
