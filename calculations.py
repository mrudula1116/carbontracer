# calculations.py
"""
Carbon emission calculation logic based on standard factors (EPA, Defra, and standard studies).
All emission outputs are in kg CO2e (carbon dioxide equivalent) per year.
"""

# Emission Factors (in kg CO2e per unit)
EMISSION_FACTORS = {
    # Home Energy
    "electricity_per_kwh": 0.40,  # kg CO2e per kWh
    "gas_per_m3": 2.02,           # kg CO2e per cubic meter
    
    # Transport (per km)
    "car_petrol": 0.192,
    "car_diesel": 0.171,
    "car_hybrid": 0.109,
    "car_electric": 0.053,
    "public_transit": 0.052,      # Average bus/train per passenger-km
    
    # Flights (per flight, round-trip)
    "flight_short": 300.0,        # ~1500 km roundtrip
    "flight_long": 1800.0,        # ~12000 km roundtrip
    
    # Diet (annual kg CO2e per person)
    "diet_heavy_meat": 3300.0,
    "diet_average_meat": 2500.0,
    "diet_vegetarian": 1700.0,
    "diet_vegan": 1500.0,
    
    # Waste (annual base kg per person)
    "waste_per_capita_kg": 400.0,
    "waste_landfill_factor": 0.5, # kg CO2e per kg waste
}

# National / Global Benchmarks for Comparison (Annual metric tons CO2e per capita)
BENCHMARKS = {
    "US Average": 16.0,
    "UK Average": 6.5,
    "EU Average": 7.0,
    "Global Average": 4.7,
    "Target (to combat warming)": 2.0
}

def calculate_home_emissions(electricity_kwh_per_month: float, 
                             gas_m3_per_month: float, 
                             clean_energy_pct: float) -> float:
    """
    Calculates annual home energy emissions in kg CO2e.
    """
    annual_electricity = electricity_kwh_per_month * 12
    # Adjust for clean energy percentage (solar panels or green tariff)
    adjusted_electricity = annual_electricity * (1.0 - (clean_energy_pct / 100.0))
    elec_emissions = adjusted_electricity * EMISSION_FACTORS["electricity_per_kwh"]
    
    gas_emissions = (gas_m3_per_month * 12) * EMISSION_FACTORS["gas_per_m3"]
    return elec_emissions + gas_emissions

def calculate_transport_emissions(vehicle_type: str, 
                                  weekly_car_km: float, 
                                  weekly_transit_km: float, 
                                  short_flights: int, 
                                  long_flights: int) -> float:
    """
    Calculates annual travel and transport emissions in kg CO2e.
    """
    # Car emissions
    car_factor = 0.0
    if vehicle_type == "Petrol (Gasoline)":
        car_factor = EMISSION_FACTORS["car_petrol"]
    elif vehicle_type == "Diesel":
        car_factor = EMISSION_FACTORS["car_diesel"]
    elif vehicle_type == "Hybrid":
        car_factor = EMISSION_FACTORS["car_hybrid"]
    elif vehicle_type == "Electric":
        car_factor = EMISSION_FACTORS["car_electric"]
    else:
        car_factor = 0.0 # No car / None
        
    annual_car_km = weekly_car_km * 52
    car_emissions = annual_car_km * car_factor
    
    # Public transit emissions
    annual_transit_km = weekly_transit_km * 52
    transit_emissions = annual_transit_km * EMISSION_FACTORS["public_transit"]
    
    # Flights emissions
    flight_emissions = (short_flights * EMISSION_FACTORS["flight_short"]) + \
                       (long_flights * EMISSION_FACTORS["flight_long"])
                       
    return car_emissions + transit_emissions + flight_emissions

def calculate_diet_emissions(diet_type: str) -> float:
    """
    Calculates annual diet emissions in kg CO2e.
    """
    if diet_type == "Meat Heavy":
        return EMISSION_FACTORS["diet_heavy_meat"]
    elif diet_type == "Average Meat Eater":
        return EMISSION_FACTORS["diet_average_meat"]
    elif diet_type == "Vegetarian":
        return EMISSION_FACTORS["diet_vegetarian"]
    elif diet_type == "Vegan":
        return EMISSION_FACTORS["diet_vegan"]
    return EMISSION_FACTORS["diet_average_meat"]

def calculate_waste_emissions(household_size: int, 
                              recycles_paper: bool, 
                              recycles_plastic: bool, 
                              recycles_glass: bool, 
                              recycles_metal: bool, 
                              composts: bool) -> float:
    """
    Calculates annual waste emissions in kg CO2e.
    """
    # Baseline waste per household
    baseline_waste = household_size * EMISSION_FACTORS["waste_per_capita_kg"]
    
    # Calculate recycling reduction factor
    reduction = 0.0
    if recycles_paper:
        reduction += 0.15
    if recycles_plastic:
        reduction += 0.10
    if recycles_glass:
        reduction += 0.10
    if recycles_metal:
        reduction += 0.10
    if composts:
        reduction += 0.20
        
    # Cap reduction at 65% for realistic limits
    reduction = min(reduction, 0.65)
    
    net_waste = baseline_waste * (1.0 - reduction)
    # Assume 1/household size is the user's individual portion
    user_waste = net_waste / max(1, household_size) 
    
    return user_waste * EMISSION_FACTORS["waste_landfill_factor"]

def calculate_total_footprint(home_emissions: float, 
                              transport_emissions: float, 
                              diet_emissions: float, 
                              waste_emissions: float) -> dict:
    """
    Aggregates emissions and converts to metric tons CO2e.
    """
    total_kg = home_emissions + transport_emissions + diet_emissions + waste_emissions
    return {
        "home_t": home_emissions / 1000.0,
        "transport_t": transport_emissions / 1000.0,
        "diet_t": diet_emissions / 1000.0,
        "waste_t": waste_emissions / 1000.0,
        "total_t": total_kg / 1000.0
    }
