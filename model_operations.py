import math
from typing import Any, Callable, List, Dict
from data_loader import load_json

class BaseModelOperations:
    """
    Base class providing common operations among UAVs.
    """

    def __init__(self):
        # load parameters from config
        self._PARAMETERS: Dict[str, Any] = load_json(file_path="config.json")

    @staticmethod
    def _execute_if_not_zero(value: float, callback: Callable[[], Any]) -> Any:
        """
        Executes a callback function if the provided value is not zero.
        Args:
            value (float): The value to check against zero.
            callback (Callable[[], Any]): The function to execute.
        Returns:
            Any: The result of the callback function or an empty string if value is zero.
        """
        # if value == 0:
        #     return ""
        # else:
        #     return callback()
        return callback() if value != 0 else ''

    def calculate_premium(self, final_rate: float, value: float) -> float:
        """
        Calculates the premium based on the final rate and value.
        Args:
            final_rate (float): The final rate to apply.
            value (float): The value of the UAV.
        Returns:
            float: The calculated premium.
        """
        return (
            self._execute_if_not_zero(value, lambda: value * final_rate) / 100
        )  # ()/100 Removes percentage from final rate

    def calculate_total_net(
        self, product_list: List[Dict[str, Any]], insurance_type: str
    ) -> float:
        """
        Calculates total net premium for a list of UAVs.
        Args:
            product_list (List[Dict[str, Any]]): The list of UAVs dictionaries.
            insurance_type (str): The type of insurance ('hull' or 'tpl').
        Returns:
            float: The total net premium.
        """
        return round(sum(product.get(insurance_type, 0) for product in product_list), 0)
        # elif insurance_type == "tpl":
        #     return round(sum(product.get("tpl_layer_premium", []) for product in product_list), 0)

    def calculate_total_gross(
        self, product_list: List[Dict[str, Any]], brokerage: float, insurance_type: str
    ) -> float:
        """
        Calculates total gross premium for a list of UAVs.
        Args:
            product_list (List[Dict[str, Any]]): The list of UAVs dictionaries.
            brokerage (float): The brokerage rate.
            insurance_type (str): The type of insurance ('hull' or 'tpl').
        Returns:
            float: The total gross premium.
        """
        # if insurance_type == "hull":
        hull_net = self.calculate_total_net(product_list, insurance_type)
        return round(hull_net / (1 - brokerage), 0)


    @staticmethod
    def calculate_premium_total(premiums: List[float]) -> float:
        """
        Calculates sum of all premiums in the provided list.
        Args:
            premiums (List[float]): A list of premium amounts.
        Returns:
            float: The sum of all premiums.
        """
        return sum(premiums)


class DroneOperations(BaseModelOperations):
    """
    Provides operations specific to drones for premium calculations.
    """
    def __init__(self):
        super().__init__()

    def hull_base_rate(self, drone_value: float, in_percentage: bool = False) -> float:
        """
        Calculates base rate for hull insurance of a drone.
        Args:
            drone_value (float): The value of the drone.
            in_percentage (bool, optional): return the rate in percentage or not. Defaults to False.
        Returns:
            float: The hull base rate.
        """
        gross_base_rates = self._PARAMETERS.get("gross_base_rates", {})
        base_rate = self._execute_if_not_zero(
            drone_value, lambda: gross_base_rates["hull"]
        )
        return base_rate * 100 if in_percentage else base_rate

    def hull_weight_adj(self, drone_value: float, drone_weight: str) -> float:
        """
        Calculates weight adjustment for hull insurance.
        Args:
            drone_value (float): The value of the drone.
            drone_weight (str): The weight category of the drone.
        Returns:
            float: The hull weight adjustment factor.
        """
        max_takeoff_weight_adj = self._PARAMETERS.get("max_takeoff_weight_adj", {})
        return self._execute_if_not_zero(
            drone_value, lambda: max_takeoff_weight_adj[drone_weight]
        )

    def hull_final_rate(
        self, drone_value: float, drone_weight: str, in_percentage: bool = False
    ) -> float:
        """
        Calculates final hull insurance rate for a drone.
        Args:
            drone_value (float): The value of the drone.
            drone_weight (str): The weight category of the drone.
            in_percentage (bool, optional): Whether to return the rate as a percentage. Defaults to False.
        Returns:
            float: The final hull insurance rate.
        """
        final_rate = self._execute_if_not_zero(
            drone_value,
            lambda: self.hull_base_rate(drone_value)
            * self.hull_weight_adj(drone_value, drone_weight),
        )
        return final_rate * 100 if in_percentage else final_rate

    def __calculate_riesebell(self, base_limit: float, z: float, x: float) -> float:
        """
        Private method to calculate Riebesell curve value.
        Args:
            base_limit (float): base limit value.
            z (float): z parameter for the curve.
            x (float): x value for which to calculate the curve.
        Returns:
            float: result of the calculation.
        """
        return pow((x / base_limit), math.log(1 + z, 2))

    def tpl_base_rate(self, drone_value: float, in_percentage: bool = False) -> float:
        """
        Calculates base rate for TPL insurance of a drone.
        Args:
            drone_value (float): value of the drone.
            in_percentage (bool, optional): Whether to return the rate as a percentage. Defaults to False.
        Returns:
            float: The TPL base rate.
        """
        gross_base_rates = self._PARAMETERS.get("gross_base_rates", {})
        base_rate = self._execute_if_not_zero(
            drone_value, lambda: gross_base_rates["liability"]
        )
        return base_rate * 100 if in_percentage else base_rate

    def tpl_base_layer_premium(self, drone_value: float) -> float:
        """
        Calculates base layer premium for TPL insurance.
        Args:
            drone_value (float): value of the drone.
        Returns:
            float: The TPL base layer premium.
        """
        return self._execute_if_not_zero(
            drone_value, lambda: self.tpl_base_rate(drone_value) * drone_value
        )

    def tpl_ilf(self, drone_value: float, tpl_limit: float, tpl_excess: float) -> float:
        """
        Calculates the ILF for TPL insurance.
        Args:
            drone_value (float): value of the drone.
            tpl_limit (float): TPL limit.
            tpl_excess (float): TPL excess.
        Returns:
            float: The TPL ILF.
        """
        ilf_riebesell_curve = self._PARAMETERS.get("ilf_riebesell_curve", {})
        base_limit = ilf_riebesell_curve["base_limit"]
        z = ilf_riebesell_curve["z"]
        tpl_sum = tpl_limit + tpl_excess
        return self._execute_if_not_zero(
            drone_value,
            lambda: self.__calculate_riesebell(base_limit, z, tpl_sum)
            - self.__calculate_riesebell(base_limit, z, tpl_excess),
        )

    def tpl_layer_premium(
        self, drone_value: float, tpl_limit: float, tpl_excess: float
    ) -> float:
        """
        Calculates TPL layer premium for a drone.
        Args:
            drone_value (float): value of the drone.
            tpl_limit (float): TPL limit.
            tpl_excess (float): TPL excess.

        Returns:
            float: The TPL layer premium.
        """
        return self._execute_if_not_zero(
            drone_value,
            lambda: self.tpl_base_layer_premium(drone_value)
            * self.tpl_ilf(drone_value, tpl_limit, tpl_excess),
        )


class CameraOperations(BaseModelOperations):
    """
    Provides operations specific to cameras for premium calculations.
    """
    def __init__(self, drone_operations: DroneOperations):
        super().__init__()
        self.drone_operations = drone_operations
    def rate(
        self, drones_list: list[dict[str, Any]], in_percentage: bool = False
    ) -> float:
        """
        Calculates the rate for camera hull insurance based on attached drones.
        Args:
            drones_list (List[Dict[str, Any]]): The list of drones.
            in_percentage (bool, optional): Whether to return the rate as a percentage. Defaults to False.
        Returns:
            float: The camera hull insurance rate.
        """
        rate = max(self.drone_operations.hull_final_rate(drone['value'], drone['weight']) for drone in drones_list if drone["has_detachable_camera"] and drone["value"] > 0)
        # new_rate = (rate)
        return rate * 100 if in_percentage else rate


class PremiumAdjustments:
    """
    Provides methods for adjusting premiums.
    """
    @staticmethod
    def limited_drones_in_use(
        drones: List[Dict[str, Any]], max_drones_in_air: int
    ) -> List[Dict[str, Any]]:
        """
        Adjusts hull premium for remaining drones not flew by clients.
        Args:
            drones (List[Dict[str, Any]]): The list of drones.
            max_drones_in_air (int): The maximum number of drones allowed to be in the air.
        Returns:
            List[Dict[str, Any]]: The list of drones with adjusted hull premiums.
        """
        sorted_drones = sorted(
            drones, key=lambda drone: drone["hull_premium"], reverse=True
        )
        for idx, drone in enumerate(sorted_drones):
            if idx < max_drones_in_air:
                continue
            drone["hull_premium"] = 150
        return drones

    @staticmethod
    def limited_cameras_in_use(
        cameras: List[Dict[str, Any]],
        max_drones_in_air: int,
        drones: List[Dict[str, Any]],
    ) -> None:
        """
        Adjusts the hull premium for cameras not being used.
        Args:
            cameras (List[Dict[str, Any]]): The list of cameras.
            max_drones_in_air (int): The maximum number of drones allowed to be in the air.
            drones (List[Dict[str, Any]]): The list of drones.
        Returns:
            List[Dict[str, Any]]: The list of cameras with adjusted hull premiums.
        """
        if len(cameras) > max_drones_in_air:
            cameras_sorted = sorted(
                cameras, key=lambda camera: camera["value"], reverse=True
            )
            for idx, camera in enumerate(cameras_sorted):
                if idx < max_drones_in_air:
                    continue
                camera["hull_premium"] = 50
        return cameras
