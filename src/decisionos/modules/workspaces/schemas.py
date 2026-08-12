from uuid import UUID
from pydantic import BaseModel, Field

class WorkspaceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1024)

class WorkspaceCreate(WorkspaceBase):
    pass

class WorkspaceUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1024)

class WorkspaceRead(WorkspaceBase):
    id: UUID
    owner_id: UUID
