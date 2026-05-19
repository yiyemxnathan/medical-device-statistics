from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(UTC)


class Project(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    code: str = Field(index=True)
    created_at: datetime = Field(default_factory=utc_now)
    created_by: str = "system"
    is_active: bool = True


class DatasetVersion(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", index=True)
    name: str
    version: int
    source_hash: str
    row_count: int
    column_schema: dict[str, str] = Field(sa_column=Column(JSON, nullable=False))
    created_at: datetime = Field(default_factory=utc_now)
    created_by: str


class StandardPackage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    standard_name: str = Field(index=True)
    standard_version: str
    package_version: str
    table_payload: dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    enabled: bool = False
    created_at: datetime = Field(default_factory=utc_now)


class AnalysisTask(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", index=True)
    dataset_version_id: int | None = Field(
        default=None,
        foreign_key="datasetversion.id",
        index=True,
    )
    analysis_type: str = Field(index=True)
    parameters: dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    result: dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    app_version: str
    algorithm_version: str
    created_at: datetime = Field(default_factory=utc_now)
    created_by: str


class ReportSnapshot(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    report_number: str = Field(index=True)
    analysis_task_id: int = Field(foreign_key="analysistask.id", index=True)
    html: str
    metadata_json: dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    voided: bool = False
    void_reason: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    created_by: str


class AuditLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    actor: str = Field(index=True)
    action: str = Field(index=True)
    object_type: str = Field(index=True)
    object_id: str
    details: dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    created_at: datetime = Field(default_factory=utc_now)
