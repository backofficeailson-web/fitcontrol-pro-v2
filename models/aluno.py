"""Aluno (student) model."""
from datetime import datetime, UTC, date

from models import db


class Aluno(db.Model):
    __tablename__ = "alunos"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    nome = db.Column(db.String(160), nullable=False, index=True)
    email = db.Column(db.String(180), nullable=True)
    telefone = db.Column(db.String(40), nullable=True)
    nascimento = db.Column(db.Date, nullable=True)
    sexo = db.Column(db.String(20), nullable=True)
    altura = db.Column(db.Float, nullable=True)
    peso_inicial = db.Column(db.Float, nullable=True)
    objetivo = db.Column(db.String(120), nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default="ativo", nullable=False)

    condicoes_especiais = db.Column(db.String(255), nullable=True)
    nivel_condicionamento = db.Column(db.String(40), default="iniciante", nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    avaliacoes = db.relationship(
        "Avaliacao",
        backref="aluno",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="Avaliacao.data.desc()",
    )
    treinos = db.relationship(
        "Treino",
        backref="aluno",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="Treino.created_at.desc()",
    )

    @property
    def idade(self) -> int | None:
        if not self.nascimento:
            return None
        today = date.today()
        years = today.year - self.nascimento.year
        if (today.month, today.day) < (self.nascimento.month, self.nascimento.day):
            years -= 1
        return max(years, 0)

    @property
    def total_avaliacoes(self) -> int:
        return self.avaliacoes.count()

    @property
    def total_treinos(self) -> int:
        return self.treinos.count()

    @property
    def ultima_avaliacao(self):
        return self.avaliacoes.first()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "telefone": self.telefone,
            "nascimento": self.nascimento.isoformat() if self.nascimento else None,
            "sexo": self.sexo,
            "altura": self.altura,
            "peso_inicial": self.peso_inicial,
            "objetivo": self.objetivo,
            "observacoes": self.observacoes,
            "status": self.status,
            "condicoes_especiais": self.condicoes_especiais,
            "nivel_condicionamento": self.nivel_condicionamento,
            "idade": self.idade,
        }

    def __repr__(self) -> str:
        return f"<Aluno id={self.id} nome={self.nome}>"
