from sqlmodel import Session, SQLModel, create_engine, select

from app.models.records import AuditLog, Project
from app.services.audit import record_audit


def test_record_audit_does_not_commit_unrelated_pending_objects():
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(Project(name="Catheter DV", code="DV-001"))
        record_audit(
            session=session,
            actor="qa.user",
            action="project.created",
            object_type="project",
            object_id="pending",
            details={"code": "DV-001"},
        )
        session.rollback()

    with Session(engine) as session:
        assert session.exec(select(Project)).all() == []
        assert session.exec(select(AuditLog)).all() == []


def test_record_audit_persists_when_caller_commits():
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        audit = record_audit(
            session=session,
            actor="qa.user",
            action="dataset.imported",
            object_type="dataset_version",
            object_id="1",
            details={"rows": 12},
        )
        assert audit.id is not None
        session.commit()

    with Session(engine) as session:
        stored = session.exec(select(AuditLog)).one()
        assert stored.action == "dataset.imported"
        assert stored.details == {"rows": 12}
