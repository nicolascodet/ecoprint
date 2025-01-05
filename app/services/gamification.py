from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class Achievement:
    id: str
    name: str
    description: str
    points: int
    icon: str

@dataclass
class OpportunityCost:
    co2_saved: float
    trees_equivalent: float
    car_trips_avoided: float

class GamificationService:
    def __init__(self):
        self.achievements = {
            "distance_1": Achievement(
                id="distance_1",
                name="First Mile",
                description="Travel your first mile with green transport",
                points=100,
                icon="🌱"
            ),
            "distance_10": Achievement(
                id="distance_10",
                name="Green Explorer",
                description="Travel 10 miles with green transport",
                points=500,
                icon="🚲"
            ),
            "co2_saved_10": Achievement(
                id="co2_saved_10",
                name="Climate Champion",
                description="Save 10kg of CO2 emissions",
                points=1000,
                icon="🌍"
            )
        }

    def calculate_points(self, distance: float, duration: int, transport_mode: str) -> int:
        """Calculate points for an activity."""
        base_points = int(distance * 10)  # 10 points per meter
        
        # Bonus points for eco-friendly transport
        if transport_mode in ["WALKING", "RUNNING"]:
            base_points *= 2
        elif transport_mode == "CYCLING":
            base_points *= 1.5
            
        return base_points

    def calculate_opportunity_cost(self, distance: float, transport_mode: str) -> OpportunityCost:
        """Calculate environmental impact savings."""
        # Average car CO2 emissions: 200g/km
        car_emissions_per_km = 0.2
        
        if transport_mode in ["WALKING", "RUNNING", "CYCLING"]:
            co2_saved = distance * car_emissions_per_km
        else:
            co2_saved = 0
            
        return OpportunityCost(
            co2_saved=co2_saved,
            trees_equivalent=co2_saved / 20,  # 1 tree absorbs ~20kg CO2 per year
            car_trips_avoided=distance / 5  # Average car trip is 5km
        )

    def check_achievements(self, stats: Dict[str, float]) -> List[Achievement]:
        """Check for new achievements based on user stats."""
        new_achievements = []
        
        if stats["total_distance"] >= 1.6:  # 1 mile
            new_achievements.append(self.achievements["distance_1"])
            
        if stats["total_distance"] >= 16:  # 10 miles
            new_achievements.append(self.achievements["distance_10"])
            
        if stats["total_co2_saved"] >= 10:  # 10kg CO2
            new_achievements.append(self.achievements["co2_saved_10"])
            
        return new_achievements

    def get_motivational_message(self, impact: OpportunityCost) -> str:
        """Generate a motivational message based on impact."""
        if impact.co2_saved > 0:
            return (
                f"Great job! You saved {impact.co2_saved:.1f}kg of CO2, "
                f"equivalent to {impact.trees_equivalent:.1f} trees absorbing CO2 for a year. "
                f"Keep up the green transport!"
            )
        return "Every green journey counts! Keep making sustainable choices." 