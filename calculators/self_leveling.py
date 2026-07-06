from config import SELF_LEVELING


def calculate(area: float) -> dict:
    return {"self_leveling": area * SELF_LEVELING["min"]}
