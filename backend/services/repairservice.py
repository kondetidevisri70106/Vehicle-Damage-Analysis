from backend.config import REPAIR_ACTIONS

REPAIR_DESCRIPTION = {
    "repaint": "Surface repainting required.",
    "repair": "Panel beating / dent repair required.",
    "replace": "Component replacement recommended.",
    "inspect": "Structural inspection recommended.",
}


def recommend_repair(dominant_damage, severity):
    action = REPAIR_ACTIONS.get(dominant_damage, "repair")
    if severity == "severe" and action == "repair":
        action = "replace"
    return {
        "action": action,
        "description": REPAIR_DESCRIPTION.get(action, ""),
        "damage_class": dominant_damage,
        "severity": severity,
    }