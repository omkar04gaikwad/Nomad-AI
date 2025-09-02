import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
import cohere
import os

class SummaryAgent:
    """
    Summary Agent that generates natural language itineraries using LangChain
    and local LLM for creating day-wise travel plans.
    """
    
    def __init__(self):
        # Initialize with Cohere API
        try:
            self.co = cohere.Client(os.getenv("COHERE_API_KEY", "fwksPuItAUmlEh924jWDxOfKvynurjXXx15zHTPU"))
            self.use_cohere = True
        except:
            # Fallback to a simple template-based approach
            self.co = None
            self.use_cohere = False
        
        self.itinerary_template = self._create_itinerary_template()
    
    def generate_itinerary(self, form_data: Dict[str, Any], 
                          budget_analysis: Dict[str, Any],
                          search_results: Dict[str, Any],
                          context_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive day-wise itinerary.
        
        Args:
            form_data: User travel form data
            budget_analysis: Budget analysis from BudgetAgent
            search_results: Search results from SearchAgent
            context_info: Context information from ContextAgent
            
        Returns:
            Dictionary with generated itinerary
        """
        try:
            # Extract key information
            destination = form_data.get('destination', '')
            start_date = form_data.get('startDate', '')
            end_date = form_data.get('endDate', '')
            people = int(form_data.get('people', 1))
            activities = form_data.get('activities', [])
            
            # Calculate trip duration
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            duration = (end_dt - start_dt).days + 1
            
            # Generate day-wise itinerary
            daily_itineraries = self._generate_daily_itineraries(
                destination, start_dt, duration, activities, 
                search_results, context_info
            )
            
            # Calculate total estimated costs
            total_costs = self._calculate_total_costs(
                search_results, daily_itineraries, people
            )
            
            # Generate summary and recommendations
            summary = self._generate_trip_summary(
                destination, duration, total_costs, budget_analysis, context_info
            )
            
            return {
                "success": True,
                "itinerary": {
                    "destination": destination,
                    "start_date": start_date,
                    "end_date": end_date,
                    "duration_days": duration,
                    "total_people": people,
                    "daily_plans": daily_itineraries,
                    "total_estimated_cost": total_costs,
                    "budget_utilization": self._calculate_budget_utilization(
                        total_costs, budget_analysis
                    )
                },
                "summary": summary,
                "recommendations": self._generate_recommendations(
                    budget_analysis, context_info, search_results
                ),
                "disclaimer": self._get_disclaimer(),
                "export_info": {
                    "pdf_available": True,
                    "export_format": "PDF",
                    "generated_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_itinerary": self._generate_fallback_itinerary(form_data)
            }
    
    def _generate_daily_itineraries(self, destination: str, start_date: datetime,
                                   duration: int, activities: List[str],
                                   search_results: Dict[str, Any],
                                   context_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate day-wise itineraries."""
        daily_plans = []
        
        for day in range(duration):
            current_date = start_date + timedelta(days=day)
            day_number = day + 1
            
            # Generate day title
            day_title = self._generate_day_title(destination, day_number, current_date)
            
            # Select activities for the day
            day_activities = self._select_day_activities(
                activities, search_results, day_number, context_info
            )
            
            # Generate day description
            day_description = self._generate_day_description(
                destination, day_activities, context_info
            )
            
            # Calculate day costs
            day_costs = self._calculate_day_costs(day_activities)
            
            # Create day plan
            day_plan = {
                "day": day_number,
                "date": current_date.strftime("%Y-%m-%d"),
                "title": day_title,
                "description": day_description,
                "activities": day_activities,
                "estimated_cost": day_costs,
                "weather_info": self._get_day_weather(context_info, current_date),
                "best_times": self._get_day_best_times(day_activities, context_info),
                "transportation": self._get_day_transportation(destination, day_activities),
                "meals": self._get_day_meals(day_activities)
            }
            
            daily_plans.append(day_plan)
        
        return daily_plans
    
    def _generate_day_title(self, destination: str, day_number: int, 
                           date: datetime) -> str:
        """Generate a descriptive title for each day."""
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", 
                     "Friday", "Saturday", "Sunday"]
        day_name = day_names[date.weekday()]
        
        if day_number == 1:
            return f"Day {day_number} – Arrival and Welcome to {destination}"
        elif day_number == 2:
            return f"Day {day_number} – Exploring {destination} ({day_name})"
        else:
            return f"Day {day_number} – {day_name} Adventures in {destination}"
    
    def _select_day_activities(self, activities: List[str], 
                              search_results: Dict[str, Any], day_number: int,
                              context_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Select appropriate activities for each day."""
        available_activities = search_results.get('activities', [])
        
        # Distribute activities across days
        activities_per_day = max(2, len(available_activities) // 3)  # 2-3 activities per day
        
        start_idx = (day_number - 1) * activities_per_day
        end_idx = start_idx + activities_per_day
        
        day_activities = available_activities[start_idx:end_idx]
        
        # Add free activities if needed
        if len(day_activities) < 2:
            day_activities.extend(self._get_free_activities(context_info))
        
        return day_activities[:3]  # Limit to 3 activities per day
    
    def _get_free_activities(self, context_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get free activities from context."""
        free_activities = [
            {
                "name": "City Walking Tour",
                "cost_estimate": 0,
                "duration": "2-3 hours",
                "description": "Self-guided walking tour to explore the city",
                "tags": ["sightseeing", "culture", "free"]
            },
            {
                "name": "Local Market Visit",
                "cost_estimate": 0,
                "duration": "1-2 hours",
                "description": "Visit local markets to experience local culture",
                "tags": ["culture", "food", "free"]
            },
            {
                "name": "Park Relaxation",
                "cost_estimate": 0,
                "duration": "1 hour",
                "description": "Relax in local parks and gardens",
                "tags": ["relaxation", "nature", "free"]
            }
        ]
        
        return free_activities
    
    def _generate_day_description(self, destination: str, activities: List[Dict[str, Any]],
                                 context_info: Dict[str, Any]) -> str:
        """Generate a natural language description for the day."""
        if self.use_cohere and self.co:
            # Use Cohere for generation
            activities_text = "\n".join([
                f"- {activity.get('name', '')}: {activity.get('description', '')}"
                for activity in activities
            ])
            
            context_text = f"Weather: {context_info.get('weather', {}).get('summary', {}).get('average_temperature', 20)}°C"
            
            prompt = f"""
            You are an expert travel planner creating a day itinerary. Write a natural, engaging description for this day's activities.

            Destination: {destination}
            Activities for the day:
            {activities_text}
            
            Context: {context_text}

            Write a 2-3 sentence description that flows naturally and makes the day sound exciting and well-planned. 
            Focus on the experience and what makes each activity special.
            """
            
            try:
                response = self.co.generate(
                    model='command',
                    prompt=prompt,
                    max_tokens=150,
                    temperature=0.7,
                    k=0,
                    stop_sequences=[],
                    return_likelihoods='NONE'
                )
                
                return response.generations[0].text.strip()
            except:
                # Fallback to template-based description
                activity_names = [activity.get('name', '') for activity in activities]
                return f"Experience the best of {destination} with {', '.join(activity_names)}. " \
                       f"Enjoy a perfect blend of sightseeing, culture, and local experiences."
        else:
            # Fallback template-based description
            activity_names = [activity.get('name', '') for activity in activities]
            return f"Experience the best of {destination} with {', '.join(activity_names)}. " \
                   f"Enjoy a perfect blend of sightseeing, culture, and local experiences."
    
    def _calculate_day_costs(self, activities: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate costs for the day's activities."""
        total_cost = sum(activity.get('cost_estimate', 0) for activity in activities)
        
        return {
            "activities": total_cost,
            "estimated_meals": 50,  # Average meal cost
            "transportation": 15,   # Average transportation cost
            "total": total_cost + 50 + 15
        }
    
    def _get_day_weather(self, context_info: Dict[str, Any], date: datetime) -> Dict[str, Any]:
        """Get weather information for the specific day."""
        weather_forecast = context_info.get('weather', {}).get('forecast', [])
        
        for forecast in weather_forecast:
            if forecast.get('date') == date.strftime("%Y-%m-%d"):
                return forecast
        
        # Fallback weather
        return {
            "temperature": {"average": 20},
            "condition": "sunny",
            "humidity": 65
        }
    
    def _get_day_best_times(self, activities: List[Dict[str, Any]], 
                           context_info: Dict[str, Any]) -> Dict[str, str]:
        """Get best times for activities on this day."""
        best_times = context_info.get('best_times', {})
        
        return {
            activity.get('name', ''): best_times.get(activity.get('name', ''), 'Flexible timing')
            for activity in activities
        }
    
    def _get_day_transportation(self, destination: str, activities: List[Dict[str, Any]]) -> List[str]:
        """Get transportation recommendations for the day."""
        return [
            "Use public transportation for cost-effective travel",
            "Consider walking between nearby attractions",
            "Book transportation in advance for longer distances"
        ]
    
    def _get_day_meals(self, activities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get meal recommendations for the day."""
        return [
            {
                "meal": "Breakfast",
                "suggestion": "Hotel breakfast or local café",
                "estimated_cost": 15
            },
            {
                "meal": "Lunch",
                "suggestion": "Local restaurant near activities",
                "estimated_cost": 25
            },
            {
                "meal": "Dinner",
                "suggestion": "Fine dining or casual local spot",
                "estimated_cost": 35
            }
        ]
    
    def _calculate_total_costs(self, search_results: Dict[str, Any],
                              daily_itineraries: List[Dict[str, Any]],
                              people: int) -> Dict[str, float]:
        """Calculate total estimated costs for the trip."""
        # Flight costs
        flights = search_results.get('flights', [])
        flight_cost = flights[0].get('price_estimate', 0) * people if flights else 0
        
        # Hotel costs
        hotels = search_results.get('hotels', [])
        hotel_cost = hotels[0].get('price_estimate', 0) * people if hotels else 0
        
        # Activity costs
        activity_cost = sum(
            day.get('estimated_cost', {}).get('activities', 0)
            for day in daily_itineraries
        )
        
        # Daily expenses
        daily_expenses = sum(
            day.get('estimated_cost', {}).get('total', 0) - day.get('estimated_cost', {}).get('activities', 0)
            for day in daily_itineraries
        )
        
        total_cost = flight_cost + hotel_cost + activity_cost + daily_expenses
        
        return {
            "flights": flight_cost,
            "accommodation": hotel_cost,
            "activities": activity_cost,
            "daily_expenses": daily_expenses,
            "total": total_cost
        }
    
    def _calculate_budget_utilization(self, total_costs: Dict[str, float],
                                    budget_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate budget utilization percentage."""
        total_budget = budget_analysis.get('total_budget', 0)
        total_cost = total_costs.get('total', 0)
        
        if total_budget > 0:
            utilization_percentage = (total_cost / total_budget) * 100
        else:
            utilization_percentage = 0
        
        return {
            "total_budget": total_budget,
            "total_cost": total_cost,
            "utilization_percentage": round(utilization_percentage, 2),
            "remaining_budget": max(0, total_budget - total_cost),
            "status": "within_budget" if utilization_percentage <= 100 else "over_budget"
        }
    
    def _generate_trip_summary(self, destination: str, duration: int,
                              total_costs: Dict[str, float],
                              budget_analysis: Dict[str, Any],
                              context_info: Dict[str, Any]) -> str:
        """Generate a comprehensive trip summary."""
        total_cost = total_costs.get('total', 0)
        budget_utilization = self._calculate_budget_utilization(total_costs, budget_analysis)
        
        summary = f"Your {duration}-day adventure to {destination} is perfectly planned! "
        summary += f"The total estimated cost is ${total_cost:,.2f}, "
        
        if budget_utilization['status'] == 'within_budget':
            summary += f"which is {budget_utilization['utilization_percentage']}% of your budget. "
            summary += f"You'll have ${budget_utilization['remaining_budget']:,.2f} remaining for unexpected expenses."
        else:
            summary += f"which exceeds your budget by ${abs(budget_utilization['remaining_budget']):,.2f}. "
            summary += "Consider adjusting your plans or increasing your budget."
        
        return summary
    
    def _generate_recommendations(self, budget_analysis: Dict[str, Any],
                                 context_info: Dict[str, Any],
                                 search_results: Dict[str, Any]) -> List[str]:
        """Generate personalized recommendations."""
        recommendations = []
        
        # Budget recommendations
        budget_recs = budget_analysis.get('recommendations', [])
        recommendations.extend(budget_recs[:2])
        
        # Weather recommendations
        weather_recs = context_info.get('weather', {}).get('recommendations', [])
        recommendations.extend(weather_recs[:2])
        
        # General recommendations
        recommendations.extend([
            "Book flights and hotels 2-3 months in advance for better prices",
            "Download offline maps and translation apps",
            "Keep copies of important documents",
            "Research local customs and etiquette"
        ])
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _get_disclaimer(self) -> str:
        """Get the planning disclaimer."""
        return ("NomadAI is a travel planner, not a booking system. All prices and availability "
                "are estimates based on current market conditions. Actual costs may vary. "
                "Please verify all information and book directly with service providers.")
    
    def _create_itinerary_template(self) -> str:
        """Create the prompt template for itinerary generation."""
        return """
        You are an expert travel planner creating a day itinerary. Write a natural, engaging description for this day's activities.

        Destination: {destination}
        Activities for the day:
        {activities}
        
        Context: {context}

        Write a 2-3 sentence description that flows naturally and makes the day sound exciting and well-planned. 
        Focus on the experience and what makes each activity special.
        """
    
    def _generate_fallback_itinerary(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a fallback itinerary when main generation fails."""
        destination = form_data.get('destination', 'Unknown')
        start_date = form_data.get('startDate', '')
        end_date = form_data.get('endDate', '')
        
        return {
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "duration_days": 3,
            "daily_plans": [
                {
                    "day": 1,
                    "title": f"Day 1 – Arrival in {destination}",
                    "description": f"Welcome to {destination}! Start your journey with a relaxing arrival day.",
                    "activities": [],
                    "estimated_cost": {"total": 100}
                }
            ],
            "total_estimated_cost": {"total": 1000},
            "summary": f"Your trip to {destination} is planned with estimated costs.",
            "disclaimer": self._get_disclaimer()
        }
