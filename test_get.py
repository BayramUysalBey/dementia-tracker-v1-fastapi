from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
response = client.get("/")
print("STATUS:", response.status_code)
print("BODY:")
print(response.text)
