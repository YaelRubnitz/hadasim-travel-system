"""Pure movement analytics over ordered tracks."""
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from app.locations.geo import calculate_distance
from app.locations.types import StudentTrack, TrackPoint
from app.locations.constants import (
    DEFAULT_STOP_RADIUS_KM,
    DEFAULT_MIN_STOP_DURATION_S,
    DEFAULT_JUMP_SPEED_KPH,
    DEFAULT_MIN_JUMP_DURATION_S,
)


@dataclass(frozen=True)
class MovementThresholds:
    stop_radius_km: float = DEFAULT_STOP_RADIUS_KM
    min_stop_duration_s: float = DEFAULT_MIN_STOP_DURATION_S
    jump_speed_kph: float = DEFAULT_JUMP_SPEED_KPH
    min_jump_duration_s: float = DEFAULT_MIN_JUMP_DURATION_S


@dataclass(frozen=True)
class MovementSegment:
    start: TrackPoint
    end: TrackPoint
    distance_km: float
    duration_seconds: float
    speed_kph: float


@dataclass(frozen=True)
class Stop:
    start_at: datetime
    end_at: datetime
    center_lat: float
    center_lon: float
    duration_seconds: float
    point_count: int


@dataclass(frozen=True)
class MovementAnomaly:
    kind: Literal["implausible_speed"]
    segment: MovementSegment
    speed_kph: float
    threshold_kph: float


def iter_segments(track: StudentTrack) -> list[MovementSegment]:
    points = track.points
    if len(points) < 2:
        return []

    segments: list[MovementSegment] = []
    for i in range(len(points) - 1):
        start, end = points[i], points[i + 1]
        distance_km = calculate_distance(
            start.latitude, start.longitude, end.latitude, end.longitude
        )
        duration_seconds = (end.recorded_at - start.recorded_at).total_seconds()
        if duration_seconds < 0:
            continue
        speed_kph = (distance_km / (duration_seconds / 3600.0)) if duration_seconds > 0 else 0.0
        segments.append(
            MovementSegment(
                start=start,
                end=end,
                distance_km=distance_km,
                duration_seconds=duration_seconds,
                speed_kph=speed_kph,
            )
        )
    return segments


def total_path_distance_km(track: StudentTrack) -> float:
    return sum(segment.distance_km for segment in iter_segments(track))


def net_displacement_km(track: StudentTrack) -> float:
    if not track.points:
        return 0.0
    first, last = track.points[0], track.points[-1]
    return calculate_distance(
        first.latitude, first.longitude, last.latitude, last.longitude
    )


def _cluster_centroid(cluster: list[TrackPoint]) -> tuple[float, float]:
    lat = sum(p.latitude for p in cluster) / len(cluster)
    lon = sum(p.longitude for p in cluster) / len(cluster)
    return lat, lon


def _finalize_stop(cluster: list[TrackPoint]) -> Stop | None:
    if len(cluster) < 2:
        return None
    start_at = cluster[0].recorded_at
    end_at = cluster[-1].recorded_at
    duration_seconds = (end_at - start_at).total_seconds()
    center_lat, center_lon = _cluster_centroid(cluster)
    return Stop(
        start_at=start_at,
        end_at=end_at,
        center_lat=center_lat,
        center_lon=center_lon,
        duration_seconds=duration_seconds,
        point_count=len(cluster),
    )


def detect_stops(
    track: StudentTrack,
    thresholds: MovementThresholds | None = None,
) -> list[Stop]:
    thresholds = thresholds or MovementThresholds()
    if len(track.points) < 2:
        return []

    stops: list[Stop] = []
    cluster: list[TrackPoint] = [track.points[0]]

    for point in track.points[1:]:
        center_lat, center_lon = _cluster_centroid(cluster)
        dist_km = calculate_distance(center_lat, center_lon, point.latitude, point.longitude)
        if dist_km <= thresholds.stop_radius_km:
            cluster.append(point)
        else:
            stop = _finalize_stop(cluster)
            if stop and stop.duration_seconds >= thresholds.min_stop_duration_s:
                stops.append(stop)
            cluster = [point]

    stop = _finalize_stop(cluster)
    if stop and stop.duration_seconds >= thresholds.min_stop_duration_s:
        stops.append(stop)

    return stops


def detect_implausible_segments(
    track: StudentTrack,
    thresholds: MovementThresholds | None = None,
) -> list[MovementAnomaly]:
    thresholds = thresholds or MovementThresholds()
    anomalies: list[MovementAnomaly] = []
    for segment in iter_segments(track):
        if (
            segment.duration_seconds >= thresholds.min_jump_duration_s
            and segment.speed_kph > thresholds.jump_speed_kph
        ):
            anomalies.append(
                MovementAnomaly(
                    kind="implausible_speed",
                    segment=segment,
                    speed_kph=segment.speed_kph,
                    threshold_kph=thresholds.jump_speed_kph,
                )
            )
    return anomalies
