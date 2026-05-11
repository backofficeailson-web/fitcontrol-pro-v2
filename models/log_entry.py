"""LogEntry model - structured event audit logs."""
from datetime import datetime

from models import db


class LogEntry(db.Model):
    __tablename__ = "log_entries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    category = db.Column(db.String(40), nullable=False, default="general")
    level = db.Column(db.String(20), nullable=False, default="INFO")
    message = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.String(60), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<LogEntry id={self.id} cat={self.category} level={self.level}>"
