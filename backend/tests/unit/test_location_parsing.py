"""
Unit tests for location ingest payload parsing (boundary layer).
"""
from datetime import datetime, timezone

import pytest
from fastapi import HTTPException

from app.locations.parsing import (
    normalize_timestamp,
    parse_location_update_payload,
)
from tests.conftest import JERUSALEM_LAT, JERUSALEM_LON, dms_payload


class TestNormalizeTimestamp:
    def test_none_returns_none(self):
        assert normalize_timestamp(None) is None

    def test_datetime_unchanged(self):
        dt = datetime(2026, 5, 17, 10, 0, 0, tzinfo=timezone.utc)
        assert normalize_timestamp(dt) is dt

    def test_iso_string_with_z(self):
        result = normalize_timestamp("2026-05-17T10:00:00Z")
        assert result == datetime(2026, 5, 17, 10, 0, 0, tzinfo=timezone.utc)

    def test_invalid_string_passed_through(self):
        raw = "not-a-timestamp"
        assert normalize_timestamp(raw) == raw


class TestParseLocationUpdatePayload:
    def test_parses_dms_payload(self):
        data = dms_payload("81111111", JERUSALEM_LAT, JERUSALEM_LON)
        parsed = parse_location_update_payload(data)
        assert parsed.latitude == pytest.approx(31 + 46 / 60 + 20 / 3600, rel=1e-6)
        assert parsed.longitude == pytest.approx(35 + 13 / 60 + 5 / 3600, rel=1e-6)
        assert parsed.timestamp is None

    def test_invalid_coordinates_raises_400(self):
        with pytest.raises(HTTPException) as exc:
            parse_location_update_payload({"ID": "1", "Coordinates": {}})
        assert exc.value.status_code == 400
        assert exc.value.detail == "Invalid coordinates format"
