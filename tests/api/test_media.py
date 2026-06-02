import pytest
from httpx import AsyncClient
import io # fake file creator
from app.core.settings import settings


@pytest.mark.asyncio
async def test_create_and_read_media(
    client: AsyncClient,
    user_mock_data: dict
):
    # 1. Create a user and get token
    response_create = await client.post("/api/v1/users/create", json=user_mock_data)
    assert response_create.status_code == 201
    created_user_id = response_create.json()["id"]
    
    login_data = {
        "username": user_mock_data["email"],
        "password": user_mock_data["password"]
    }
    response_login = await client.post("/api/v1/auth/token", data=login_data)
    assert response_login.status_code == 200
    token = response_login.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}
    
	# 2. Create an invalid .txt file in memory
    fake_txt_file = io.BytesIO(b"This is just some text, definitely not an image.")
    
    files = {"file": ("invalid.txt", fake_txt_file, "text/plain")}
    form_data = {
        "type": "photo", 
        "name": "Trying to trick the system"
    }
    response_media = await client.post(
        "/api/v1/media", 
        data=form_data,
        files=files,
        headers=auth_headers
    )
    assert response_media.status_code == 400

    
    # 3. Create an media
    with open("tests/mock_media.jpg", "rb") as f:
        files = {"file": ("mock_media.jpg", f, "image/jpeg")}
        form_data = {
        	"type": "photo", 
        	"name": "This is your memories"
    }
        response_media = await client.post(
        	"/api/v1/media", 
        	data=form_data,
        	files=files,
        	headers=auth_headers
    )

    assert response_media.status_code == 201
    created_media = response_media.json()
    assert created_media["user_id"] == created_user_id
    assert created_media["media_url"].endswith(".jpg")
    assert created_media["media_url"].startswith(f"/{settings.MEDIA_UPLOAD_DIR}/")
    assert "user_id" in created_media
    
    # 4. Read media
    response_read = await client.get("/api/v1/media", headers=auth_headers)
    assert response_read.status_code == 200
    media_list = response_read.json()
    assert len(media_list) == 1
    assert media_list[0]["id"] == created_media["id"]
    

@pytest.mark.asyncio  
async def test_create_media_unauthorized(client: AsyncClient):
    fake_img_file = io.BytesIO(b"fake image data")
    files = {"file": ("test_image.jpg", fake_img_file, "image/jpeg")}
    form_data = {"type": "photo", "name": "Sneaky upload"}
    response = await client.post("/api/v1/media", data=form_data, files=files)
    assert response.status_code == 401
    error_response = response.json()
    assert error_response["detail"] == "Not authenticated"
    
    
@pytest.mark.asyncio
async def test_create_media_invalid_file_type(client: AsyncClient, user_mock_data: dict):
    response_create = await client.post("/api/v1/users/create", json=user_mock_data)
    assert response_create.status_code == 201
    created_user_id = response_create.json()["id"]
    
    login_data = {
        "username": user_mock_data["email"],
        "password": user_mock_data["password"]
    }
    response_login = await client.post("/api/v1/auth/token", data=login_data)
    assert response_login.status_code == 200
    token = response_login.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}
    
    fake_txt_file = io.BytesIO(b"fake text content")
    files = {"file": ("invalid.txt", fake_txt_file, "text/plain")}
    form_data = {"type": "photo", "name": "Trying to trick the system"}
    response_media = await client.post(
        "/api/v1/media", 
        data=form_data,
        files=files,
        headers=auth_headers
    )
    assert response_media.status_code == 400
    

@pytest.mark.asyncio
async def test_create_media_no_journal_id(client: AsyncClient, user_mock_data: dict):
    response_create = await client.post("/api/v1/users/create", json=user_mock_data)
    assert response_create.status_code == 201
    created_user_id = response_create.json()["id"]
    
    login_data = {
        "username": user_mock_data["email"],
        "password": user_mock_data["password"]
    }
    response_login = await client.post("/api/v1/auth/token", data=login_data)
    assert response_login.status_code == 200
    token = response_login.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}
    
    fake_img_file = io.BytesIO(b"fake image data")
    files = {"file": ("test_image.jpg", fake_img_file, "image/jpeg")}
    form_data = {
        "type": "photo", 
        "name": "Floating memory"
    }
    response_media = await client.post(
        "/api/v1/media", 
        data=form_data,
        files=files,
        headers=auth_headers
    )   
    assert response_media.status_code == 201
    created_media = response_media.json()
    assert created_media.get("journal_id") is None