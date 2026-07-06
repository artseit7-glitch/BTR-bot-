from config import CONCRETE

WORK_LABELS = {
    "screed":     "Заливка стяжки",
    "beacons":    "Выставление маяков",
    "gravel":     "Засыпка щебнем",
    "rebar":      "Вязка арматуры",
    "demolition": "Демонтаж",
}


def calculate(area: float, selected: list, gravel_depth: int = 0) -> dict:
    result = {}
    for item in selected:
        if item == "screed":
            result["screed"] = CONCRETE["screed"] * area
        elif item == "beacons":
            result["beacons"] = CONCRETE["beacons"] * area
        elif item == "gravel":
            price_per_m2 = max(CONCRETE["gravel_min"], CONCRETE["gravel_per_cm"] * gravel_depth)
            result["gravel"] = price_per_m2 * area
        elif item == "rebar":
            result["rebar"] = CONCRETE["rebar"] * area
        elif item == "demolition":
            result["demolition"] = CONCRETE["demolition"] * area
    return result
