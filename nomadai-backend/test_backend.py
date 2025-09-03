#!/usr/bin/env python3
"""
Simple test script for NomadAI backend
"""

import requests
import json
import time

def test_backend():
    """Test the backend API endpoints."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing NomadAI Backend...")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed!")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed with status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 2: Rate Limit Status
    print("\n2. Testing Rate Limit Status...")
    try:
        response = requests.get(f"{base_url}/api/rate-limit-status", timeout=10)
        if response.status_code == 200:
            print("✅ Rate limit status check passed!")
            data = response.json()
            print(f"   Current count: {data['current_count']}")
            print(f"   Limit: {data['limit']}")
            print(f"   Remaining: {data['remaining']}")
        else:
            print(f"❌ Rate limit status failed with status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Rate limit status failed: {e}")
    
    # Test 3: Travel Plan Creation
    print("\n3. Testing Travel Plan Creation...")
    test_data = {
        "origin": "New York",
        "destination": "Paris",
        "startDate": "2024-06-01",
        "endDate": "2024-06-07",
        "strictDates": "yes",
        "budget": "5000",
        "people": "2",
        "travelMode": "plane",
        "activities": ["sightseeing", "food", "culture"],
        "visitedBefore": "no",
        "hotelPreference": "luxury"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/travel-plan",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Travel plan creation passed!")
            result = response.json()
            print(f"   Success: {result.get('success', False)}")
            print(f"   Message: {result.get('message', 'No message')}")
            
            if result.get('travel_plan'):
                travel_plan = result['travel_plan']
                print(f"   Budget Analysis: {'✅' if travel_plan.get('budget_analysis') else '❌'}")
                print(f"   Search Results: {'✅' if travel_plan.get('search_results') else '❌'}")
                print(f"   Context Info: {'✅' if travel_plan.get('context_info') else '❌'}")
                print(f"   Itinerary: {'✅' if travel_plan.get('itinerary') else '❌'}")
        elif response.status_code == 429:
            print("⚠️ Rate limit exceeded (expected for testing)")
            error_data = response.json()
            print(f"   Message: {error_data.get('detail', {}).get('message', 'Rate limit exceeded')}")
        else:
            print(f"❌ Travel plan creation failed with status {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Travel plan creation failed: {e}")
    
    # Test 4: Search Endpoint
    print("\n4. Testing Search Endpoint...")
    try:
        response = requests.get(
            f"{base_url}/api/search?query=romantic restaurants in Paris&category=activities",
            timeout=10
        )
        if response.status_code == 200:
            print("✅ Search endpoint passed!")
            data = response.json()
            print(f"   Total results: {data.get('total_results', 0)}")
        else:
            print(f"❌ Search endpoint failed with status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Search endpoint failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Backend testing completed!")
    print("\n📋 Next steps:")
    print("1. If all tests passed, your backend is working correctly")
    print("2. You can now start the frontend to test the full application")
    print("3. Check the API documentation at: http://localhost:8000/docs")

if __name__ == "__main__":
    # Wait a bit for the server to start
    print("⏳ Waiting for server to start...")
    time.sleep(5)
    test_backend()

