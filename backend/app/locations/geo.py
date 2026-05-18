"""Pure geographic calculations (no database, HTTP, or framework dependencies)."""
import math


def dmms_to_decimal(degrees: str, minutes: str, seconds: str) -> float:
    return float(degrees) + float(minutes) / 60 + float(seconds) / 3600


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c
