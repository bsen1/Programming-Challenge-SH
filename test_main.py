import requests
from main import is_in_zone, BASE_URL

def test_point_inside():
    zone = [[-122.5, 37.5], [-122.0, 37.5], [-122.0, 38.0], [-122.5, 38.0], [-122.5, 37.5]]
    assert is_in_zone([-122.25, 37.75], [zone]) == True
    print("PASS test_point_inside")

def test_point_outside():
    zone = [[-122.5, 37.5], [-122.0, 37.5], [-122.0, 38.0], [-122.5, 38.0], [-122.5, 37.5]]
    assert is_in_zone([-123.0, 37.75], [zone]) == False
    print("PASS test_point_outside")

def test_point_on_boundary():
    zone = [[-122.0414543152, 37.3443685049],
            [-122.0328712464, 37.3443685049],
            [-122.0328712464, 37.3576050714],
            [-122.0414543152, 37.3576050714],
            [-122.0414543152, 37.3443685049]]
    loc = [-122.0328712464, 37.3504867401]
    assert is_in_zone(loc, [zone]) == True  # boundary = in zone
    print("PASS test_point_on_boundary")

def test_multiple_zones():
    # Point in second zone only
    zone1 = [[-122.5, 37.5], [-122.0, 37.5], [-122.0, 38.0], [-122.5, 38.0], [-122.5, 37.5]]
    zone2 = [[-121.5, 36.5], [-121.0, 36.5], [-121.0, 37.0], [-121.5, 37.0], [-121.5, 36.5]]
    assert is_in_zone([-121.25, 36.75], [zone1, zone2]) == True
    print("PASS test_multiple_zones")


def test_api_returns_valid_response():
    response = requests.get(f"{BASE_URL}/1", timeout=5)
    data = response.json()
    assert "features" in data
    assert len(data["features"]) >= 2
    assert data["features"][0]["geometry"]["type"] == "Point"
    assert data["features"][1]["geometry"]["type"] == "Polygon"
    print("PASS test_api_returns_valid_response")

def test_api_bad_response():
    response = requests.get(f"{BASE_URL}/10", timeout=5)
    data = response.json()
    features = data.get("features")
    assert not features
    print("PASS test_api_bad_response_handled")


if __name__ == "__main__":
    test_point_inside()
    test_point_outside()
    test_point_on_boundary()
    test_multiple_zones()
    test_api_returns_valid_response()
    test_api_bad_response()

    print("\nAll tests passed")