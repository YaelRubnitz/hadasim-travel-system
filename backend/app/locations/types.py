"""Shared types for location time-series and analytics."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TrackPoint:
    person_tz: str
    latitude: float
    longitude: float
    recorded_at: datetime


@dataclass(frozen=True)
class StudentTrack:
    person_tz: str
    points: tuple[TrackPoint, ...]
