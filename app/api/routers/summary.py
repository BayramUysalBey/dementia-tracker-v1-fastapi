import uuid
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.db.models.users import User
from app.services.care_assignment import CareAssignmentService
from app.services.summary_client import SummaryClient, get_summary_client
from app.services.summary import SummaryService

router = APIRouter()


@router.get("/{patient_id}/summary")
async def get_patient_summary(
    patient_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    care_service: CareAssignmentService = Depends(CareAssignmentService),
    summary_service: SummaryService = Depends(SummaryService),
    summary_client: SummaryClient = Depends(get_summary_client),
):
    await care_service.verify_caregiver_access(caregiver_id=current_user.id, patient_id=patient_id)

    data = await summary_service.gather_data(patient_id)

    summary = await summary_client.summarize(data)
    return {"summary": summary}