from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import  Depends
from app.db.session import get_db
from app.db.crud.emergency_contacts import EmergencyContactCRUD
from app.db.models.emergency_contact import EmergencyContact
from app.schemas.emergency_contact import EmergencyContactCreate


class EmergencyContactCService:
    def __init__(
        self, 
        db: AsyncSession = Depends(get_db), 
        crud: EmergencyContactCRUD = Depends(EmergencyContactCRUD)
    ):
        self.db = db
        self.crud = crud