import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.monthly_report import MonthlyReport
from app.db.session import get_db
from fastapi import Depends


class MonthlyReportCRUD:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
    
    async def create_monthly_report(self, obj_in: dict) -> MonthlyReport:
        db_object = MonthlyReport(**obj_in)
        self.db.add(db_object)
        await self.db.flush()
        return db_object

    async def monthly_report_for_user(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Sequence[MonthlyReport]:
        result = await self.db.execute(select(MonthlyReport).where(MonthlyReport.user_id == user_id).offset(skip).limit(limit))
        return result.scalars().all()

    async def update_monthly_report(self, db_object: MonthlyReport, obj_in: dict) -> MonthlyReport:
        for field, value in obj_in.items():
            if hasattr(db_object, field):
                setattr(db_object, field, value)
                await self.db.flush()
        return db_object
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> Sequence[MonthlyReport]:
        result = await self.db.execute(select(MonthlyReport).offset(skip).limit(limit))
        return result.scalars().all()
    
    async def get_monthly_report_by_id(self, note_id: uuid.UUID) -> MonthlyReport | None:
        result = await self.db.execute(select(MonthlyReport).where(MonthlyReport.id == note_id))
        return result.scalars().first()