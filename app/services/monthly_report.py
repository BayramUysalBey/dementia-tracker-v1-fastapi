from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import  Depends
from app.db.session import get_db
from app.db.crud.monthly_report import MonthlyReportCRUD
from app.db.models.monthly_report import MonthlyReport
from app.schemas.monthly_report import MonthlyReportCreate, MonthlyReportUpdate
import uuid
from fastapi import HTTPException, status, Depends


class MonthlyReportService:
    def __init__(
        self, 
        db: AsyncSession = Depends(get_db), 
        crud: MonthlyReportCRUD = Depends(MonthlyReportCRUD)
    ):
        self.db = db
        self.crud = crud
        
    async def create_monthly_report(self, create_in: MonthlyReportCreate, current_user_id: uuid.UUID) -> MonthlyReport:
        create_data = create_in.model_dump()
        create_data["author_id"] = current_user_id
        note = await self.crud.create_monthly_report(create_data)
        await self.db.refresh(note)
        return note
        
    async def get_all_monthly_report(self, user_id: uuid.UUID, skip: int = 0, limit: int = 1000) -> Sequence[MonthlyReport]:
        return await self.crud.monthly_report_for_user(user_id=user_id, skip=skip, limit=limit)
    
    async def update_monthly_report(self, monthly_report_id: uuid.UUID, user_id: uuid.UUID, user_in: MonthlyReportUpdate):
        db_object = await self.crud.get_monthly_report_by_id(monthly_report_id)
        if not db_object or db_object.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Monthly Report not found")
        update_data = user_in.model_dump(exclude_unset=True)
        updated_monthly_report = await self.crud.update_monthly_report(db_object, update_data)
        await self.db.refresh(updated_monthly_report)
        return updated_monthly_report