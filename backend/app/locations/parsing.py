"""
Inbound location update parsing (raw request dict → typed values).

Boundary between external device JSON and application orchestration.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from fastapi import HTTPException

from app.locations.geo import dmms_to_decimal


@dataclass(frozen=True)
class ParsedLocationPayload:
    latitude: float
    longitude: float
    timestamp: datetime | None


def normalize_timestamp(value: Any) -> datetime | None:
    """
    Normalize client ``Time`` for persistence.

    - Missing / ``None`` → ``None`` (DB default applies on insert).
    - ``datetime`` → unchanged.
    - ISO-8601 ``str`` (e.g. ``2026-05-17T10:00:00Z``) → ``datetime``.
    - Unparseable ``str`` → returned as-is (same downstream behavior as before).
  """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return value
    return value


def parse_location_update_payload(data: dict) -> ParsedLocationPayload:
    """
    Parse DMS coordinates and optional time from POST /locations/update body.

    Raises:
        HTTPException(400): ``Invalid coordinates format`` on missing/invalid structure.
    """
    try:
        lat_d = data["Coordinates"]["Latitude"]
        lon_d = data["Coordinates"]["Longitude"]

        latitude = dmms_to_decimal(lat_d["Degrees"], lat_d["Minutes"], lat_d["Seconds"])
        longitude = dmms_to_decimal(lon_d["Degrees"], lon_d["Minutes"], lon_d["Seconds"])
        timestamp = normalize_timestamp(data.get("Time"))

        return ParsedLocationPayload(
            latitude=latitude,
            longitude=longitude,
            timestamp=timestamp,
        )
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid coordinates format")
