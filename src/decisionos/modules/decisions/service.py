from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from decisionos.core.exceptions import NotFoundError, ForbiddenError
from decisionos.modules.decisions.models import Decision
from decisionos.modules.decisions.repository import DecisionRepository
from decisionos.modules.decisions.schemas import DecisionCreate, DecisionUpdate
from decisionos.modules.decisions.enums import DecisionStatus
from decisionos.modules.workspaces.service import WorkspaceService

class DecisionService:
    # Define valid status transitions
    _TRANSITIONS = {
        DecisionStatus.DRAFT: [DecisionStatus.ACTIVE],
        DecisionStatus.ACTIVE: [DecisionStatus.UNDER_REVIEW],
        DecisionStatus.UNDER_REVIEW: [DecisionStatus.DECIDED],
        DecisionStatus.DECIDED: [DecisionStatus.COMPLETED],
        DecisionStatus.COMPLETED: [],
    }

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = DecisionRepository(session)
        self.workspace_service = WorkspaceService(session)

    def _validate_transition(self, current: DecisionStatus, requested: DecisionStatus):
        if requested not in self._TRANSITIONS.get(current, []):
            raise ForbiddenError(f"Invalid status transition from {current} to {requested}")

    async def _verify_workspace_access(self, workspace_id: UUID, user_id: UUID):
        await self.workspace_service.get_workspace(workspace_id, user_id)

    async def create_decision(self, workspace_id: UUID, data: DecisionCreate, user_id: UUID) -> Decision:
        await self._verify_workspace_access(workspace_id, user_id)
        return await self.repository.create({**data.model_dump(), "workspace_id": workspace_id})

    async def get_decision(self, decision_id: UUID, user_id: UUID) -> Decision:
        decision = await self.repository.get_by_id(decision_id)
        if not decision:
            raise NotFoundError("Decision not found")
        await self._verify_workspace_access(decision.workspace_id, user_id)
        return decision

    async def list_decisions(self, workspace_id: UUID, user_id: UUID) -> list[Decision]:
        await self._verify_workspace_access(workspace_id, user_id)
        return await self.repository.get_by_workspace(workspace_id)

    async def update_decision(self, decision_id: UUID, data: DecisionUpdate, user_id: UUID) -> Decision:
        decision = await self.get_decision(decision_id, user_id)
        
        if data.status and data.status != decision.status:
            self._validate_transition(decision.status, data.status)

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(decision, key, value)
        
        await self.session.flush()
        return decision

    async def delete_decision(self, decision_id: UUID, user_id: UUID) -> None:
        decision = await self.get_decision(decision_id, user_id)
        await self.repository.delete(decision)
