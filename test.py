from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_main_home():
	response = client.get("/")
	assert response.status_code == 200
	assert response.json() == {
		"message": "Welcome to the Dementia Tracker V2 API"
	}

def test_health():
	response = client.get("/health")
	assert response.status_code == 200
	assert response.json()["status"] == "up"