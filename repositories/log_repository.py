"""Log repository."""
from models import db
from models.log_entry import LogEntry


class LogRepository:
    @classmethod
    def write(
        cls,
        *,
        category: str,
        message: str,
        level: str = "INFO",
        user_id: int | None = None,
        ip_address: str | None = None,
    ) -> LogEntry:
        entry = LogEntry(
            category=category,
            level=level,
            message=message,
            user_id=user_id,
            ip_address=ip_address,
        )
        db.session.add(entry)
        db.session.commit()
        return entry

    @classmethod
    def latest_for_user(cls, user_id: int, limit: int = 10) -> list[LogEntry]:
        return (
            db.session.query(LogEntry)
            .filter(LogEntry.user_id == user_id)
            .order_by(LogEntry.created_at.desc())
            .limit(limit)
            .all()
        )
