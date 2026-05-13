from fastapi import FastAPI
from app.api.routers import api_router
from app.core.settings import settings
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Dementia Tracker V1 API",
    description="Main API for Dementia Tracker",
    version=settings.VERSION
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(api_router, prefix="/api")

@app.get("/")
async def main():
    return {"message": "Welcome to the Dementia Tracker V1 API!"}