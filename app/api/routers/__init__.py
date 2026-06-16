from fastapi import APIRouter
from app.api.routers import users, status, accounts, auth, emergency_contact, medication, journal, reminder, media, habit, note, care_assignment


api_router = APIRouter()
api_router.include_router(users.router, prefix="/v1/users", tags=["Users"])
api_router.include_router(status.router, prefix="/v1/status", tags=["Status"])
api_router.include_router(accounts.router, prefix="/v1/accounts", tags=["Accounts"])
api_router.include_router(auth.router, prefix="/v1/auth", tags=["Auth"])
api_router.include_router(emergency_contact.router, prefix="/v1/emergency_contact", tags=["Emergency Contact"])
api_router.include_router(medication.router, prefix="/v1/medication", tags=["Medication"])
api_router.include_router(journal.router, prefix="/v1/journal", tags=["Journal"])
api_router.include_router(reminder.router, prefix="/v1/reminder", tags=["Reminder"])
api_router.include_router(media.router, prefix="/v1/media", tags=["Media"])
api_router.include_router(habit.router, prefix="/v1/habit", tags=["Habit"])
api_router.include_router(note.router, prefix="/v1/note", tags=["Note"])
api_router.include_router(care_assignment.router, prefix="/v1/care-assignments", tags=["Care Assignments"])