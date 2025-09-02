# 🚀 NomadAI - Your Personal AI Travel Planner

NomadAI is a personal AI travel planner that replicates the role of old-school human travel agents. It doesn't handle booking, but produces a personalized, budget-aware itinerary that travelers can follow manually. Think of it as your digital travel companion that helps you plan the perfect trip without the hassle of booking systems.

## 🎯 What NomadAI Does

- **Personalized Itinerary Creation**: Generates day-wise travel plans tailored to your preferences
- **Budget Analysis**: AI-powered budget allocation and cost estimation
- **Smart Recommendations**: Uses embeddings to find the best flights, hotels, and activities
- **Weather & Context**: Provides seasonal insights and weather-aware planning
- **Estimated Costs**: Shows realistic cost estimates (not live prices)
- **PDF Export**: Export your complete itinerary as a PDF

## ⚠️ Important Disclaimer

**NomadAI is a travel planner, not a booking system.** All prices and availability are estimates based on current market conditions. Actual costs may vary. Please verify all information and book directly with service providers.

## 🏗️ Project Structure

```
nomadai-backend/
├── src/
│   ├── api/
│   │   └── routes/
│   │       └── form.py          # FastAPI routes and endpoints
│   ├── core/                    # Core application logic
│   ├── models/                  # Pydantic models and data schemas
│   ├── services/                # AI agents and business logic
│   │   ├── budget_agent.py      # Budget analysis using Cohere
│   │   ├── search_agent.py      # Semantic search using embeddings
│   │   ├── context_agent.py     # Weather and seasonal context
│   │   └── summary_agent.py     # Itinerary generation using LangChain
│   └── utils/                   # Utility functions and helpers
├── data/                        # Mock datasets
│   ├── flights.json            # Flight options with estimated prices
│   ├── hotels.json             # Hotel options with estimated prices
│   └── activities.json         # Activity options with estimated costs
├── logs/                        # Log files and temporary outputs
├── tests/                       # Test files
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## 🤖 AI Agents

### 1. Budget Agent (Cohere)
- Analyzes travel preferences and suggests budget allocation
- Outputs JSON with budget breakdown (flights, accommodation, activities, food, transportation)
- Provides money-saving tips and feasibility scores

### 2. Search Agent (Hugging Face Embeddings)
- Queries mock datasets for flights, hotels, and activities
- Uses semantic search to match user preferences
- Filters results based on budget and location

### 3. Context Agent (Hugging Face + OpenWeather)
- Adds seasonal and weather context to recommendations
- Provides packing suggestions and best times for activities
- Includes local events and seasonal tips

### 4. Summary Agent (LangChain)
- Generates natural language day-wise itineraries
- Creates engaging descriptions for each day
- Calculates total estimated costs and budget utilization

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Cohere API key (for budget analysis)
- OpenAI API key (for itinerary generation)
- OpenWeather API key (for weather data - optional)

### Installation

1. **Clone and navigate to the backend directory**
```bash
cd nomadai-backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Copy example environment file
cp env.example .env

# Add your API keys
echo "COHERE_API_KEY=your_cohere_api_key_here" >> .env
echo "OPENAI_API_KEY=your_openai_api_key_here" >> .env
echo "OPENWEATHER_API_KEY=your_openweather_api_key_here" >> .env
```

5. **Run the development server**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the server is running, you can access:

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🛠️ API Endpoints

### Travel Planning

#### `POST /api/travel-plan`
Create a comprehensive travel plan with AI agents.

**Request Body:**
```json
{
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
```

**Response:**
```json
{
  "success": true,
  "message": "Travel plan created successfully!",
  "travel_plan": {
    "budget_analysis": { ... },
    "search_results": { ... },
    "context_info": { ... },
    "itinerary": { ... }
  },
  "disclaimer": "NomadAI is a travel planner, not a booking system..."
}
```

#### `GET /api/search`
Search for recommendations using semantic search.

**Parameters:**
- `query`: Search query (e.g., "romantic restaurants in Paris")
- `category`: "flights", "hotels", "activities", or "all"

#### `GET /api/health`
Health check endpoint to verify all services are running.

#### `GET /api/rate-limit-status`
Check current rate limit status for the client.

**Response:**
```json
{
  "user_id": "127.0.0.1",
  "current_count": 2,
  "limit": 5,
  "remaining": 3,
  "reset_date": "2024-01-15",
  "percentage_used": 40.0,
  "message": "You have 3 requests remaining today."
}
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# AI Services
COHERE_API_KEY=your_cohere_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Weather API (optional)
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
```

## 🧪 Testing

Run tests using pytest:

```bash
pytest tests/
```

## 📝 Development

### Code Structure

- **Routes** (`src/api/routes/`): FastAPI route handlers
- **Services** (`src/services/`): AI agents and business logic
- **Models** (`src/models/`): Pydantic models for data validation
- **Core** (`src/core/`): Core application configuration and utilities
- **Utils** (`src/utils/`): Helper functions and utilities

### Adding New Features

1. Create new route files in `src/api/routes/`
2. Add business logic in `src/services/`
3. Define data models in `src/models/`
4. Add tests in `tests/`

## 🚦 Rate Limiting

NomadAI implements a daily rate limiting system to manage API costs and prevent abuse:

### Features
- **Daily Limit**: 5 requests per day per user (IP-based)
- **Automatic Reset**: Limits reset daily at midnight
- **Visual Feedback**: Frontend shows usage progress and remaining requests
- **Graceful Handling**: Clear error messages when limit is exceeded
- **Data Persistence**: Rate limit data stored in `data/rate_limits.json`

### How It Works
1. Each API request is tracked by client IP address
2. Requests are counted per day (resets at midnight)
3. When limit is reached, API returns HTTP 429 (Too Many Requests)
4. Frontend displays usage progress and disables the submit button
5. Old rate limit data is automatically cleaned up after 7 days

### Rate Limit Response
When limit is exceeded:
```json
{
  "error": "Rate limit exceeded",
  "message": "Daily limit of 5 requests exceeded. Please try again tomorrow.",
  "limit_info": {
    "current_count": 5,
    "limit": 5,
    "remaining": 0,
    "reset_date": "2024-01-15"
  }
}
```

## 🎨 Mock Data

The system uses realistic mock datasets for:

- **Flights**: Airline, origin, destination, duration, price estimates
- **Hotels**: Hotel name, location, price estimates, tier (budget/mid-range/luxury)
- **Activities**: Name, category, location, cost estimates, tags

All prices are estimates based on current market conditions.

## 🔍 Features

### 🤖 AI-Powered Planning
- Natural language processing for user input
- Personalized recommendations based on preferences
- Dynamic itinerary creation with day-by-day planning
- Budget-aware suggestions

### 🔍 Semantic Search
- Sentence transformers for text embeddings
- Intelligent matching of user preferences
- Filtering by budget, location, and activities
- Fast similarity search

### 🌤️ Weather & Context
- OpenWeather API integration for real weather data
- Seasonal recommendations and tips
- Activity-specific weather advice
- Packing suggestions

### 📊 Budget Management
- AI-powered budget allocation
- Cost estimation and tracking
- Budget utilization analysis
- Money-saving recommendations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

**Built with ❤️ for travelers who want intelligent planning without the complexity of booking systems**

