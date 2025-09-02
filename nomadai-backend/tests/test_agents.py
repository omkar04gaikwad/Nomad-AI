import pytest
from unittest.mock import Mock, patch
from src.services.budget_agent import BudgetAgent
from src.services.search_agent import SearchAgent
from src.services.context_agent import ContextAgent
from src.services.summary_agent import SummaryAgent

class TestBudgetAgent:
    """Test the Budget Agent functionality."""
    
    def test_budget_agent_initialization(self):
        """Test that BudgetAgent initializes correctly."""
        with patch.dict('os.environ', {'COHERE_API_KEY': 'test_key'}):
            agent = BudgetAgent()
            assert agent is not None
    
    def test_budget_analysis_fallback(self):
        """Test budget analysis with fallback when API fails."""
        with patch.dict('os.environ', {'COHERE_API_KEY': 'invalid_key'}):
            agent = BudgetAgent()
            form_data = {
                'budget': '5000',
                'destination': 'Paris',
                'people': '2',
                'activities': ['sightseeing', 'food'],
                'hotelPreference': 'mid-range',
                'travelMode': 'plane'
            }
            
            result = agent.analyze_budget(form_data)
            assert result['success'] == False
            assert 'fallback_allocation' in result

class TestSearchAgent:
    """Test the Search Agent functionality."""
    
    def test_search_agent_initialization(self):
        """Test that SearchAgent initializes correctly."""
        agent = SearchAgent()
        assert agent is not None
        assert hasattr(agent, 'flights_data')
        assert hasattr(agent, 'hotels_data')
        assert hasattr(agent, 'activities_data')
    
    def test_search_flights(self):
        """Test flight search functionality."""
        agent = SearchAgent()
        flights = agent._search_flights('New York', 'Paris', 1000, 2)
        assert isinstance(flights, list)
    
    def test_search_hotels(self):
        """Test hotel search functionality."""
        agent = SearchAgent()
        hotels = agent._search_hotels('Paris', 'mid-range', 500, 2)
        assert isinstance(hotels, list)
    
    def test_search_activities(self):
        """Test activity search functionality."""
        agent = SearchAgent()
        activities = agent._search_activities('Paris', ['culture', 'food'], 200)
        assert isinstance(activities, list)

class TestContextAgent:
    """Test the Context Agent functionality."""
    
    def test_context_agent_initialization(self):
        """Test that ContextAgent initializes correctly."""
        agent = ContextAgent()
        assert agent is not None
    
    def test_get_season(self):
        """Test season determination."""
        agent = ContextAgent()
        assert agent._get_season(1) == 'winter'
        assert agent._get_season(3) == 'spring'
        assert agent._get_season(6) == 'summer'
        assert agent._get_season(9) == 'autumn'
    
    def test_is_peak_season(self):
        """Test peak season determination."""
        agent = ContextAgent()
        assert agent._is_peak_season('paris', 6) == True
        assert agent._is_peak_season('paris', 1) == False
    
    def test_get_packing_suggestions(self):
        """Test packing suggestions generation."""
        agent = ContextAgent()
        weather_info = {
            'summary': {
                'average_temperature': 25,
                'rainy_days': 2
            }
        }
        suggestions = agent._get_packing_suggestions(weather_info)
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

class TestSummaryAgent:
    """Test the Summary Agent functionality."""
    
    def test_summary_agent_initialization(self):
        """Test that SummaryAgent initializes correctly."""
        agent = SummaryAgent()
        assert agent is not None
    
    def test_generate_day_title(self):
        """Test day title generation."""
        agent = SummaryAgent()
        from datetime import datetime
        
        title = agent._generate_day_title('Paris', 1, datetime(2024, 6, 1))
        assert 'Day 1' in title
        assert 'Paris' in title
    
    def test_calculate_day_costs(self):
        """Test day cost calculation."""
        agent = SummaryAgent()
        activities = [
            {'cost_estimate': 25},
            {'cost_estimate': 35}
        ]
        costs = agent._calculate_day_costs(activities)
        assert costs['activities'] == 60
        assert costs['total'] == 60 + 50 + 15  # activities + meals + transport
    
    def test_get_disclaimer(self):
        """Test disclaimer generation."""
        agent = SummaryAgent()
        disclaimer = agent._get_disclaimer()
        assert 'travel planner' in disclaimer.lower()
        assert 'booking system' in disclaimer.lower()

class TestIntegration:
    """Test integration between agents."""
    
    def test_full_workflow(self):
        """Test the complete workflow from form data to itinerary."""
        form_data = {
            'origin': 'New York',
            'destination': 'Paris',
            'startDate': '2024-06-01',
            'endDate': '2024-06-03',
            'budget': '3000',
            'people': '2',
            'activities': ['sightseeing', 'culture'],
            'hotelPreference': 'mid-range',
            'travelMode': 'plane'
        }
        
        # Mock budget analysis
        budget_analysis = {
            'success': True,
            'total_budget': 3000,
            'budget_analysis': {
                'allocation': {
                    'flights': {'percentage': 40, 'amount': 1200},
                    'accommodation': {'percentage': 30, 'amount': 900},
                    'activities': {'percentage': 20, 'amount': 600}
                }
            }
        }
        
        # Mock search results
        search_results = {
            'success': True,
            'flights': [{'price_estimate': 600}],
            'hotels': [{'price_estimate': 150}],
            'activities': [{'cost_estimate': 25}]
        }
        
        # Mock context info
        context_info = {
            'success': True,
            'weather': {'summary': {'average_temperature': 20}},
            'seasonal_context': {'season': 'summer', 'peak_season': True}
        }
        
        # Test summary agent with mocked inputs
        summary_agent = SummaryAgent()
        result = summary_agent.generate_itinerary(
            form_data, budget_analysis, search_results, context_info
        )
        
        assert result['success'] == True
        assert 'itinerary' in result
        assert 'disclaimer' in result
