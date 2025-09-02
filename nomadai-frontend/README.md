# NomadAI Frontend

A modern React/Next.js frontend for NomadAI - Your Personal AI Travel Planner.

## 🚀 Features

- **Interactive Travel Planning Form**: Comprehensive form with validation for trip details
- **Real-time AI Integration**: Connects to the NomadAI backend for personalized travel plans
- **Budget Analysis Visualization**: Visual budget allocation with progress bars
- **Daily Itinerary Display**: Day-wise travel plans with estimated costs
- **Weather Integration**: Weather forecasts for travel dates
- **Activity Tags**: Visual representation of selected activities
- **PDF Export**: Export travel plans as PDF (coming soon)
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## 🛠️ Tech Stack

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **React Hooks**: State management and side effects

## 📦 Installation

1. Navigate to the frontend directory:
```bash
cd nomadai-frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## 🔧 Configuration

The frontend connects to the NomadAI backend API running on `http://localhost:8000`. Make sure the backend is running before using the frontend.

## 📱 Usage

1. **Open the Application**: Navigate to the homepage
2. **Plan Your Trip**: Click "Plan My Trip" to open the travel planning form
3. **Fill in Details**: Complete the form with your travel preferences:
   - Trip basics (origin, destination, dates)
   - Budget and number of travelers
   - Travel preferences (mode, hotel type, activities)
4. **Generate Plan**: Submit the form to generate your personalized travel plan
5. **Review Results**: View your comprehensive travel plan including:
   - Budget analysis with visual breakdown
   - AI recommendations for flights, hotels, and activities
   - Daily itinerary with estimated costs
   - Weather forecasts
6. **Export**: Download your travel plan as PDF (feature coming soon)

## 🎨 Components

### Core Components

- **TravelPlanningModal**: Main form for collecting travel preferences
- **ActivityTags**: Visual display of selected activities with icons
- **Main Page**: Dashboard displaying travel plans and chat interface

### Form Features

- **Validation**: Real-time form validation with error messages
- **Default Values**: Sensible defaults for better user experience
- **Responsive Layout**: Adapts to different screen sizes
- **Accessibility**: Proper labels and keyboard navigation

## 🔗 API Integration

The frontend communicates with the NomadAI backend through the following endpoints:

- `POST /api/travel-plan`: Submit travel form and receive comprehensive plan
- `GET /api/health`: Health check endpoint

## 🎯 Key Features

### Travel Planning Form
- Origin and destination cities
- Travel dates with validation
- Budget allocation
- Number of travelers
- Travel mode selection
- Hotel preferences
- Activity selection (multiple choice)
- Previous visit information

### Results Display
- Budget analysis with percentage breakdown
- AI recommendations summary
- Detailed daily itinerary
- Weather information
- Estimated costs for each day
- Activity recommendations

### User Experience
- Loading states with visual feedback
- Error handling and display
- Responsive design for all devices
- Smooth animations and transitions
- Clear disclaimers about estimates

## 🚧 Development

### Project Structure
```
src/
├── app/
│   ├── components/
│   │   ├── TravelPlanningModal.tsx
│   │   └── ActivityTags.tsx
│   ├── globals.css
│   └── page.tsx
├── types/
└── utils/
```

### Adding New Features
1. Create new components in `src/app/components/`
2. Update TypeScript interfaces as needed
3. Add styling using Tailwind CSS classes
4. Test responsiveness on different screen sizes

## 📄 License

This project is part of the NomadAI travel planning system.

## 🤝 Contributing

1. Follow the existing code style and patterns
2. Add TypeScript types for new features
3. Test on multiple screen sizes
4. Ensure accessibility standards are met

---

**Note**: NomadAI is a travel planner, not a booking system. All prices and availability are estimates. Please verify all information and book directly with service providers.
