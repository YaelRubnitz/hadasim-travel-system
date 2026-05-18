"""Unit tests for deterministic proximity / group analytics (Phase B1)."""
import pytest

from app.locations.analytics.proximity import (
    ProximityThresholds,
    build_class_proximity_snapshot,
    class_centroid,
    detect_isolated_students,
    nearest_peer_distance_m,
)
from app.locations.geo import calculate_distance
from app.locations.types import TrackPoint
from datetime import datetime, timezone

UTC = timezone.utc

JERU_LAT, JERU_LON = 31.7722, 35.2181
BEER_LAT, BEER_LON = 31.2528, 34.8978


def _pt(tz: str, lat: float, lon: float) -> TrackPoint:
    return TrackPoint(tz, lat, lon, datetime(2026, 5, 17, 12, 0, 0, tzinfo=UTC))


class TestClassCentroid:
    def test_empty_returns_none(self):
        assert class_centroid({}) is None

    def test_single_point_is_centroid(self):
        points = {"a": _pt("a", JERU_LAT, JERU_LON)}
        c = class_centroid(points)
        assert c.latitude == pytest.approx(JERU_LAT)
        assert c.longitude == pytest.approx(JERU_LON)


class TestNearestPeer:
    def test_two_students_50m_apart(self):
        # ~0.00045 deg latitude ≈ 50m
        points = {
            "a": _pt("a", JERU_LAT, JERU_LON),
            "b": _pt("b", JERU_LAT + 0.00045, JERU_LON),
        }
        dist_m = nearest_peer_distance_m("a", points)
        assert dist_m is not None
        assert dist_m == pytest.approx(50, rel=0.15)

    def test_singleton_returns_none(self):
        points = {"a": _pt("a", JERU_LAT, JERU_LON)}
        assert nearest_peer_distance_m("a", points) is None


class TestDetectIsolatedStudents:
    def test_far_student_is_isolated(self):
        points = {
            "near1": _pt("near1", JERU_LAT, JERU_LON),
            "near2": _pt("near2", JERU_LAT + 0.0002, JERU_LON),
            "far": _pt("far", BEER_LAT, BEER_LON),
        }
        isolated = detect_isolated_students(points)
        assert len(isolated) == 1
        assert isolated[0].student_tz == "far"

    def test_clustered_students_not_isolated(self):
        points = {
            "a": _pt("a", JERU_LAT, JERU_LON),
            "b": _pt("b", JERU_LAT + 0.0002, JERU_LON),
        }
        assert detect_isolated_students(points) == []


class TestClassProximitySnapshot:
    def test_far_from_teacher_matches_three_km_rule(self):
        teacher = _pt("t", JERU_LAT, JERU_LON)
        students = {
            "near": _pt("near", JERU_LAT + 0.0002, JERU_LON),
            "far": _pt("far", BEER_LAT, BEER_LON),
        }
        snap = build_class_proximity_snapshot(
            "ClassA", students, teacher, ProximityThresholds()
        )
        assert "far" in snap.far_from_teacher
        assert "near" not in snap.far_from_teacher
        dist_teacher_far = calculate_distance(
            teacher.latitude, teacher.longitude, BEER_LAT, BEER_LON
        )
        assert dist_teacher_far > 3.0

    def test_snapshot_distance_maps_cover_all_students(self):
        teacher = _pt("t", JERU_LAT, JERU_LON)
        students = {"s1": _pt("s1", JERU_LAT, JERU_LON)}
        snap = build_class_proximity_snapshot("ClassA", students, teacher)
        assert "s1" in snap.student_distances_to_teacher_km
        assert "s1" in snap.student_distances_to_centroid_m
