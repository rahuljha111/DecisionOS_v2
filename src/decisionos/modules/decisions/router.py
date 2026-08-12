from uuid import UUID
from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from decisionos.core.database.session import get_db
from decisionos.core.security.principals import get_current_user
from decisionos.modules.decisions.schemas import DecisionCreate, DecisionRead, DecisionUpdate
from decisionos.modules.decisions.service import DecisionService

router = APIRouter()

@router.post("/workspaces/{workspace_id}/decisions", response_model=DecisionRead, status_code=status.HTTP_201_CREATED)
async def create_decision(
    workspace_id: UUID,
    data: DecisionCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UUID, Depends(get_current_user)]
):
    return await DecisionService(session).create_decision(workspace_id, data, user)

@router.get("/workspaces/{workspace_id}/decisions", response_model=list[DecisionRead])
async def list_decisions(
    workspace_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UUID, Depends(get_current_user)]
):
    return await DecisionService(session).list_decisions(workspace_id, user)

@router.get("/{decision_id}", response_model=DecisionRead)
async def get_decision(
    decision_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UUID, Depends(get_current_user)]
):
    return await DecisionService(session).get_decision(decision_id, user)

@router.patch("/{decision_id}", response_model=DecisionRead)
async def update_decision(
    decision_id: UUID,
    data: DecisionUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UUID, Depends(get_current_user)]
):
    return await DecisionService(session).update_decision(decision_id, data, user)

@router.delete("/{decision_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_decision(
    decision_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UUID, Depends(get_current_user)]
):
    await DecisionService(session).delete_decision(decision_id, user)
