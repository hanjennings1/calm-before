import pytest

from models import db, County, Zip, ZipCounty


@pytest.fixture
def seed_locations(app):
    """A small set of test data, based on real ZIPs (coordinates approximate)."""
    db.session.add_all([
        County(fips="45073", name="Oconee County", state="SC"),
        County(fips="45077", name="Pickens County", state="SC"),
        County(fips="44009", name="Washington County", state="RI"),
        Zip(code="29678", lat=34.68, lon=-82.95),   # spans two counties
        Zip(code="02891", lat=41.36, lon=-71.81),   # leading zero
        Zip(code="06001", lat=41.79, lon=-72.85),   # no county link (like Connecticut)
    ])
    db.session.flush()
    db.session.add_all([
        ZipCounty(zip_code="29678", county_fips="45073", land_area=205_441_258),
        ZipCounty(zip_code="29678", county_fips="45077", land_area=1_172_038),
        ZipCounty(zip_code="02891", county_fips="44009", land_area=100_000_000),
    ])
    db.session.commit()


def test_zip_spanning_two_counties_lists_primary_first(client, seed_locations):
    data = client.get("/api/location/29678").get_json()

    assert data["primary_county"]["name"] == "Oconee County"
    assert [c["fips"] for c in data["counties"]] == ["45073", "45077"]
    assert data["counties"][0]["land_share"] > 0.99


def test_zip_with_leading_zero(client, seed_locations):
    response = client.get("/api/location/02891")

    assert response.status_code == 200
    assert response.get_json()["zip"] == "02891"


def test_zip_without_county_still_returns_coordinates(client, seed_locations):
    data = client.get("/api/location/06001").get_json()

    assert data["lat"] == 41.79
    assert data["primary_county"] is None
    assert data["counties"] == []


def test_unknown_zip_returns_404(client, seed_locations):
    response = client.get("/api/location/99999")

    assert response.status_code == 404
    assert "not found" in response.get_json()["error"]


@pytest.mark.parametrize("bad_zip", ["abc", "1234", "123456"])
def test_invalid_zip_returns_400(client, bad_zip):
    response = client.get(f"/api/location/{bad_zip}")

    assert response.status_code == 400