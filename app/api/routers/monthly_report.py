import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from app.schemas.monthly_report import MonthlyReportCreate, MonthlyReportRead, MonthlyReportUpdate
from app.services.monthly_report import MonthlyReportService
from app.api.deps import get_current_user
from app.db.models.monthly_report import MonthlyReport
from app.db.models.users import User


router = APIRouter()


@router.post("", response_model=MonthlyReportRead, status_code=status.HTTP_201_CREATED)
async def create_monthly_report(
    monthly_report_in: MonthlyReportCreate,
    monthly_report_service: MonthlyReportService = Depends(MonthlyReportService),
    current_user: User = Depends(get_current_user)
    ):
    return await monthly_report_service.create_monthly_report(monthly_report_in, current_user_id=current_user.id)


@router.get("", response_model=List[MonthlyReportRead])
async def read_monthly_report(
    skip: int = 0, 
    limit: int = 100,
    monthly_report_service: MonthlyReportService = Depends(MonthlyReportService),
    current_user: User = Depends(get_current_user)
):
    monthly_reports = await monthly_report_service.get_all_monthly_report(user_id=current_user.id, skip=skip, limit=limit)
    if not monthly_reports:
        return []       
    return list(monthly_reports)


@router.patch("/{monthly_report_id}", response_model=MonthlyReportRead, status_code=status.HTTP_200_OK)
async def update_monthly_report(
    monthly_report_id: uuid.UUID,
    monthly_report_in: MonthlyReportUpdate,
    current_user: User = Depends(get_current_user),
    monthly_report_service: MonthlyReportService = Depends(MonthlyReportService)
):
    return await monthly_report_service.update_monthly_report(monthly_report_id, current_user.id, monthly_report_in)