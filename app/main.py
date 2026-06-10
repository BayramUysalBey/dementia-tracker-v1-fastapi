from fastapi import FastAPI
from app.api.routers import api_router
from app.core.settings import settings
from fastapi.staticfiles import StaticFiles
from nicegui import ui
from app.api.routers.status import health
from app.db.session import get_db, engine
from app.db.base import BaseDBModel
import httpx
from contextlib import asynccontextmanager


@asynccontextmanager #for lifespan
async def lifespan(app: FastAPI):
    print("Running database creation...")
    async with engine.begin() as conn:
        await conn.run_sync(BaseDBModel.metadata.create_all)
        # I explicitly used the lifespan event to generate 
        # schemas because I did not have a CI/CD pipeline 
        # configured to run Alembic migrations against the 
        # cloud database. In a professional environment, 
        # I would remove create_all and strictly execute 
        # Alembic via GitHub Actions.
    print("Database tables ensured!")
    yield


app = FastAPI(
    title="Dementia Tracker V1 API",
    description="Main API for Dementia Tracker",
    version=settings.VERSION,
    lifespan=lifespan
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
    

@ui.page("/", title="Dementia Tracker")
def display_dashboard():
    ui.switch('Dark mode', on_change=lambda e: ui.run_javascript(f'Quasar.Dark.set({str(e.value).lower()})'))
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
                response = await client.post("https://dementia-tracker.fastapicloud.dev/api/v1/auth/token", data=data)
            if response.status_code == 200:
                session["token"] = response.json().get("access_token")
                ui.notify("Login successful! Token saved.", type="positive")
            else:
                ui.notify("Login failed. Check credentials.", type="negative")
                
    ui.button("Login", on_click=do_login)
    

    ui.label("Authentication").classes('text-2xl font-bold')
    first_name = ui.input("First Name")
    last_name = ui.input("Last Name")
    email = ui.input("Email")
    user_name = ui.input("Username")
    password = ui.input("Password", password=True)
    async def do_register():
        data = {"first_name": first_name.value,
                "last_name": last_name.value,
                "role": "caregiver",
                "email": email.value,
                "username": user_name.value,
                "password": password.value}
        async with httpx.AsyncClient() as client:
            response = await client.post("https://dementia-tracker.fastapicloud.dev/api/v1/users/create", json=data)
        if response.status_code == 201:
            ui.notify("Account created successfully! You can now log in.", type="positive")
        else:
            ui.notify(f"Register failed: {response.text}", type="negative")
    ui.button("Register", on_click=do_register)


    ui.separator().classes('my-6')
    ui.label("My Habits").classes('text-2xl font-bold')
    table_container = ui.column().classes("w-full")
    async def fetch_habits():
        if not session["token"]:
            ui.notify("Please login first to get a JWT!", type="warning")
            return
        headers = {"Authorization": f"Bearer {session['token']}"}    
        async with httpx.AsyncClient() as client:
            response = await client.get("https://dementia-tracker.fastapicloud.dev/api/v1/habit", headers=headers)    
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

    ui.separator().classes('my-6')
    ui.label("Create a New Habit").classes('text-2xl font-bold')
    
    habit_name_input = ui.input("Habit Name (e.g., Morning Walk)")
    frequency_input = ui.input("Target Frequency (e.g., Daily)")
    
    async def create_new_habit():
        if not session.get("token"):
            ui.notify("Please login first!", type="warning")
            return
            
        data = {
            "name": habit_name_input.value,
            "target_frequency": frequency_input.value,
            "streak_count": 0
        }
        
        headers = {"Authorization": f"Bearer {session['token']}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post("https://dementia-tracker.fastapicloud.dev/api/v1/habit", json=data, headers=headers)
            
        if response.status_code == 201:
            ui.notify("Habit created successfully!", type="positive")
            habit_name_input.value = ""
            frequency_input.value = ""
            await fetch_habits()
        else:
            ui.notify(f"Failed to create habit: {response.text}", type="negative")
            
    ui.button("Create Habit", on_click=create_new_habit).classes('bg-green-600 text-white')


ui.run_with(app, storage_secret=settings.SECRET_KEY or "dev-secret-key-1234")
