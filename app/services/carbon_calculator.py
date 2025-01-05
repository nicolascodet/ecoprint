class CarbonCalculator:
    @staticmethod
    def calculate_transport_impact(distance: float, mode: str) -> float:
        """Calculate carbon impact for different transport modes."""
        impact_factors = {
            "car": 0.2,  # kg CO2 per km
            "bus": 0.08,
            "train": 0.04,
            "bike": 0,
            "walk": 0
        }
        return distance * impact_factors.get(mode, 0.2)

    @staticmethod
    def calculate_home_energy_impact(energy_kwh: float, energy_type: str) -> float:
        """Calculate carbon impact for home energy use."""
        impact_factors = {
            "electricity": 0.5,  # kg CO2 per kWh
            "natural_gas": 0.2,
            "renewable": 0
        }
        return energy_kwh * impact_factors.get(energy_type, 0.5)
