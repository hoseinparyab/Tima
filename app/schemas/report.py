from pydantic import BaseModel


class ReportItem(BaseModel):
    id: str
    name: str
    total_duration: int


class DailyReportItem(BaseModel):
    project_id: str
    project_name: str
    total_duration: int


class DailyReport(BaseModel):
    date: str
    total_duration: int
    entries: list[DailyReportItem]
