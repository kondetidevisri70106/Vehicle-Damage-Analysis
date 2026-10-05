from backend.config import REPAIR_ACTIONS
from backend.utils.calculations import estimate_cost


class CostModel:
    def estimate(self, component, severity, damage_class, vehicle_type="car_sedan"):
        action = REPAIR_ACTIONS.get(damage_class, "repair")
        low, high = estimate_cost(component, severity, action, vehicle_type)
        return {
            "action": action,
            "cost_min": low,
            "cost_max": high,
            "currency": "INR",
            "vehicle_type": vehicle_type,
        }