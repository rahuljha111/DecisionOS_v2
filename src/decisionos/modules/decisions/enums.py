from enum import StrEnum, auto

class DecisionStatus(StrEnum):
    DRAFT = auto()
    ACTIVE = auto()
    UNDER_REVIEW = auto()
    DECIDED = auto()
    COMPLETED = auto()

class DecisionPriority(StrEnum):
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()
