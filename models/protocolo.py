"""Protocolo model - applied evaluation protocol record."""
from datetime import datetime

from models import db


class Protocolo(db.Model):
    __tablename__ = "protocolos"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    aluno_id = db.Column(
        db.Integer, db.ForeignKey("alunos.id", ondelete="CASCADE"), nullable=True, index=True
    )

    chave = db.Column(db.String(80), nullable=False)
    nome = db.Column(db.String(160), nullable=False)
    categoria = db.Column(db.String(60), nullable=False, default="avaliacao")
    descricao = db.Column(db.Text, nullable=True)
    payload = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="ativo")

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "aluno_id": self.aluno_id,
            "chave": self.chave,
            "nome": self.nome,
            "categoria": self.categoria,
            "descricao": self.descricao,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<Protocolo id={self.id} chave={self.chave}>"
