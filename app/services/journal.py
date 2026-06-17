from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import  Depends
from app.db.session import get_db
from app.db.crud.journal import JournalCRUD
from app.db.models.journal import Journal
from app.schemas.journal import JournalCreate, JournalUpdate
import uuid
from fastapi import HTTPException, status, Depends


class JournalService:
    def __init__(
        self, 
        db: AsyncSession = Depends(get_db), 
        crud: JournalCRUD = Depends(JournalCRUD)
    ):
        self.db = db
        self.crud = crud
        
    async def create_journal(self, create_in: JournalCreate, current_user_id: uuid.UUID) -> Journal:
        from app.db.crud.users import UserCRUD
        from app.db.crud.care_assignment import CareAssignmentCRUD
        from app.services.care_assignment import CareAssignmentService
        user_crud = UserCRUD(self.db)
        patient = await user_crud.get_by_id(create_in.user_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient user not found"
            )
        care_service = CareAssignmentService(
            db=self.db,
            crud=CareAssignmentCRUD(self.db)
        )
        await care_service.verify_caregiver_access(
            caregiver_id=current_user_id,
            patient_id=create_in.user_id
        )

        create_data = create_in.model_dump()
        create_data["author_id"] = current_user_id
        journal = await self.crud.create_journal(create_data)
        await self.db.refresh(journal)
        return journal

    async def get_all_journal(self, user_id: uuid.UUID, skip: int = 0, limit: int = 1000) -> Sequence[Journal]:
        return await self.crud.journal_for_user(user_id=user_id, skip=skip, limit=limit)

    async def update_journal(self, journal_id: uuid.UUID, user_id: uuid.UUID, user_in: JournalUpdate) -> Journal:
        db_object = await self.crud.get_journal_by_id(journal_id)
        if not db_object or db_object.author_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal not found")
        update_data = user_in.model_dump(exclude_unset=True)
        updated_journal = await self.crud.update_journal(db_object, update_data)
        await self.db.refresh(updated_journal)
        return updated_journal
