from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from decisionos.core.database.session import get_db
from decisionos.core.security.dependencies import get_current_user
from decisionos.core.security.principals import Principal
from decisionos.modules.workspaces.schemas import (
    WorkspaceCreate,
    WorkspaceRead,
    WorkspaceUpdate,
)
from decisionos.modules.workspaces.service import WorkspaceService


router = APIRouter()


@router.post("/", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    data: WorkspaceCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[Principal, Depends(get_current_user)],
):
    return await WorkspaceService(session).create_workspace(data, user.id)


@router.get("/", response_model=list[WorkspaceRead])
async def list_workspaces(
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[Principal, Depends(get_current_user)],
):
    return await WorkspaceService(session).list_workspaces(user.id)


@router.get("/{workspace_id}", response_model=WorkspaceRead)
async def get_workspace(
    workspace_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[Principal, Depends(get_current_user)],
):
    return await WorkspaceService(session).get_workspace(workspace_id, user.id)


@router.patch("/{workspace_id}", response_model=WorkspaceRead)
async def update_workspace(
    workspace_id: UUID,
    data: WorkspaceUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[Principal, Depends(get_current_user)],
):
    return await WorkspaceService(session).update_workspace(
        workspace_id,
        data,
        user.id,
    )


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[Principal, Depends(get_current_user)],
):
    await WorkspaceService(session).delete_workspace(
        workspace_id,
        user.id,
    )