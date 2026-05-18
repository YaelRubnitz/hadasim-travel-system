"""Synthetic movement tracks for deterministic analytics tests."""
from datetime import datetime, timedelta, timezone

from app.locations.types import StudentTrack, TrackPoint

UTC = timezone.utc


def make_point(
    person_tz: str,
    latitude: float,
    longitude: float,
    recorded_at: datetime,
) -> TrackPoint:
    if recorded_at.tzinfo is None:
        recorded_at = recorded_at.replace(tzinfo=UTC)
    return TrackPoint(
        person_tz=person_tz,
        latitude=latitude,
        longitude=longitude,
        recorded_at=recorded_at,
    )


def make_track(person_tz: str, points: list[TrackPoint]) -> StudentTrack:
    ordered = tuple(sorted(points, key=lambda p: (p.recorded_at, p.latitude, p.longitude)))
    return StudentTrack(person_tz=person_tz, points=ordered)


def stationary_track(
    person_tz: str,
    latitude: float,
    longitude: float,
    *,
    count: int = 6,
    interval_s: int = 60,
    start: datetime | None = None,
) -> StudentTrack:
    start = start or datetime(2026, 5, 17, 10, 0, 0, tzinfo=UTC)
    points = [
        make_point(
            person_tz,
            latitude,
            longitude,
            start + timedelta(seconds=i * interval_s),
        )
        for i in range(count)
    ]
    return make_track(person_tz, points)


def straight_line_track(
    person_tz: str,
    start_lat: float,
    start_lon: float,
    *,
    count: int = 5,
    interval_s: int = 120,
    step_lat: float = 0.001,
) -> StudentTrack:
    start = datetime(2026, 5, 17, 10, 0, 0, tzinfo=UTC)
    points = [
        make_point(
            person_tz,
            start_lat + i * step_lat,
            start_lon,
            start + timedelta(seconds=i * interval_s),
        )
        for i in range(count)
    ]
    return make_track(person_tz, points)


def teleport_track(person_tz: str) -> StudentTrack:
    """Two clusters far apart with a short interval (implausible speed)."""
    t0 = datetime(2026, 5, 17, 10, 0, 0, tzinfo=UTC)
    jerusalem = make_point(person_tz, 31.7722, 35.2181, t0)
    beer_sheva = make_point(person_tz, 31.2528, 34.8978, t0 + timedelta(seconds=60))
    return make_track(person_tz, [jerusalem, beer_sheva])
