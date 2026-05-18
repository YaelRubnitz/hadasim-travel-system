"""
HTTP contract characterization for /locations/* (status codes, JSON shapes).
"""
import pytest

from tests.conftest import (
    BEER_SHEVA_LAT,
    BEER_SHEVA_LON,
    JERUSALEM_LAT,
    JERUSALEM_LON,
    dms_payload,
)


class TestPostLocationsUpdate:
    def test_public_ingest_returns_location_read_shape(self, client, student_near):
        """POST /locations/update is unauthenticated; response matches LocationRead."""
        payload = dms_payload(student_near.tz, JERUSALEM_LAT, JERUSALEM_LON)
        response = client.post("/locations/update", json=payload)
        assert response.status_code == 200
        body = response.json()
        assert set(body.keys()) == {"student_tz", "latitude", "longitude", "timestamp"}
        assert body["student_tz"] == student_near.tz

    def test_unknown_tz_returns_404(self, client):
        response = client.post(
            "/locations/update",
            json=dms_payload("99999999", JERUSALEM_LAT, JERUSALEM_LON),
        )
        assert response.status_code == 404

    def test_invalid_body_returns_400(self, client, student_near):
        response = client.post(
            "/locations/update",
            json={"ID": student_near.tz, "Coordinates": {}},
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid coordinates format"


class TestAuthenticatedLocationReads:
    def test_last_location_requires_auth(self, client, student_near):
        response = client.get(f"/locations/{student_near.tz}/last-location")
        assert response.status_code == 401

    def test_last_location_success(self, authenticated_client, student_near):
        authenticated_client.post(
            "/locations/update",
            json=dms_payload(student_near.tz, JERUSALEM_LAT, JERUSALEM_LON),
        )
        response = authenticated_client.get(f"/locations/{student_near.tz}/last-location")
        assert response.status_code == 200
        assert "latitude" in response.json()

    def test_path_returns_list(self, authenticated_client, student_near):
        authenticated_client.post(
            "/locations/update",
            json=dms_payload(student_near.tz, JERUSALEM_LAT, JERUSALEM_LON),
        )
        response = authenticated_client.get(f"/locations/{student_near.tz}/path")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) >= 1

    def test_class_last_locations_scoped_to_teacher_class(
        self, authenticated_client, teacher, student_near, student_other_class
    ):
        authenticated_client.post(
            "/locations/update",
            json=dms_payload(student_near.tz, JERUSALEM_LAT, JERUSALEM_LON),
        )
        authenticated_client.post(
            "/locations/update",
            json=dms_payload(student_other_class.tz, BEER_SHEVA_LAT, BEER_SHEVA_LON),
        )
        response = authenticated_client.get("/locations/class-last-locations")
        assert response.status_code == 200
        tzs = {row["student_tz"] for row in response.json()}
        assert student_near.tz in tzs
        assert student_other_class.tz not in tzs

    def test_far_students_json_contract(
        self, authenticated_client, teacher, student_near, student_far
    ):
        authenticated_client.post(
            "/locations/update",
            json=dms_payload(teacher.tz, JERUSALEM_LAT, JERUSALEM_LON),
        )
        authenticated_client.post(
            "/locations/update",
            json=dms_payload(student_near.tz, JERUSALEM_LAT, JERUSALEM_LON),
        )
        authenticated_client.post(
            "/locations/update",
            json=dms_payload(student_far.tz, BEER_SHEVA_LAT, BEER_SHEVA_LON),
        )
        response = authenticated_client.get("/locations/far-students")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["student_tz"] == student_far.tz
        assert "distance" in data[0]

    def test_golden_seed_style_payload_stable_lat_lng(self, client, student_near):
        """Same DMS numbers as seed_data.py Jerusalem entry."""
        payload = {
            "ID": student_near.tz,
            "Coordinates": {
                "Longitude": {"Degrees": "35", "Minutes": "13", "Seconds": "05"},
                "Latitude": {"Degrees": "31", "Minutes": "46", "Seconds": "20"},
            },
        }
        response = client.post("/locations/update", json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["latitude"] == pytest.approx(31.772222, rel=1e-5)
        assert body["longitude"] == pytest.approx(35.218056, rel=1e-5)
