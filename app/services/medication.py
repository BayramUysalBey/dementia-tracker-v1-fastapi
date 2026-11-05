from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import  Depends
from app.db.session import get_db
from app.db.crud.medication import MedicationCRUD
from app.db.models.medication import Medication
from app.schemas.medication import MedicationCreate, MedicationUpdate
import uuid
from fastapi import HTTPException, status, Depends


class MedicationService:
    def __init__(
        self, 
        db: AsyncSession = Depends(get_db), 
        crud: MedicationCRUD = Depends(MedicationCRUD)
    ):
        self.db = db
        self.crud = crud
        
    async def create_medication(self, create_in: MedicationCreate, current_user_id: uuid.UUID) -> Medication:
        # Imported inside the function: app.services.care_assignment imports from this module, so a top-level import would be circular.
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
        medication = await self.crud.create_medication(create_data)
        await self.db.refresh(medication)
        return medication
        
    async def get_all_medication(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Sequence[Medication]:
        return await self.crud.medication_for_user(user_id=user_id, skip=skip, limit=limit)
    
    async def update_medication(self, medication_id: uuid.UUID, user_id: uuid.UUID, user_in: MedicationUpdate) -> Medication:
        db_object = await self.crud.get_medication_by_id(medication_id)
        # Only the author may edit an entry. The subject can read their record
        # (see JournalCRUD.journal_for_user) but not alter what a caregiver wrote.
        if not db_object or db_object.author_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")
        update_data = user_in.model_dump(exclude_unset=True)
        updated_medication = await self.crud.update_medication(db_object, update_data)
        await self.db.refresh(updated_medication)
        return updated_medication