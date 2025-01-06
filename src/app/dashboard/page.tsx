'use client';

import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Leaf, Cloud, Home, Car, ShoppingBag, Plus, TrendingDown } from 'lucide-react';
import { activities as activitiesApi, auth } from '@/services/api';
import api from '@/services/api';
import { useRouter, useSearchParams } from 'next/navigation';

interface User {
  id: number;
  email: string;
  full_name: string;
  total_distance: number;
  total_co2_saved: number;
  points: number;
  strava_connected: boolean;
}

interface Activity {
  id: number;
  activity_type: string;
  description: string;
  carbon_impact: number;
  timestamp: string;
}

interface QuickAction {
  type: string;
  impact: number;
  icon: React.ComponentType;
}

interface ChartDataPoint {
  date: string;
  impact: number;
}

const Dashboard = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [userData, setUserData] = useState<User | null>(null);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);
  const [stravaAuthUrl, setStravaAuthUrl] = useState<string | null>(null);
  const [quickActions] = useState<QuickAction[]>([
    { type: 'Transport', impact: -1.2, icon: Car },
    { type: 'Home', impact: -0.8, icon: Home },
    { type: 'Shopping', impact: -0.7, icon: ShoppingBag },
  ]);

  useEffect(() => {
    const loadData = async () => {
      try {
        const user = await auth.getCurrentUser();
        setUserData(user);
        
        // Get Strava auth URL if not connected
        if (!user.strava_connected) {
          try {
            const response = await api.get('/api/strava/auth');
            setStravaAuthUrl(response.data.auth_url);
          } catch (error) {
            console.error('Failed to get Strava auth URL:', error);
          }
        }
        
        // Only try to load activities if we have them implemented
        try {
          const activitiesData = await activitiesApi.getAll();
          setActivities(activitiesData);
          
          // Format activities for chart
          const formattedData = activitiesData.map((activity: Activity) => ({
            date: new Date(activity.timestamp).toLocaleDateString(),
            impact: activity.carbon_impact,
          }));
          setChartData(formattedData);
        } catch (error) {
          console.log('Activities not implemented yet');
        }
      } catch (error) {
        console.error('Error loading data:', error);
        router.push('/login');
      }
    };

    loadData();

    // Check if we need to request location permission
    if (searchParams.get('requestLocation') === 'true') {
      requestLocationPermission();
    }
  }, [router, searchParams]);

  const requestLocationPermission = () => {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          try {
            // Send location to backend
            await api.post('/api/user/location', {
              latitude: position.coords.latitude,
              longitude: position.coords.longitude,
            });
            console.log('Location updated successfully');
          } catch (error) {
            console.error('Failed to update location:', error);
          }
        },
        (error) => {
          console.error('Location permission denied:', error);
          alert('Location access is required to track your sustainable transport activities. Please enable location services to continue.');
        }
      );
    }
  };

  const handleActivityClick = async (activityType: string) => {
    try {
      let impact = 0;
      if (activityType === 'Transport') {
        const result = await activitiesApi.calculateTransportImpact(10, 'bus'); // Example values
        impact = result.carbon_impact;
      } else if (activityType === 'Home') {
        const result = await activitiesApi.calculateHomeEnergyImpact(100, 'electricity'); // Example values
        impact = result.carbon_impact;
      }

      await activitiesApi.create({
        activity_type: activityType.toLowerCase(),
        description: `New ${activityType.toLowerCase()} activity`,
        carbon_impact: impact,
      });

      // Refresh activities
      const newActivities = await activitiesApi.getAll();
      setActivities(newActivities);
    } catch (error) {
      console.error('Failed to create activity:', error);
      alert('Failed to create activity. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <div className="flex items-center space-x-4">
            {userData?.strava_connected ? (
              <span className="text-green-600 font-medium">Connected to Strava ✓</span>
            ) : stravaAuthUrl ? (
              <a
                href={stravaAuthUrl}
                className="text-blue-600 hover:text-blue-800 font-medium"
              >
                Connect Strava
              </a>
            ) : (
              <span>Loading Strava...</span>
            )}
            <div className="flex items-center space-x-2">
              <Leaf className="text-green-600 h-5 w-5" />
              <span className="text-green-800 font-medium">
                {userData ? `${userData.total_co2_saved || 0} tons CO₂e saved` : 'Loading...'}
              </span>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-800 mb-2">Total Distance</h3>
            <p className="text-2xl font-bold text-green-600">
              {userData ? `${(userData.total_distance || 0).toFixed(1)} km` : '...'}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-800 mb-2">CO₂ Saved</h3>
            <p className="text-2xl font-bold text-green-600">
              {userData ? `${(userData.total_co2_saved || 0).toFixed(1)} tons` : '...'}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-800 mb-2">Points</h3>
            <p className="text-2xl font-bold text-green-600">
              {userData ? userData.points || 0 : '...'}
            </p>
          </div>
        </div>

        {/* Chart */}
        {activities.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Activity History</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="impact" stroke="#059669" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard; 