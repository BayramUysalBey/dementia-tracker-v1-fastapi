from fastapi import APIRouter
from app.api.routers import users, status, accounts, auth, emergency_contact, medication, journal


api_router = APIRouter()
api_router.include_router(users.router, prefix="/v1/users", tags=["Users"])
api_router.include_router(status.router, prefix="/v1/status", tags=["Status"])
api_router.include_router(accounts.router, prefix="/v1/accounts", tags=["Accounts"])
api_router.include_router(auth.router, prefix="/v1/auth", tags=["Auth"])
api_router.include_router(emergency_contact.router, prefix="/v1/emergency_contact", tags=["Emergency Contact"])
api_router.include_router(medication.router, prefix="/v1/medication", tags=["Medication"])
api_router.include_router(journal.router, prefix="/v1/journal", tags=["Journal"])