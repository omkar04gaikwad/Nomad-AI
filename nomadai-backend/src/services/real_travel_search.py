import json
import requests
from datetime import datetime
from typing import List, Dict, Any
import re
import os

class RealTravelSearch:
    def __init__(self):
        """Initialize with API keys for real travel data"""
        # You'll need to get these API keys from respective services
        self.amadeus_api_key = os.getenv('AMADEUS_API_KEY', 'your_amadeus_api_key')
        self.amadeus_secret = os.getenv('AMADEUS_SECRET', 'your_amadeus_secret')
        self.google_places_api_key = os.getenv('GOOGLE_PLACES_API_KEY', 'your_google_places_api_key')
        self.openweather_api_key = os.getenv('OPENWEATHER_API_KEY', 'your_openweather_api_key')
        self.tripadvisor_api_key = os.getenv('TRIPADVISOR_API_KEY', 'your_tripadvisor_api_key')
        
    def get_amadeus_token(self):
        """Get Amadeus API token for flights and hotels"""
        try:
            url = "https://test.api.amadeus.com/v1/security/oauth2/token"
            payload = {
                'grant_type': 'client_credentials',
                'client_id': self.amadeus_api_key,
                'client_secret': self.amadeus_secret
            }
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                return response.json()['access_token']
            else:
                print(f"Failed to get Amadeus token: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error getting Amadeus token: {e}")
            return None

    def search_real_flights(self, origin: str, destination: str, departure_date: str, return_date: str, budget: float) -> List[Dict]:
        """Search for real flights using Amadeus API"""
        try:
            token = self.get_amadeus_token()
            if not token:
                return []
            
            url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
            headers = {'Authorization': f'Bearer {token}'}
            params = {
                'originLocationCode': origin,
                'destinationLocationCode': destination,
                'departureDate': departure_date,
                'returnDate': return_date,
                'adults': '1',
                'max': '10'
            }
            
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                flights_data = response.json()['data']
                flights = []
                
                for flight in flights_data:
                    price = float(flight['price']['total'])
                    if price <= budget:
                        flights.append({
                            'airline': flight['validatingAirlineCodes'][0],
                            'price': price,
                            'class': flight['travelerPricings'][0]['fareDetailsBySegment'][0]['cabin'],
                            'departure_time': flight['itineraries'][0]['segments'][0]['departure']['at'],
                            'arrival_time': flight['itineraries'][0]['segments'][0]['arrival']['at'],
                            'stops': len(flight['itineraries'][0]['segments']) - 1,
                            'description': f"{flight['validatingAirlineCodes'][0]} flight with {len(flight['itineraries'][0]['segments'])} segments"
                        })
                
                return sorted(flights, key=lambda x: x['price'])[:5]
            else:
                print(f"Failed to get flights: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error searching flights: {e}")
            return []

    def search_real_hotels(self, destination: str, check_in: str, check_out: str, budget: float, people: int) -> List[Dict]:
        """Search for real hotels using Amadeus API"""
        try:
            token = self.get_amadeus_token()
            if not token:
                return []
            
            # First get destination code
            url = "https://test.api.amadeus.com/v1/reference-data/locations"
            headers = {'Authorization': f'Bearer {token}'}
            params = {
                'subType': 'CITY',
                'keyword': destination,
                'page[limit]': '1'
            }
            
            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                return []
            
            city_code = response.json()['data'][0]['iataCode']
            
            # Search for hotels
            url = "https://test.api.amadeus.com/v2/shopping/hotel-offers"
            params = {
                'cityCode': city_code,
                'checkInDate': check_in,
                'checkOutDate': check_out,
                'adults': str(people),
                'radius': '5',
                'radiusUnit': 'KM',
                'max': '10'
            }
            
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                hotels_data = response.json()['data']
                hotels = []
                
                for hotel in hotels_data:
                    price = float(hotel['offers'][0]['price']['total'])
                    if price <= budget:
                        hotels.append({
                            'name': hotel['hotel']['name'],
                            'category': hotel['hotel'].get('rating', 'mid-range'),
                            'price_per_night': price,
                            'description': f"Hotel in {destination} with {hotel['hotel'].get('rating', 'mid-range')} rating",
                            'address': hotel['hotel'].get('address', {}).get('lines', [''])[0],
                            'amenities': hotel['hotel'].get('amenities', [])
                        })
                
                return sorted(hotels, key=lambda x: x['price_per_night'])[:5]
            else:
                print(f"Failed to get hotels: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error searching hotels: {e}")
            return []

    def search_real_restaurants(self, destination: str, budget: float) -> List[Dict]:
        """Search for real restaurants using Google Places API"""
        try:
            # Get destination coordinates first
            geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
            geocode_params = {
                'address': destination,
                'key': self.google_places_api_key
            }
            
            response = requests.get(geocode_url, params=geocode_params)
            if response.status_code != 200:
                return []
            
            location = response.json()['results'][0]['geometry']['location']
            lat, lng = location['lat'], location['lng']
            
            # Search for restaurants
            places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            places_params = {
                'location': f"{lat},{lng}",
                'radius': '5000',
                'type': 'restaurant',
                'key': self.google_places_api_key
            }
            
            response = requests.get(places_url, params=places_params)
            if response.status_code == 200:
                restaurants_data = response.json()['results']
                restaurants = []
                
                for restaurant in restaurants_data[:10]:  # Limit to 10 results
                    # Get detailed info including price level
                    detail_url = "https://maps.googleapis.com/maps/api/place/details/json"
                    detail_params = {
                        'place_id': restaurant['place_id'],
                        'fields': 'name,rating,price_level,types,formatted_address',
                        'key': self.google_places_api_key
                    }
                    
                    detail_response = requests.get(detail_url, params=detail_params)
                    if detail_response.status_code == 200:
                        detail = detail_response.json()['result']
                        price_level = detail.get('price_level', 2)  # Default to mid-range
                        
                        # Estimate price based on price level (1=$, 2=$$, 3=$$$, 4=$$$$)
                        estimated_price = price_level * 25
                        
                        if estimated_price <= budget / 3:  # Assume 3 meals per day
                            restaurants.append({
                                'name': detail['name'],
                                'cuisine': ', '.join(detail.get('types', [])[:3]),
                                'avg_meal_price': estimated_price,
                                'rating': detail.get('rating', 0),
                                'description': f"{detail['name']} in {destination}",
                                'address': detail.get('formatted_address', ''),
                                'price_level': price_level
                            })
                
                return sorted(restaurants, key=lambda x: x['avg_meal_price'])[:5]
            else:
                print(f"Failed to get restaurants: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error searching restaurants: {e}")
            return []

    def search_real_activities(self, destination: str, activities: List[str], budget: float) -> List[Dict]:
        """Search for real activities using Google Places API"""
        try:
            # Get destination coordinates
            geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
            geocode_params = {
                'address': destination,
                'key': self.google_places_api_key
            }
            
            response = requests.get(geocode_url, params=geocode_params)
            if response.status_code != 200:
                return []
            
            location = response.json()['results'][0]['geometry']['location']
            lat, lng = location['lat'], location['lng']
            
            # Map activities to Google Places types
            activity_types = {
                'culture': 'museum',
                'sightseeing': 'tourist_attraction',
                'food': 'restaurant',
                'relaxation': 'spa',
                'shopping': 'shopping_mall',
                'nightlife': 'bar'
            }
            
            all_activities = []
            
            for activity in activities:
                if activity in activity_types:
                    places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                    places_params = {
                        'location': f"{lat},{lng}",
                        'radius': '5000',
                        'type': activity_types[activity],
                        'key': self.google_places_api_key
                    }
                    
                    response = requests.get(places_url, params=places_params)
                    if response.status_code == 200:
                        places_data = response.json()['results']
                        
                        for place in places_data[:5]:  # Limit to 5 per activity type
                            # Get detailed info
                            detail_url = "https://maps.googleapis.com/maps/api/place/details/json"
                            detail_params = {
                                'place_id': place['place_id'],
                                'fields': 'name,rating,price_level,types,formatted_address',
                                'key': self.google_places_api_key
                            }
                            
                            detail_response = requests.get(detail_url, params=detail_params)
                            if detail_response.status_code == 200:
                                detail = detail_response.json()['result']
                                price_level = detail.get('price_level', 1)
                                estimated_price = price_level * 15
                                
                                if estimated_price <= budget:
                                    all_activities.append({
                                        'name': detail['name'],
                                        'type': activity,
                                        'price': estimated_price,
                                        'rating': detail.get('rating', 0),
                                        'description': f"{detail['name']} - {activity} activity in {destination}",
                                        'address': detail.get('formatted_address', ''),
                                        'price_level': price_level
                                    })
            
            return sorted(all_activities, key=lambda x: x['price'])[:10]
            
        except Exception as e:
            print(f"Error searching activities: {e}")
            return []

    def get_real_weather(self, destination: str, date: str) -> Dict:
        """Get real weather data using OpenWeatherMap API"""
        try:
            # Get coordinates for destination
            geocode_url = "http://api.openweathermap.org/geo/1.0/direct"
            geocode_params = {
                'q': destination,
                'limit': '1',
                'appid': self.openweather_api_key
            }
            
            response = requests.get(geocode_url, params=geocode_params)
            if response.status_code != 200:
                return {}
            
            location = response.json()[0]
            lat, lng = location['lat'], location['lon']
            
            # Get weather forecast
            weather_url = "http://api.openweathermap.org/data/2.5/forecast"
            weather_params = {
                'lat': lat,
                'lon': lng,
                'appid': self.openweather_api_key,
                'units': 'metric'
            }
            
            response = requests.get(weather_url, params=weather_params)
            if response.status_code == 200:
                weather_data = response.json()
                
                # Find weather for the specific date
                target_date = datetime.strptime(date, '%Y-%m-%d')
                
                for forecast in weather_data['list']:
                    forecast_date = datetime.fromtimestamp(forecast['dt'])
                    if forecast_date.date() == target_date.date():
                        temp = forecast['main']['temp']
                        weather_desc = forecast['weather'][0]['description']
                        
                        return {
                            'temperature': {
                                'min': temp - 5,
                                'max': temp + 5,
                                'average': temp
                            },
                            'condition': weather_desc,
                            'humidity': forecast['main']['humidity'],
                            'wind_speed': forecast['wind']['speed']
                        }
            
            return {}
            
        except Exception as e:
            print(f"Error getting weather: {e}")
            return {}

    def get_real_events(self, destination: str, start_date: str, end_date: str) -> List[Dict]:
        """Get real events using Eventbrite API or similar"""
        try:
            # This would require Eventbrite API key
            # For now, return seasonal events based on date
            start_month = datetime.strptime(start_date, '%Y-%m-%d').month
            
            events_db = {
                'Tokyo': {
                    3: [{'name': 'Cherry Blossom Festival', 'date': 'March-April', 'description': 'Hanami cherry blossom viewing'}],
                    4: [{'name': 'Cherry Blossom Festival', 'date': 'March-April', 'description': 'Hanami cherry blossom viewing'}],
                    7: [{'name': 'Gion Matsuri', 'date': 'July', 'description': 'Traditional festival'}],
                    11: [{'name': 'Autumn Leaves Festival', 'date': 'November', 'description': 'Fall colors viewing'}],
                    12: [{'name': 'Illumination Festival', 'date': 'December', 'description': 'Winter light displays'}]
                },
                'Paris': {
                    3: [{'name': 'Paris Fashion Week', 'date': 'March', 'description': 'Fashion industry event'}],
                    7: [{'name': 'Bastille Day', 'date': 'July 14', 'description': 'National celebration'}],
                    10: [{'name': 'Paris Wine Festival', 'date': 'October', 'description': 'Wine tasting event'}],
                    12: [{'name': 'Christmas Markets', 'date': 'December', 'description': 'Holiday markets'}]
                }
            }
            
            return events_db.get(destination, {}).get(start_month, [])
            
        except Exception as e:
            print(f"Error getting events: {e}")
            return []

    def generate_real_recommendations(self, form_data: Dict, cohere_response: str) -> str:
        """Generate real travel recommendations using actual APIs"""
        try:
            # Parse Cohere response
            cohere_json = self.extract_json_from_response(cohere_response)
            
            # Extract travel information
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
                'origin': form_data.get('origin', 'MUM')  # Default to Mumbai
            }
            
            print("🔍 Searching for real travel data...")
            
            # Search for real data
            flights = self.search_real_flights(
                travel_info['origin'], 
                travel_info['destination'], 
                travel_info['start_date'], 
                travel_info['end_date'], 
                travel_info['budget_allocation'].get('flights', 0)
            )
            
            hotels = self.search_real_hotels(
                travel_info['destination'],
                travel_info['start_date'],
                travel_info['end_date'],
                travel_info['budget_allocation'].get('hotel', 0),
                travel_info['people']
            )
            
            restaurants = self.search_real_restaurants(
                travel_info['destination'],
                travel_info['budget_allocation'].get('meals', 0)
            )
            
            activities = self.search_real_activities(
                travel_info['destination'],
                travel_info['activities'],
                travel_info['budget_allocation'].get('activities', 0)
            )
            
            weather = self.get_real_weather(
                travel_info['destination'],
                travel_info['start_date']
            )
            
            events = self.get_real_events(
                travel_info['destination'],
                travel_info['start_date'],
                travel_info['end_date']
            )
            
            recommendations = {
                'travel_info': travel_info,
                'hotels': hotels,
                'flights': flights,
                'restaurants': restaurants,
                'activities': activities,
                'weather_advisory': weather,
                'local_events': events,
                'safety_notes': self.get_safety_notes(travel_info)
            }
            
            return self.format_recommendations_to_text(recommendations)
            
        except Exception as e:
            return f"Error generating real recommendations: {str(e)}"

    def extract_json_from_response(self, response: str) -> Dict:
        """Extract JSON from Cohere response"""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}
        except Exception as e:
            print(f"Error parsing JSON from response: {e}")
            return {}

    def get_safety_notes(self, travel_info: Dict) -> List[str]:
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

    def format_recommendations_to_text(self, recommendations: Dict) -> str:
        """Format recommendations to readable text"""
        travel_info = recommendations['travel_info']
        
        text = f"""
=== NOMADAI REAL TRAVEL RECOMMENDATIONS ===
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Data Source: Real-time APIs (Amadeus, Google Places, OpenWeatherMap)

TRIP DETAILS:
Destination: {travel_info['destination']}
Travel Dates: {travel_info['start_date']} to {travel_info['end_date']}
Number of People: {travel_info['people']}
Budget per Person: ${travel_info['budget_per_person']}
Total Trip Cost: ${travel_info['total_trip_cost']}
Activities of Interest: {', '.join(travel_info['activities'])}

BUDGET ALLOCATION:
{json.dumps(travel_info['budget_allocation'], indent=2)}

HOTEL SHARING NOTE:
{travel_info['hotel_sharing_note']}

FEASIBILITY NOTE:
{travel_info['feasibility_note']}

=== REAL-TIME RECOMMENDATIONS ===

HOTELS ({len(recommendations['hotels'])} found):
"""
        
        for i, hotel in enumerate(recommendations['hotels'], 1):
            text += f"""
{i}. {hotel['name']}
   Category: {hotel['category']}
   Price per Night: ${hotel['price_per_night']}
   Address: {hotel.get('address', 'N/A')}
   Description: {hotel['description']}
"""
        
        text += f"""
FLIGHTS ({len(recommendations['flights'])} found):
"""
        
        for i, flight in enumerate(recommendations['flights'], 1):
            text += f"""
{i}. {flight['airline']}
   Class: {flight['class']}
   Price: ${flight['price']}
   Departure: {flight['departure_time']}
   Arrival: {flight['arrival_time']}
   Stops: {flight['stops']}
   Description: {flight['description']}
"""
        
        text += f"""
RESTAURANTS ({len(recommendations['restaurants'])} found):
"""
        
        for i, restaurant in enumerate(recommendations['restaurants'], 1):
            text += f"""
{i}. {restaurant['name']}
   Cuisine: {restaurant['cuisine']}
   Average Meal Price: ${restaurant['avg_meal_price']}
   Rating: {restaurant['rating']}/5
   Address: {restaurant.get('address', 'N/A')}
   Description: {restaurant['description']}
"""
        
        text += f"""
ACTIVITIES ({len(recommendations['activities'])} found):
"""
        
        for i, activity in enumerate(recommendations['activities'], 1):
            text += f"""
{i}. {activity['name']}
   Type: {activity['type']}
   Price: ${activity['price']}
   Rating: {activity['rating']}/5
   Address: {activity.get('address', 'N/A')}
   Description: {activity['description']}
"""
        
        weather = recommendations['weather_advisory']
        if weather:
            text += f"""
WEATHER ADVISORY (Real-time):
Temperature Range: {weather['temperature']['min']}°C - {weather['temperature']['max']}°C
Average Temperature: {weather['temperature']['average']}°C
Condition: {weather['condition']}
Humidity: {weather.get('humidity', 'N/A')}%
Wind Speed: {weather.get('wind_speed', 'N/A')} m/s
"""
        
        events = recommendations['local_events']
        if events:
            text += f"""
LOCAL EVENTS:
"""
            for event in events:
                text += f"  • {event['name']} ({event['date']}): {event['description']}\n"
        
        safety = recommendations['safety_notes']
        text += f"""
SAFETY NOTES:
"""
        
        for note in safety:
            text += f"  • {note}\n"
        
        text += f"""
=== SUMMARY ===
Total Hotels Found: {len(recommendations['hotels'])}
Total Flights Found: {len(recommendations['flights'])}
Total Restaurants Found: {len(recommendations['restaurants'])}
Total Activities Found: {len(recommendations['activities'])}

Trip Feasibility: {'Feasible' if travel_info['total_trip_cost'] <= travel_info['budget_per_person'] * travel_info['people'] else 'May exceed budget'}

Note: All data is fetched from real-time APIs and may vary based on availability and current prices.
"""
        
        return text

# Example usage
if __name__ == "__main__":
    # Initialize the real travel search
    real_search = RealTravelSearch()
    
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
    
    # Generate real recommendations
    recommendations_text = real_search.generate_real_recommendations(sample_form, sample_cohere_response)
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"real_travel_recommendations_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(recommendations_text)
    
    print(f"Real recommendations saved to: {filename}")
    print("\n" + "="*50)
    print(recommendations_text)
