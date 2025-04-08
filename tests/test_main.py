from fastapi.testclient import TestClient
from src.analogapi.main import app

client = TestClient(app)

# ROOT ENDPOINT
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to AnalogAPI"}

# CREATE CAMERA
def test_create_camera():
    camera_data = {
        "brand": "Canon",
        "model": "AE-1",
        "format": "35mm",
        "type": "SLR",
        "years": "1976-1984",
        "lens_mount": "Canon FD",
        "notes": "Classic film camera"
    }
    response = client.post("/cameras/", json=camera_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["brand"] == "Canon"
    assert response_data["model"] == "AE-1"
    assert "id" in response_data  

# GET ALL CAMERAS
def test_get_all_cameras():
# EXAMPLE
    camera_data = {
        "brand": "Pentax",
        "model": "K1000",
        "format": "35mm",
        "type": "SLR",
        "years": "1976-1997",
        "lens_mount": "Pentax K",
        "notes": "Popular student camera"
    }
    client.post("/cameras/", json=camera_data)


    response = client.get("/cameras/")
    assert response.status_code == 200
    cameras = response.json()
    assert isinstance(cameras, list)
    assert len(cameras) > 0 

# GET CAMERA BY ID
def test_get_camera_by_id():

    camera_data = {
        "brand": "Nikon",
        "model": "F3",
        "format": "35mm",
        "type": "SLR",
        "years": "1980-2000",
        "lens_mount": "Nikon F",
        "notes": "Professional film camera"
    }
    create_response = client.post("/cameras/", json=camera_data)
    camera_id = create_response.json()["id"]

    response = client.get(f"/cameras/{camera_id}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["brand"] == "Nikon"
    assert response_data["model"] == "F3"
    assert response_data["id"] == camera_id

# EDITS CAMERA
def test_edit_camera():

    camera_data = {
        "brand": "Olympus",
        "model": "OM-1",
        "format": "35mm",
        "type": "SLR",
        "years": "1972-1987",
        "lens_mount": "Olympus OM",
        "notes": "Compact film camera"
    }
    create_response = client.post("/cameras/", json=camera_data)
    camera_id = create_response.json()["id"]


    updated_data = {
        "brand": "Olympus",
        "model": "OM-1",
        "format": "35mm",
        "type": "SLR",
        "years": "1972-1987",
        "lens_mount": "Olympus OM",
        "notes": "Updated compact film camera"
    }
    response = client.put(f"/cameras/{camera_id}", json=updated_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["notes"] == "Updated compact film camera"
    assert response_data["id"] == camera_id

# DELETES CAMERA
def test_delete_camera():

    camera_data = {
        "brand": "Minolta",
        "model": "X-700",
        "format": "35mm",
        "type": "SLR",
        "years": "1981-1999",
        "lens_mount": "Minolta MD",
        "notes": "Advanced film camera"
    }
    create_response = client.post("/cameras/", json=camera_data)
    camera_id = create_response.json()["id"]

    response = client.delete(f"/cameras/{camera_id}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Camera with id {camera_id} deleted successfully"}

# GET DELETED CAMERA
    response = client.get(f"/cameras/{camera_id}")
    assert response.status_code == 404