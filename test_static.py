from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
response = client.get("/_nicegui/3.12.0/static/vue.esm-browser.prod.js")
print("STATUS:", response.status_code)
print("BODY length:", len(response.content))
