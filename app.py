from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

class HealthStatus(BaseModel):
	status: str
	database: str
	version: str


@app.get("/")
async def home():
	return {
		"message": "Welcome to the Dementia Tracker V1 API"
	}

@app.get("/health", response_model=HealthStatus)
async def health():
	"""
	Checks the health status of the API and its dependencies.
	"""
	return {
		"status": "up",
		"database": "disconnected",
		"version": "1.0.0"
	}