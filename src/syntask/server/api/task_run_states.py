"""
Routes for interacting with task run state objects.
"""

from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException, Path, status

import syntask.server.models as models
import syntask.server.schemas as schemas
from syntask.server.database.dependencies import provide_database_interface
from syntask.server.database.interface import SyntaskDBInterface
from syntask.server.utilities.server import SyntaskRouter

router = SyntaskRouter(prefix="/task_run_states", tags=["Task Run States"])


@router.get("/{id}")
async def read_task_run_state(
    task_run_state_id: UUID = Path(
        ..., description="The task run state id", alias="id"
    ),
    db: SyntaskDBInterface = Depends(provide_database_interface),
) -> schemas.states.State:
    """
    Get a task run state by id.
    """
    async with db.session_context() as session:
        task_run_state = await models.task_run_states.read_task_run_state(
            session=session, task_run_state_id=task_run_state_id
        )
    if not task_run_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Flow run state not found"
        )
    return task_run_state


@router.get("/")
async def read_task_run_states(
    task_run_id: UUID,
    db: SyntaskDBInterface = Depends(provide_database_interface),
) -> List[schemas.states.State]:
    """
    Get states associated with a task run.
    """
    async with db.session_context() as session:
        return await models.task_run_states.read_task_run_states(
            session=session, task_run_id=task_run_id
        )
