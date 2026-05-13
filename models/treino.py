"""Treino (workout plan) model."""
from datetime import datetime, UTC

from models import db


class Treino(db.Model):
    __tablename__ = "treinos"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    aluno_id = db.Column(
        db.Integer, db.ForeignKey("alunos.id", ondelete="CASCADE"), nullable=False, index=True
    )

    nome = db.Column(db.String(160), nullable=False)
    objetivo = db.Column(db.String(80), nullable=False, default="hipertrofia")
    modalidade = db.Column(db.String(60), nullable=False, default="musculacao")
    fase = db.Column(db.String(60), nullable=False, default="adaptacao")
    divisao = db.Column(db.String(40), nullable=False, default="ABC")
    frequencia_semanal = db.Column(db.Integer, nullable=False, default=3)
    nivel = db.Column(db.String(40), nullable=False, default="iniciante")
    protocolo_origem = db.Column(db.String(80), nullable=True)
    duracao_semanas = db.Column(db.Integer, nullable=False, default=8)

    observacoes = db.Column(db.Text, nullable=True)
    alerta_medico = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="ativo")

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    exercicios = db.relationship(
        "Exercicio",
        backref="treino",
        lazy="select",
        cascade="all, delete-orphan",
        order_by="Exercicio.dia_semana, Exercicio.ordem",
    )

    @property
    def total_exercicios(self) -> int:
        return len(self.exercicios)

    @property
    def dias_treino(self) -> list[str]:
        dias = sorted({e.dia_semana for e in self.exercicios if e.dia_semana})
        return dias

    def exercicios_por_dia(self) -> dict[str, list]:
        agrupado: dict[str, list] = {}
        for ex in self.exercicios:
            agrupado.setdefault(ex.dia_semana or "Geral", []).append(ex)
        return agrupado

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "aluno_id": self.aluno_id,
            "nome": self.nome,
            "objetivo": self.objetivo,
            "modalidade": self.modalidade,
            "fase": self.fase,
            "divisao": self.divisao,
            "frequencia_semanal": self.frequencia_semanal,
            "nivel": self.nivel,
            "protocolo_origem": self.protocolo_origem,
            "duracao_semanas": self.duracao_semanas,
            "observacoes": self.observacoes,
            "alerta_medico": self.alerta_medico,
            "status": self.status,
            "exercicios": [e.to_dict() for e in self.exercicios],
        }

    def __repr__(self) -> str:
        return f"<Treino id={self.id} nome={self.nome}>"
