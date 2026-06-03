from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
response = client.get("/")
print("STATUS:", response.status_code)
print("HEADERS:")
for k, v in response.headers.items():
    print(f"{k}: {v}")
