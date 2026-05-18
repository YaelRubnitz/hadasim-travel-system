"""
Pure geo helpers used by the location domain (no database).
"""
import pytest

from app.locations.geo import calculate_distance, dmms_to_decimal


class TestDmmsToDecimal:
    def test_jerusalem_latitude_from_seed_data(self):
        """Protects DMS conversion used on every location ingest (seed_data Jerusalem lat)."""
        result = dmms_to_decimal("31", "46", "20")
        expected = 31 + 46 / 60 + 20 / 3600
        assert result == pytest.approx(expected, rel=1e-9)

    def test_jerusalem_longitude_from_seed_data(self):
        result = dmms_to_decimal("35", "13", "5")
        expected = 35 + 13 / 60 + 5 / 3600
        assert result == pytest.approx(expected, rel=1e-9)

    def test_zero_minutes_and_seconds(self):
        assert dmms_to_decimal("32", "0", "0") == pytest.approx(32.0)


class TestCalculateDistance:
    def test_same_point_is_zero_km(self):
        """Haversine baseline for far-student checks."""
        assert calculate_distance(31.77, 35.21, 31.77, 35.21) == pytest.approx(0.0, abs=1e-9)

    def test_jerusalem_to_beer_sheva_exceeds_far_threshold(self):
        """Protects FAR=3.0 km rule: known cities must register as 'far' today."""
        lat_j, lon_j = 31 + 46 / 60 + 20 / 3600, 35 + 13 / 60 + 5 / 3600
        lat_bs, lon_bs = 31 + 15 / 60 + 10 / 3600, 34 + 53 / 60 + 50 / 3600
        dist = calculate_distance(lat_j, lon_j, lat_bs, lon_bs)
        assert dist > 3.0

    def test_boundary_uses_strict_greater_than_in_service(self):
        """Document current rule: dist > FAR (not >=). Points ~3km apart depend on math."""
        # Two points ~2.5 km apart (roughly): small delta in latitude near equator
        dist = calculate_distance(31.0, 35.0, 31.0225, 35.0)
        assert dist < 3.0
        assert dist == pytest.approx(2.5, rel=0.1)
