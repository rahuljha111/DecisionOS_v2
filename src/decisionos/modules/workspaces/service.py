from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from decisionos.core.exceptions import NotFoundError, ForbiddenError
from decisionos.modules.workspaces.models import Workspace
from decisionos.modules.workspaces.repository import WorkspaceRepository
from decisionos.modules.workspaces.schemas import WorkspaceCreate, WorkspaceUpdate

class WorkspaceService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = WorkspaceRepository(session)

    async def create_workspace(self, data: WorkspaceCreate, owner_id: UUID) -> Workspace:
        return await self.repository.create({**data.model_dump(), "owner_id": owner_id})

    async def get_workspace(self, workspace_id: UUID, user_id: UUID) -> Workspace:
        workspace = await self.repository.get_by_id(workspace_id)
        if not workspace:
            raise NotFoundError("Workspace not found")
        if workspace.owner_id != user_id:
            raise ForbiddenError("You do not have access to this workspace")
        return workspace

    async def list_workspaces(self, user_id: UUID) -> list[Workspace]:
        return await self.repository.get_by_owner(user_id)

    async def update_workspace(self, workspace_id: UUID, data: WorkspaceUpdate, user_id: UUID) -> Workspace:
        workspace = await self.get_workspace(workspace_id, user_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(workspace, key, value)
        await self.session.flush()
        return workspace

    async def delete_workspace(self, workspace_id: UUID, user_id: UUID) -> None:
        workspace = await self.get_workspace(workspace_id, user_id)
        await self.repository.delete(workspace)
