import unittest
from model_operations import DroneOperations, CameraOperations, PremiumAdjustments

class TestOperations(unittest.TestCase):

    def setUp(self):
        # Initialize operations
        self.drone_operations = DroneOperations()
        self.camera_operations = CameraOperations()

        # Mock parameters (these comes from config.json in actual use)
        self.drone_operations._PARAMETERS = {
            'gross_base_rates': {'hull': 0.6, 'liability': 0.2},
            'max_takeoff_weight_adj': {'0 - 5kg': 1, '5 - 10kg': 1.2, '10 - 20kg': 1.6, '>20kg': 2.5},
            'ilf_riebesell_curve': {'base_limit': 1000000, 'z': 0.2}
        }

        # mock data
        self.example_data = {
            "drones": [
                {
                    "serial_number": "AAA-111",
                    "value": 10000,
                    "weight": "0 - 5kg",
                    "has_detachable_camera": True,
                    "tpl_limit": 1000000,      
                    "tpl_excess": 0,
                    "hull_premium": 600,
                    "tpl_layer_premium": 200
                },
                {
                    "serial_number": "BBB-222",
                    "value": 12000,
                    "weight": "10 - 20kg",
                    "has_detachable_camera": False,
                    "tpl_limit":  4000000,   
                    "tpl_excess": 1000000,
                    "hull_premium": 1152,
                    "tpl_layer_premium": 126
                },
                {
                    "serial_number": "AAA-123",
                    "value": 15000,
                    "weight": "5 - 10kg",
                    "has_detachable_camera": True,
                    "tpl_limit": 5000000,
                    "tpl_excess": 5000000,
                    "hull_premium": 1080,
                    "tpl_layer_premium": 92
                }
            ],
            "detachable_cameras": [
                {
                    "serial_number": "ZZZ-999",
                    "value": 5000,
                    "hull_premium": 360
                },
                {
                    "serial_number": "YYY-888",
                    "value": 2500,
                    "hull_premium": 180
                },
                {
                    "serial_number": "XXX-777",
                    "value": 1500,
                    "hull_premium": 108,
                },
                {
                    "serial_number": "WWW-666",
                    "value": 2000,
                    "hull_premium": 144,
                }
            ],
            "brokerage": 0.3
        }

    def test_hull_base_rate(self):
        drone = self.example_data["drones"][0]
        base_rate = self.drone_operations.hull_base_rate(drone['value'])
        self.assertEqual(base_rate, 0.6) 

    def test_hull_weight_adj(self):
        drone = self.example_data["drones"][0]
        weight_adj = self.drone_operations.hull_weight_adj(drone['value'], drone['weight'])
        self.assertEqual(weight_adj, 1) 

    def test_hull_final_rate(self):
        drone = self.example_data["drones"][0]
        final_rate = self.drone_operations.hull_final_rate(drone['value'], drone['weight'])
        self.assertAlmostEqual(final_rate, 0.6, places=2) 

    def test_tpl_ilf(self):
        drone = self.example_data["drones"][0]
        ilf = self.drone_operations.tpl_ilf(drone['value'], drone['tpl_limit'], drone['tpl_excess'])
        self.assertAlmostEqual(ilf, 1.00, places=2) 

    def test_camera_rate(self):
        rate = self.camera_operations.rate(self.example_data["drones"])
        self.assertAlmostEqual(rate, 0.072, places=2) 
        
    def test_limited_drones_in_use(self):
        adjusted_drones = PremiumAdjustments.limited_drones_in_use(self.example_data["drones"], 2)
        # The first drone should get the base premium of 150 since it has the lowest premium
        self.assertEqual(adjusted_drones[0]['hull_premium'], 150)  

    def test_limited_cameras_in_use(self):
        adjusted_cameras = PremiumAdjustments.limited_cameras_in_use(self.example_data["detachable_cameras"], 2, self.example_data["drones"])
        # The third and fourth camera should get the base premium of 50
        self.assertEqual(self.example_data["detachable_cameras"][3]['hull_premium'], 50) and self.assertEqual(self.example_data["detachable_cameras"][2]['hull_premium'], 50)

    def test_calculate_total_net(self):
        # Test total net premiums for drones and cameras
        total_net_hull = self.drone_operations.calculate_total_net(self.example_data["drones"], 'hull')
        self.assertEqual(total_net_hull, 2832)

        total_net_tpl = self.drone_operations.calculate_total_net(self.example_data["drones"], 'tpl')
        self.assertEqual(total_net_tpl, 418) 

        total_net_cameras = self.camera_operations.calculate_total_net(self.example_data["detachable_cameras"], 'hull')
        self.assertEqual(total_net_cameras, 792)

    def test_calculate_total_gross(self):
        # Test total gross premiums for drones and cameras, factoring in brokerage
        brokerage = self.example_data["brokerage"]

        total_gross_hull = self.drone_operations.calculate_total_gross(self.example_data["drones"], brokerage, 'hull')
        expected_gross_hull =  round(2832 / (1 - brokerage), 0)
        self.assertAlmostEqual(total_gross_hull, expected_gross_hull, places=2)

        total_gross_tpl = self.drone_operations.calculate_total_gross(self.example_data["drones"], brokerage, 'tpl')
        expected_gross_tpl = round(418 / (1 - brokerage), 0)
        self.assertAlmostEqual(total_gross_tpl, expected_gross_tpl, places=2)

        total_gross_cameras = self.camera_operations.calculate_total_gross(self.example_data["detachable_cameras"], brokerage, 'hull')
        expected_gross_cameras = round(792 / (1 - brokerage), 0)
        self.assertAlmostEqual(total_gross_cameras, expected_gross_cameras, places=2)

if __name__ == '__main__':
    unittest.main()