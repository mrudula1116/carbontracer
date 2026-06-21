# test_calculations.py
import unittest
import calculations

class TestCarbonCalculations(unittest.TestCase):

    def test_home_emissions(self):
        # 100 kWh/month, 50 m3/month gas, 0% clean energy
        # Elec: 100 * 12 * 0.4 = 480
        # Gas: 50 * 12 * 2.02 = 1212
        # Total: 1692
        result = calculations.calculate_home_emissions(100.0, 50.0, 0.0)
        self.assertAlmostEqual(result, 1692.0, places=1)
        
        # With 50% clean energy
        # Elec: 100 * 12 * 0.4 * 0.5 = 240
        # Gas: 1212
        # Total: 1452
        result_clean = calculations.calculate_home_emissions(100.0, 50.0, 50.0)
        self.assertAlmostEqual(result_clean, 1452.0, places=1)

    def test_transport_emissions(self):
        # Petrol car, 100 km/week car, 50 km/week transit, 2 short flights, 1 long flight
        # Car: 100 * 52 * 0.192 = 998.4
        # Transit: 50 * 52 * 0.052 = 135.2
        # Flights: 2 * 300 + 1 * 1800 = 2400
        # Total: 3533.6
        result = calculations.calculate_transport_emissions(
            "Petrol (Gasoline)", 100.0, 50.0, 2, 1
        )
        self.assertAlmostEqual(result, 3533.6, places=1)
        
        # Test no car
        result_no_car = calculations.calculate_transport_emissions(
            "None", 0.0, 100.0, 0, 0
        )
        # Transit: 100 * 52 * 0.052 = 270.4
        self.assertAlmostEqual(result_no_car, 270.4, places=1)

    def test_diet_emissions(self):
        self.assertEqual(calculations.calculate_diet_emissions("Vegan"), 1500.0)
        self.assertEqual(calculations.calculate_diet_emissions("Vegetarian"), 1700.0)
        self.assertEqual(calculations.calculate_diet_emissions("Average Meat Eater"), 2500.0)
        self.assertEqual(calculations.calculate_diet_emissions("Meat Heavy"), 3300.0)

    def test_waste_emissions(self):
        # Household size 1, no recycling
        # Base: 400 kg, Landfill factor: 0.5
        # Total: 200 kg CO2e
        result = calculations.calculate_waste_emissions(1, False, False, False, False, False)
        self.assertAlmostEqual(result, 200.0, places=1)
        
        # Household size 2, recycles paper (15%) and plastic (10%)
        # Base: 2 * 400 = 800 kg. Reduction = 25%. Net waste = 600 kg.
        # User share = 600 / 2 = 300 kg. Landfill = 300 * 0.5 = 150 kg CO2e
        result_recycled = calculations.calculate_waste_emissions(2, True, True, False, False, False)
        self.assertAlmostEqual(result_recycled, 150.0, places=1)

    def test_total_footprint(self):
        res = calculations.calculate_total_footprint(1000.0, 2000.0, 1500.0, 150.0)
        self.assertEqual(res["home_t"], 1.0)
        self.assertEqual(res["transport_t"], 2.0)
        self.assertEqual(res["diet_t"], 1.5)
        self.assertEqual(res["waste_t"], 0.15)
        self.assertEqual(res["total_t"], 4.65)
    def test_negative_home_input(self):

     with self.assertRaises(ValueError):

        calculations.calculate_home_emissions(
            -100,
            50,
            0
        )
    def test_invalid_clean_energy(self):

      with self.assertRaises(ValueError):

        calculations.calculate_home_emissions(
            100,
            50,
            120
        )
    def test_invalid_vehicle(self):

     with self.assertRaises(ValueError):

        calculations.calculate_transport_emissions(
            "Spaceship",
            100,
            50,
            0,
            0
        )
    def test_invalid_diet(self):

     with self.assertRaises(ValueError):

        calculations.calculate_diet_emissions(
            "Alien Diet"
        )
if __name__ == "__main__":
    unittest.main()
