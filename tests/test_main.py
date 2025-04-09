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
    }
    response = client.put(f"/cameras/{camera_id}", json=updated_data)
    assert response.status_code == 200
    response_data = response.json()
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
    }
    create_response = client.post("/cameras/", json=camera_data)
    camera_id = create_response.json()["id"]

    response = client.delete(f"/cameras/{camera_id}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Camera with id {camera_id} deleted successfully"}

# GET DELETED CAMERA
    response = client.get(f"/cameras/{camera_id}")
    assert response.status_code == 404

# CREATE FILM
def test_create_film():
    film_data = {
        "brand": "Kodak",
        "name": "Portra 400",
        "format": "35mm",
        "type": "Color",
        "iso": 400,
        "grain": "Fine"
    }
    response = client.post("/films/", json=film_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["brand"] == "Kodak"
    assert response_data["name"] == "Portra 400"
    assert "id" in response_data 

# GET ALL FILM STCOK
def test_get_all_films():

    film_data = {
        "brand": "Ilford",
        "name": "HP5 Plus",
        "format": "35mm",
        "type": "B&W",
        "iso": 400,
        "grain": "Medium"
    }
    client.post("/films/", json=film_data)
    response = client.get("/films/")
    assert response.status_code == 200
    films = response.json()
    assert isinstance(films, list)
    assert len(films) > 0 

# GET FILM BY ID
def test_get_film_by_id():

    film_data = {
        "brand": "Fujifilm",
        "name": "Superia 400",
        "format": "35mm",
        "type": "Color",
        "iso": 400,
        "grain": "Fine"
    }
    create_response = client.post("/films/", json=film_data)
    film_id = create_response.json()["id"]

    response = client.get(f"/films/{film_id}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["brand"] == "Fujifilm"
    assert response_data["name"] == "Superia 400"
    assert response_data["id"] == film_id

# EDIT FILM STOCK
def test_edit_film():

    film_data = {
        "brand": "Kodak",
        "name": "Tri-X 400",
        "format": "35mm",
        "type": "B&W",
        "iso": 400,
        "grain": "Medium"
    }
    create_response = client.post("/films/", json=film_data)
    film_id = create_response.json()["id"]

    updated_data = {
        "brand": "Kodak",
        "name": "Tri-X 400",
        "format": "35mm",
        "type": "B&W",
        "iso": 400,
        "grain": "Fine"
    }
    response = client.put(f"/films/{film_id}", json=updated_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["grain"] == "Fine"
    assert response_data["id"] == film_id

# DELETE FILM
def test_delete_film():
    film_data = {
        "brand": "Kodak",
        "name": "Ektar 100",
        "format": "35mm",
        "type": "Color",
        "iso": 100,
        "grain": "Fine"
    }
    create_response = client.post("/films/", json=film_data)
    film_id = create_response.json()["id"]

    response = client.delete(f"/films/{film_id}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Film stock with id {film_id} deleted successfully"}

    response = client.get(f"/films/{film_id}")
    assert response.status_code == 404