from uuid import UUID
from pydantic import BaseModel, Field
from decisionos.modules.decisions.enums import DecisionStatus, DecisionPriority

class DecisionBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2048)
    status: DecisionStatus = DecisionStatus.DRAFT
    priority: DecisionPriority = DecisionPriority.MEDIUM

class DecisionCreate(DecisionBase):
    pass

class DecisionUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2048)
    status: DecisionStatus | None = None
    priority: DecisionPriority | None = None

class DecisionRead(DecisionBase):
    id: UUID
    workspace_id: UUID
