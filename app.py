from fastapi import FastAPI

from pydantic import BaseModel

app = FastAPI()

class HealthStatus(BaseModel):
	status: str
	database: str
	version: str


@app.get("/")
def home():
	return {
		"message": "Welcome to the Dementia Tracker V2 API"
	}

@app.get("/health", response_model=HealthStatus)
async def health():
	"""
	Docstring for health
	"""
	return {
		"status": "up",
		"database": "disconnected",
		"version": "2.0.0"
	}