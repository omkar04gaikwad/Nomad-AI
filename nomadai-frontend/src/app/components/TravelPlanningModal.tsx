'use client';

import { useState } from 'react';

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

interface TravelPlanningModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: TravelFormData) => void;
}

export default function TravelPlanningModal({ isOpen, onClose, onSubmit }: TravelPlanningModalProps) {
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

  const [errors, setErrors] = useState<Partial<TravelFormData>>({});

  const handleInputChange = (field: keyof TravelFormData, value: string | string[]) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined
      }));
    }
  };

  const handleActivityChange = (activity: string) => {
    setFormData(prev => ({
      ...prev,
      activities: prev.activities.includes(activity)
        ? prev.activities.filter(a => a !== activity)
        : [...prev.activities, activity]
    }));
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<TravelFormData> = {};

    if (!formData.origin.trim()) {
      newErrors.origin = 'Origin is required';
    }
    if (!formData.destination.trim()) {
      newErrors.destination = 'Destination is required';
    }
    if (!formData.startDate) {
      newErrors.startDate = 'Start date is required';
    }
    if (!formData.endDate) {
      newErrors.endDate = 'End date is required';
    }
    if (formData.startDate && formData.endDate && formData.startDate >= formData.endDate) {
      newErrors.endDate = 'End date must be after start date';
    }
    if (!formData.budget || parseInt(formData.budget) <= 0) {
      newErrors.budget = 'Valid budget is required';
    }
    if (!formData.people || parseInt(formData.people) <= 0) {
      newErrors.people = 'Number of people is required';
    }
    if (!formData.travelMode) {
      newErrors.travelMode = 'Travel mode is required';
    }
    if (formData.activities.length === 0) {
      newErrors.activities = 'Please select at least one activity';
    }
    if (!formData.hotelPreference) {
      newErrors.hotelPreference = 'Hotel preference is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  const resetForm = () => {
    setFormData({
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
    setErrors({});
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">🚀 Plan Your Perfect Trip</h2>
            <p className="text-sm text-gray-600 mt-1">Let NomadAI create your personalized travel itinerary</p>
          </div>
          <button
            onClick={handleClose}
            className="text-gray-500 hover:text-gray-700 text-2xl font-bold"
          >
            ×
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Trip Basics */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-800 border-b border-gray-200 pb-2">
              📍 Trip Basics
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Origin City
                </label>
                <input
                  type="text"
                  value={formData.origin}
                  onChange={(e) => handleInputChange('origin', e.target.value)}
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    errors.origin ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="e.g., New York"
                  required
                />
                {errors.origin && (
                  <p className="text-red-500 text-xs mt-1">{errors.origin}</p>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Destination City
                </label>
                <input
                  type="text"
                  value={formData.destination}
                  onChange={(e) => handleInputChange('destination', e.target.value)}
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    errors.destination ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="e.g., Paris"
                  required
                />
                {errors.destination && (
                  <p className="text-red-500 text-xs mt-1">{errors.destination}</p>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Start Date
                </label>
                <input
                  type="date"
                  value={formData.startDate}
                  onChange={(e) => handleInputChange('startDate', e.target.value)}
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    errors.startDate ? 'border-red-500' : 'border-gray-300'
                  }`}
                  min={new Date().toISOString().split('T')[0]}
                  required
                />
                {errors.startDate && (
                  <p className="text-red-500 text-xs mt-1">{errors.startDate}</p>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  End Date
                </label>
                <input
                  type="date"
                  value={formData.endDate}
                  onChange={(e) => handleInputChange('endDate', e.target.value)}
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    errors.endDate ? 'border-red-500' : 'border-gray-300'
                  }`}
                  min={formData.startDate || new Date().toISOString().split('T')[0]}
                  required
                />
                {errors.endDate && (
                  <p className="text-red-500 text-xs mt-1">{errors.endDate}</p>
                )}
              </div>
            </div>
          </div>

          {/* Budget & Travelers */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-800 border-b border-gray-200 pb-2">
              💰 Budget & Travelers
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Total Budget (USD)
                </label>
                <input
                  type="number"
                  value={formData.budget}
                  onChange={(e) => handleInputChange('budget', e.target.value)}
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    errors.budget ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="e.g., 5000"
                  min="1"
                  step="1"
                  required
                />
                {errors.budget && (
                  <p className="text-red-500 text-xs mt-1">{errors.budget}</p>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Number of Travelers
                </label>
                <select
                  value={formData.people}
                  onChange={(e) => handleInputChange('people', e.target.value)}
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    errors.people ? 'border-red-500' : 'border-gray-300'
                  }`}
                  required
                >
                  {[1, 2, 3, 4, 5, 6, 7, 8].map(num => (
                    <option key={num} value={num.toString()}>{num} {num === 1 ? 'person' : 'people'}</option>
                  ))}
                </select>
                {errors.people && (
                  <p className="text-red-500 text-xs mt-1">{errors.people}</p>
                )}
              </div>
            </div>
          </div>

          {/* Travel Preferences */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-800 border-b border-gray-200 pb-2">
              🎯 Travel Preferences
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Travel Mode
                </label>
                <select
                  value={formData.travelMode}
                  onChange={(e) => handleInputChange('travelMode', e.target.value)}
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    errors.travelMode ? 'border-red-500' : 'border-gray-300'
                  }`}
                  required
                >
                  <option value="">Select travel mode</option>
                  <option value="plane">✈️ Plane</option>
                  <option value="train">🚂 Train</option>
                  <option value="car">🚗 Car</option>
                  <option value="bus">🚌 Bus</option>
                </select>
                {errors.travelMode && (
                  <p className="text-red-500 text-xs mt-1">{errors.travelMode}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Hotel Preference
                </label>
                <select
                  value={formData.hotelPreference}
                  onChange={(e) => handleInputChange('hotelPreference', e.target.value)}
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    errors.hotelPreference ? 'border-red-500' : 'border-gray-300'
                  }`}
                  required
                >
                  <option value="">Select hotel preference</option>
                  <option value="budget">💰 Budget</option>
                  <option value="mid-range">🏨 Mid-range</option>
                  <option value="luxury">⭐ Luxury</option>
                </select>
                {errors.hotelPreference && (
                  <p className="text-red-500 text-xs mt-1">{errors.hotelPreference}</p>
                )}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Activities (select multiple)
              </label>
              <div className={`grid grid-cols-2 md:grid-cols-3 gap-3 p-3 border rounded-md ${
                errors.activities ? 'border-red-500' : 'border-gray-300'
              }`}>
                {[
                  'sightseeing', 'culture', 'food', 'adventure', 
                  'relaxation', 'shopping', 'nightlife', 'nature'
                ].map((activity) => (
                  <label key={activity} className="flex items-center p-2 hover:bg-gray-50 rounded cursor-pointer">
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
              {errors.activities && (
                <p className="text-red-500 text-xs mt-1">{errors.activities}</p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Visited Destination Before?
                </label>
                <div className="flex space-x-4">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="visitedBefore"
                      value="yes"
                      checked={formData.visitedBefore === 'yes'}
                      onChange={(e) => handleInputChange('visitedBefore', e.target.value)}
                      className="mr-2"
                    />
                    Yes
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="visitedBefore"
                      value="no"
                      checked={formData.visitedBefore === 'no'}
                      onChange={(e) => handleInputChange('visitedBefore', e.target.value)}
                      className="mr-2"
                    />
                    No
                  </label>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Strict Dates?
                </label>
                <div className="flex space-x-4">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="strictDates"
                      value="yes"
                      checked={formData.strictDates === 'yes'}
                      onChange={(e) => handleInputChange('strictDates', e.target.value)}
                      className="mr-2"
                    />
                    Yes
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="strictDates"
                      value="no"
                      checked={formData.strictDates === 'no'}
                      onChange={(e) => handleInputChange('strictDates', e.target.value)}
                      className="mr-2"
                    />
                    No
                  </label>
                </div>
              </div>
            </div>
          </div>

          {/* Submit Buttons */}
          <div className="flex justify-end space-x-4 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={handleClose}
              className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors flex items-center space-x-2"
            >
              <span>🚀</span>
              <span>Create My Travel Plan</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
