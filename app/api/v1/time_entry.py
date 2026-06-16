from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, HTTPException, Query, status

from app.api.v1.projects import get_project_or_404
from app.api.v1.workspace import get_workspace_or_404, has_workspace_access
from app.dependencies import CurrentUser
from app.models.time_entry import TimeEntry
from app.schemas.time_entry import TimeEntryRead, TimeEntryStart, TimeEntryUpdate

router = APIRouter(prefix="/time-entry", tags=["time-entry"])


async def get_time_entry_or_404(entry_id: str) -> TimeEntry:
    entry = await TimeEntry.get(entry_id)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Time entry not found")
    return entry


async def ensure_project_access(project_id: str, current_user: CurrentUser) -> None:
    project = await get_project_or_404(project_id)
    workspace = await get_workspace_or_404(project.workspace_id)
    if not has_workspace_access(current_user, workspace):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


@router.post("/start", response_model=TimeEntryRead, status_code=status.HTTP_201_CREATED)
async def start_time_entry(
    payload: TimeEntryStart,
    current_user: CurrentUser,
) -> TimeEntry:
    await ensure_project_access(payload.project_id, current_user)

    running = await TimeEntry.find_one(
        TimeEntry.user_id == str(current_user.id),
        TimeEntry.end == None,  # noqa: E711
    )
    if running:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a running timer",
        )

    entry = TimeEntry(
        user_id=str(current_user.id),
        project_id=payload.project_id,
        start=datetime.utcnow(),
        description=payload.description,
    )
    await entry.insert()
    return entry


@router.post("/stop", response_model=TimeEntryRead)
async def stop_time_entry(current_user: CurrentUser) -> TimeEntry:
    entry = await TimeEntry.find_one(
        TimeEntry.user_id == str(current_user.id),
        TimeEntry.end == None,  # noqa: E711
    )
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No running timer found")

    entry.end = datetime.utcnow()
    entry.duration = entry.calc_duration()
    await entry.save()
    return entry


@router.get("", response_model=list[TimeEntryRead])
async def list_time_entries(
    current_user: CurrentUser,
    date: date = Query(..., description="YYYY-MM-DD"),
) -> list[TimeEntry]:
    day_start = datetime.combine(date, time.min)
    day_end = day_start + timedelta(days=1)

    return await TimeEntry.find(
        TimeEntry.user_id == str(current_user.id),
        TimeEntry.start >= day_start,
        TimeEntry.start < day_end,
    ).to_list()


@router.put("/{entry_id}", response_model=TimeEntryRead)
async def update_time_entry(
    entry_id: str,
    payload: TimeEntryUpdate,
    current_user: CurrentUser,
) -> TimeEntry:
    entry = await get_time_entry_or_404(entry_id)
    if entry.user_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    updates = payload.model_dump(exclude_unset=True)
    if "project_id" in updates and updates["project_id"] is not None:
        await ensure_project_access(updates["project_id"], current_user)

    for key, value in updates.items():
        setattr(entry, key, value)

    if entry.end is not None:
        entry.duration = entry.calc_duration()
    else:
        entry.duration = None

    await entry.save()
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_time_entry(
    entry_id: str,
    current_user: CurrentUser,
) -> None:
    entry = await get_time_entry_or_404(entry_id)
    if entry.user_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    await entry.delete()
