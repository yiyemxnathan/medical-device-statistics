from typing import Any

from sqlmodel import Session, select

from app.core.config import settings
from app.models.records import AnalysisTask, Project
from app.services.audit import record_audit

SYSTEM_PROJECT_CODE = "SYSTEM"
SYSTEM_PROJECT_NAME = "System Calculations"


def ensure_system_project(session: Session) -> Project:
    project = session.exec(
        select(Project).where(Project.code == SYSTEM_PROJECT_CODE)
    ).first()
    if project is not None:
        return project

    project = Project(
        code=SYSTEM_PROJECT_CODE,
        name=SYSTEM_PROJECT_NAME,
        created_by="system",
    )
    session.add(project)
    session.flush()
    return project


def create_controlled_analysis_task(
    session: Session,
    analysis_type: str,
    parameters: dict[str, Any],
    result: dict[str, Any],
) -> AnalysisTask:
    project = ensure_system_project(session)
    task = AnalysisTask(
        project_id=project.id,
        analysis_type=analysis_type,
        parameters=parameters,
        result=result,
        app_version=settings.app_version,
        algorithm_version=settings.algorithm_version,
        created_by="system",
    )
    session.add(task)
    session.flush()
    record_audit(
        session=session,
        actor="system",
        action="create",
        object_type="AnalysisTask",
        object_id=str(task.id),
        details={
            "analysis_type": analysis_type,
            "project_code": SYSTEM_PROJECT_CODE,
        },
    )
    session.commit()
    session.refresh(task)
    return task
