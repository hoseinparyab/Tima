from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, HTTPException, Query, status

from app.dependencies import CurrentUser
from app.models.project import Project
from app.models.time_entry import TimeEntry
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.report import DailyReport, DailyReportItem, ReportItem

router = APIRouter(prefix="/reports", tags=["reports"])


def parse_date_range(from_date: date, to_date: date) -> tuple[datetime, datetime]:
    if to_date < from_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="'to' must be on or after 'from'",
        )
    start = datetime.combine(from_date, time.min)
    end = datetime.combine(to_date + timedelta(days=1), time.min)
    return start, end


async def get_accessible_project_ids(current_user: User) -> list[str]:
    user_id = str(current_user.id)
    workspaces = await Workspace.find(
        {"$or": [{"owner_id": user_id}, {"members": user_id}]}
    ).to_list()
    workspace_ids = [str(ws.id) for ws in workspaces]
    if not workspace_ids:
        return []

    projects = await Project.find({"workspace_id": {"$in": workspace_ids}}).to_list()
    return [str(p.id) for p in projects]


@router.get(
    "/user",
    response_model=list[ReportItem],
    summary="گزارش زمان به تفکیک کاربر",
    description=(
        "مجموع زمان کارکرد (ثانیه) هر کاربر را در بازه `from` تا `to` برمی‌گرداند. "
        "فقط پروژه‌های workspaceهای قابل دسترس کاربر جاری لحاظ می‌شوند."
    ),
)
async def user_report(
    current_user: CurrentUser,
    from_date: date = Query(..., alias="from"),
    to_date: date = Query(..., alias="to"),
) -> list[ReportItem]:
    start, end = parse_date_range(from_date, to_date)
    project_ids = await get_accessible_project_ids(current_user)
    if not project_ids:
        return []

    entries = await TimeEntry.find(
        {"project_id": {"$in": project_ids}, "start": {"$gte": start, "$lt": end}, "duration": {"$ne": None}}
    ).to_list()

    totals: dict[str, int] = {}
    for entry in entries:
        totals[entry.user_id] = totals.get(entry.user_id, 0) + (entry.duration or 0)

    result: list[ReportItem] = []
    for user_id, total in totals.items():
        user = await User.get(user_id)
        result.append(
            ReportItem(
                id=user_id,
                name=user.fullname if user else "Unknown",
                total_duration=total,
            )
        )
    return result


@router.get(
    "/project",
    response_model=list[ReportItem],
    summary="گزارش زمان به تفکیک پروژه",
    description=(
        "مجموع زمان کارکرد (ثانیه) هر پروژه را در بازه `from` تا `to` برمی‌گرداند. "
        "فقط پروژه‌های workspaceهای قابل دسترس کاربر جاری لحاظ می‌شوند."
    ),
)
async def project_report(
    current_user: CurrentUser,
    from_date: date = Query(..., alias="from"),
    to_date: date = Query(..., alias="to"),
) -> list[ReportItem]:
    start, end = parse_date_range(from_date, to_date)
    project_ids = await get_accessible_project_ids(current_user)
    if not project_ids:
        return []

    entries = await TimeEntry.find(
        {"project_id": {"$in": project_ids}, "start": {"$gte": start, "$lt": end}, "duration": {"$ne": None}}
    ).to_list()

    totals: dict[str, int] = {}
    for entry in entries:
        totals[entry.project_id] = totals.get(entry.project_id, 0) + (entry.duration or 0)

    result: list[ReportItem] = []
    for project_id, total in totals.items():
        project = await Project.get(project_id)
        result.append(
            ReportItem(
                id=project_id,
                name=project.name if project else "Unknown",
                total_duration=total,
            )
        )
    return result


@router.get(
    "/daily",
    response_model=DailyReport,
    summary="گزارش روزانه",
    description=(
        "خلاصه زمان کارکرد کاربر جاری در یک روز مشخص. "
        "شامل مجموع کل و تفکیک به تفکیک پروژه. پارامتر `date` با فرمت `YYYY-MM-DD`."
    ),
)
async def daily_report(
    current_user: CurrentUser,
    date: date = Query(...),
) -> DailyReport:
    day_start = datetime.combine(date, time.min)
    day_end = day_start + timedelta(days=1)

    entries = await TimeEntry.find(
        TimeEntry.user_id == str(current_user.id),
        TimeEntry.start >= day_start,
        TimeEntry.start < day_end,
        TimeEntry.duration != None,  # noqa: E711
    ).to_list()

    totals: dict[str, int] = {}
    for entry in entries:
        totals[entry.project_id] = totals.get(entry.project_id, 0) + (entry.duration or 0)

    items: list[DailyReportItem] = []
    total_duration = 0
    for project_id, duration in totals.items():
        project = await Project.get(project_id)
        items.append(
            DailyReportItem(
                project_id=project_id,
                project_name=project.name if project else "Unknown",
                total_duration=duration,
            )
        )
        total_duration += duration

    return DailyReport(
        date=date.isoformat(),
        total_duration=total_duration,
        entries=items,
    )
