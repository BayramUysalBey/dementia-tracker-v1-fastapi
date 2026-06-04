import sentry_sdk
from fastapi import FastAPI
from app.api.routers import api_router
from app.core.settings import settings
from fastapi.staticfiles import StaticFiles
from nicegui import ui
from app.api.routers.status import health
from app.db.session import get_db, engine
from app.db.base import BaseDBModel
import httpx
import asyncio

async def _init_db():
    async with engine.begin() as conn:
        await conn.run_sync(BaseDBModel.metadata.create_all)

try:
    asyncio.run(_init_db())
    print("Database tables ensured!")
except Exception as e:
    print(f"DB init failed: {e}")

import httpx



app = FastAPI(
    title="Dementia Tracker V1 API",
    description="Main API for Dementia Tracker",
    version=settings.VERSION
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(api_router, prefix="/api")

@app.get("/api/welcome")
async def main():
    return {"message": "Welcome to the Dementia Tracker V1 API!"}

# niceGUI: frontends for api endpoints
async def check_real_health():
    db_generator = get_db()
    db_session = await anext(db_generator)
    real_status = await health(db_session=db_session)
    ui.notify(f"DB Status: {real_status.database}")
    

@ui.page("/")
def display_dashboard():
    with ui.column().classes('p-6 gap-3'):
        ui.label("NiceGUI + FastAPI United!").classes('text-2xl font-bold text-indigo-900')
        ui.label("Both running on the same port in unified memory heap.")
        ui.button("Test Real Health", on_click=check_real_health)
        
        session = {"token": None}
        ui.label("Authentication").classes('text-2xl font-bold')
        email_input = ui.input("Email")
        password_input = ui.input("Password", password=True)
        async def do_login():
            data = {"username": email_input.value, "password": password_input.value}
            async with httpx.AsyncClient() as client:
                response = await client.post(settings.BASE_URL_FRONT_ONE, data=data)
            if response.status_code == 200:
                session["token"] = response.json().get("access_token")
                ui.notify("Login successful! Token saved.", type="positive")
            else:
                ui.notify("Login failed. Check credentials.", type="negative")
                
    ui.button("Login", on_click=do_login)

    ui.separator().classes('my-6')
    ui.label("My Habits").classes('text-2xl font-bold')
    table_container = ui.column().classes("w-full")
    async def fetch_habits():
        if not session["token"]:
            ui.notify("Please login first to get a JWT!", type="warning")
            return
        headers = {"Authorization": f"Bearer {session['token']}"}    
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.BASE_URL_FRONT_TWO, headers=headers)    
            if response.status_code == 200:
                habits_data = response.json()
                table_container.clear()
                with table_container:
                    if not habits_data:
                        ui.label("No habits found in DB.")
                    else:
                        columns = [
                            {"name": "name", "label": "Habit Name", "field": "name"},
                            {"name": 'target_frequency', "label": "Target Frequency", "field": "target_frequency"},
                            {"name": "streak_count", "label": "Current Streak", "field": "streak_count", "classes": "text-center text-orange-600 font-bold", "headerClasses": "text-center"}
                            
                        ]
                        ui.table(columns=columns, rows=habits_data).classes("w-full")
            else:
                ui.notify("Failed to fetch habits. Invalid token?", type="negative")

    ui.button("Fetch Habits with JWT", on_click=fetch_habits)    

ui.run_with(app, storage_secret=settings.SECRET_KEY or "dev-secret-key-1234")
