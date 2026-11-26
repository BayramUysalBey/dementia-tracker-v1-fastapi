import uuid
from fastapi import Depends
from app.db.crud.habit import HabitCRUD
from app.schemas.habit import HabitRead
from app.db.crud.medication import MedicationCRUD
from app.schemas.medication import MedicationRead
from app.db.crud.note import NoteCRUD
from app.schemas.note import NoteRead
from app.db.crud.journal import JournalCRUD
from app.schemas.journal import JournalRead

class SummaryService:
    def __init__(
        self,
        habit_crud: HabitCRUD = Depends(HabitCRUD),
        medication_crud: MedicationCRUD = Depends(MedicationCRUD),
        note_crud: NoteCRUD = Depends(NoteCRUD),
        journal_crud: JournalCRUD = Depends(JournalCRUD)
    ):
        self.habit_crud = habit_crud
        self.medication_crud = medication_crud
        self.note_crud = note_crud
        self.journal_crud = journal_crud

    async def get_habits(self, patient_id: uuid.UUID) -> list[dict]:
        habits = await self.habit_crud.habit_for_user(user_id=patient_id)
        return [HabitRead.model_validate(h).model_dump(mode="json") for h in habits]

    async def get_medications(self, patient_id: uuid.UUID) -> list[dict]:
        medications = await self.medication_crud.medication_for_user(user_id=patient_id)
        return [MedicationRead.model_validate(m).model_dump(mode="json") for m in medications]

    async def get_notes(self, patient_id: uuid.UUID) -> list[dict]:
        notes = await self.note_crud.note_for_user(user_id=patient_id)
        return [NoteRead.model_validate(n).model_dump(mode="json") for n in notes]

    async def get_journals(self, patient_id: uuid.UUID) -> list[dict]:
        journals = await self.journal_crud.journal_for_user(user_id=patient_id)
        return [JournalRead.model_validate(j).model_dump(mode="json") for j in journals]

    async def gather_data(self, patient_id: uuid.UUID) -> dict:
        return {
            "habits": await self.get_habits(patient_id),
            "medications": await self.get_medications(patient_id),
            "notes": await self.get_notes(patient_id),
            "journals": await self.get_journals(patient_id)
            
        }