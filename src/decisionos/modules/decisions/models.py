from uuid import UUID
from sqlalchemy import ForeignKey, String, Enum
from sqlalchemy.orm import Mapped, mapped_column
from decisionos.core.database.base import Base
from decisionos.core.database.mixins import TimestampMixin, UUIDMixin
from decisionos.modules.decisions.enums import DecisionStatus, DecisionPriority

class Decision(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "decisions"

    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    status: Mapped[DecisionStatus] = mapped_column(Enum(DecisionStatus), default=DecisionStatus.DRAFT)
    priority: Mapped[DecisionPriority] = mapped_column(Enum(DecisionPriority), default=DecisionPriority.MEDIUM)
