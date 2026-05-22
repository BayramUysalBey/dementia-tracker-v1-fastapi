import uuid
from pydantic import BaseModel, ConfigDict
from app.db.models.monthly_report import MonthlyReportType

class MonthlyReportBase(BaseModel):
    title: str | None = None
    content: str | None = None
    category: MonthlyReportType | None = None
    user_note: MonthlyReportType | None = None
    author_note: MonthlyReportType | None = None

       
class MonthlyReportCreate(MonthlyReportBase):
   user_id: uuid.UUID
   title: str | None = None
   content: str | None = None
   category: MonthlyReportType | None = None
   user_note: MonthlyReportType | None = None
   author_note: MonthlyReportType | None = None
    

class MonthlyReportUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    category: MonthlyReportType | None = None
    user_note: MonthlyReportType | None = None
    author_note: MonthlyReportType | None = None
    
    
class MonthlyReportRead(MonthlyReportBase):
    id: uuid.UUID
    user_id: uuid.UUID
    author_id: uuid.UUID
    title: str | None = None
    content: str | None = None
    category: MonthlyReportType | None = None
    user_note: MonthlyReportType | None = None
    author_note: MonthlyReportType | None = None
    model_config = ConfigDict(from_attributes=True)