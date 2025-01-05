# EcoPrint

A web application that tracks your sustainable transport activities through Strava integration and calculates your carbon footprint savings.

## Features

- Strava Integration for activity tracking
- CO2 savings calculation for walking, running, and cycling activities
- Gamification with points system
- Real-time activity syncing
- Location-based tracking

## Tech Stack

- Backend: FastAPI (Python)
- Frontend: Next.js (React)
- Database: SQLite
- Authentication: JWT
- Third-party Integration: Strava API

## Environment Variables

Required environment variables:

```env
# App Settings
SECRET_KEY=your-secret-key
ALGORITHM=HS256

# Strava API
STRAVA_CLIENT_ID=your-strava-client-id
STRAVA_CLIENT_SECRET=your-strava-client-secret
STRAVA_WEBHOOK_VERIFY_TOKEN=your-webhook-verify-token

# URLs
VERCEL_URL=your-vercel-url
FRONTEND_URL=your-frontend-url
```

## Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables
4. Run the development server: `uvicorn app.main:app --reload`

## Deployment

The application is configured for deployment on Vercel. Connect your GitHub repository to Vercel and set the required environment variables in the Vercel dashboard.
