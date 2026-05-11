"""Avaliação física model with anthropometric measurements."""
from datetime import datetime, date

from models import db


class Avaliacao(db.Model):
    __tablename__ = "avaliacoes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    aluno_id = db.Column(
        db.Integer, db.ForeignKey("alunos.id", ondelete="CASCADE"), nullable=False, index=True
    )

    data = db.Column(db.Date, default=date.today, nullable=False, index=True)
    protocolo = db.Column(db.String(60), default="pollock_3", nullable=False)

    peso = db.Column(db.Float, nullable=True)
    altura = db.Column(db.Float, nullable=True)
    cintura = db.Column(db.Float, nullable=True)
    quadril = db.Column(db.Float, nullable=True)
    peito = db.Column(db.Float, nullable=True)
    braco = db.Column(db.Float, nullable=True)
    coxa = db.Column(db.Float, nullable=True)
    panturrilha = db.Column(db.Float, nullable=True)
    abdomen = db.Column(db.Float, nullable=True)

    dobra_triceps = db.Column(db.Float, nullable=True)
    dobra_peitoral = db.Column(db.Float, nullable=True)
    dobra_subaxilar = db.Column(db.Float, nullable=True)
    dobra_subescapular = db.Column(db.Float, nullable=True)
    dobra_abdominal = db.Column(db.Float, nullable=True)
    dobra_suprailiaca = db.Column(db.Float, nullable=True)
    dobra_coxa = db.Column(db.Float, nullable=True)

    percentual_gordura = db.Column(db.Float, nullable=True)
    massa_magra = db.Column(db.Float, nullable=True)
    massa_gorda = db.Column(db.Float, nullable=True)
    imc = db.Column(db.Float, nullable=True)
    rcq = db.Column(db.Float, nullable=True)
    tmb = db.Column(db.Float, nullable=True)
    classificacao_imc = db.Column(db.String(40), nullable=True)

    observacoes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "aluno_id": self.aluno_id,
            "data": self.data.isoformat() if self.data else None,
            "protocolo": self.protocolo,
            "peso": self.peso,
            "altura": self.altura,
            "cintura": self.cintura,
            "quadril": self.quadril,
            "peito": self.peito,
            "braco": self.braco,
            "coxa": self.coxa,
            "panturrilha": self.panturrilha,
            "abdomen": self.abdomen,
            "dobras": {
                "triceps": self.dobra_triceps,
                "peitoral": self.dobra_peitoral,
                "subaxilar": self.dobra_subaxilar,
                "subescapular": self.dobra_subescapular,
                "abdominal": self.dobra_abdominal,
                "suprailiaca": self.dobra_suprailiaca,
                "coxa": self.dobra_coxa,
            },
            "percentual_gordura": self.percentual_gordura,
            "massa_magra": self.massa_magra,
            "massa_gorda": self.massa_gorda,
            "imc": self.imc,
            "rcq": self.rcq,
            "tmb": self.tmb,
            "classificacao_imc": self.classificacao_imc,
            "observacoes": self.observacoes,
        }

    def __repr__(self) -> str:
        return f"<Avaliacao id={self.id} aluno_id={self.aluno_id} data={self.data}>"
