from fastapi.testclient import TestClient
import os
import pytest
from sqlalchemy.sql import text

os.environ["TEST_DATABASE_URL"] = "postgresql://user:password@localhost:5432/analogapi_test"

from src.analogapi.database import initialize_engine_and_session, clear_database, get_session
initialize_engine_and_session(db_url=os.environ["TEST_DATABASE_URL"])
from src.analogapi.main import app

client = TestClient(app)

# CLEAR DB FOR TESTS
@pytest.fixture(autouse=True)
def clear_db():
    test_db_url = os.getenv("TEST_DATABASE_URL")
    if not test_db_url:
        raise ValueError("TEST_DATABASE_URL must be set for tests")
    clear_database(db_url=test_db_url)

# PREDEFINED DATA
@pytest.fixture
def setup_data():
    tag1_response = client.post("/tags/", json={"name": "SLR"})
    assert tag1_response.status_code == 200, f"Failed to create tag 'SLR': {tag1_response.json()}"
    tag2_response = client.post("/tags/", json={"name": "moda"})
    assert tag2_response.status_code == 200, f"Failed to create tag 'moda': {tag2_response.json()}"
    tag1_id = tag1_response.json()["id"]
    tag2_id = tag2_response.json()["id"]

    camera1_response = client.post("/cameras/", json={
        "brand": "Canon",
        "model": "AE-1",
        "format": "35mm",
        "type": "SLR",
        "years": "1976-1984",
        "lens_mount": "Canon FD",
        "tag_ids": [tag1_id, tag2_id]
    })
    assert camera1_response.status_code == 200, f"Failed to create camera: {camera1_response.json()}"

    camera2_response = client.post("/cameras/", json={
        "brand": "Hasselblad",
        "model": "500C/M",
        "format": "120",
        "type": "Medium Format",
        "years": "1970-1994",
        "lens_mount": "Hasselblad V",
        "tag_ids": [tag1_id]
    })
    assert camera2_response.status_code == 200, f"Failed to create camera: {camera2_response.json()}"

    film1_response = client.post("/films/", json={
        "brand": "Kodak",
        "name": "Portra 400",
        "format": "35mm",
        "type": "Color",
        "iso": 400,
        "grain": "Fine",
        "tag_ids": [tag1_id]
    })
    assert film1_response.status_code == 200, f"Failed to create film: {film1_response.json()}"

    film2_response = client.post("/films/", json={
        "brand": "Ilford",
        "name": "HP5 Plus",
        "format": "120",
        "type": "B&W",
        "iso": 400,
        "grain": "Medium",
        "tag_ids": [tag2_id]
    })
    assert film2_response.status_code == 200, f"Failed to create film: {film2_response.json()}"

# EMPTY DB
def test_database_is_empty():
    test_db_url = os.getenv("TEST_DATABASE_URL")
    session = get_session(test_db_url)()
    try:
        result = session.execute(text("SELECT COUNT(*) FROM tags")).scalar()
        assert result == 0, f"Expected 0 tags, but found {result}"
    finally:
        session.close()

# TEST CLEAR DATABASE IN PRODUCTION
def test_clear_database_in_production():
    os.environ["ENVIRONMENT"] = "production"
    test_db_url = os.getenv("TEST_DATABASE_URL")
    with pytest.raises(RuntimeError, match="Cannot clear database in production environment"):
        clear_database(db_url=test_db_url)
    os.environ["ENVIRONMENT"] = "development"

# ROOT ENDPOINT
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to AnalogAPI"}

# CAMERAS
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

# GET ALL CAMERAS WITH PREDEFINED DATA
def test_get_all_cameras_with_tags(setup_data):
    response = client.get("/cameras/")
    assert response.status_code == 200
    cameras = response.json()
    assert len(cameras) == 2  
    assert len(cameras[0]["tags"]) == 2
    assert len(cameras[1]["tags"]) == 1

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

# GET CAMERA BY INVALID ID
def test_get_camera_by_invalid_id():
    response = client.get("/cameras/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Camera not found"}

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
        "lens_mount": "Olympus OM Updated",
    }
    response = client.put(f"/cameras/{camera_id}", json=updated_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["lens_mount"] == "Olympus OM Updated"
    assert response_data["id"] == camera_id

# EDIT CAMERA INVALID ID
def test_edit_camera_invalid_id():
    updated_data = {
        "brand": "Olympus",
        "model": "OM-1",
        "format": "35mm",
        "type": "SLR",
        "years": "1972-1987",
        "lens_mount": "Olympus OM Updated",
    }
    response = client.put("/cameras/999", json=updated_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Camera not found"}

# EDIT CAMERA WITH INVALID TAG
def test_edit_camera_invalid_tag():
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
        "lens_mount": "Olympus OM Updated",
        "tag_ids": [999]  
    }
    response = client.put(f"/cameras/{camera_id}", json=updated_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "One or more tags not found"}

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

# DELETE CAMERA INVALID ID
def test_delete_camera_invalid_id():
    response = client.delete("/cameras/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Camera not found"}

# GET COMPATIBLE FILMS FOR CAMERA
def test_get_compatible_films():
    camera_data = {
        "brand": "Nikon",
        "model": "F3",
        "format": "35mm",
        "type": "SLR",
        "years": "1980-2000",
        "lens_mount": "Nikon F",
    }
    create_camera_response = client.post("/cameras/", json=camera_data)
    camera_id = create_camera_response.json()["id"]

    film1_response = client.post("/films/", json={
        "brand": "Kodak",
        "name": "Portra 400",
        "format": "35mm",
        "type": "Color",
        "iso": 400,
        "grain": "Fine"
    })
    assert film1_response.status_code == 200

    film2_response = client.post("/films/", json={
        "brand": "Ilford",
        "name": "HP5 Plus",
        "format": "120",
        "type": "B&W",
        "iso": 400,
        "grain": "Medium"
    })
    assert film2_response.status_code == 200

    response = client.get(f"/cameras/{camera_id}/compatible-films")
    assert response.status_code == 200
    compatible_films = response.json()
    assert len(compatible_films) == 1 
    assert compatible_films[0]["name"] == "Portra 400"

# GET COMPATIBLE FILMS FOR INVALID CAMERA
def test_get_compatible_films_invalid_camera():
    response = client.get("/cameras/999/compatible-films")
    assert response.status_code == 404
    assert response.json() == {"detail": "Camera not found"}

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

# FILM
# GET ALL FILM STOCK
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

# GET ALL FILMS WITH PREDEFINED DATA
def test_get_all_films_with_tags(setup_data):
    response = client.get("/films/")
    assert response.status_code == 200
    films = response.json()
    assert len(films) == 2 
    assert len(films[0]["tags"]) == 1
    assert len(films[1]["tags"]) == 1

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

# GET FILM BY INVALID ID
def test_get_film_by_invalid_id():
    response = client.get("/films/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Film stock not found"}

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

# EDIT FILM INVALID ID
def test_edit_film_invalid_id():
    updated_data = {
        "brand": "Kodak",
        "name": "Tri-X 400",
        "format": "35mm",
        "type": "B&W",
        "iso": 400,
        "grain": "Fine"
    }
    response = client.put("/films/999", json=updated_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Film stock not found"}

# EDIT FILM WITH INVALID TAG
def test_edit_film_invalid_tag():
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
        "grain": "Fine",
        "tag_ids": [999] 
    }
    response = client.put(f"/films/{film_id}", json=updated_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "One or more tags not found"}

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

# DELETE FILM INVALID ID
def test_delete_film_invalid_id():
    response = client.delete("/films/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Film stock not found"}

# CREATE FILM WITH INVALID ISO
def test_create_film_invalid_iso():
    film_data = {
        "brand": "Kodak",
        "name": "Portra 400",
        "format": "35mm",
        "type": "Color",
        "iso": -400,  
        "grain": "Fine"
    }
    response = client.post("/films/", json=film_data)
    assert response.status_code == 422  
    assert "greater than 0" in response.json()["detail"][0]["msg"]

    film_data = {
        "brand": "Kodak",
        "name": "Portra 400",
        "format": "35mm",
        "type": "Color",
        "iso": 0,
        "grain": "Fine"
    }
    response = client.post("/films/", json=film_data)
    assert response.status_code == 422  
    assert "greater than 0" in response.json()["detail"][0]["msg"]

# GET COMPATIBLE CAMERAS FOR FILM
def test_get_compatible_cameras():
    film_data = {
        "brand": "Ilford",
        "name": "HP5 Plus",
        "format": "120",
        "type": "B&W",
        "iso": 400,
        "grain": "Medium"
    }
    create_film_response = client.post("/films/", json=film_data)
    film_id = create_film_response.json()["id"]

    camera1_response = client.post("/cameras/", json={
        "brand": "Nikon",
        "model": "F3",
        "format": "35mm",
        "type": "SLR",
        "years": "1980-2000",
        "lens_mount": "Nikon F",
    })
    assert camera1_response.status_code == 200

    camera2_response = client.post("/cameras/", json={
        "brand": "Hasselblad",
        "model": "500C/M",
        "format": "120",
        "type": "Medium Format",
        "years": "1970-1994",
        "lens_mount": "Hasselblad V",
    })
    assert camera2_response.status_code == 200

    response = client.get(f"/films/{film_id}/compatible-cameras")
    assert response.status_code == 200
    compatible_cameras = response.json()
    assert len(compatible_cameras) == 1  
    assert compatible_cameras[0]["model"] == "500C/M"

# GET COMPATIBLE CAMERAS FOR INVALID FILM
def test_get_compatible_cameras_invalid_film():
    response = client.get("/films/999/compatible-cameras")
    assert response.status_code == 404
    assert response.json() == {"detail": "Film stock not found"}

# CREATE A TAG
def test_create_tag():
    tag_data = {
        "name": "SLR"
    }
    response = client.post("/tags/", json=tag_data)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"
    response_data = response.json()
    assert response_data["name"] == "SLR"
    assert "id" in response_data  

# CREATE TAG DUPLICATE
def test_create_tag_duplicate():
    tag_data = {"name": "SLR"}
    response = client.post("/tags/", json=tag_data)
    assert response.status_code == 200 

    response = client.post("/tags/", json=tag_data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Tag already exists"}

# GET ALL TAGS
def test_get_all_tags():
    tag_data = {
        "name": "reversible"
    }
    response = client.post("/tags/", json=tag_data)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"

    response = client.get("/tags/")
    assert response.status_code == 200
    tags = response.json()
    assert isinstance(tags, list)
    assert len(tags) > 0 

# GET TAG BY ID
def test_get_tag_by_id():
    tag_data = {
        "name": "expired-friendly"
    }
    create_response = client.post("/tags/", json=tag_data)
    assert create_response.status_code == 200, f"Expected 200, got {create_response.status_code}: {create_response.json()}"
    tag_id = create_response.json()["id"]

    response = client.get(f"/tags/{tag_id}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["name"] == "expired-friendly"
    assert response_data["id"] == tag_id

# GET TAG BY INVALID ID
def test_get_tag_by_invalid_id():
    response = client.get("/tags/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Tag not found"}

# EDIT A TAG
def test_edit_tag():
    tag_data = {
        "name": "moda"
    }
    create_response = client.post("/tags/", json=tag_data)
    assert create_response.status_code == 200, f"Expected 200, got {create_response.status_code}: {create_response.json()}"
    tag_id = create_response.json()["id"]

    updated_data = {
        "name": "fashion"
    }
    response = client.put(f"/tags/{tag_id}", json=updated_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["name"] == "fashion"
    assert response_data["id"] == tag_id

# EDIT TAG DUPLICATE NAME
def test_edit_tag_duplicate_name():
    tag1_data = {"name": "moda"}
    tag1_response = client.post("/tags/", json=tag1_data)
    assert tag1_response.status_code == 200
    tag1_id = tag1_response.json()["id"]

    tag2_data = {"name": "fashion"}
    tag2_response = client.post("/tags/", json=tag2_data)
    assert tag2_response.status_code == 200
    tag2_id = tag2_response.json()["id"]

    updated_data = {"name": "fashion"}
    response = client.put(f"/tags/{tag1_id}", json=updated_data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Tag name already exists"}

# EDIT TAG INVALID ID
def test_edit_tag_invalid_id():
    updated_data = {"name": "fashion"}
    response = client.put("/tags/999", json=updated_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Tag not found"}

# DELETE TAG
def test_delete_tag():
    tag_data = {
        "name": "formato-medio"
    }
    create_response = client.post("/tags/", json=tag_data)
    assert create_response.status_code == 200, f"Expected 200, got {create_response.status_code}: {create_response.json()}"
    tag_id = create_response.json()["id"]

    response = client.delete(f"/tags/{tag_id}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Tag with id {tag_id} deleted successfully"}

    response = client.get(f"/tags/{tag_id}")
    assert response.status_code == 404

# DELETE TAG INVALID ID
def test_delete_tag_invalid_id():
    response = client.delete("/tags/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Tag not found"}

# DELETE TAG REMOVES ASSOCIATIONS
def test_delete_tag_removes_associations():
    tag_data = {"name": "SLR"}
    tag_response = client.post("/tags/", json=tag_data)
    tag_id = tag_response.json()["id"]

    camera_data = {
        "brand": "Canon",
        "model": "AE-1",
        "format": "35mm",
        "type": "SLR",
        "years": "1976-1984",
        "lens_mount": "Canon FD",
        "tag_ids": [tag_id]
    }
    camera_response = client.post("/cameras/", json=camera_data)
    camera_id = camera_response.json()["id"]

    client.delete(f"/tags/{tag_id}")

    response = client.get(f"/cameras/{camera_id}")
    assert response.status_code == 200
    assert len(response.json()["tags"]) == 0

# CREATE CAMERA W/TAGS
def test_create_camera_with_tags():
    tag1_data = {"name": "SLR"}
    tag2_data = {"name": "moda"}
    tag1_response = client.post("/tags/", json=tag1_data)
    assert tag1_response.status_code == 200, f"Expected 200, got {tag1_response.status_code}: {tag1_response.json()}"
    tag2_response = client.post("/tags/", json=tag2_data)
    assert tag2_response.status_code == 200, f"Expected 200, got {tag2_response.status_code}: {tag2_response.json()}"
    tag1_id = tag1_response.json()["id"]
    tag2_id = tag2_response.json()["id"]

    camera_data = {
        "brand": "Canon",
        "model": "AE-1",
        "format": "35mm",
        "type": "SLR",
        "years": "1976-1984",
        "lens_mount": "Canon FD",
        "tag_ids": [tag1_id, tag2_id]
    }
    response = client.post("/cameras/", json=camera_data)
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data["tags"]) == 2
    assert response_data["tags"][0]["id"] == tag1_id
    assert response_data["tags"][1]["id"] == tag2_id

# CREATE CAMERA WITH INVALID TAG
def test_create_camera_with_invalid_tag():
    camera_data = {
        "brand": "Canon",
        "model": "AE-1",
        "format": "35mm",
        "type": "SLR",
        "years": "1976-1984",
        "lens_mount": "Canon FD",
        "tag_ids": [999] 
    }
    response = client.post("/cameras/", json=camera_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "One or more tags not found"}

# CREATE FILM W/TAGS
def test_create_film_with_tags():
    tag1_data = {"name": "reversible"}
    tag2_data = {"name": "expired-friendly"}
    tag1_response = client.post("/tags/", json=tag1_data)
    assert tag1_response.status_code == 200, f"Expected 200, got {tag1_response.status_code}: {tag1_response.json()}"
    tag2_response = client.post("/tags/", json=tag2_data)
    assert tag2_response.status_code == 200, f"Expected 200, got {tag2_response.status_code}: {tag2_response.json()}"
    tag1_id = tag1_response.json()["id"]
    tag2_id = tag2_response.json()["id"]

    film_data = {
        "brand": "Kodak",
        "name": "Portra 400",
        "format": "35mm",
        "type": "Color",
        "iso": 400,
        "grain": "Fine",
        "tag_ids": [tag1_id, tag2_id]
    }
    response = client.post("/films/", json=film_data)
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data["tags"]) == 2
    assert response_data["tags"][0]["id"] == tag1_id
    assert response_data["tags"][1]["id"] == tag2_id

# CREATE FILM WITH INVALID TAG
def test_create_film_with_invalid_tag():
    film_data = {
        "brand": "Kodak",
        "name": "Portra 400",
        "format": "35mm",
        "type": "Color",
        "iso": 400,
        "grain": "Fine",
        "tag_ids": [999]
    }
    response = client.post("/films/", json=film_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "One or more tags not found"}