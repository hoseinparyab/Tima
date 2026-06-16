from fastapi import APIRouter, Depends, HTTPException, status

from beanie.odm.operators.update.general import Set

from app.core.ids import ensure_valid_object_id
from app.dependencies import CurrentUser
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.workspace import AddMemberRequest, WorkspaceCreate, WorkspaceRead

router = APIRouter(prefix="/workspace", tags=["workspace"])


def has_workspace_access(user: User, workspace: Workspace) -> bool:
    user_id = str(user.id)
    return user_id == workspace.owner_id or user_id in workspace.members


async def get_workspace_or_404(workspace_id: str) -> Workspace:
    ensure_valid_object_id(workspace_id, "Workspace")
    workspace = await Workspace.get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    return workspace


@router.post(
    "",
    response_model=WorkspaceRead,
    status_code=status.HTTP_201_CREATED,
    summary="ساخت workspace جدید",
    description=(
        "یک فضای کاری جدید می‌سازد. کاربر جاری به‌عنوان مالک (owner) ثبت می‌شود "
        "و به لیست اعضا اضافه می‌گردد. شناسه workspace به `workspace_ids` کاربر افزوده می‌شود."
    ),
)
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

    workspace_id = str(workspace.id)
    updated_ids = [*current_user.workspace_ids, workspace_id]
    await User.find(User.id == current_user.id).update(Set({User.workspace_ids: updated_ids}))
    current_user.workspace_ids = updated_ids
    return workspace


@router.get(
    "",
    response_model=list[WorkspaceRead],
    summary="لیست workspaceهای من",
    description="همه workspaceهایی را برمی‌گرداند که کاربر جاری مالک یا عضو آن‌هاست.",
)
async def list_workspaces(current_user: CurrentUser) -> list[Workspace]:
    user_id = str(current_user.id)
    return await Workspace.find(
        {"$or": [{"owner_id": user_id}, {"members": user_id}]}
    ).to_list()


@router.get(
    "/{workspace_id}",
    response_model=WorkspaceRead,
    summary="جزئیات یک workspace",
    description=(
        "اطلاعات یک workspace را با شناسه MongoDB برمی‌گرداند. "
        "فقط مالک یا اعضای همان workspace دسترسی دارند. "
        "شناسه باید ۲۴ کاراکتر hex باشد (مثال: `6a3154dbbad755e188506348`)."
    ),
)
async def get_workspace(
    workspace_id: str,
    current_user: CurrentUser,
) -> Workspace:
    workspace = await get_workspace_or_404(workspace_id)
    if not has_workspace_access(current_user, workspace):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return workspace


@router.post(
    "/{workspace_id}/add-member",
    response_model=WorkspaceRead,
    summary="افزودن عضو به workspace",
    description=(
        "یک کاربر موجود را به workspace اضافه می‌کند. فقط **مالک** workspace مجاز است. "
        "بدنه درخواست: `{ \"user_id\": \"<شناسه کاربر>\" }`. "
        "شناسه workspace و user_id هر دو باید ObjectId معتبر MongoDB باشند."
    ),
)
async def add_member(
    workspace_id: str,
    payload: AddMemberRequest,
    current_user: CurrentUser,
) -> Workspace:
    workspace = await get_workspace_or_404(workspace_id)
    if str(current_user.id) != workspace.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owner can add members")

    ensure_valid_object_id(payload.user_id, "User")
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
