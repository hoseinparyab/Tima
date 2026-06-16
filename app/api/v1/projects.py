from fastapi import APIRouter, HTTPException, Query, status

from app.api.v1.workspace import get_workspace_or_404, has_workspace_access
from app.dependencies import CurrentUser
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])


async def get_project_or_404(project_id: str) -> Project:
    project = await Project.get(project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    current_user: CurrentUser,
) -> Project:
    workspace = await get_workspace_or_404(payload.workspace_id)
    if not has_workspace_access(current_user, workspace):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    project = Project(**payload.model_dump())
    await project.insert()
    return project


@router.get("", response_model=list[ProjectRead])
async def list_projects(
    current_user: CurrentUser,
    workspace_id: str = Query(...),
) -> list[Project]:
    workspace = await get_workspace_or_404(workspace_id)
    if not has_workspace_access(current_user, workspace):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return await Project.find(Project.workspace_id == workspace_id).to_list()


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: str,
    current_user: CurrentUser,
) -> Project:
    project = await get_project_or_404(project_id)
    workspace = await get_workspace_or_404(project.workspace_id)
    if not has_workspace_access(current_user, workspace):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return project


@router.put("/{project_id}", response_model=ProjectRead)
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


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: CurrentUser,
) -> None:
    project = await get_project_or_404(project_id)
    workspace = await get_workspace_or_404(project.workspace_id)
    if not has_workspace_access(current_user, workspace):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    await project.delete()
