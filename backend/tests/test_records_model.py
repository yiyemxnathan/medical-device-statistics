from sqlmodel import Session, SQLModel, create_engine, select

from app.db import session as db_session
from app.models.records import (
    AnalysisTask,
    AuditLog,
    DatasetVersion,
    Project,
    ReportSnapshot,
    StandardPackage,
)


def test_dataset_version_is_linked_to_project_and_keeps_hash():
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        project = Project(name="Catheter DV", code="DV-001")
        session.add(project)
        session.commit()
        session.refresh(project)

        dataset = DatasetVersion(
            project_id=project.id,
            name="tensile results",
            version=1,
            source_hash="sha256:abc",
            row_count=12,
            column_schema={"force_n": "number", "group": "text"},
            created_by="qa.user",
        )
        session.add(dataset)
        session.commit()

        stored = session.exec(select(DatasetVersion)).one()
        assert stored.project_id == project.id
        assert stored.source_hash == "sha256:abc"
        assert stored.column_schema["force_n"] == "number"


def test_audit_log_records_action_and_object():
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        audit = AuditLog(
            actor="qa.user",
            action="dataset.imported",
            object_type="dataset_version",
            object_id="1",
            details={"rows": 12},
        )
        session.add(audit)
        session.commit()

        stored = session.exec(select(AuditLog)).one()
        assert stored.action == "dataset.imported"
        assert stored.details == {"rows": 12}


def test_create_db_and_tables_creates_record_tables_on_configured_engine(monkeypatch):
    engine = create_engine("sqlite://")
    monkeypatch.setattr(db_session, "engine", engine)

    db_session.create_db_and_tables()

    assert set(SQLModel.metadata.tables) >= {
        "project",
        "datasetversion",
        "standardpackage",
        "analysistask",
        "reportsnapshot",
        "auditlog",
    }


def test_record_relationship_fields_have_foreign_key_metadata():
    expected_foreign_keys = {
        DatasetVersion.__table__.c.project_id: "project.id",
        AnalysisTask.__table__.c.project_id: "project.id",
        AnalysisTask.__table__.c.dataset_version_id: "datasetversion.id",
        ReportSnapshot.__table__.c.analysis_task_id: "analysistask.id",
    }

    for column, expected_target in expected_foreign_keys.items():
        assert {str(foreign_key.column) for foreign_key in column.foreign_keys} == {
            expected_target
        }


def test_json_columns_are_not_nullable():
    expected_not_nullable_json_columns = [
        DatasetVersion.__table__.c.column_schema,
        StandardPackage.__table__.c.table_payload,
        AuditLog.__table__.c.details,
        AnalysisTask.__table__.c.parameters,
        AnalysisTask.__table__.c.result,
        ReportSnapshot.__table__.c.metadata_json,
    ]

    for column in expected_not_nullable_json_columns:
        assert column.nullable is False


def test_engine_kwargs_are_sqlite_specific():
    assert db_session.engine_kwargs("sqlite:///./statistics.db") == {
        "connect_args": {"check_same_thread": False}
    }
    assert db_session.engine_kwargs("postgresql://user:pass@localhost/statistics") == {}
