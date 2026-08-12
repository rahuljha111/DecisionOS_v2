from __future__ import annotations
from uuid import UUID
from typing import List, TYPE_CHECKING
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decisionos.core.database.base import Base
from decisionos.core.database.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from decisionos.modules.decisions.models import Decision

class Workspace(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    decisions: Mapped[List["Decision"]] = relationship(
        "Decision", backref="workspace", cascade="all, delete-orphan"
    )
