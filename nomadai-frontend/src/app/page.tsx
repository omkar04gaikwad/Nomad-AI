'use client';

import { useState, useEffect } from 'react';
import TravelPlanningModal from './components/TravelPlanningModal';
import ActivityTags from './components/ActivityTags';

interface TravelFormData {
  origin: string;
  destination: string;
  startDate: string;
  endDate: string;
  strictDates: string;
  budget: string;
  people: string;
  travelMode: string;
  activities: string[];
  visitedBefore: string;
  hotelPreference: string;
}

interface TravelPlan {
  budget_analysis: any;
  search_results: any;
  context_info: any;
  itinerary: any;
  form_data: TravelFormData;
}

export default function Home() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [travelPlan, setTravelPlan] = useState<TravelPlan | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [rateLimitInfo, setRateLimitInfo] = useState<any>(null);
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: 'Hello! I\'m NomadAI, your AI travel planner. I can help you create personalized itineraries with budget analysis, weather insights, and smart recommendations. Click the "Plan My Trip" button to get started!'
    }
  ]);

  const openModal = () => {
    setIsModalOpen(true);
  };

  const checkRateLimit = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/rate-limit-status');
      if (response.ok) {
        const data = await response.json();
        setRateLimitInfo(data);
      }
    } catch (error) {
      console.error('Error checking rate limit:', error);
    }
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  // Check rate limit on page load
  useEffect(() => {
    checkRateLimit();
  }, []);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const submitTravelPlan = async (formData: TravelFormData) => {
    setLoading(true);
    setError(null);

    try {
      // Check rate limit before submitting
      await checkRateLimit();

    try {
      // Show loading message
      setMessages(prev => [...prev, {
        id: prev.length + 1,
        type: 'user',
        content: `Planning trip from ${formData.origin} to ${formData.destination} with budget $${formData.budget}`
      }]);

      // Send form data to backend
      const response = await fetch('http://localhost:8000/api/travel-plan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (result.success) {
        setTravelPlan(result.travel_plan);
        
        // Add success message with summary
        const itinerary = result.travel_plan.itinerary?.itinerary;
        const budgetAnalysis = result.travel_plan.budget_analysis;
        
        let summaryMessage = `✅ Your travel plan is ready!\n\n`;
        summaryMessage += `📍 Destination: ${itinerary?.destination}\n`;
        summaryMessage += `📅 Duration: ${itinerary?.duration_days} days\n`;
        summaryMessage += `💰 Total Estimated Cost: ${formatCurrency(itinerary?.total_estimated_cost?.total || 0)}\n`;
        summaryMessage += `👥 Travelers: ${itinerary?.total_people}\n\n`;
        
        if (budgetAnalysis?.budget_analysis?.allocation) {
          summaryMessage += `📊 Budget Allocation:\n`;
          Object.entries(budgetAnalysis.budget_analysis.allocation).forEach(([category, data]: [string, any]) => {
            summaryMessage += `• ${category.charAt(0).toUpperCase() + category.slice(1)}: ${data.percentage}%\n`;
          });
        }
        
        summaryMessage += `\n📋 Your detailed itinerary is displayed below. You can export it as PDF!`;
        
        setMessages(prev => [...prev, {
          id: prev.length + 1,
          type: 'assistant',
          content: summaryMessage
        }]);
      } else {
        throw new Error(result.message || 'Failed to create travel plan');
      }
    } catch (error: any) {
      console.error('Error creating travel plan:', error);
      
      // Check if it's a rate limit error
      if (error.status === 429) {
        const errorData = await error.json();
        setError(`Rate limit exceeded: ${errorData.detail.message}`);
        setMessages(prev => [...prev, {
          id: prev.length + 1,
          type: 'assistant',
          content: `❌ ${errorData.detail.message}`
        }]);
      } else {
        setError(error instanceof Error ? error.message : 'An error occurred');
        setMessages(prev => [...prev, {
          id: prev.length + 1,
          type: 'assistant',
          content: `❌ Sorry, I encountered an error while creating your travel plan. Please try again.`
        }]);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-800">🚀 NomadAI</h1>
          <div className="text-sm text-gray-600">Your Personal AI Travel Planner</div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-6xl mx-auto space-y-6">
          {/* Disclaimer */}
          <div className="bg-yellow-100 border-l-4 border-yellow-500 p-4 rounded">
            <p className="text-yellow-700 text-sm">
              <strong>⚠️ Important:</strong> NomadAI is a travel planner, not a booking system. 
              All prices and availability are estimates. Please verify all information and book directly with service providers.
            </p>
          </div>

          {/* Rate Limit Info */}
          {rateLimitInfo && (
            <div className="bg-blue-100 border-l-4 border-blue-500 p-4 rounded">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-700 text-sm font-medium">
                    📊 Daily Usage: {rateLimitInfo.current_count}/{rateLimitInfo.limit} requests
                  </p>
                  <p className="text-blue-600 text-xs">
                    {rateLimitInfo.message}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-20 bg-blue-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        rateLimitInfo.percentage_used > 80 ? 'bg-red-500' : 
                        rateLimitInfo.percentage_used > 60 ? 'bg-yellow-500' : 'bg-blue-500'
                      }`}
                      style={{ width: `${Math.min(rateLimitInfo.percentage_used, 100)}%` }}
                    ></div>
                  </div>
                  <span className="text-blue-700 text-xs font-medium">
                    {Math.round(rateLimitInfo.percentage_used)}%
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Chat Messages */}
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-3xl px-4 py-3 rounded-lg ${
                    message.type === 'user'
                      ? 'bg-blue-500 text-white'
                      : 'bg-white border border-gray-200 text-gray-800'
                  }`}
                >
                  <pre className="whitespace-pre-wrap font-sans">{message.content}</pre>
                </div>
              </div>
            ))}
          </div>

          {/* Travel Plan Results */}
          {travelPlan && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-semibold mb-6">📋 Your Complete Travel Plan</h2>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Budget Analysis */}
                <div className="border rounded-lg p-4">
                  <h3 className="text-lg font-semibold mb-3">💰 Budget Analysis</h3>
                  {travelPlan.budget_analysis?.budget_analysis?.allocation && (
                    <div className="space-y-2">
                      {Object.entries(travelPlan.budget_analysis.budget_analysis.allocation).map(([category, data]: [string, any]) => (
                        <div key={category} className="flex justify-between items-center">
                          <span className="capitalize">{category}:</span>
                          <div className="flex items-center space-x-2">
                            <div className="w-20 bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-blue-500 h-2 rounded-full" 
                                style={{ width: `${data.percentage}%` }}
                              ></div>
                            </div>
                            <span className="text-sm font-medium">{data.percentage}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {travelPlan.budget_analysis?.recommendations && (
                    <div className="mt-4">
                      <h4 className="font-semibold mb-2">💡 Recommendations:</h4>
                      <ul className="text-sm space-y-1">
                        {travelPlan.budget_analysis.recommendations.slice(0, 3).map((rec: string, index: number) => (
                          <li key={index} className="flex items-start">
                            <span className="mr-2">•</span>
                            <span>{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {/* Search Results Summary */}
                <div className="border rounded-lg p-4">
                  <h3 className="text-lg font-semibold mb-3">🔍 AI Recommendations</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span>✈️ Flights:</span>
                      <span className="font-medium">{travelPlan.search_results?.flights?.length || 0} options found</span>
                    </div>
                    <div className="flex justify-between">
                      <span>🏨 Hotels:</span>
                      <span className="font-medium">{travelPlan.search_results?.hotels?.length || 0} options found</span>
                    </div>
                    <div className="flex justify-between">
                      <span>🎯 Activities:</span>
                      <span className="font-medium">{travelPlan.search_results?.activities?.length || 0} options found</span>
                    </div>
                  </div>
                  
                  {travelPlan.context_info?.weather?.summary && (
                    <div className="mt-4">
                      <h4 className="font-semibold mb-2">🌤️ Weather Forecast:</h4>
                      <p className="text-sm">
                        Average temperature: {travelPlan.context_info.weather.summary.average_temperature?.toFixed(1)}°C
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Form Data Summary */}
              {travelPlan.form_data && (
                <div className="mt-8 border rounded-lg p-4">
                  <h3 className="text-lg font-semibold mb-4">📋 Trip Details</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <span className="font-medium">From:</span> {travelPlan.form_data.origin}
                    </div>
                    <div>
                      <span className="font-medium">To:</span> {travelPlan.form_data.destination}
                    </div>
                    <div>
                      <span className="font-medium">Budget:</span> {formatCurrency(parseInt(travelPlan.form_data.budget))}
                    </div>
                    <div>
                      <span className="font-medium">Travelers:</span> {travelPlan.form_data.people}
                    </div>
                  </div>
                  <div>
                    <span className="font-medium">Selected Activities:</span>
                    <div className="mt-2">
                      <ActivityTags activities={travelPlan.form_data.activities} />
                    </div>
                  </div>
                </div>
              )}

              {/* Detailed Itinerary */}
              {travelPlan.itinerary?.itinerary && (
                <div className="mt-8 border rounded-lg p-4">
                  <h3 className="text-lg font-semibold mb-4">📅 Daily Itinerary</h3>
                  <div className="space-y-4">
                    {travelPlan.itinerary.itinerary.daily_plans?.map((day: any, index: number) => (
                      <div key={index} className="bg-gray-50 p-4 rounded-lg">
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-semibold text-lg">{day.title}</h4>
                          <span className="text-sm text-gray-600 bg-white px-2 py-1 rounded">
                            {formatCurrency(day.estimated_cost?.total || 0)}
                          </span>
                        </div>
                        <p className="text-gray-700 mb-3">{day.description}</p>
                        
                        {day.activities && day.activities.length > 0 && (
                          <div className="mb-3">
                            <h5 className="font-medium mb-2">Activities:</h5>
                            <div className="space-y-1">
                              {day.activities.map((activity: any, actIndex: number) => (
                                <div key={actIndex} className="flex justify-between text-sm">
                                  <span>• {activity.name}</span>
                                  <span className="text-gray-600">
                                    {formatCurrency(activity.cost_estimate || 0)}
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {day.weather_info && (
                          <div className="text-sm text-gray-600">
                            <span>🌤️ {day.weather_info.condition} • {day.weather_info.temperature?.average?.toFixed(1)}°C</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Export Button */}
              <div className="mt-6 flex justify-center">
                <button className="bg-green-600 text-white py-3 px-8 rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2">
                  <span>📄</span>
                  <span>Export as PDF</span>
                </button>
              </div>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="bg-red-100 border-l-4 border-red-500 p-4 rounded">
              <p className="text-red-700">
                <strong>Error:</strong> {error}
              </p>
            </div>
          )}

          {/* Loading State */}
          {loading && (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">AI agents are creating your personalized travel plan...</p>
              <p className="text-sm text-gray-500 mt-2">This may take a few moments</p>
            </div>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center space-x-4">
            <button
              onClick={openModal}
              disabled={loading || (rateLimitInfo && rateLimitInfo.remaining === 0)}
              className={`flex-1 font-medium py-3 px-6 rounded-lg transition-colors duration-200 flex items-center justify-center space-x-2 ${
                loading || (rateLimitInfo && rateLimitInfo.remaining === 0)
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-500 hover:bg-blue-600'
              } text-white`}
            >
              <span>🚀</span>
              <span>
                {loading ? 'Creating Plan...' : 
                 rateLimitInfo && rateLimitInfo.remaining === 0 ? 'Daily Limit Reached' : 
                 'Plan My Trip'}
              </span>
            </button>
            <div className="text-sm text-gray-500">
              {loading ? 'AI agents are working...' : 
               rateLimitInfo && rateLimitInfo.remaining === 0 ? 'Daily limit reached. Try again tomorrow.' :
               'Click to start planning your adventure'}
            </div>
          </div>
        </div>
      </div>

      {/* Travel Planning Modal */}
      <TravelPlanningModal 
        isOpen={isModalOpen} 
        onClose={closeModal}
        onSubmit={(formData) => {
          submitTravelPlan(formData);
          closeModal();
        }}
      />
    </div>
  );
}
