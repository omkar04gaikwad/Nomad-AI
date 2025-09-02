import json
from datetime import datetime
import cohere
import os

def generate_cohere_prompt(form_entry):
    """
    Generate Cohere API prompt from form entry
    """
    prompt = f"""You are NomadAI, an intelligent travel planner.  
Using the details provided below, create a budget allocation.  

Trip Details:
- Origin: {form_entry['origin']}  
- Destination: {form_entry['destination']}  
- Travel Dates: {form_entry['startDate']} to {form_entry['endDate']}  
- Strict Dates: {form_entry['strictDates']}  
- Budget per person: {form_entry['budget']} USD  
- Number of People: {form_entry['people']}  
- Travel Mode: {form_entry['travelMode']}  
- Activities of Interest: {', '.join(form_entry['activities'])}  
- Visited Before: {form_entry['visitedBefore']}  
- Hotel Preference: {form_entry['hotelPreference']}  

Important Notes:
- The budget is PER PERSON, not total for all people  
- Hotels can be shared rooms (2 people per room) to reduce costs  
- Calculate total trip cost = (budget per person × number of people)  
- For hotel costs, consider room sharing when beneficial  

Tasks:
1. Allocate the budget per person across these categories: flights, hotel (consider room sharing), meals, activities, documentation (only if not visited before).  
2. Calculate if the total trip cost exceeds the given budget per person × number of people:  
   - If new budget ≤ actual budget → no date changes needed, proceed with current dates  
   - If new budget > actual budget:  
     - If dates are strict → suggest the new required budget per person with detailed breakdown and indicate surplus amount.  
     - If dates are flexible → suggest the top 3 alternate date ranges close to the requested ones where the budget fits, or the 3 closest possible.  
3. Provide a short `hotel_sharing_note` explaining **why this hotel setup is needed and for whom** (e.g. "Luxury hotel chosen for honeymoon couple, room shared by both travelers").  
4. Output must be valid JSON with fields:  
   - budget_allocation_per_person (object with costs per person)  
   - total_trip_cost (number: budget per person × number of people)  
   - hotel_sharing_note (short summary, 1–2 sentences only)  
   - feasibility_note (string)  
   - new_dates (array; empty if budget is sufficient or strict dates, otherwise contains 3 suggested date ranges with total estimated costs)  """

    return prompt

def save_prompt_to_file(form_entry, prompt):
    """
    Save the generated prompt to a file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"cohere_prompt_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as file:
        file.write("=== FORM DATA ===\n")
        file.write(json.dumps(form_entry, indent=2))
        file.write("\n\n=== COHERE PROMPT ===\n")
        file.write(prompt)
    
    return filename

def call_cohere_api(prompt):
    """
    Call Cohere API with the generated prompt
    """
    try:
        # Initialize Cohere client
        co = cohere.Client("fwksPuItAUmlEh924jWDxOfKvynurjXXx15zHTPU")
        
        # Call the API
        response = co.generate(
            model='command',
            prompt=prompt,
            max_tokens=1000,
            temperature=0.7,
            k=0,
            stop_sequences=[],
            return_likelihoods='NONE'
        )
        
        return response.generations[0].text.strip()
        
    except Exception as e:
        return f"Error calling Cohere API: {str(e)}"

def process_form_with_cohere(form_entry):
    """
    Generate prompt and call Cohere API
    """
    # Generate the prompt
    prompt = generate_cohere_prompt(form_entry)
    
    # Call Cohere API
    cohere_response = call_cohere_api(prompt)
    
    # Save both prompt and response
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"cohere_response_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as file:
        file.write("=== FORM DATA ===\n")
        file.write(json.dumps(form_entry, indent=2))
        file.write("\n\n=== COHERE PROMPT ===\n")
        file.write(prompt)
        file.write("\n\n=== COHERE RESPONSE ===\n")
        file.write(cohere_response)
    
    return filename, cohere_response

# Example usage
if __name__ == "__main__":
    # Example form entry
    sample_form = {
        "timestamp": "2025-09-01T10:54:19.909806",
        "origin": "Mumbai",
        "destination": "Tokyo",
        "startDate": "2025-09-15",
        "endDate": "2025-09-19",
        "strictDates": "yes",
        "budget": "1998",
        "people": "2",
        "travelMode": "partner",
        "activities": ["food", "culture", "relaxation"],
        "visitedBefore": "no",
        "hotelPreference": "mid-range"
    }
    
    # Test with Cohere API
    filename, response = process_form_with_cohere(sample_form)
    print(f"Response saved to: {filename}")
    print("\nCohere API Response:")
    print("=" * 50)
    print(response)
