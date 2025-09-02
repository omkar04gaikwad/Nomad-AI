import json
import requests
from datetime import datetime
from sentence_transformers import SentenceTransformer, util
import torch
import numpy as np
from typing import List, Dict, Any
import re

class TravelSearchEngine:
    def __init__(self):
        """Initialize the travel search engine with sentence transformer model"""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.weather_api_key = "your_openweather_api_key"  # Replace with actual API key
        
    def extract_travel_info(self, form_data: Dict, cohere_response: str) -> Dict[str, Any]:
        """Extract travel information from form data and Cohere response"""
        try:
            # Parse Cohere response to get budget allocation
            cohere_json = self._extract_json_from_response(cohere_response)
            
            travel_info = {
                'destination': form_data['destination'],
                'start_date': form_data['startDate'],
                'end_date': form_data['endDate'],
                'budget_per_person': float(form_data['budget']),
                'people': int(form_data['people']),
                'activities': form_data['activities'],
                'hotel_preference': form_data['hotelPreference'],
                'travel_mode': form_data['travelMode'],
                'budget_allocation': cohere_json.get('budget_allocation_per_person', {}),
                'total_trip_cost': cohere_json.get('total_trip_cost', 0),
                'hotel_sharing_note': cohere_json.get('hotel_sharing_note', ''),
                'feasibility_note': cohere_json.get('feasibility_note', ''),
                'weather_info': self._get_weather_info(form_data['destination'], form_data['startDate']),
                'season': self._get_season(form_data['startDate'])
            }
            return travel_info
        except Exception as e:
            print(f"Error extracting travel info: {e}")
            return {}
    
    def _extract_json_from_response(self, response: str) -> Dict:
        """Extract JSON from Cohere response"""
        try:
            # Find JSON pattern in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}
        except Exception as e:
            print(f"Error parsing JSON from response: {e}")
            return {}
    
    def _get_season(self, date_str: str) -> str:
        """Determine season from date"""
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            month = date.month
            
            if month in [12, 1, 2]:
                return 'winter'
            elif month in [3, 4, 5]:
                return 'spring'
            elif month in [6, 7, 8]:
                return 'summer'
            else:
                return 'autumn'
        except:
            return 'unknown'
    
    def _get_weather_info(self, destination: str, date: str) -> Dict:
        """Get weather information for destination and date"""
        try:
            # This would use OpenWeatherMap API in production
            # For now, return mock weather data
            season = self._get_season(date)
            weather_data = {
                'temperature': self._get_mock_temperature(destination, season),
                'condition': self._get_mock_condition(season),
                'season': season,
                'recommendations': self._get_weather_recommendations(season)
            }
            return weather_data
        except Exception as e:
            print(f"Error getting weather info: {e}")
            return {}
    
    def _get_mock_temperature(self, destination: str, season: str) -> Dict:
        """Mock temperature data based on destination and season"""
        base_temps = {
            'Tokyo': {'winter': 5, 'spring': 15, 'summer': 25, 'autumn': 18},
            'Paris': {'winter': 3, 'spring': 12, 'summer': 22, 'autumn': 14},
            'New York': {'winter': 0, 'spring': 12, 'summer': 24, 'autumn': 15},
            'London': {'winter': 5, 'spring': 10, 'summer': 18, 'autumn': 12}
        }
        
        temp = base_temps.get(destination, {'winter': 10, 'spring': 15, 'summer': 20, 'autumn': 15})[season]
        return {
            'min': temp - 5,
            'max': temp + 5,
            'average': temp
        }
    
    def _get_mock_condition(self, season: str) -> str:
        """Mock weather condition based on season"""
        conditions = {
            'winter': 'cold, possible snow',
            'spring': 'mild, occasional rain',
            'summer': 'warm, sunny',
            'autumn': 'cool, changing weather'
        }
        return conditions.get(season, 'variable')
    
    def _get_weather_recommendations(self, season: str) -> List[str]:
        """Get weather-based recommendations"""
        recommendations = {
            'winter': ['Pack warm clothing', 'Check for snow closures', 'Indoor activities recommended'],
            'spring': ['Light jacket recommended', 'Umbrella for rain', 'Cherry blossom viewing'],
            'summer': ['Light clothing', 'Sunscreen essential', 'Outdoor activities ideal'],
            'autumn': ['Layered clothing', 'Beautiful fall colors', 'Moderate outdoor activities']
        }
        return recommendations.get(season, ['Check local weather forecast'])
    
    def search_hotels(self, travel_info: Dict) -> List[Dict]:
        """Search for hotels based on travel information"""
        query = f"hotels in {travel_info['destination']} {travel_info['hotel_preference']} {travel_info['season']}"
        
        # Mock hotel database with embeddings
        hotels_db = self._get_mock_hotels_db(travel_info['destination'])
        
        # Create embeddings for query and hotels
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        hotel_embeddings = self.model.encode([hotel['description'] for hotel in hotels_db], convert_to_tensor=True)
        
        # Calculate similarities
        similarities = util.pytorch_cos_sim(query_embedding, hotel_embeddings)[0]
        
        # Get top matches
        top_indices = torch.topk(similarities, min(5, len(hotels_db))).indices
        
        results = []
        for idx in top_indices:
            hotel = hotels_db[idx]
            hotel['similarity_score'] = float(similarities[idx])
            hotel['price_per_night'] = self._calculate_hotel_price(
                hotel['category'], 
                travel_info['budget_allocation'].get('hotel', 0),
                travel_info['people']
            )
            results.append(hotel)
        
        return sorted(results, key=lambda x: x['similarity_score'], reverse=True)
    
    def search_flights(self, travel_info: Dict) -> List[Dict]:
        """Search for flights based on travel information"""
        query = f"flights from {travel_info.get('origin', 'any')} to {travel_info['destination']} {travel_info['travel_mode']}"
        
        # Mock flight database
        flights_db = self._get_mock_flights_db(travel_info['destination'])
        
        # Create embeddings
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        flight_embeddings = self.model.encode([flight['description'] for flight in flights_db], convert_to_tensor=True)
        
        # Calculate similarities
        similarities = util.pytorch_cos_sim(query_embedding, flight_embeddings)[0]
        
        # Get top matches
        top_indices = torch.topk(similarities, min(5, len(flights_db))).indices
        
        results = []
        for idx in top_indices:
            flight = flights_db[idx]
            flight['similarity_score'] = float(similarities[idx])
            flight['price'] = self._calculate_flight_price(
                flight['airline'],
                travel_info['budget_allocation'].get('flights', 0)
            )
            results.append(flight)
        
        return sorted(results, key=lambda x: x['similarity_score'], reverse=True)
    
    def search_restaurants(self, travel_info: Dict) -> List[Dict]:
        """Search for restaurants based on travel information"""
        query = f"restaurants in {travel_info['destination']} {travel_info['season']} local cuisine"
        
        # Mock restaurant database
        restaurants_db = self._get_mock_restaurants_db(travel_info['destination'])
        
        # Create embeddings
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        restaurant_embeddings = self.model.encode([rest['description'] for rest in restaurants_db], convert_to_tensor=True)
        
        # Calculate similarities
        similarities = util.pytorch_cos_sim(query_embedding, restaurant_embeddings)[0]
        
        # Get top matches
        top_indices = torch.topk(similarities, min(5, len(restaurants_db))).indices
        
        results = []
        for idx in top_indices:
            restaurant = restaurants_db[idx]
            restaurant['similarity_score'] = float(similarities[idx])
            restaurant['avg_meal_price'] = self._calculate_meal_price(
                restaurant['cuisine_type'],
                travel_info['budget_allocation'].get('meals', 0)
            )
            results.append(restaurant)
        
        return sorted(results, key=lambda x: x['similarity_score'], reverse=True)
    
    def search_activities(self, travel_info: Dict) -> List[Dict]:
        """Search for activities based on travel information"""
        activities_query = ' '.join(travel_info['activities'])
        query = f"activities in {travel_info['destination']} {activities_query} {travel_info['season']}"
        
        # Mock activities database
        activities_db = self._get_mock_activities_db(travel_info['destination'])
        
        # Create embeddings
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        activity_embeddings = self.model.encode([act['description'] for act in activities_db], convert_to_tensor=True)
        
        # Calculate similarities
        similarities = util.pytorch_cos_sim(query_embedding, activity_embeddings)[0]
        
        # Get top matches
        top_indices = torch.topk(similarities, min(5, len(activities_db))).indices
        
        results = []
        for idx in top_indices:
            activity = activities_db[idx]
            activity['similarity_score'] = float(similarities[idx])
            activity['price'] = self._calculate_activity_price(
                activity['type'],
                travel_info['budget_allocation'].get('activities', 0)
            )
            results.append(activity)
        
        return sorted(results, key=lambda x: x['similarity_score'], reverse=True)
    
    def _get_mock_hotels_db(self, destination: str) -> List[Dict]:
        """Mock hotel database"""
        hotels = {
            'Tokyo': [
                {'name': 'Park Hyatt Tokyo', 'category': 'luxury', 'description': 'luxury hotel tokyo shinjuku skyline views'},
                {'name': 'Hotel Gracery Shinjuku', 'category': 'mid-range', 'description': 'mid-range hotel tokyo shinjuku godzilla'},
                {'name': 'Capsule Hotel Anshin Oyado', 'category': 'budget', 'description': 'budget capsule hotel tokyo shinjuku'},
                {'name': 'Aman Tokyo', 'category': 'luxury', 'description': 'ultra luxury hotel tokyo otemachi views'},
                {'name': 'Tokyu Stay Ginza', 'category': 'mid-range', 'description': 'mid-range hotel tokyo ginza shopping'}
            ],
            'Paris': [
                {'name': 'Ritz Paris', 'category': 'luxury', 'description': 'luxury hotel paris place vendome'},
                {'name': 'Hotel du Louvre', 'category': 'mid-range', 'description': 'mid-range hotel paris louvre museum'},
                {'name': 'Hotel des Arts', 'category': 'budget', 'description': 'budget hotel paris montmartre'},
                {'name': 'Four Seasons George V', 'category': 'luxury', 'description': 'ultra luxury hotel paris champs elysees'},
                {'name': 'Hotel de la Paix', 'category': 'mid-range', 'description': 'mid-range hotel paris latin quarter'}
            ]
        }
        return hotels.get(destination, [])
    
    def _get_mock_flights_db(self, destination: str) -> List[Dict]:
        """Mock flight database"""
        flights = {
            'Tokyo': [
                {'airline': 'Japan Airlines', 'description': 'direct flight tokyo japan airlines premium economy'},
                {'airline': 'ANA', 'description': 'direct flight tokyo ana all nippon airways business'},
                {'airline': 'United Airlines', 'description': 'connecting flight tokyo united airlines economy'},
                {'airline': 'Singapore Airlines', 'description': 'connecting flight tokyo singapore airlines premium'},
                {'airline': 'Qatar Airways', 'description': 'connecting flight tokyo qatar airways business'}
            ],
            'Paris': [
                {'airline': 'Air France', 'description': 'direct flight paris air france premium economy'},
                {'airline': 'Lufthansa', 'description': 'connecting flight paris lufthansa business class'},
                {'airline': 'British Airways', 'description': 'connecting flight paris british airways economy'},
                {'airline': 'Emirates', 'description': 'connecting flight paris emirates first class'},
                {'airline': 'Delta Airlines', 'description': 'direct flight paris delta airlines economy'}
            ]
        }
        return flights.get(destination, [])
    
    def _get_mock_restaurants_db(self, destination: str) -> List[Dict]:
        """Mock restaurant database"""
        restaurants = {
            'Tokyo': [
                {'name': 'Sukiyabashi Jiro', 'cuisine_type': 'sushi', 'description': 'famous sushi restaurant tokyo ginza jiro'},
                {'name': 'Narisawa', 'cuisine_type': 'fine_dining', 'description': 'fine dining restaurant tokyo aoyama french japanese'},
                {'name': 'Ichiran Ramen', 'cuisine_type': 'ramen', 'description': 'popular ramen restaurant tokyo shinjuku'},
                {'name': 'Tsukiji Outer Market', 'cuisine_type': 'seafood', 'description': 'seafood market restaurant tokyo tsukiji'},
                {'name': 'Gonpachi', 'cuisine_type': 'izakaya', 'description': 'izakaya restaurant tokyo roppongi'}
            ],
            'Paris': [
                {'name': 'Le Comptoir du Relais', 'cuisine_type': 'french', 'description': 'french bistro paris saint germain'},
                {'name': 'L\'Astrance', 'cuisine_type': 'fine_dining', 'description': 'fine dining restaurant paris 16th arrondissement'},
                {'name': 'Le Chateaubriand', 'cuisine_type': 'french', 'description': 'modern french restaurant paris 11th arrondissement'},
                {'name': 'Breizh Cafe', 'cuisine_type': 'crepes', 'description': 'crepe restaurant paris marais'},
                {'name': 'L\'As du Fallafel', 'cuisine_type': 'middle_eastern', 'description': 'falafel restaurant paris marais'}
            ]
        }
        return restaurants.get(destination, [])
    
    def _get_mock_activities_db(self, destination: str) -> List[Dict]:
        """Mock activities database"""
        activities = {
            'Tokyo': [
                {'name': 'Senso-ji Temple', 'type': 'culture', 'description': 'traditional temple tokyo asakusa culture'},
                {'name': 'Shibuya Crossing', 'type': 'sightseeing', 'description': 'famous crossing tokyo shibuya people watching'},
                {'name': 'Tsukiji Fish Market', 'type': 'food', 'description': 'fish market tokyo tsukiji seafood food'},
                {'name': 'Tokyo Skytree', 'type': 'sightseeing', 'description': 'observation tower tokyo skytree views'},
                {'name': 'Meiji Shrine', 'type': 'culture', 'description': 'shrine tokyo harajuku culture relaxation'}
            ],
            'Paris': [
                {'name': 'Eiffel Tower', 'type': 'sightseeing', 'description': 'iconic tower paris eiffel views'},
                {'name': 'Louvre Museum', 'type': 'culture', 'description': 'art museum paris louvre culture'},
                {'name': 'Notre-Dame Cathedral', 'type': 'culture', 'description': 'cathedral paris notre dame culture'},
                {'name': 'Champs-Elysees', 'type': 'sightseeing', 'description': 'famous avenue paris champs elysees shopping'},
                {'name': 'Montmartre', 'type': 'culture', 'description': 'artistic neighborhood paris montmartre culture'}
            ]
        }
        return activities.get(destination, [])
    
    def _calculate_hotel_price(self, category: str, budget: float, people: int) -> float:
        """Calculate hotel price based on category and budget"""
        base_prices = {'luxury': 300, 'mid-range': 150, 'budget': 80}
        base_price = base_prices.get(category, 150)
        
        # Adjust for number of people (room sharing)
        if people > 1:
            base_price = base_price * 1.5  # Shared room premium
        
        return min(base_price, budget / 3)  # Max 1/3 of budget per night
    
    def _calculate_flight_price(self, airline: str, budget: float) -> float:
        """Calculate flight price based on airline and budget"""
        airline_prices = {
            'Japan Airlines': 1200,
            'ANA': 1100,
            'Air France': 1000,
            'Lufthansa': 950,
            'United Airlines': 800,
            'Singapore Airlines': 1300,
            'Qatar Airways': 1400,
            'British Airways': 900,
            'Emirates': 1500,
            'Delta Airlines': 850
        }
        return min(airline_prices.get(airline, 1000), budget)
    
    def _calculate_meal_price(self, cuisine_type: str, budget: float) -> float:
        """Calculate meal price based on cuisine type and budget"""
        cuisine_prices = {
            'fine_dining': 150,
            'french': 80,
            'sushi': 100,
            'ramen': 15,
            'seafood': 60,
            'izakaya': 40,
            'crepes': 20,
            'middle_eastern': 25
        }
        return min(cuisine_prices.get(cuisine_type, 50), budget / 10)  # Max 1/10 of budget per meal
    
    def _calculate_activity_price(self, activity_type: str, budget: float) -> float:
        """Calculate activity price based on type and budget"""
        activity_prices = {
            'culture': 25,
            'sightseeing': 30,
            'food': 50,
            'relaxation': 40
        }
        return min(activity_prices.get(activity_type, 30), budget / 5)  # Max 1/5 of budget per activity
    
    def get_travel_recommendations(self, form_data: Dict, cohere_response: str) -> Dict[str, Any]:
        """Get comprehensive travel recommendations"""
        travel_info = self.extract_travel_info(form_data, cohere_response)
        
        if not travel_info:
            return {'error': 'Failed to extract travel information'}
        
        recommendations = {
            'travel_info': travel_info,
            'hotels': self.search_hotels(travel_info),
            'flights': self.search_flights(travel_info),
            'restaurants': self.search_restaurants(travel_info),
            'activities': self.search_activities(travel_info),
            'weather_advisory': self._get_weather_advisory(travel_info),
            'local_events': self._get_local_events(travel_info),
            'safety_notes': self._get_safety_notes(travel_info)
        }
        
        return recommendations
    
    def _get_weather_advisory(self, travel_info: Dict) -> Dict:
        """Get weather advisory based on travel info"""
        weather = travel_info.get('weather_info', {})
        season = weather.get('season', 'unknown')
        
        advisories = {
            'winter': ['Pack warm clothing', 'Check for snow closures', 'Indoor activities recommended'],
            'spring': ['Light jacket recommended', 'Umbrella for rain', 'Cherry blossom viewing'],
            'summer': ['Light clothing', 'Sunscreen essential', 'Outdoor activities ideal'],
            'autumn': ['Layered clothing', 'Beautiful fall colors', 'Moderate outdoor activities']
        }
        
        return {
            'season': season,
            'temperature': weather.get('temperature', {}),
            'condition': weather.get('condition', ''),
            'recommendations': advisories.get(season, ['Check local weather forecast'])
        }
    
    def _get_local_events(self, travel_info: Dict) -> List[Dict]:
        """Get local events during travel period"""
        destination = travel_info['destination']
        season = travel_info['weather_info'].get('season', 'unknown')
        
        events_db = {
            'Tokyo': {
                'spring': [{'name': 'Cherry Blossom Festival', 'date': 'March-April', 'description': 'Hanami cherry blossom viewing'}],
                'summer': [{'name': 'Gion Matsuri', 'date': 'July', 'description': 'Traditional festival'}],
                'autumn': [{'name': 'Autumn Leaves Festival', 'date': 'November', 'description': 'Fall colors viewing'}],
                'winter': [{'name': 'Illumination Festival', 'date': 'December', 'description': 'Winter light displays'}]
            },
            'Paris': {
                'spring': [{'name': 'Paris Fashion Week', 'date': 'March', 'description': 'Fashion industry event'}],
                'summer': [{'name': 'Bastille Day', 'date': 'July 14', 'description': 'National celebration'}],
                'autumn': [{'name': 'Paris Wine Festival', 'date': 'October', 'description': 'Wine tasting event'}],
                'winter': [{'name': 'Christmas Markets', 'date': 'December', 'description': 'Holiday markets'}]
            }
        }
        
        return events_db.get(destination, {}).get(season, [])
    
    def _get_safety_notes(self, travel_info: Dict) -> List[str]:
        """Get safety notes for the destination"""
        destination = travel_info['destination']
        
        safety_db = {
            'Tokyo': [
                'Very safe city with low crime rates',
                'Efficient public transportation',
                'English signage available in major areas',
                'Emergency services: 110 (police), 119 (fire/ambulance)'
            ],
            'Paris': [
                'Generally safe but beware of pickpockets in tourist areas',
                'Avoid walking alone at night in certain areas',
                'Keep valuables secure in crowded places',
                'Emergency services: 17 (police), 18 (fire), 15 (ambulance)'
            ]
        }
        
        return safety_db.get(destination, ['Check local travel advisories', 'Register with embassy if needed'])

# Example usage
if __name__ == "__main__":
    # Initialize the search engine
    search_engine = TravelSearchEngine()
    
    # Sample form data
    sample_form = {
        "origin": "Mumbai",
        "destination": "Tokyo",
        "startDate": "2025-03-15",
        "endDate": "2025-03-20",
        "strictDates": "yes",
        "budget": "2000",
        "people": "2",
        "travelMode": "partner",
        "activities": ["food", "culture", "relaxation"],
        "visitedBefore": "no",
        "hotelPreference": "mid-range"
    }
    
    # Sample Cohere response
    sample_cohere_response = '''
    {
        "budget_allocation_per_person": {
            "flights": 800,
            "hotel": 400,
            "meals": 300,
            "activities": 300,
            "documentation": 200
        },
        "total_trip_cost": 4000,
        "hotel_sharing_note": "Mid-range hotel chosen for couple, room shared by both travelers to optimize costs.",
        "feasibility_note": "Trip is feasible within budget with room sharing strategy.",
        "new_dates": []
    }
    '''
    
    # Get recommendations
    recommendations = search_engine.get_travel_recommendations(sample_form, sample_cohere_response)
    
    # Print results
    print("=== TRAVEL RECOMMENDATIONS ===")
    print(json.dumps(recommendations, indent=2))
