# recommendations.py
"""
Data models and functions for carbon footprint reduction suggestions and personalized saving projections.
"""

def get_reduction_actions(user_inputs: dict) -> list:
    """
    Returns a list of actionable steps tailored to user inputs.
    Each item contains details and a formula to estimate the exact kg CO2e saved per year.
    """
    actions = []
    
    # --- Home Energy Actions ---
    electricity_kwh = user_inputs.get("electricity_kwh", 0)
    clean_energy_pct = user_inputs.get("clean_energy_pct", 0)
    gas_m3 = user_inputs.get("gas_m3", 0)
    
    # 1. Switch to Renewable Energy
    if clean_energy_pct < 100:
        potential_savings = (electricity_kwh * 12 * 0.40) * (1.0 - (clean_energy_pct / 100.0))
        if potential_savings > 10:
            actions.append({
                "id": "switch_renewables",
                "category": "Home Energy",
                "title": "Switch to a 100% Green Energy Tariff",
                "description": "Switch your home electricity supply to a certified renewable supplier or install solar panels.",
                "potential_savings_kg": round(potential_savings),
                "difficulty": "Medium"
            })
            
    # 2. LED Lighting
    actions.append({
        "id": "led_bulbs",
        "category": "Home Energy",
        "title": "Replace Old Bulbs with LEDs",
        "description": "Replacing 10 incandescent bulbs with LEDs saves energy and lasts up to 25 times longer.",
        "potential_savings_kg": 150,
        "difficulty": "Easy"
    })
    
    # 3. Thermostat Adjustment
    if gas_m3 > 0:
        gas_savings = (gas_m3 * 12 * 2.02) * 0.10  # 10% saving on heating
        actions.append({
            "id": "thermostat_down",
            "category": "Home Energy",
            "title": "Lower Thermostat by 1°C",
            "description": "Turning down the temperature by just 1°C (or 2°F) reduces your space heating footprint by about 10%.",
            "potential_savings_kg": round(gas_savings) if gas_savings > 0 else 180,
            "difficulty": "Easy"
        })
        
    # 4. Energy Efficient Appliances
    actions.append({
        "id": "efficient_appliances",
        "category": "Home Energy",
        "title": "Upgrade to Energy-Star Appliances",
        "description": "When replacing refrigerators, washing machines, or dishwashers, opt for top energy-rated models.",
        "potential_savings_kg": 120,
        "difficulty": "Hard"
    })

    # --- Transport Actions ---
    weekly_car_km = user_inputs.get("weekly_car_km", 0)
    vehicle_type = user_inputs.get("vehicle_type", "None")
    weekly_transit_km = user_inputs.get("weekly_transit_km", 0)
    short_flights = user_inputs.get("short_flights", 0)
    long_flights = user_inputs.get("long_flights", 0)
    
    # Calculate vehicle emissions
    car_factor = 0.0
    if vehicle_type == "Petrol (Gasoline)":
        car_factor = 0.192
    elif vehicle_type == "Diesel":
        car_factor = 0.171
    elif vehicle_type == "Hybrid":
        car_factor = 0.109
    elif vehicle_type == "Electric":
        car_factor = 0.053
        
    current_annual_car = weekly_car_km * 52 * car_factor
    
    # 1. Commute Smart (Replace 20% car travel with transit or cycling)
    if weekly_car_km > 0:
        transit_replacement_savings = (weekly_car_km * 0.20 * 52 * car_factor) - (weekly_car_km * 0.20 * 52 * 0.052)
        actions.append({
            "id": "active_travel",
            "category": "Transport",
            "title": "Replace 20% of Driving with Cycling/Walking/Transit",
            "description": "Walk, cycle, or take public transit for short trips instead of driving your vehicle.",
            "potential_savings_kg": max(50, round(transit_replacement_savings)),
            "difficulty": "Easy"
        })
        
    # 2. Switch to EV
    if vehicle_type in ["Petrol (Gasoline)", "Diesel", "Hybrid"]:
        ev_savings = current_annual_car - (weekly_car_km * 52 * 0.053)
        if ev_savings > 100:
            actions.append({
                "id": "switch_ev",
                "category": "Transport",
                "title": "Switch to an Electric Vehicle (EV)",
                "description": "If planning to purchase a new car, upgrade to a battery electric vehicle.",
                "potential_savings_kg": round(ev_savings),
                "difficulty": "Hard"
            })
            
    # 3. Work from Home (Reduce car commute by 2 days/week)
    if weekly_car_km > 100:
        wfh_savings = current_annual_car * (2 / 5) * 0.7  # Assume 70% of car travel is commute
        actions.append({
            "id": "wfh_commute",
            "category": "Transport",
            "title": "Work from Home 2 Days per Week",
            "description": "If your job permits, work remotely two days a week to slash commuter fuel consumption.",
            "potential_savings_kg": round(wfh_savings),
            "difficulty": "Medium"
        })
        
    # 4. Reduce Flights
    if short_flights > 0:
        actions.append({
            "id": "reduce_short_flights",
            "category": "Transport",
            "title": "Replace 1 Short-Haul Flight with Train",
            "description": "Take high-speed rail instead of flying for domestic or regional business trips.",
            "potential_savings_kg": 300,
            "difficulty": "Medium"
        })
    if long_flights > 0:
        actions.append({
            "id": "reduce_long_flights",
            "category": "Transport",
            "title": "Cut Down 1 Long-Haul Flight/Year",
            "description": "Consolidate international trips or choose virtual meetings for business travel when possible.",
            "potential_savings_kg": 1800,
            "difficulty": "Hard"
        })

    # --- Diet Actions ---
    diet_type = user_inputs.get("diet_type", "Average Meat Eater")
    
    # 1. Meatless Mondays (Shift 1/7 of meat to vegan/veg)
    if diet_type in ["Meat Heavy", "Average Meat Eater"]:
        meat_to_veg_diff = 2500 - 1700
        savings = meat_to_veg_diff * (1 / 7)
        actions.append({
            "id": "meatless_mondays",
            "category": "Food & Diet",
            "title": "Adopt 'Meatless Mondays'",
            "description": "Commit to one day of entirely plant-based meals per week.",
            "potential_savings_kg": round(savings),
            "difficulty": "Easy"
        })
        
    # 2. Transition Diet
    if diet_type == "Meat Heavy":
        actions.append({
            "id": "diet_to_average",
            "category": "Food & Diet",
            "title": "Reduce Red Meat Consumption",
            "description": "Reduce daily beef, pork, and lamb intake down to average levels. Substitute with poultry or fish.",
            "potential_savings_kg": 800, # 3300 - 2500
            "difficulty": "Easy"
        })
    if diet_type in ["Meat Heavy", "Average Meat Eater"]:
        actions.append({
            "id": "diet_to_vegetarian",
            "category": "Food & Diet",
            "title": "Go Vegetarian",
            "description": "Eliminate meat and fish from your diet entirely, switching to dairy, eggs, and plant alternatives.",
            "potential_savings_kg": 1600 if diet_type == "Meat Heavy" else 800,
            "difficulty": "Medium"
        })
    if diet_type in ["Meat Heavy", "Average Meat Eater", "Vegetarian"]:
        vegan_savings = {
            "Meat Heavy": 1800,
            "Average Meat Eater": 1000,
            "Vegetarian": 200
        }
        actions.append({
            "id": "diet_to_vegan",
            "category": "Food & Diet",
            "title": "Go Vegan (Plant-Based)",
            "description": "Eliminate all animal-derived products (meat, dairy, eggs, honey).",
            "potential_savings_kg": vegan_savings[diet_type],
            "difficulty": "Hard"
        })

    # --- Waste Actions ---
    recycles_paper = user_inputs.get("recycles_paper", False)
    recycles_plastic = user_inputs.get("recycles_plastic", False)
    recycles_glass = user_inputs.get("recycles_glass", False)
    recycles_metal = user_inputs.get("recycles_metal", False)
    composts = user_inputs.get("composts", False)
    
    # Suggest recycling actions not yet adopted
    if not recycles_plastic:
        actions.append({
            "id": "recycle_plastic",
            "category": "Shopping & Waste",
            "title": "Recycle All Household Plastics",
            "description": "Sort and recycle rigid food containers, bottles, and wraps in municipal recycling bins.",
            "potential_savings_kg": 40,
            "difficulty": "Easy"
        })
    if not recycles_paper:
        actions.append({
            "id": "recycle_paper",
            "category": "Shopping & Waste",
            "title": "Recycle Cardboard and Paper Products",
            "description": "Ensure cardboard boxes, newspapers, and packaging are clean, dry, and recycled.",
            "potential_savings_kg": 60,
            "difficulty": "Easy"
        })
    if not composts:
        actions.append({
            "id": "compost_waste",
            "category": "Shopping & Waste",
            "title": "Compost Organic Food Scraps",
            "description": "Use a backyard compost pile or municipal compost bin to prevent food scraps from rotting in landfills.",
            "potential_savings_kg": 80,
            "difficulty": "Medium"
        })
        
    actions.append({
        "id": "reduce_food_waste",
        "category": "Shopping & Waste",
        "title": "Zero Food Waste (Smart Shopping)",
        "description": "Plan meals, use leftovers, and keep track of expiration dates to reduce organic waste.",
        "potential_savings_kg": 50,
        "difficulty": "Easy"
    })
    
    return actions
