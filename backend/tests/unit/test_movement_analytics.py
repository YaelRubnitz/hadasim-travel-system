"""Unit tests for deterministic movement analytics (Phase A4)."""
from datetime import datetime, timedelta, timezone

import pytest

from app.locations.analytics.movement import (
    MovementThresholds,
    detect_implausible_segments,
    detect_stops,
    iter_segments,
    net_displacement_km,
    total_path_distance_km,
)
from tests.fixtures.tracks import (
    make_point,
    make_track,
    stationary_track,
    straight_line_track,
    teleport_track,
)

UTC = timezone.utc


class TestIterSegments:
    def test_empty_track_has_no_segments(self):
        track = make_track("1", [])
        assert iter_segments(track) == []

    def test_single_point_has_no_segments(self):
        track = stationary_track("1", 31.0, 35.0, count=1)
        assert iter_segments(track) == []

    def test_two_points_yield_one_segment(self):
        track = straight_line_track("1", 31.0, 35.0, count=2, interval_s=600)
        segments = iter_segments(track)
        assert len(segments) == 1
        assert segments[0].distance_km > 0
        assert segments[0].duration_seconds == pytest.approx(600, rel=0.01)


class TestPathDistance:
    def test_total_path_sums_segment_lengths(self):
        track = straight_line_track("1", 31.0, 35.0, count=4, step_lat=0.001)
        assert total_path_distance_km(track) > 0
        segments = iter_segments(track)
        assert total_path_distance_km(track) == pytest.approx(
            sum(s.distance_km for s in segments), rel=1e-6
        )

    def test_net_displacement_for_stationary_is_near_zero(self):
        track = stationary_track("1", 31.7722, 35.2181, count=5, interval_s=120)
        assert net_displacement_km(track) == pytest.approx(0.0, abs=0.001)

    def test_net_displacement_straight_line_positive(self):
        track = straight_line_track("1", 31.0, 35.0, count=3, step_lat=0.01)
        assert net_displacement_km(track) > 0


class TestDetectStops:
    def test_stationary_track_produces_one_stop(self):
        track = stationary_track("1", 31.7722, 35.2181, count=6, interval_s=60)
        stops = detect_stops(track)
        assert len(stops) == 1
        assert stops[0].duration_seconds >= 300
        assert stops[0].point_count >= 2

    def test_moving_track_produces_no_stop(self):
        track = straight_line_track(
            "1", 31.0, 35.0, count=5, interval_s=120, step_lat=0.002
        )
        stops = detect_stops(track)
        assert stops == []

    def test_short_pause_below_min_duration_not_a_stop(self):
        t0 = datetime(2026, 5, 17, 10, 0, 0, tzinfo=UTC)
        points = [
            make_point("1", 31.0, 35.0, t0),
            make_point("1", 31.0, 35.0, t0 + timedelta(seconds=120)),
            make_point("1", 31.05, 35.0, t0 + timedelta(seconds=240)),
        ]
        track = make_track("1", points)
        stops = detect_stops(track)
        assert stops == []


class TestDetectImplausibleSegments:
    def test_teleport_track_flags_jump(self):
        track = teleport_track("1")
        anomalies = detect_implausible_segments(track)
        assert len(anomalies) >= 1
        assert anomalies[0].kind == "implausible_speed"
        assert anomalies[0].speed_kph > 25

    def test_slow_segment_not_flagged(self):
        track = straight_line_track("1", 31.0, 35.0, count=2, interval_s=3600)
        assert detect_implausible_segments(track) == []

    def test_short_spike_below_min_duration_not_flagged(self):
        t0 = datetime(2026, 5, 17, 10, 0, 0, tzinfo=UTC)
        points = [
            make_point("1", 31.7722, 35.2181, t0),
            make_point("1", 31.85, 35.3, t0 + timedelta(seconds=10)),
        ]
        track = make_track("1", points)
        thresholds = MovementThresholds(min_jump_duration_s=30)
        assert detect_implausible_segments(track, thresholds) == []
