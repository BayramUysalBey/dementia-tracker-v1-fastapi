from typing import List, Union, Dict
from fastapi import FastAPI, Query, UploadFile, HTTPException
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

app = FastAPI()

items = ["severity", "disease", "solutions", "meds"]


class HealthStatus(BaseModel):
	status: str
	database: str
	version: str


class Settings(BaseSettings):
	API_KEY: Union[str, int] = ""
	model_config = SettingsConfigDict(env_file=".env", env_file_encoding= "utf-8",)
	
settings = Settings()
print(settings.API_KEY)


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


@app.get("/items/{item_id}")
async def read_item(item_id: int):
	return {"item_id": item_id}


@app.get("/search")
async def searching(q: List[int] = Query(None), limit: int = 10):
    return {"q": q, limit: 2} # The limit value was given as an example.


@app.get("/items")
async def patient_sample():
	return items[2] # The value patient_items is given as an example.



@app.post("/upload/")
async def upload_file(file: UploadFile):
    return {"filename": file.filename, "content_type": file.content_type}


@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int):
    if item_id < 0 or item_id >= len(items):
        raise HTTPException(status_code=404, detail="Item index out of range")
    items.pop(item_id)
    return None


def calculate_total(price: float, quantity: int):
	return float(price + quantity)
# print(calculate_total(2, 7))


def greet(name:str = "Guest"):
	return f"Hello {name}! How are you today?"
# print(greet())


def process_names(names: List[str]):
    return ",".join(names)
# print(process_names(["Alice", "Boby", "Charlize"]))

user_scores: Dict[str, List[int]] = {
    "Alice": [85, 92, 78],
    "Boby": [95, 88, 91],
    "Charlize": [100, 100, 99]
}
# print(f"Scores for Alice: {user_scores['Alice']}")
# print(f"Scores for Alice: {user_scores['Alice'][1]}")