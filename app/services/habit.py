from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import  Depends
from app.db.session import get_db
from app.db.crud.habit import HabitCRUD
from app.db.models.habit import Habit
from app.schemas.habit import HabitCreate, HabitUpdate
import uuid
from fastapi import HTTPException, status, Depends


class HabitService:
    def __init__(
        self, 
        db: AsyncSession = Depends(get_db), 
        crud: HabitCRUD = Depends(HabitCRUD)
    ):
        self.db = db
        self.crud = crud
        
    async def create_habit(self, create_in: HabitCreate, current_user_id: uuid.UUID) -> Habit:
        from app.db.crud.users import UserCRUD
        from app.db.crud.care_assignment import CareAssignmentCRUD
        from app.services.care_assignment import CareAssignmentService
        # Records are authored by a caregiver about a patient. A user may not
        # write a record about themselves — provenance matters for clinical reporting.
        if create_in.user_id == current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Records must be authored by a caregiver, not by the patient"
                        )
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
        habit = await self.crud.create_habit(create_data)
        await self.db.refresh(habit)
        return habit
      
    async def get_all_habit(self, user_id: uuid.UUID, skip: int = 0, limit: int = 1000) -> Sequence[Habit]:
        return await self.crud.habit_for_user(user_id=user_id, skip=skip, limit=limit)
    
    async def update_habit(self, habit_id: uuid.UUID, user_id: uuid.UUID, user_in: HabitUpdate) -> Habit:
        db_object = await self.crud.get_habit_by_id(habit_id)
        if not db_object or db_object.author_id != user_id:
        # Only the author may edit an entry. The subject can read their record
        # (see JournalCRUD.journal_for_user) but not alter what a caregiver wrote.
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
        update_data = user_in.model_dump(exclude_unset=True)
        updated_habit = await self.crud.update_habit(db_object, update_data)
        await self.db.refresh(updated_habit)
        return updated_habit