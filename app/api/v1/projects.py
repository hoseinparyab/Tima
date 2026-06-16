from fastapi import APIRouter, HTTPException, Query, status

from app.api.v1.workspace import get_workspace_or_404, has_workspace_access
from app.core.ids import ensure_valid_object_id
from app.dependencies import CurrentUser
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])


async def get_project_or_404(project_id: str) -> Project:
    ensure_valid_object_id(project_id, "Project")
    project = await Project.get(project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
    summary="ساخت پروژه جدید",
    description=(
        "پروژه جدید داخل یک workspace می‌سازد. "
        "کاربر باید به آن workspace دسترسی داشته باشد. "
        "فیلدها: `workspace_id`, `name`, `description`, `color`, `is_billable`."
    ),
)
async def create_project(
    payload: ProjectCreate,
    current_user: CurrentUser,
) -> Project:
    ensure_valid_object_id(payload.workspace_id, "Workspace")
    workspace = await get_workspace_or_404(payload.workspace_id)
    if not has_workspace_access(current_user, workspace):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    project = Project(**payload.model_dump())
    await project.insert()
    return project


@router.get(
    "",
    response_model=list[ProjectRead],
    summary="لیست پروژه‌های یک workspace",
    description="همه پروژه‌های متعلق به `workspace_id` داده‌شده را برمی‌گرداند. پارامتر `workspace_id` اجباری است.",
)
async def list_projects(
    current_user: CurrentUser,
    workspace_id: str = Query(...),
) -> list[Project]:
    ensure_valid_object_id(workspace_id, "Workspace")
    workspace = await get_workspace_or_404(workspace_id)
    if not has_workspace_access(current_user, workspace):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return await Project.find(Project.workspace_id == workspace_id).to_list()


@router.get(
    "/{project_id}",
    response_model=ProjectRead,
    summary="جزئیات یک پروژه",
    description="اطلاعات یک پروژه را با شناسه آن برمی‌گرداند. دسترسی از طریق workspace والد کنترل می‌شود.",
)
async def get_project(
    project_id: str,
    current_user: CurrentUser,
) -> Project:
    project = await get_project_or_404(project_id)
    workspace = await get_workspace_or_404(project.workspace_id)
    if not has_workspace_access(current_user, workspace):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return project


@router.put(
    "/{project_id}",
    response_model=ProjectRead,
    summary="ویرایش پروژه",
    description="فیلدهای `name`, `description`, `color`, `is_billable` را به‌صورت جزئی (partial) به‌روزرسانی می‌کند.",
)
async def update_project(
    project_id: str,
    payload: ProjectUpdate,
    current_user: CurrentUser,
) -> Project:
    project = await get_project_or_404(project_id)
    workspace = await get_workspace_or_404(project.workspace_id)
    if not has_workspace_access(current_user, workspace):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(project, key, value)
    await project.save()
    return project


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="حذف پروژه",
    description="پروژه را به‌طور دائم حذف می‌کند. فقط کاربران دارای دسترسی به workspace والد مجازند.",
)
async def delete_project(
    project_id: str,
    current_user: CurrentUser,
) -> None:
    project = await get_project_or_404(project_id)
    workspace = await get_workspace_or_404(project.workspace_id)
    if not has_workspace_access(current_user, workspace):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    await project.delete()
