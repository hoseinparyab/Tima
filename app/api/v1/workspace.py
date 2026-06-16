from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import CurrentUser
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.workspace import AddMemberRequest, WorkspaceCreate, WorkspaceRead

router = APIRouter(prefix="/workspace", tags=["workspace"])


def has_workspace_access(user: User, workspace: Workspace) -> bool:
    user_id = str(user.id)
    return user_id == workspace.owner_id or user_id in workspace.members


async def get_workspace_or_404(workspace_id: str) -> Workspace:
    workspace = await Workspace.get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    return workspace


@router.post("", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    payload: WorkspaceCreate,
    current_user: CurrentUser,
) -> Workspace:
    workspace = Workspace(
        name=payload.name,
        owner_id=str(current_user.id),
        members=[str(current_user.id)],
    )
    await workspace.insert()

    current_user.workspace_ids.append(str(workspace.id))
    await current_user.save()
    return workspace


@router.get("", response_model=list[WorkspaceRead])
async def list_workspaces(current_user: CurrentUser) -> list[Workspace]:
    user_id = str(current_user.id)
    return await Workspace.find(
        {"$or": [{"owner_id": user_id}, {"members": user_id}]}
    ).to_list()


@router.get("/{workspace_id}", response_model=WorkspaceRead)
async def get_workspace(
    workspace_id: str,
    current_user: CurrentUser,
) -> Workspace:
    workspace = await get_workspace_or_404(workspace_id)
    if not has_workspace_access(current_user, workspace):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return workspace


@router.post("/{workspace_id}/add-member", response_model=WorkspaceRead)
async def add_member(
    workspace_id: str,
    payload: AddMemberRequest,
    current_user: CurrentUser,
) -> Workspace:
    workspace = await get_workspace_or_404(workspace_id)
    if str(current_user.id) != workspace.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owner can add members")

    member = await User.get(payload.user_id)
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if payload.user_id not in workspace.members:
        workspace.members.append(payload.user_id)
        await workspace.save()

    if str(workspace.id) not in member.workspace_ids:
        member.workspace_ids.append(str(workspace.id))
        await member.save()

    return workspace
