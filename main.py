from typing import Dict, List, Any
from model_operations import BaseModelOperations, DroneOperations, CameraOperations, PremiumAdjustments
from data_loader import get_example_data
import json

#
# Starter code for Modelling Case Study Exercise
#

def compute_model(model_data: Dict[str, Any]) -> None:
    """
    Computes the model calculations based on the provided model data.
    Args:
        model_data (Dict[str, Any]): provided data.
    """
    model_operations = BaseModelOperations()
    drone_operations = DroneOperations()
    camera_operations = CameraOperations(drone_operations)

    # DRONES
    drones: List[Dict[str, Any]] = model_data.get("drones", [])
    for drone in drones:
        drone['hull_base_rate'] = drone_operations.hull_base_rate(drone['value'], in_percentage=True)
        drone['hull_weight_adjustment'] = drone_operations.hull_weight_adj(drone['value'], drone['weight'])
        
        hull_final_rate = drone_operations.hull_final_rate(drone['value'], drone['weight'], in_percentage=True)
        drone['hull_final_rate'] = round(hull_final_rate, 1)
        
        drone['hull_premium'] = drone_operations.calculate_premium(drone['hull_final_rate'], drone['value'])
        drone['tpl_base_rate'] = drone_operations.tpl_base_rate(drone['value'], in_percentage=True)
        drone['tpl_base_layer_premium'] = drone_operations.tpl_base_layer_premium(drone['value'])
        
        tpl_ilf =  drone_operations.tpl_ilf(drone['value'], drone['tpl_limit'], drone['tpl_excess'])
        drone['tpl_ilf'] = round(tpl_ilf, 2)
        
        tpl_layer_premium = drone_operations.tpl_layer_premium(drone['value'], drone['tpl_limit'], drone['tpl_excess'])
        drone['tpl_layer_premium'] = round(tpl_layer_premium, 0)
        
    # CAMERAS
    cameras: List[Dict[str, Any]] = model_data.get("detachable_cameras", [])
    highest_drone_rate: float = camera_operations.rate(drones, in_percentage=True)
    for camera in cameras:
        camera['hull_rate'] = round(highest_drone_rate, 1)
        camera['hull_premium'] = camera_operations.calculate_premium(highest_drone_rate, camera['value'])
        
    # calculate net totals
    net_premium: Dict[str, Any] = model_data.get("net_prem", {})
    net_premium["drones_hull"] = drone_operations.calculate_total_net(drones, insurance_type='hull_premium')
    net_premium["drones_tpl"] = drone_operations.calculate_total_net(drones, insurance_type='tpl_layer_premium')
    net_premium["cameras_hull"] = camera_operations.calculate_total_net(cameras, insurance_type='hull_premium')
    
    net_sum: List[float] = [value for value in net_premium.values() if isinstance(value, (int, float))]
    net_premium["total"] = model_operations.calculate_premium_total(net_sum)
   
    # calculate gross totals
    gross_premium: Dict[str, Any] = model_data.get("gross_prem", {})
    brokerage: float = model_data['brokerage']
    gross_premium["drones_hull"] = drone_operations.calculate_total_gross(drones, brokerage, insurance_type='hull_premium')
    gross_premium["drones_tpl"] = drone_operations.calculate_total_gross(drones, brokerage, insurance_type='tpl_layer_premium')
    gross_premium["cameras_hull"] = camera_operations.calculate_total_gross(cameras, brokerage, insurance_type='hull_premium')
    
    gross_sum: List[float] = [value for value in gross_premium.values() if isinstance(value, (int, float))]
    gross_premium["total"] = model_operations.calculate_premium_total(gross_sum)
    
    
def main(apply_adjustments: bool = False) -> str:
    """
    Performs the rating calculations and returns the result as a JSON string.
    Returns:
        str: The JSON-formatted string of the model data after computations.
    """
    # Get the example data
    model_data: Dict[str, Any] = get_example_data()
    drones: List[Dict[str, Any]] = model_data.get("drones", [])
    cameras: List[Dict[str, Any]] = model_data.get("detachable_cameras", [])
    max_drones_in_air: int = model_data.get("max_drones_in_air", None)
    
    # Compute initial rating calculations
    compute_model(model_data)
    
    # Apply extensions for drones
    if apply_adjustments:
        PremiumAdjustments.limited_drones_in_use(drones, max_drones_in_air)

        # Apply extensions for cameras
        PremiumAdjustments.limited_cameras_in_use(cameras, max_drones_in_air, drones)
    
    return json.dumps(model_data, indent=2)
    
# Run the model
if __name__ == '__main__':
    print(main(apply_adjustments=True))