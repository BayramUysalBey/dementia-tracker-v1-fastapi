from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


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
	return {
		"status": "up",
		"database": "disconnected",
		"version": "1.0.0"
	}