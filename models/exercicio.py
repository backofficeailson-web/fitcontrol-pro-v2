"""Exercicio model - individual exercise within a workout."""
from datetime import datetime, UTC

from models import db


class Exercicio(db.Model):
    __tablename__ = "exercicios"

    id = db.Column(db.Integer, primary_key=True)
    treino_id = db.Column(
        db.Integer,
        db.ForeignKey("treinos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    nome = db.Column(db.String(160), nullable=False)
    grupo_muscular = db.Column(db.String(60), nullable=False, default="geral")
    series = db.Column(db.Integer, nullable=False, default=3)
    repeticoes = db.Column(db.String(40), nullable=False, default="10-12")
    carga = db.Column(db.String(40), nullable=True)
    descanso = db.Column(db.String(40), nullable=True, default="60s")
    rpe = db.Column(db.Float, nullable=True)
    rir = db.Column(db.Integer, nullable=True)
    tempo_execucao = db.Column(db.String(40), nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
    dia_semana = db.Column(db.String(20), nullable=False, default="A")
    ordem = db.Column(db.Integer, nullable=False, default=1)
    tecnica = db.Column(db.String(60), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "treino_id": self.treino_id,
            "nome": self.nome,
            "grupo_muscular": self.grupo_muscular,
            "series": self.series,
            "repeticoes": self.repeticoes,
            "carga": self.carga,
            "descanso": self.descanso,
            "rpe": self.rpe,
            "rir": self.rir,
            "tempo_execucao": self.tempo_execucao,
            "observacoes": self.observacoes,
            "dia_semana": self.dia_semana,
            "ordem": self.ordem,
            "tecnica": self.tecnica,
        }

    def __repr__(self) -> str:
        return f"<Exercicio id={self.id} nome={self.nome}>"
