from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime
import json
import os

# Import the new AI agents
from src.services.budget_agent import BudgetAgent
from src.services.search_agent import SearchAgent
from src.services.context_agent import ContextAgent
from src.services.summary_agent import SummaryAgent
from src.utils.rate_limiter import RateLimiter

# Simple Pydantic model for form data
class TravelFormData(BaseModel):
    origin: str
    destination: str
    startDate: str
    endDate: str
    strictDates: str
    budget: str
    people: str
    travelMode: str
    activities: List[str]
    visitedBefore: str
    hotelPreference: str

# Initialize FastAPI app
app = FastAPI(
    title="NomadAI Travel Planning API",
    description="AI-powered travel planning companion that creates personalized itineraries",
    version="2.0.0"
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI agents
budget_agent = BudgetAgent()
search_agent = SearchAgent()
context_agent = ContextAgent()
summary_agent = SummaryAgent()

# Initialize rate limiter (5 requests per day)
rate_limiter = RateLimiter(limit=5)

@app.get("/")
async def root():
    return {"message": "NomadAI Travel Planning API is running!"}

@app.post("/api/travel-plan")
async def create_travel_plan(form_data: TravelFormData, request: Request):
    """
    Create a comprehensive travel plan using AI agents
    """
    try:
        # Get client IP for rate limiting
        client_ip = request.client.host
        
        # Check rate limit
        rate_limit_check = rate_limiter.check_limit(client_ip)
        if not rate_limit_check["allowed"]:
            raise HTTPException(
                status_code=429, 
                detail={
                    "error": "Rate limit exceeded",
                    "message": rate_limit_check["message"],
                    "limit_info": {
                        "current_count": rate_limit_check["current_count"],
                        "limit": rate_limit_check["limit"],
                        "remaining": rate_limit_check["remaining"],
                        "reset_date": rate_limit_check["reset_date"]
                    }
                }
            )
        # Convert form data to dictionary
        form_entry = {
            "origin": form_data.origin,
            "destination": form_data.destination,
            "startDate": form_data.startDate,
            "endDate": form_data.endDate,
            "strictDates": form_data.strictDates,
            "budget": form_data.budget,
            "people": form_data.people,
            "travelMode": form_data.travelMode,
            "activities": form_data.activities,
            "visitedBefore": form_data.visitedBefore,
            "hotelPreference": form_data.hotelPreference,
            "timestamp": datetime.now().isoformat()
        }
        
        # Step 1: Budget Analysis
        print("🔍 Analyzing budget...")
        budget_analysis = budget_agent.analyze_budget(form_entry)
        
        # Step 2: Search for Recommendations
        print("🔍 Searching for recommendations...")
        search_results = search_agent.search_recommendations(form_entry, budget_analysis)
        
        # Step 3: Get Travel Context
        print("🌤️ Getting travel context...")
        context_info = context_agent.get_travel_context(
            form_entry["destination"],
            form_entry["startDate"],
            form_entry["endDate"],
            form_entry["activities"]
        )
        
        # Step 4: Generate Itinerary
        print("📋 Generating itinerary...")
        itinerary_result = summary_agent.generate_itinerary(
            form_entry,
            budget_analysis,
            search_results,
            context_info
        )
        
        # Increment rate limit counter
        rate_limiter.increment_request(client_ip)
        
        # Save form data to JSON file
        json_file_path = "data/travel_forms.json"
        
        # Load existing data or create new list
        try:
            with open(json_file_path, 'r') as file:
                existing_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = []
        
        # Add new entry
        existing_data.append(form_entry)
        
        # Save to JSON file
        with open(json_file_path, 'w') as file:
            json.dump(existing_data, file, indent=2)
        
        # Return comprehensive travel plan
        return {
            "success": True,
            "message": "Travel plan created successfully!",
            "timestamp": form_entry['timestamp'],
            "travel_plan": {
                "budget_analysis": budget_analysis,
                "search_results": search_results,
                "context_info": context_info,
                "itinerary": itinerary_result
            },
            "disclaimer": "NomadAI is a travel planner, not a booking system. All prices and availability are estimates.",
            "total_entries": len(existing_data)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create travel plan. Please try again."
        }

@app.get("/api/travel-forms")
async def get_all_forms():
    """
    Get all stored travel form data
    """
    json_file_path = "data/travel_forms.json"
    
    try:
        with open(json_file_path, 'r') as file:
            forms_data = json.load(file)
        return {
            "success": True,
            "total_entries": len(forms_data),
            "data": forms_data
        }
    except FileNotFoundError:
        return {
            "success": True,
            "total_entries": 0,
            "data": [],
            "message": "No forms submitted yet"
        }

@app.get("/api/search")
async def search_recommendations(query: str, category: str = "all"):
    """
    Search for recommendations using semantic search
    """
    try:
        results = search_agent.get_semantic_search_results(query, category)
        return {
            "success": True,
            "query": query,
            "category": category,
            "results": results,
            "total_results": len(results)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Search failed. Please try again."
        }

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "services": {
            "budget_agent": "available",
            "search_agent": "available",
            "context_agent": "available",
            "summary_agent": "available"
        }
    }

@app.get("/api/rate-limit-status")
async def get_rate_limit_status(request: Request):
    """
    Get current rate limit status for the client
    """
    client_ip = request.client.host
    stats = rate_limiter.get_user_stats(client_ip)
    
    return {
        "user_id": stats["user_id"],
        "current_count": stats["current_count"],
        "limit": stats["limit"],
        "remaining": stats["remaining"],
        "reset_date": stats["reset_date"],
        "percentage_used": stats["percentage_used"],
        "message": f"You have {stats['remaining']} requests remaining today."
    }

