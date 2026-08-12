import pytest
import asyncio
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from decisionos.modules.decisions.service import DecisionService
from decisionos.modules.decisions.enums import DecisionStatus
from decisionos.core.exceptions import ForbiddenError

def test_invalid_status_transition_raises_forbidden():
    async def run():
        # Setup: Create a mock session and service
        mock_session = AsyncMock(spec=AsyncSession)
        service = DecisionService(mock_session)
        
        # Mock the workspace service to avoid DB calls
        service.workspace_service = AsyncMock()
        
        # Attempt to transition DRAFT -> DECIDED (Invalid)
        with pytest.raises(ForbiddenError):
            service._validate_transition(DecisionStatus.DRAFT, DecisionStatus.DECIDED)
    
    asyncio.run(run())

def test_valid_status_transition_succeeds():
    async def run():
        # Setup: Create a mock session and service
        mock_session = AsyncMock(spec=AsyncSession)
        service = DecisionService(mock_session)
        
        # Should not raise
        service._validate_transition(DecisionStatus.DRAFT, DecisionStatus.ACTIVE)
    
    asyncio.run(run())
