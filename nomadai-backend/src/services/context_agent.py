import json
import os
import requests
from typing import Dict, Any, List
from datetime import datetime, timedelta
from transformers import pipeline

class ContextAgent:
    """
    Context Agent that adds seasonal and weather context to travel recommendations
    using Hugging Face text models and OpenWeather API.
    """
    
    def __init__(self):
        self.weather_api_key = os.getenv("OPENWEATHER_API_KEY")
        self.text_generator = pipeline("text-generation", model="gpt2", max_length=100)
        
    def get_travel_context(self, destination: str, start_date: str, end_date: str, 
                          activities: List[str]) -> Dict[str, Any]:
        """
        Get comprehensive travel context including weather, seasonal information,
        and activity recommendations.
        
        Args:
            destination: Travel destination
            start_date: Trip start date
            end_date: Trip end date
            activities: Preferred activities
            
        Returns:
            Dictionary with travel context information
        """
        try:
            # Parse dates
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            # Get weather information
            weather_info = self._get_weather_forecast(destination, start_dt, end_dt)
            
            # Get seasonal context
            seasonal_context = self._get_seasonal_context(destination, start_dt, end_dt)
            
            # Get activity-specific recommendations
            activity_recommendations = self._get_activity_recommendations(
                destination, activities, weather_info, seasonal_context
            )
            
            # Generate contextual insights
            contextual_insights = self._generate_contextual_insights(
                destination, weather_info, seasonal_context, activities
            )
            
            return {
                "success": True,
                "weather": weather_info,
                "seasonal_context": seasonal_context,
                "activity_recommendations": activity_recommendations,
                "contextual_insights": contextual_insights,
                "packing_suggestions": self._get_packing_suggestions(weather_info),
                "best_times": self._get_best_times(activities, weather_info),
                "local_events": self._get_local_events(destination, start_dt, end_dt)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_context": self._get_fallback_context(destination, start_date, end_date)
            }
    
    def _get_weather_forecast(self, destination: str, start_date: datetime, 
                             end_date: datetime) -> Dict[str, Any]:
        """Get weather forecast for the destination."""
        if not self.weather_api_key:
            return self._get_mock_weather(destination, start_date, end_date)
        
        try:
            # Get coordinates for destination
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct"
            geo_params = {
                "q": destination,
                "limit": 1,
                "appid": self.weather_api_key
            }
            
            geo_response = requests.get(geo_url, params=geo_params)
            geo_data = geo_response.json()
            
            if not geo_data:
                return self._get_mock_weather(destination, start_date, end_date)
            
            lat = geo_data[0]["lat"]
            lon = geo_data[0]["lon"]
            
            # Get weather forecast
            weather_url = f"https://api.openweathermap.org/data/2.5/forecast"
            weather_params = {
                "lat": lat,
                "lon": lon,
                "appid": self.weather_api_key,
                "units": "metric"
            }
            
            weather_response = requests.get(weather_url, params=weather_params)
            weather_data = weather_response.json()
            
            # Process weather data
            daily_forecasts = []
            current_date = start_date
            
            while current_date <= end_date:
                day_forecast = self._extract_daily_forecast(weather_data, current_date)
                daily_forecasts.append(day_forecast)
                current_date += timedelta(days=1)
            
            return {
                "destination": destination,
                "forecast": daily_forecasts,
                "summary": self._generate_weather_summary(daily_forecasts),
                "recommendations": self._get_weather_recommendations(daily_forecasts)
            }
            
        except Exception as e:
            print(f"Weather API error: {e}")
            return self._get_mock_weather(destination, start_date, end_date)
    
    def _get_mock_weather(self, destination: str, start_date: datetime, 
                          end_date: datetime) -> Dict[str, Any]:
        """Provide mock weather data when API is unavailable."""
        current_date = start_date
        daily_forecasts = []
        
        while current_date <= end_date:
            # Generate mock weather based on destination and season
            if "paris" in destination.lower():
                temp = 15 + (current_date.month - 6) * 2  # Warmer in summer
                condition = "partly cloudy" if current_date.month in [3, 4, 9, 10] else "sunny"
            elif "tokyo" in destination.lower():
                temp = 20 + (current_date.month - 6) * 3  # Hotter in summer
                condition = "rainy" if current_date.month in [6, 7] else "sunny"
            elif "london" in destination.lower():
                temp = 12 + (current_date.month - 6) * 2  # Mild climate
                condition = "rainy" if current_date.month in [10, 11, 12] else "cloudy"
            else:
                temp = 18
                condition = "sunny"
            
            daily_forecasts.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "temperature": {
                    "min": temp - 5,
                    "max": temp + 5,
                    "average": temp
                },
                "condition": condition,
                "humidity": 65,
                "wind_speed": 10
            })
            
            current_date += timedelta(days=1)
        
        return {
            "destination": destination,
            "forecast": daily_forecasts,
            "summary": self._generate_weather_summary(daily_forecasts),
            "recommendations": self._get_weather_recommendations(daily_forecasts)
        }
    
    def _extract_daily_forecast(self, weather_data: Dict[str, Any], 
                               target_date: datetime) -> Dict[str, Any]:
        """Extract daily forecast from API response."""
        target_date_str = target_date.strftime("%Y-%m-%d")
        
        # Find forecasts for the target date
        day_forecasts = []
        for item in weather_data.get("list", []):
            item_date = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
            if item_date == target_date_str:
                day_forecasts.append(item)
        
        if day_forecasts:
            # Calculate daily averages
            temps = [f["main"]["temp"] for f in day_forecasts]
            humidities = [f["main"]["humidity"] for f in day_forecasts]
            wind_speeds = [f["wind"]["speed"] for f in day_forecasts]
            
            return {
                "date": target_date_str,
                "temperature": {
                    "min": min(temps),
                    "max": max(temps),
                    "average": sum(temps) / len(temps)
                },
                "condition": day_forecasts[0]["weather"][0]["main"].lower(),
                "humidity": sum(humidities) / len(humidities),
                "wind_speed": sum(wind_speeds) / len(wind_speeds)
            }
        
        # Fallback
        return {
            "date": target_date_str,
            "temperature": {"min": 15, "max": 25, "average": 20},
            "condition": "sunny",
            "humidity": 65,
            "wind_speed": 10
        }
    
    def _generate_weather_summary(self, forecasts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate weather summary from daily forecasts."""
        temps = [f["temperature"]["average"] for f in forecasts]
        conditions = [f["condition"] for f in forecasts]
        
        return {
            "average_temperature": sum(temps) / len(temps),
            "temperature_range": {
                "min": min(temps),
                "max": max(temps)
            },
            "most_common_condition": max(set(conditions), key=conditions.count),
            "rainy_days": sum(1 for c in conditions if "rain" in c),
            "sunny_days": sum(1 for c in conditions if "sunny" in c or "clear" in c)
        }
    
    def _get_weather_recommendations(self, forecasts: List[Dict[str, Any]]) -> List[str]:
        """Generate weather-based recommendations."""
        recommendations = []
        summary = self._generate_weather_summary(forecasts)
        
        if summary["rainy_days"] > len(forecasts) * 0.3:
            recommendations.append("Pack rain gear and waterproof shoes")
        
        if summary["average_temperature"] < 10:
            recommendations.append("Bring warm clothing and layers")
        elif summary["average_temperature"] > 25:
            recommendations.append("Pack light clothing and sun protection")
        
        if summary["wind_speed"] > 15:
            recommendations.append("Consider wind-resistant clothing")
        
        return recommendations
    
    def _get_seasonal_context(self, destination: str, start_date: datetime, 
                             end_date: datetime) -> Dict[str, Any]:
        """Get seasonal context for the destination."""
        month = start_date.month
        
        seasonal_info = {
            "season": self._get_season(month),
            "peak_season": self._is_peak_season(destination, month),
            "seasonal_activities": self._get_seasonal_activities(destination, month),
            "seasonal_tips": self._get_seasonal_tips(destination, month),
            "crowd_level": self._get_crowd_level(destination, month)
        }
        
        return seasonal_info
    
    def _get_season(self, month: int) -> str:
        """Get season based on month."""
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "autumn"
    
    def _is_peak_season(self, destination: str, month: int) -> bool:
        """Determine if it's peak season for the destination."""
        peak_seasons = {
            "paris": [5, 6, 7, 8, 9],  # Spring to early autumn
            "tokyo": [3, 4, 10, 11],   # Cherry blossom and autumn
            "london": [6, 7, 8],       # Summer
            "berlin": [5, 6, 7, 8, 9]  # Spring to early autumn
        }
        
        for city, peak_months in peak_seasons.items():
            if city in destination.lower():
                return month in peak_months
        
        return month in [6, 7, 8]  # Default to summer peak
    
    def _get_seasonal_activities(self, destination: str, month: int) -> List[str]:
        """Get seasonal activities for the destination."""
        activities = {
            "paris": {
                3: ["Cherry blossom viewing", "Spring fashion shows"],
                6: ["Summer festivals", "Outdoor dining"],
                9: ["Wine harvest", "Autumn fashion"],
                12: ["Christmas markets", "Winter sales"]
            },
            "tokyo": {
                3: ["Cherry blossom viewing", "Spring festivals"],
                6: ["Hydrangea viewing", "Rainy season activities"],
                10: ["Autumn foliage", "Food festivals"],
                12: ["Winter illuminations", "New Year preparations"]
            }
        }
        
        for city, seasonal_acts in activities.items():
            if city in destination.lower():
                return seasonal_acts.get(month, [])
        
        return []
    
    def _get_seasonal_tips(self, destination: str, month: int) -> List[str]:
        """Get seasonal travel tips."""
        tips = {
            "paris": {
                3: ["Book restaurants in advance for spring break"],
                6: ["Expect higher prices during summer peak"],
                9: ["Enjoy pleasant weather and fewer crowds"],
                12: ["Experience magical Christmas atmosphere"]
            }
        }
        
        for city, seasonal_tips in tips.items():
            if city in destination.lower():
                return seasonal_tips.get(month, [])
        
        return ["Check local events and festivals", "Book accommodations early"]
    
    def _get_crowd_level(self, destination: str, month: int) -> str:
        """Get expected crowd level."""
        if self._is_peak_season(destination, month):
            return "high"
        elif month in [11, 12, 1, 2]:  # Winter months
            return "low"
        else:
            return "moderate"
    
    def _get_activity_recommendations(self, destination: str, activities: List[str],
                                     weather_info: Dict[str, Any], 
                                     seasonal_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get activity-specific recommendations based on context."""
        recommendations = {}
        
        for activity in activities:
            activity_tips = []
            
            if "outdoor" in activity.lower() or "sightseeing" in activity.lower():
                if weather_info["summary"]["rainy_days"] > 0:
                    activity_tips.append("Check weather forecast and have indoor backup plans")
                if weather_info["summary"]["average_temperature"] < 10:
                    activity_tips.append("Dress warmly and consider shorter outdoor sessions")
            
            if "food" in activity.lower():
                if seasonal_context["season"] == "summer":
                    activity_tips.append("Try seasonal dishes and outdoor dining")
                elif seasonal_context["season"] == "winter":
                    activity_tips.append("Enjoy warm comfort foods and indoor dining")
            
            if "culture" in activity.lower():
                if seasonal_context["peak_season"]:
                    activity_tips.append("Book tickets in advance due to high demand")
                else:
                    activity_tips.append("Enjoy shorter lines and more intimate experiences")
            
            recommendations[activity] = activity_tips
        
        return recommendations
    
    def _generate_contextual_insights(self, destination: str, weather_info: Dict[str, Any],
                                     seasonal_context: Dict[str, Any], 
                                     activities: List[str]) -> List[str]:
        """Generate contextual insights using text generation."""
        insights = []
        
        # Create context prompt
        context_text = f"Travel to {destination} during {seasonal_context['season']} with activities: {', '.join(activities)}"
        
        try:
            # Generate insights using text generation
            generated_text = self.text_generator(context_text, max_length=50)[0]["generated_text"]
            insights.append(f"AI Insight: {generated_text}")
        except:
            # Fallback insights
            insights.append(f"Best time for {destination} activities is during {seasonal_context['season']}")
        
        # Add weather-based insights
        if weather_info["summary"]["rainy_days"] > 0:
            insights.append("Pack rain gear and plan indoor activities for rainy days")
        
        if seasonal_context["peak_season"]:
            insights.append("Expect higher prices and larger crowds during peak season")
        
        return insights
    
    def _get_packing_suggestions(self, weather_info: Dict[str, Any]) -> List[str]:
        """Get packing suggestions based on weather."""
        suggestions = []
        summary = weather_info["summary"]
        
        if summary["average_temperature"] < 15:
            suggestions.extend(["Warm jacket", "Sweaters", "Scarf and gloves"])
        elif summary["average_temperature"] > 25:
            suggestions.extend(["Light clothing", "Sunscreen", "Hat", "Sunglasses"])
        
        if summary["rainy_days"] > 0:
            suggestions.extend(["Umbrella", "Waterproof shoes", "Rain jacket"])
        
        suggestions.extend(["Comfortable walking shoes", "Camera", "Travel documents"])
        
        return suggestions
    
    def _get_best_times(self, activities: List[str], weather_info: Dict[str, Any]) -> Dict[str, str]:
        """Get best times for activities based on weather."""
        best_times = {}
        
        for activity in activities:
            if "outdoor" in activity.lower() or "sightseeing" in activity.lower():
                best_times[activity] = "Morning or late afternoon to avoid peak sun"
            elif "food" in activity.lower():
                best_times[activity] = "Lunch (12-2 PM) or dinner (7-9 PM)"
            elif "culture" in activity.lower():
                best_times[activity] = "Morning when venues are less crowded"
            else:
                best_times[activity] = "Flexible timing based on your schedule"
        
        return best_times
    
    def _get_local_events(self, destination: str, start_date: datetime, 
                         end_date: datetime) -> List[Dict[str, Any]]:
        """Get local events during the travel period."""
        # Mock local events - in a real implementation, this would call an events API
        events = {
            "paris": [
                {"name": "Paris Fashion Week", "date": "March", "type": "cultural"},
                {"name": "Bastille Day", "date": "July 14", "type": "national"},
                {"name": "Christmas Markets", "date": "December", "type": "seasonal"}
            ],
            "tokyo": [
                {"name": "Cherry Blossom Festival", "date": "March-April", "type": "seasonal"},
                {"name": "Gion Matsuri", "date": "July", "type": "cultural"},
                {"name": "Autumn Leaves Festival", "date": "November", "type": "seasonal"}
            ]
        }
        
        for city, city_events in events.items():
            if city in destination.lower():
                return city_events
        
        return []
    
    def _get_fallback_context(self, destination: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Provide fallback context when main analysis fails."""
        return {
            "weather": {"summary": {"average_temperature": 20, "rainy_days": 2}},
            "seasonal_context": {"season": "spring", "peak_season": False},
            "packing_suggestions": ["Comfortable clothing", "Walking shoes", "Camera"],
            "best_times": {"general": "Morning and evening for outdoor activities"}
        }
