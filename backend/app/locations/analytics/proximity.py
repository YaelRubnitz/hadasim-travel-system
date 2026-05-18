"""Pure proximity and group analytics over latest points."""
from dataclasses import dataclass
from datetime import datetime, timezone

from app.locations.geo import calculate_distance
from app.locations.types import TrackPoint

from app.locations.constants import (
    DEFAULT_FAR_FROM_TEACHER_KM,
    DEFAULT_ISOLATED_PEER_DISTANCE_M,
)

@dataclass(frozen=True)
class LatLng:
    latitude: float
    longitude: float


@dataclass(frozen=True)
class ProximityThresholds:
    far_from_teacher_km: float = DEFAULT_FAR_FROM_TEACHER_KM
    isolated_peer_distance_m: float = DEFAULT_ISOLATED_PEER_DISTANCE_M


@dataclass(frozen=True)
class IsolatedStudent:
    student_tz: str
    nearest_peer_distance_m: float | None
    distance_to_centroid_m: float


@dataclass(frozen=True)
class ClassProximitySnapshot:
    class_name: str
    recorded_at: datetime
    centroid: LatLng | None
    teacher_point: TrackPoint | None
    student_distances_to_teacher_km: dict[str, float]
    student_distances_to_centroid_m: dict[str, float]
    far_from_teacher: list[str]
    isolated: list[IsolatedStudent]


def _km_to_m(km: float) -> float:
    return km * 1000.0


def class_centroid(points: dict[str, TrackPoint]) -> LatLng | None:
    if not points:
        return None
    lat = sum(p.latitude for p in points.values()) / len(points)
    lon = sum(p.longitude for p in points.values()) / len(points)
    return LatLng(latitude=lat, longitude=lon)


def nearest_peer_distance_m(subject_tz: str, points: dict[str, TrackPoint]) -> float | None:
    subject = points.get(subject_tz)
    if subject is None:
        return None

    peers = [p for tz, p in points.items() if tz != subject_tz]
    if not peers:
        return None

    return min(
        _km_to_m(
            calculate_distance(
                subject.latitude,
                subject.longitude,
                peer.latitude,
                peer.longitude,
            )
        )
        for peer in peers
    )


def detect_isolated_students(
    student_points: dict[str, TrackPoint],
    thresholds: ProximityThresholds | None = None,
) -> list[IsolatedStudent]:
    thresholds = thresholds or ProximityThresholds()
    if len(student_points) < 2:
        return []

    centroid = class_centroid(student_points)
    isolated: list[IsolatedStudent] = []

    for tz in student_points:
        peer_dist_m = nearest_peer_distance_m(tz, student_points)
        if peer_dist_m is None or peer_dist_m <= thresholds.isolated_peer_distance_m:
            continue

        dist_centroid_m = 0.0
        if centroid is not None:
            p = student_points[tz]
            dist_centroid_m = _km_to_m(
                calculate_distance(
                    p.latitude, p.longitude, centroid.latitude, centroid.longitude
                )
            )

        isolated.append(
            IsolatedStudent(
                student_tz=tz,
                nearest_peer_distance_m=peer_dist_m,
                distance_to_centroid_m=dist_centroid_m,
            )
        )

    return isolated


def build_class_proximity_snapshot(
    class_name: str,
    student_points: dict[str, TrackPoint],
    teacher_point: TrackPoint | None,
    thresholds: ProximityThresholds | None = None,
) -> ClassProximitySnapshot:
    thresholds = thresholds or ProximityThresholds()
    centroid = class_centroid(student_points)

    recorded_at = datetime.min.replace(tzinfo=timezone.utc)
    all_points = list(student_points.values())
    if teacher_point is not None:
        all_points.append(teacher_point)
    if all_points:
        recorded_at = max(p.recorded_at for p in all_points)

    student_distances_to_teacher_km: dict[str, float] = {}
    student_distances_to_centroid_m: dict[str, float] = {}
    far_from_teacher: list[str] = []

    for tz, student in student_points.items():
        if centroid is not None:
            student_distances_to_centroid_m[tz] = _km_to_m(
                calculate_distance(
                    student.latitude,
                    student.longitude,
                    centroid.latitude,
                    centroid.longitude,
                )
            )

        if teacher_point is not None:
            dist_km = calculate_distance(
                teacher_point.latitude,
                teacher_point.longitude,
                student.latitude,
                student.longitude,
            )
            student_distances_to_teacher_km[tz] = dist_km
            if dist_km > thresholds.far_from_teacher_km:
                far_from_teacher.append(tz)

    isolated = detect_isolated_students(student_points, thresholds)

    return ClassProximitySnapshot(
        class_name=class_name,
        recorded_at=recorded_at,
        centroid=centroid,
        teacher_point=teacher_point,
        student_distances_to_teacher_km=student_distances_to_teacher_km,
        student_distances_to_centroid_m=student_distances_to_centroid_m,
        far_from_teacher=far_from_teacher,
        isolated=isolated,
    )
