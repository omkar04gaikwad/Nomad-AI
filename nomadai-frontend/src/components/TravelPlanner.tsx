import React, { useState } from 'react';

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
}

const TravelPlanner: React.FC = () => {
  const [formData, setFormData] = useState<TravelFormData>({
    origin: '',
    destination: '',
    startDate: '',
    endDate: '',
    strictDates: 'yes',
    budget: '',
    people: '1',
    travelMode: 'plane',
    activities: [],
    visitedBefore: 'no',
    hotelPreference: 'mid-range'
  });

  const [travelPlan, setTravelPlan] = useState<TravelPlan | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const activityOptions = [
    'sightseeing',
    'culture',
    'food',
    'adventure',
    'relaxation',
    'shopping',
    'nightlife',
    'nature'
  ];

  const handleActivityChange = (activity: string) => {
    setFormData(prev => ({
      ...prev,
      activities: prev.activities.includes(activity)
        ? prev.activities.filter(a => a !== activity)
        : [...prev.activities, activity]
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/travel-plan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const result = await response.json();

      if (result.success) {
        setTravelPlan(result.travel_plan);
      } else {
        setError(result.message || 'Failed to create travel plan');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-4">
          🚀 NomadAI Travel Planner
        </h1>
        <p className="text-lg text-gray-600 mb-4">
          Your personal AI travel companion that creates personalized itineraries
        </p>
        <div className="bg-yellow-100 border-l-4 border-yellow-500 p-4 mb-6">
          <p className="text-yellow-700">
            <strong>⚠️ Important:</strong> NomadAI is a travel planner, not a booking system. 
            All prices and availability are estimates. Please verify all information and book directly with service providers.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Travel Form */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-semibold mb-6">Plan Your Trip</h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Origin
                </label>
                <input
                  type="text"
                  value={formData.origin}
                  onChange={(e) => setFormData(prev => ({ ...prev, origin: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., New York"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Destination
                </label>
                <input
                  type="text"
                  value={formData.destination}
                  onChange={(e) => setFormData(prev => ({ ...prev, destination: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Paris"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Start Date
                </label>
                <input
                  type="date"
                  value={formData.startDate}
                  onChange={(e) => setFormData(prev => ({ ...prev, startDate: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  End Date
                </label>
                <input
                  type="date"
                  value={formData.endDate}
                  onChange={(e) => setFormData(prev => ({ ...prev, endDate: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Budget (USD)
                </label>
                <input
                  type="number"
                  value={formData.budget}
                  onChange={(e) => setFormData(prev => ({ ...prev, budget: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., 5000"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Number of People
                </label>
                <select
                  value={formData.people}
                  onChange={(e) => setFormData(prev => ({ ...prev, people: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {[1, 2, 3, 4, 5, 6].map(num => (
                    <option key={num} value={num.toString()}>{num}</option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Hotel Preference
              </label>
              <select
                value={formData.hotelPreference}
                onChange={(e) => setFormData(prev => ({ ...prev, hotelPreference: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="budget">Budget</option>
                <option value="mid-range">Mid-Range</option>
                <option value="luxury">Luxury</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Activities (select multiple)
              </label>
              <div className="grid grid-cols-2 gap-2">
                {activityOptions.map(activity => (
                  <label key={activity} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.activities.includes(activity)}
                      onChange={() => handleActivityChange(activity)}
                      className="mr-2"
                    />
                    <span className="capitalize">{activity}</span>
                  </label>
                ))}
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-3 px-6 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating Your Travel Plan...' : 'Create Travel Plan'}
            </button>
          </form>
        </div>

        {/* Travel Plan Results */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-semibold mb-6">Your Travel Plan</h2>
          
          {error && (
            <div className="bg-red-100 border-l-4 border-red-500 p-4 mb-4">
              <p className="text-red-700">{error}</p>
            </div>
          )}

          {loading && (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">AI agents are creating your personalized travel plan...</p>
            </div>
          )}

          {travelPlan && (
            <div className="space-y-6">
              {/* Budget Analysis */}
              <div className="border rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-3">💰 Budget Analysis</h3>
                {travelPlan.budget_analysis?.budget_analysis?.allocation && (
                  <div className="space-y-2">
                    {Object.entries(travelPlan.budget_analysis.budget_analysis.allocation).map(([category, data]: [string, any]) => (
                      <div key={category} className="flex justify-between">
                        <span className="capitalize">{category}:</span>
                        <span>{data.percentage}%</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Search Results */}
              <div className="border rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-3">🔍 Recommendations</h3>
                <div className="space-y-3">
                  <div>
                    <strong>Flights:</strong> {travelPlan.search_results?.flights?.length || 0} options found
                  </div>
                  <div>
                    <strong>Hotels:</strong> {travelPlan.search_results?.hotels?.length || 0} options found
                  </div>
                  <div>
                    <strong>Activities:</strong> {travelPlan.search_results?.activities?.length || 0} options found
                  </div>
                </div>
              </div>

              {/* Itinerary */}
              {travelPlan.itinerary?.itinerary && (
                <div className="border rounded-lg p-4">
                  <h3 className="text-lg font-semibold mb-3">📋 Your Itinerary</h3>
                  <div className="space-y-4">
                    <div>
                      <strong>Destination:</strong> {travelPlan.itinerary.itinerary.destination}
                    </div>
                    <div>
                      <strong>Duration:</strong> {travelPlan.itinerary.itinerary.duration_days} days
                    </div>
                    <div>
                      <strong>Total Estimated Cost:</strong> {formatCurrency(travelPlan.itinerary.itinerary.total_estimated_cost?.total || 0)}
                    </div>
                    
                    {/* Daily Plans */}
                    <div className="mt-4">
                      <h4 className="font-semibold mb-2">Daily Plans:</h4>
                      <div className="space-y-2">
                        {travelPlan.itinerary.itinerary.daily_plans?.map((day: any, index: number) => (
                          <div key={index} className="bg-gray-50 p-3 rounded">
                            <div className="font-medium">{day.title}</div>
                            <div className="text-sm text-gray-600">{day.description}</div>
                            <div className="text-sm text-gray-500 mt-1">
                              Estimated Cost: {formatCurrency(day.estimated_cost?.total || 0)}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Export Button */}
              <button className="w-full bg-green-600 text-white py-3 px-6 rounded-md hover:bg-green-700">
                📄 Export as PDF
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TravelPlanner;
