import json
import os
from typing import Dict, Any, List
from sentence_transformers import SentenceTransformer
import numpy as np
from pathlib import Path

class SearchAgent:
    """
    Search Agent that uses Hugging Face embeddings to find relevant flights, 
    hotels, and activities from mock datasets based on user preferences.
    """
    
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.data_path = Path(__file__).parent.parent.parent / "data"
        self.flights_data = self._load_data("flights.json")
        self.hotels_data = self._load_data("hotels.json")
        self.activities_data = self._load_data("activities.json")
        
    def _load_data(self, filename: str) -> List[Dict[str, Any]]:
        """Load data from JSON files."""
        try:
            with open(self.data_path / filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {filename} not found, using empty dataset")
            return []
    
    def search_recommendations(self, form_data: Dict[str, Any], budget_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for relevant flights, hotels, and activities based on user preferences.
        
        Args:
            form_data: User travel form data
            budget_analysis: Budget analysis from BudgetAgent
            
        Returns:
            Dictionary with recommended flights, hotels, and activities
        """
        try:
            # Extract search parameters
            origin = form_data.get('origin', '')
            destination = form_data.get('destination', '')
            budget = int(form_data.get('budget', 0))
            people = int(form_data.get('people', 1))
            activities_preferences = form_data.get('activities', [])
            hotel_preference = form_data.get('hotelPreference', 'mid-range')
            
            # Get budget allocation
            budget_allocation = budget_analysis.get('budget_analysis', {}).get('allocation', {})
            flight_budget = budget_allocation.get('flights', {}).get('amount', budget * 0.4)
            hotel_budget = budget_allocation.get('accommodation', {}).get('amount', budget * 0.3)
            activity_budget = budget_allocation.get('activities', {}).get('amount', budget * 0.2)
            
            # Search for recommendations
            flights = self._search_flights(origin, destination, flight_budget, people)
            hotels = self._search_hotels(destination, hotel_preference, hotel_budget, people)
            activities = self._search_activities(destination, activities_preferences, activity_budget)
            
            return {
                "success": True,
                "flights": flights,
                "hotels": hotels,
                "activities": activities,
                "search_summary": {
                    "total_flights_found": len(flights),
                    "total_hotels_found": len(hotels),
                    "total_activities_found": len(activities),
                    "budget_utilization": {
                        "flights": sum(f.get('price_estimate', 0) for f in flights),
                        "hotels": sum(h.get('price_estimate', 0) * people for h in hotels),
                        "activities": sum(a.get('cost_estimate', 0) for a in activities)
                    }
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "flights": [],
                "hotels": [],
                "activities": []
            }
    
    def _search_flights(self, origin: str, destination: str, budget: float, people: int) -> List[Dict[str, Any]]:
        """Search for flights matching criteria."""
        relevant_flights = []
        
        for flight in self.flights_data:
            # Basic filtering
            if (flight.get('origin', '').lower() == origin.lower() and 
                flight.get('destination', '').lower() == destination.lower()):
                
                # Check budget constraint
                total_cost = flight.get('price_estimate', 0) * people
                if total_cost <= budget:
                    relevant_flights.append(flight)
        
        # Sort by price and return top 3
        relevant_flights.sort(key=lambda x: x.get('price_estimate', 0))
        return relevant_flights[:3]
    
    def _search_hotels(self, destination: str, preference: str, budget: float, people: int) -> List[Dict[str, Any]]:
        """Search for hotels matching criteria."""
        relevant_hotels = []
        
        for hotel in self.hotels_data:
            # Basic filtering
            if hotel.get('location', '').lower().startswith(destination.lower()):
                
                # Check tier preference
                tier_match = self._match_hotel_tier(hotel.get('tier', ''), preference)
                
                # Check budget constraint
                total_cost = hotel.get('price_estimate', 0) * people
                if tier_match and total_cost <= budget:
                    relevant_hotels.append(hotel)
        
        # Sort by rating and return top 3
        relevant_hotels.sort(key=lambda x: x.get('rating', 0), reverse=True)
        return relevant_hotels[:3]
    
    def _search_activities(self, destination: str, preferences: List[str], budget: float) -> List[Dict[str, Any]]:
        """Search for activities matching criteria using embeddings."""
        relevant_activities = []
        
        # Create query embedding
        query_text = f"activities in {destination} for {', '.join(preferences)}"
        query_embedding = self.model.encode(query_text)
        
        activity_scores = []
        
        for activity in self.activities_data:
            # Basic location filtering
            if activity.get('location', '').lower().startswith(destination.lower()):
                
                # Check budget constraint
                if activity.get('cost_estimate', 0) <= budget:
                    
                    # Calculate similarity score using embeddings
                    activity_text = f"{activity.get('name', '')} {activity.get('description', '')} {' '.join(activity.get('tags', []))}"
                    activity_embedding = self.model.encode(activity_text)
                    
                    similarity = np.dot(query_embedding, activity_embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(activity_embedding)
                    )
                    
                    # Check tag overlap
                    tag_overlap = len(set(preferences) & set(activity.get('tags', [])))
                    
                    # Combined score
                    combined_score = similarity * 0.7 + (tag_overlap / len(preferences)) * 0.3
                    
                    activity_scores.append((activity, combined_score))
        
        # Sort by score and return top 5
        activity_scores.sort(key=lambda x: x[1], reverse=True)
        relevant_activities = [activity for activity, score in activity_scores[:5]]
        
        return relevant_activities
    
    def _match_hotel_tier(self, hotel_tier: str, preference: str) -> bool:
        """Match hotel tier with user preference."""
        tier_mapping = {
            'budget': ['budget'],
            'mid-range': ['mid-range', 'budget'],
            'luxury': ['luxury', 'mid-range', 'budget']
        }
        
        return hotel_tier in tier_mapping.get(preference.lower(), [])
    
    def get_semantic_search_results(self, query: str, category: str = 'all') -> List[Dict[str, Any]]:
        """
        Perform semantic search across all datasets.
        
        Args:
            query: Search query
            category: 'flights', 'hotels', 'activities', or 'all'
            
        Returns:
            List of relevant items with similarity scores
        """
        query_embedding = self.model.encode(query)
        results = []
        
        datasets = {
            'flights': self.flights_data,
            'hotels': self.hotels_data,
            'activities': self.activities_data
        }
        
        for cat, data in datasets.items():
            if category == 'all' or category == cat:
                for item in data:
                    # Create text representation for embedding
                    if cat == 'flights':
                        item_text = f"{item.get('airline', '')} {item.get('origin', '')} to {item.get('destination', '')}"
                    elif cat == 'hotels':
                        item_text = f"{item.get('hotel_name', '')} {item.get('location', '')} {item.get('description', '')}"
                    else:  # activities
                        item_text = f"{item.get('name', '')} {item.get('description', '')} {' '.join(item.get('tags', []))}"
                    
                    item_embedding = self.model.encode(item_text)
                    similarity = np.dot(query_embedding, item_embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(item_embedding)
                    )
                    
                    results.append({
                        'item': item,
                        'category': cat,
                        'similarity_score': float(similarity)
                    })
        
        # Sort by similarity score
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return results[:10]  # Return top 10 results
