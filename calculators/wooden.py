from config import WOODEN

WORK_LABELS = {
    "lags":     "Установка лаг",
    "osb":      "Укладка ОСП/фанеры",
    "laminate": "Укладка ламината",
    "linoleum": "Настил линолеума",
    "tile":     "Укладка плитки/керамогранита",
    "plinth":   "Монтаж плинтуса",
}


def calculate(area: float, selected: list, plinth_meters: float = 0) -> dict:
    result = {}
    for item in selected:
        mn, mx = WOODEN[item]
        if item == "plinth":
            result["plinth"] = (mn * plinth_meters, mx * plinth_meters)
        else:
            result[item] = (mn * area, mx * area)
    return result
