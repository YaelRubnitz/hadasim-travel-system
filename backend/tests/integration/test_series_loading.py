"""Integration tests for track loading from locationupdate (Phase A1)."""
from datetime import datetime, timedelta, timezone

import pytest
from sqlmodel import Session

from app.locations.series import fetch_track
from app.locations.types import StudentTrack
from app.models.location import LocationUpdate
from app.services.locations_service import create_location_service
from tests.conftest import JERUSALEM_LAT, JERUSALEM_LON, dms_payload

UTC = timezone.utc


def _insert_row(
    session: Session,
    tz: str,
    lat: float,
    lon: float,
    when: datetime,
) -> None:
    session.add(
        LocationUpdate(
            student_tz=tz,
            latitude=lat,
            longitude=lon,
            timestamp=when,
        )
    )
    session.commit()


class TestFetchTrack:
    def test_returns_points_ordered_by_timestamp_then_id(self, session, student_near):
        t1 = datetime(2026, 5, 17, 10, 0, 0, tzinfo=UTC)
        t2 = datetime(2026, 5, 17, 11, 0, 0, tzinfo=UTC)
        t3 = datetime(2026, 5, 17, 12, 0, 0, tzinfo=UTC)
        _insert_row(session, student_near.tz, 31.0, 35.0, t2)
        _insert_row(session, student_near.tz, 31.1, 35.0, t1)
        _insert_row(session, student_near.tz, 31.2, 35.0, t3)

        track = fetch_track(session, student_near.tz)
        assert isinstance(track, StudentTrack)
        lats = [p.latitude for p in track.points]
        assert lats == [31.1, 31.0, 31.2]

    def test_empty_track_when_no_rows(self, session, student_near):
        track = fetch_track(session, student_near.tz)
        assert track.person_tz == student_near.tz
        assert track.points == ()

    def test_since_until_window(self, session, student_near):
        base = datetime(2026, 5, 17, 10, 0, 0, tzinfo=UTC)
        for i in range(5):
            _insert_row(session, student_near.tz, 31.0 + i * 0.01, 35.0, base + timedelta(hours=i))
        track = fetch_track(
            session,
            student_near.tz,
            since=base + timedelta(hours=1),
            until=base + timedelta(hours=3),
        )
        assert len(track.points) == 3

    def test_since_after_until_returns_empty(self, session, student_near):
        base = datetime(2026, 5, 17, 10, 0, 0, tzinfo=UTC)
        _insert_row(session, student_near.tz, 31.0, 35.0, base)
        track = fetch_track(
            session,
            student_near.tz,
            since=base + timedelta(hours=2),
            until=base,
        )
        assert track.points == ()

    def test_limit_returns_last_n_in_window_sorted_asc(self, session, student_near):
        base = datetime(2026, 5, 17, 10, 0, 0, tzinfo=UTC)
        for i in range(5):
            _insert_row(session, student_near.tz, 31.0 + i, 35.0, base + timedelta(hours=i))
        track = fetch_track(session, student_near.tz, limit=2)
        assert len(track.points) == 2
        assert track.points[0].latitude == pytest.approx(34.0)
        assert track.points[1].latitude == pytest.approx(35.0)

    def test_via_create_location_service(self, session, student_near):
        data = dms_payload(student_near.tz, JERUSALEM_LAT, JERUSALEM_LON)
        create_location_service(session, data)
        track = fetch_track(session, student_near.tz)
        assert len(track.points) == 1
        assert track.points[0].latitude == pytest.approx(31 + 46 / 60 + 20 / 3600, rel=1e-5)
