from sqlmodel import Session

from app.models.records import AuditLog


def record_audit(
    session: Session,
    actor: str,
    action: str,
    object_type: str,
    object_id: str,
    details: dict,
) -> AuditLog:
    entry = AuditLog(
        actor=actor,
        action=action,
        object_type=object_type,
        object_id=object_id,
        details=details,
    )
    session.add(entry)
    session.flush()
    return entry
