from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
from app.services.carbon_calculator import CarbonCalculator
import aiohttp
import asyncio
from dataclasses import dataclass
from enum import Enum

# Add milestone definitions
MILESTONES = {
    "carbon_saved": [
        {"amount": 1, "title": "Carbon Saver Rookie", "message": "Saved your first kg of CO2!"},
        {"amount": 5, "title": "Earth Guardian", "message": "Saved 5kg of CO2!"},
        {"amount": 10, "title": "Climate Champion", "message": "Saved 10kg of CO2!"},
        {"amount": 50, "title": "Planet Protector", "message": "Saved 50kg of CO2!"},
        {"amount": 100, "title": "Carbon Warrior", "message": "Saved 100kg of CO2!"},
    ],
    "green_trips": [
        {"amount": 1, "title": "First Green Trip", "message": "Completed your first eco-friendly trip!"},
        {"amount": 10, "title": "Green Explorer", "message": "10 eco-friendly trips completed!"},
        {"amount": 50, "title": "Sustainable Voyager", "message": "50 eco-friendly trips - you're on a roll!"},
    ],
    "streaks": [
        {"amount": 3, "title": "Green Streak", "message": "3 days in a row of eco-friendly travel!"},
        {"amount": 7, "title": "Weekly Warrior", "message": "A full week of green trips!"},
        {"amount": 30, "title": "Monthly Master", "message": "30 days of sustainable choices!"},
    ]
}

class TransportMode(Enum):
    STILL = "still"
    WALKING = "walk"
    RUNNING = "run"
    BIKING = "bike"
    BUS = "bus"
    TRAIN = "train"
    CAR = "car"
    FLIGHT = "flight"

@dataclass
class Trip:
    start_time: datetime
    start_location: Dict
    transport_mode: TransportMode
    locations: List[Dict]
    distance: float = 0
    carbon_impact: float = 0
    is_active: bool = True
    route_details: Dict = None
    predicted_impact: float = 0
    eco_alternatives: List[Dict] = None

@dataclass
class UserStats:
    total_carbon_saved: float = 0
    green_trips_count: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    last_activity_date: Optional[datetime] = None
    achieved_milestones: List[Dict] = None
    
    def __post_init__(self):
        self.achieved_milestones = []

class ActivityTracker:
    def __init__(self):
        self.carbon_calculator = CarbonCalculator()
        self.current_trip: Optional[Trip] = None
        self.trips: List[Trip] = []
        self.TRIP_END_THRESHOLD = timedelta(minutes=5)
        self.last_update = None
        self.common_routes = {}
        self.user_stats: Dict[int, UserStats] = {}  # user_id -> UserStats
        
    def get_user_stats(self, user_id: int) -> UserStats:
        if user_id not in self.user_stats:
            self.user_stats[user_id] = UserStats()
        return self.user_stats[user_id]
        
    def update_user_stats(self, user_id: int, trip_data: Dict) -> Optional[Dict]:
        """Update user stats and check for new milestones."""
        stats = self.get_user_stats(user_id)
        current_date = datetime.now().date()
        
        # Update carbon saved
        carbon_saved = trip_data["carbon_impact"]
        if trip_data["transport_mode"] in ["walk", "bike", "run"]:
            stats.green_trips_count += 1
            # Extra carbon saved for choosing green transport
            carbon_saved += self.carbon_calculator.calculate_transport_impact(
                trip_data["distance"] / 1000,
                "car"  # Compare to if they had driven
            )
        
        stats.total_carbon_saved += carbon_saved
        
        # Update streak
        if stats.last_activity_date:
            if stats.last_activity_date.date() == current_date - timedelta(days=1):
                stats.current_streak += 1
                stats.longest_streak = max(stats.current_streak, stats.longest_streak)
            elif stats.last_activity_date.date() != current_date:
                stats.current_streak = 1
        else:
            stats.current_streak = 1
            
        stats.last_activity_date = datetime.now()
        
        # Check for new milestones
        new_milestones = []
        
        # Carbon saved milestones
        for milestone in MILESTONES["carbon_saved"]:
            if (milestone["amount"] <= stats.total_carbon_saved and 
                milestone not in stats.achieved_milestones):
                new_milestone = {**milestone, "type": "carbon_saved"}
                stats.achieved_milestones.append(new_milestone)
                new_milestones.append(new_milestone)
        
        # Green trips milestones
        for milestone in MILESTONES["green_trips"]:
            if (milestone["amount"] <= stats.green_trips_count and 
                milestone not in stats.achieved_milestones):
                new_milestone = {**milestone, "type": "green_trips"}
                stats.achieved_milestones.append(new_milestone)
                new_milestones.append(new_milestone)
        
        # Streak milestones
        for milestone in MILESTONES["streaks"]:
            if (milestone["amount"] <= stats.current_streak and 
                milestone not in stats.achieved_milestones):
                new_milestone = {**milestone, "type": "streaks"}
                stats.achieved_milestones.append(new_milestone)
                new_milestones.append(new_milestone)
        
        if new_milestones:
            return {
                "new_milestones": new_milestones,
                "stats_update": {
                    "total_carbon_saved": stats.total_carbon_saved,
                    "green_trips": stats.green_trips_count,
                    "current_streak": stats.current_streak,
                    "longest_streak": stats.longest_streak
                }
            }
        return None
        
    def get_impact_report(self, user_id: int, period: str = "weekly") -> Dict:
        """Generate impact report for different time periods."""
        stats = self.get_user_stats(user_id)
        now = datetime.now()
        
        # Filter trips for the specified period
        if period == "daily":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            title = "Today's Impact"
        elif period == "weekly":
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            title = "This Week's Impact"
        else:  # monthly
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            title = "This Month's Impact"
            
        period_trips = [
            trip for trip in self.trips 
            if trip.start_time >= start_date and 
            trip.transport_mode.value in ["walk", "bike", "run"]
        ]
        
        # Calculate impact
        total_distance = sum(trip.distance for trip in period_trips)
        carbon_saved = sum(
            self.carbon_calculator.calculate_transport_impact(
                trip.distance / 1000,
                "car"  # Compare to if they had driven
            )
            for trip in period_trips
        )
        
        # Get achievements for the period
        period_achievements = [
            m for m in stats.achieved_milestones
            if datetime.fromisoformat(m.get("achieved_at", now.isoformat())) >= start_date
        ]
        
        return {
            "title": title,
            "period": period,
            "stats": {
                "total_distance": total_distance,
                "carbon_saved": carbon_saved,
                "green_trips": len(period_trips),
                "achievements": period_achievements
            },
            "summary": f"You've saved {carbon_saved:.1f}kg of CO2 through {len(period_trips)} green trips!",
            "streak": {
                "current": stats.current_streak,
                "longest": stats.longest_streak
            }
        }

    async def process_location_update(self, location_data: Dict) -> Optional[Dict]:
        """Process location updates to detect and track trips."""
        current_time = datetime.fromisoformat(location_data["timestamp"].replace('Z', '+00:00'))
        
        # Convert speed from m/s to km/h for better readability
        speed_kmh = location_data.get("speed", 0) * 3.6
        
        # Detect transport mode
        transport_mode = await self._detect_transport_mode(
            location_data["activity_type"],
            speed_kmh,
            location_data
        )
        
        # If starting a new trip, predict impact
        if not self.current_trip and transport_mode != TransportMode.STILL:
            predicted_data = self._predict_trip_impact(location_data)
            if predicted_data:
                return {
                    "message": "Trip started",
                    "prediction": {
                        "likely_destination": predicted_data["destination"],
                        "estimated_distance": predicted_data["distance"],
                        "estimated_carbon": predicted_data["carbon_impact"],
                        "eco_alternatives": predicted_data["alternatives"]
                    }
                }
        
        # Handle trip start/end/update
        activity = await self._handle_trip_state(location_data, transport_mode, current_time)
        
        self.last_update = current_time
        return activity
    
    async def _detect_transport_mode(self, activity_type: str, speed_kmh: float, location: Dict) -> TransportMode:
        """Enhanced transport mode detection using multiple data points."""
        # Speed thresholds in km/h
        SPEED_THRESHOLDS = {
            "WALKING": 7,
            "RUNNING": 15,
            "BIKING": 30,
            "TRAIN": 150,
            "FLIGHT": 250
        }
        
        if activity_type == "STILL" or speed_kmh < 1:
            return TransportMode.STILL
            
        # Flight detection (high altitude or speed)
        if location.get("altitude", 0) > 1000 or speed_kmh > SPEED_THRESHOLDS["FLIGHT"]:
            return TransportMode.FLIGHT
            
        # Train detection (consistent high speed, follows train tracks)
        if speed_kmh > SPEED_THRESHOLDS["TRAIN"]:
            # TODO: Add train track proximity check using Google Maps API
            return TransportMode.TRAIN
            
        # Basic movement detection
        if speed_kmh <= SPEED_THRESHOLDS["WALKING"]:
            return TransportMode.WALKING
        elif speed_kmh <= SPEED_THRESHOLDS["RUNNING"]:
            return TransportMode.RUNNING
        elif speed_kmh <= SPEED_THRESHOLDS["BIKING"]:
            return TransportMode.BIKING
        
        # Vehicle detection
        if activity_type == "IN_VEHICLE":
            # TODO: Add bus route proximity check
            return TransportMode.CAR
            
        return TransportMode.CAR  # Default to car if unsure
    
    async def _handle_trip_state(self, location_data: Dict, transport_mode: TransportMode, current_time: datetime) -> Optional[Dict]:
        """Handle trip state changes and updates."""
        if transport_mode == TransportMode.STILL:
            return await self._handle_stationary_update(current_time)
            
        location = {
            "lat": location_data["latitude"],
            "lng": location_data["longitude"],
            "timestamp": current_time,
            "speed": location_data.get("speed", 0),
            "altitude": location_data.get("altitude", 0)
        }
        
        if not self.current_trip:
            # Start new trip
            self.current_trip = Trip(
                start_time=current_time,
                start_location=location,
                transport_mode=transport_mode,
                locations=[location]
            )
            return None
            
        # Update existing trip
        if transport_mode != self.current_trip.transport_mode:
            # Mode of transport changed - end current trip and start new one
            completed_trip = await self._end_current_trip(current_time)
            self.current_trip = Trip(
                start_time=current_time,
                start_location=location,
                transport_mode=transport_mode,
                locations=[location]
            )
            return completed_trip
            
        # Update current trip
        distance = self._calculate_distance(
            self.current_trip.locations[-1]["lat"],
            self.current_trip.locations[-1]["lng"],
            location["lat"],
            location["lng"]
        )
        
        self.current_trip.distance += distance
        self.current_trip.locations.append(location)
        
        # Update carbon impact
        self.current_trip.carbon_impact = self.carbon_calculator.calculate_transport_impact(
            self.current_trip.distance / 1000,  # Convert to kilometers
            self.current_trip.transport_mode.value
        )
        
        return None
    
    async def _handle_stationary_update(self, current_time: datetime) -> Optional[Dict]:
        """Handle updates when user is stationary."""
        if not self.current_trip:
            return None
            
        # Check if we should end the current trip
        if current_time - self.last_update > self.TRIP_END_THRESHOLD:
            return await self._end_current_trip(current_time)
            
        return None
    
    async def _end_current_trip(self, end_time: datetime) -> Dict:
        """End current trip and return trip data."""
        if not self.current_trip:
            return None
            
        # Get route details from Google Maps
        route_details = await self._get_route_details(
            self.current_trip.locations[0],
            self.current_trip.locations[-1],
            self.current_trip.transport_mode
        )
        
        trip_data = {
            "activity_type": "transport",
            "transport_mode": self.current_trip.transport_mode.value,
            "distance": self.current_trip.distance,
            "carbon_impact": self.current_trip.carbon_impact,
            "start_time": self.current_trip.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "start_location": self.current_trip.start_location,
            "end_location": self.current_trip.locations[-1],
            "route_details": route_details,
            "waypoints": self.current_trip.locations
        }
        
        self.trips.append(self.current_trip)
        self.current_trip = None
        return trip_data
    
    async def _get_route_details(self, start: Dict, end: Dict, mode: TransportMode) -> Dict:
        """Get route details from Google Maps API."""
        # TODO: Implement Google Maps API integration
        return {
            "estimated_distance": self.current_trip.distance,
            "estimated_duration": None,
            "route_type": mode.value
        }
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in meters using Haversine formula."""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371000  # Earth's radius in meters
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c
        
        return distance 
    
    def _predict_trip_impact(self, start_location: Dict) -> Optional[Dict]:
        """Predict trip details based on historical data and current time."""
        # Find similar trips from history
        similar_trips = self._find_similar_trips(start_location)
        if not similar_trips:
            return None
            
        # Get most likely destination and transport mode
        likely_trip = max(similar_trips, key=lambda t: t["frequency"])
        
        # Calculate estimated impact
        estimated_distance = likely_trip["distance"]
        estimated_carbon = self.carbon_calculator.calculate_transport_impact(
            estimated_distance / 1000,
            likely_trip["transport_mode"]
        )
        
        # Generate eco-friendly alternatives
        alternatives = self._generate_alternatives(
            estimated_distance,
            likely_trip["transport_mode"]
        )
        
        return {
            "destination": likely_trip["end_location"],
            "distance": estimated_distance,
            "carbon_impact": estimated_carbon,
            "alternatives": alternatives
        }
    
    def _find_similar_trips(self, start_location: Dict) -> List[Dict]:
        """Find similar trips based on starting point and time of day."""
        similar_trips = []
        current_hour = datetime.fromisoformat(start_location["timestamp"].replace('Z', '+00:00')).hour
        
        for route, data in self.common_routes.items():
            start_lat, start_lng = map(float, route.split('|')[0].split(','))
            if self._is_nearby(start_lat, start_lng, start_location["lat"], start_location["lng"]):
                # Check if this is a common time for this route
                if current_hour in data["common_hours"]:
                    similar_trips.append({
                        "end_location": data["end_location"],
                        "distance": data["avg_distance"],
                        "transport_mode": data["common_mode"],
                        "frequency": data["frequency"]
                    })
        
        return similar_trips
    
    def _generate_alternatives(self, distance: float, current_mode: str) -> List[Dict]:
        """Generate eco-friendly alternative transport options."""
        alternatives = []
        
        # Only suggest alternatives for car trips
        if current_mode == "car":
            if distance <= 5000:  # 5km
                alternatives.append({
                    "mode": "bike",
                    "carbon_impact": 0,
                    "health_benefit": "15-20 minutes of exercise"
                })
            if distance <= 2000:  # 2km
                alternatives.append({
                    "mode": "walk",
                    "carbon_impact": 0,
                    "health_benefit": "20-25 minutes of exercise"
                })
            # Always suggest public transport if available
            alternatives.append({
                "mode": "bus",
                "carbon_impact": self.carbon_calculator.calculate_transport_impact(
                    distance / 1000,
                    "bus"
                ),
                "carbon_saved": self.carbon_calculator.calculate_transport_impact(
                    distance / 1000,
                    "car"
                ) - self.carbon_calculator.calculate_transport_impact(
                    distance / 1000,
                    "bus"
                )
            })
        
        return alternatives
    
    def _is_nearby(self, lat1: float, lon1: float, lat2: float, lon2: float, threshold: float = 100) -> bool:
        """Check if two points are within threshold meters of each other."""
        distance = self._calculate_distance(lat1, lon1, lat2, lon2)
        return distance <= threshold
    
    def _update_common_routes(self, trip: Trip):
        """Update common routes database with completed trip."""
        start_key = f"{trip.start_location['lat']},{trip.start_location['lng']}"
        end_key = f"{trip.locations[-1]['lat']},{trip.locations[-1]['lng']}"
        route_key = f"{start_key}|{end_key}"
        
        if route_key not in self.common_routes:
            self.common_routes[route_key] = {
                "end_location": trip.locations[-1],
                "avg_distance": trip.distance,
                "common_mode": trip.transport_mode.value,
                "frequency": 1,
                "common_hours": set([trip.start_time.hour])
            }
        else:
            data = self.common_routes[route_key]
            data["frequency"] += 1
            data["avg_distance"] = (data["avg_distance"] * (data["frequency"] - 1) + trip.distance) / data["frequency"]
            data["common_hours"].add(trip.start_time.hour)
            
            # Update most common transport mode
            if trip.transport_mode.value != data["common_mode"]:
                # TODO: Implement mode frequency tracking
                pass

    # ... (keep existing methods) ... 