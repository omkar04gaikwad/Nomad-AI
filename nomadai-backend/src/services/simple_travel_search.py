import json
from datetime import datetime
from typing import List, Dict, Any

def generate_travel_recommendations(form_data: Dict, cohere_response: str) -> str:
    """
    Generate travel recommendations based on form data and Cohere response
    """
    try:
        # Parse Cohere response to get budget allocation
        cohere_json = extract_json_from_response(cohere_response)
        
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
            'season': get_season(form_data['startDate'])
        }
        
        # Generate recommendations
        recommendations = {
            'travel_info': travel_info,
            'hotels': get_hotel_recommendations(travel_info),
            'flights': get_flight_recommendations(travel_info),
            'restaurants': get_restaurant_recommendations(travel_info),
            'activities': get_activity_recommendations(travel_info),
            'weather_advisory': get_weather_advisory(travel_info),
            'local_events': get_local_events(travel_info),
            'safety_notes': get_safety_notes(travel_info)
        }
        
        return format_recommendations_to_text(recommendations)
        
    except Exception as e:
        return f"Error generating recommendations: {str(e)}"

def extract_json_from_response(response: str) -> Dict:
    """Extract JSON from Cohere response"""
    try:
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {}
    except Exception as e:
        print(f"Error parsing JSON from response: {e}")
        return {}

def get_season(date_str: str) -> str:
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

def get_hotel_recommendations(travel_info: Dict) -> List[Dict]:
    """Get hotel recommendations based on travel info"""
    destination = travel_info['destination']
    hotel_preference = travel_info['hotel_preference']
    season = travel_info['season']
    budget = travel_info['budget_allocation'].get('hotel', 0)
    people = travel_info['people']
    
    hotels_db = {
        'Tokyo': [
            {'name': 'Park Hyatt Tokyo', 'category': 'luxury', 'price_per_night': 300, 'description': 'Luxury hotel in Shinjuku with skyline views'},
            {'name': 'Hotel Gracery Shinjuku', 'category': 'mid-range', 'price_per_night': 150, 'description': 'Mid-range hotel near Godzilla statue'},
            {'name': 'Capsule Hotel Anshin Oyado', 'category': 'budget', 'price_per_night': 80, 'description': 'Budget capsule hotel experience'},
            {'name': 'Aman Tokyo', 'category': 'luxury', 'price_per_night': 500, 'description': 'Ultra luxury hotel in Otemachi'},
            {'name': 'Tokyu Stay Ginza', 'category': 'mid-range', 'price_per_night': 120, 'description': 'Mid-range hotel in shopping district'}
        ],
        'Paris': [
            {'name': 'Ritz Paris', 'category': 'luxury', 'price_per_night': 400, 'description': 'Historic luxury hotel in Place Vendome'},
            {'name': 'Hotel du Louvre', 'category': 'mid-range', 'price_per_night': 180, 'description': 'Mid-range hotel near Louvre Museum'},
            {'name': 'Hotel des Arts', 'category': 'budget', 'price_per_night': 90, 'description': 'Budget hotel in Montmartre'},
            {'name': 'Four Seasons George V', 'category': 'luxury', 'price_per_night': 600, 'description': 'Ultra luxury hotel on Champs-Elysees'},
            {'name': 'Hotel de la Paix', 'category': 'mid-range', 'price_per_night': 160, 'description': 'Mid-range hotel in Latin Quarter'}
        ]
    }
    
    available_hotels = hotels_db.get(destination, [])
    
    # Filter by preference and budget
    filtered_hotels = []
    for hotel in available_hotels:
        if hotel_preference in hotel['category'] or hotel_preference == 'any':
            # Adjust price for room sharing
            adjusted_price = hotel['price_per_night']
            if people > 1:
                adjusted_price = adjusted_price * 1.5
            
            if adjusted_price <= budget:
                hotel['adjusted_price'] = adjusted_price
                hotel['room_sharing'] = people > 1
                filtered_hotels.append(hotel)
    
    return sorted(filtered_hotels, key=lambda x: x['adjusted_price'])[:5]

def get_flight_recommendations(travel_info: Dict) -> List[Dict]:
    """Get flight recommendations based on travel info"""
    destination = travel_info['destination']
    travel_mode = travel_info['travel_mode']
    budget = travel_info['budget_allocation'].get('flights', 0)
    
    flights_db = {
        'Tokyo': [
            {'airline': 'Japan Airlines', 'price': 1200, 'class': 'premium economy', 'description': 'Direct flight with premium service'},
            {'airline': 'ANA', 'price': 1100, 'class': 'business', 'description': 'Direct flight with business class comfort'},
            {'airline': 'United Airlines', 'price': 800, 'class': 'economy', 'description': 'Connecting flight with good value'},
            {'airline': 'Singapore Airlines', 'price': 1300, 'class': 'premium economy', 'description': 'Connecting flight with excellent service'},
            {'airline': 'Qatar Airways', 'price': 1400, 'class': 'business', 'description': 'Connecting flight with luxury amenities'}
        ],
        'Paris': [
            {'airline': 'Air France', 'price': 1000, 'class': 'premium economy', 'description': 'Direct flight with French hospitality'},
            {'airline': 'Lufthansa', 'price': 950, 'class': 'business', 'description': 'Connecting flight with German efficiency'},
            {'airline': 'British Airways', 'price': 900, 'class': 'economy', 'description': 'Connecting flight with British service'},
            {'airline': 'Emirates', 'price': 1500, 'class': 'first class', 'description': 'Connecting flight with ultimate luxury'},
            {'airline': 'Delta Airlines', 'price': 850, 'class': 'economy', 'description': 'Direct flight with American comfort'}
        ]
    }
    
    available_flights = flights_db.get(destination, [])
    
    # Filter by budget
    filtered_flights = []
    for flight in available_flights:
        if flight['price'] <= budget:
            filtered_flights.append(flight)
    
    return sorted(filtered_flights, key=lambda x: x['price'])[:5]

def get_restaurant_recommendations(travel_info: Dict) -> List[Dict]:
    """Get restaurant recommendations based on travel info"""
    destination = travel_info['destination']
    season = travel_info['season']
    budget = travel_info['budget_allocation'].get('meals', 0)
    
    restaurants_db = {
        'Tokyo': [
            {'name': 'Sukiyabashi Jiro', 'cuisine': 'sushi', 'avg_meal_price': 100, 'description': 'Famous sushi restaurant in Ginza'},
            {'name': 'Narisawa', 'cuisine': 'fine_dining', 'avg_meal_price': 150, 'description': 'Fine dining with French-Japanese fusion'},
            {'name': 'Ichiran Ramen', 'cuisine': 'ramen', 'avg_meal_price': 15, 'description': 'Popular ramen chain in Shinjuku'},
            {'name': 'Tsukiji Outer Market', 'cuisine': 'seafood', 'avg_meal_price': 60, 'description': 'Fresh seafood market with restaurants'},
            {'name': 'Gonpachi', 'cuisine': 'izakaya', 'avg_meal_price': 40, 'description': 'Traditional izakaya in Roppongi'}
        ],
        'Paris': [
            {'name': 'Le Comptoir du Relais', 'cuisine': 'french', 'avg_meal_price': 80, 'description': 'Classic French bistro in Saint Germain'},
            {'name': 'L\'Astrance', 'cuisine': 'fine_dining', 'avg_meal_price': 200, 'description': 'Michelin-starred fine dining'},
            {'name': 'Le Chateaubriand', 'cuisine': 'french', 'avg_meal_price': 120, 'description': 'Modern French cuisine'},
            {'name': 'Breizh Cafe', 'cuisine': 'crepes', 'avg_meal_price': 20, 'description': 'Authentic Breton crepes'},
            {'name': 'L\'As du Fallafel', 'cuisine': 'middle_eastern', 'avg_meal_price': 25, 'description': 'Famous falafel in Marais'}
        ]
    }
    
    available_restaurants = restaurants_db.get(destination, [])
    
    # Filter by budget
    filtered_restaurants = []
    for restaurant in available_restaurants:
        if restaurant['avg_meal_price'] <= budget / 3:  # Assume 3 meals per day
            filtered_restaurants.append(restaurant)
    
    return sorted(filtered_restaurants, key=lambda x: x['avg_meal_price'])[:5]

def get_activity_recommendations(travel_info: Dict) -> List[Dict]:
    """Get activity recommendations based on travel info"""
    destination = travel_info['destination']
    activities = travel_info['activities']
    season = travel_info['season']
    budget = travel_info['budget_allocation'].get('activities', 0)
    
    activities_db = {
        'Tokyo': [
            {'name': 'Senso-ji Temple', 'type': 'culture', 'price': 25, 'description': 'Traditional temple in Asakusa'},
            {'name': 'Shibuya Crossing', 'type': 'sightseeing', 'price': 0, 'description': 'Famous pedestrian crossing'},
            {'name': 'Tsukiji Fish Market', 'type': 'food', 'price': 50, 'description': 'Famous fish market with food tours'},
            {'name': 'Tokyo Skytree', 'type': 'sightseeing', 'price': 30, 'description': 'Observation tower with city views'},
            {'name': 'Meiji Shrine', 'type': 'culture', 'price': 0, 'description': 'Peaceful shrine in Harajuku'}
        ],
        'Paris': [
            {'name': 'Eiffel Tower', 'type': 'sightseeing', 'price': 30, 'description': 'Iconic tower with city views'},
            {'name': 'Louvre Museum', 'type': 'culture', 'price': 20, 'description': 'World-famous art museum'},
            {'name': 'Notre-Dame Cathedral', 'type': 'culture', 'price': 0, 'description': 'Historic Gothic cathedral'},
            {'name': 'Champs-Elysees', 'type': 'sightseeing', 'price': 0, 'description': 'Famous shopping avenue'},
            {'name': 'Montmartre', 'type': 'culture', 'price': 0, 'description': 'Artistic neighborhood with Sacre-Coeur'}
        ]
    }
    
    available_activities = activities_db.get(destination, [])
    
    # Filter by interests and budget
    filtered_activities = []
    for activity in available_activities:
        if (any(act in activity['type'] for act in activities) or 
            any(act in activity['description'].lower() for act in activities)):
            if activity['price'] <= budget:
                filtered_activities.append(activity)
    
    return sorted(filtered_activities, key=lambda x: x['price'])[:5]

def get_weather_advisory(travel_info: Dict) -> Dict:
    """Get weather advisory based on travel info"""
    season = travel_info['season']
    
    advisories = {
        'winter': ['Pack warm clothing', 'Check for snow closures', 'Indoor activities recommended'],
        'spring': ['Light jacket recommended', 'Umbrella for rain', 'Cherry blossom viewing'],
        'summer': ['Light clothing', 'Sunscreen essential', 'Outdoor activities ideal'],
        'autumn': ['Layered clothing', 'Beautiful fall colors', 'Moderate outdoor activities']
    }
    
    temperatures = {
        'winter': {'min': 0, 'max': 10, 'average': 5},
        'spring': {'min': 10, 'max': 20, 'average': 15},
        'summer': {'min': 20, 'max': 30, 'average': 25},
        'autumn': {'min': 10, 'max': 20, 'average': 15}
    }
    
    return {
        'season': season,
        'temperature': temperatures.get(season, {'min': 15, 'max': 25, 'average': 20}),
        'recommendations': advisories.get(season, ['Check local weather forecast'])
    }

def get_local_events(travel_info: Dict) -> List[Dict]:
    """Get local events during travel period"""
    destination = travel_info['destination']
    season = travel_info['season']
    
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

def get_safety_notes(travel_info: Dict) -> List[str]:
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

def format_recommendations_to_text(recommendations: Dict) -> str:
    """Format recommendations to readable text"""
    travel_info = recommendations['travel_info']
    
    text = f"""
=== NOMADAI TRAVEL RECOMMENDATIONS ===
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

TRIP DETAILS:
Destination: {travel_info['destination']}
Travel Dates: {travel_info['start_date']} to {travel_info['end_date']}
Number of People: {travel_info['people']}
Budget per Person: ${travel_info['budget_per_person']}
Total Trip Cost: ${travel_info['total_trip_cost']}
Season: {travel_info['season']}
Activities of Interest: {', '.join(travel_info['activities'])}

BUDGET ALLOCATION:
{json.dumps(travel_info['budget_allocation'], indent=2)}

HOTEL SHARING NOTE:
{travel_info['hotel_sharing_note']}

FEASIBILITY NOTE:
{travel_info['feasibility_note']}

=== RECOMMENDATIONS ===

HOTELS ({len(recommendations['hotels'])} found):
"""
    
    for i, hotel in enumerate(recommendations['hotels'], 1):
        text += f"""
{i}. {hotel['name']}
   Category: {hotel['category']}
   Price per Night: ${hotel['adjusted_price']}
   Room Sharing: {'Yes' if hotel.get('room_sharing', False) else 'No'}
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
   Description: {activity['description']}
"""
    
    weather = recommendations['weather_advisory']
    text += f"""
WEATHER ADVISORY:
Season: {weather['season']}
Temperature Range: {weather['temperature']['min']}°C - {weather['temperature']['max']}°C
Average Temperature: {weather['temperature']['average']}°C
Recommendations:
"""
    
    for rec in weather['recommendations']:
        text += f"  • {rec}\n"
    
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
"""
    
    return text

# Example usage
if __name__ == "__main__":
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
    
    # Generate recommendations
    recommendations_text = generate_travel_recommendations(sample_form, sample_cohere_response)
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"travel_recommendations_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(recommendations_text)
    
    print(f"Recommendations saved to: {filename}")
    print("\n" + "="*50)
    print(recommendations_text)

