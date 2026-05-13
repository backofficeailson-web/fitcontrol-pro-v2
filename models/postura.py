"""
Avaliação Postural — modelo completo.
Permite registrar análises posturais detalhadas com upload de imagens,
marcação visual, grau de desvio e observações técnicas.
"""
from __future__ import annotations

from datetime import datetime, UTC

from models import db


class AvaliacaoPostural(db.Model):
    __tablename__ = "avaliacoes_posturais"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    aluno_id = db.Column(
        db.Integer, db.ForeignKey("alunos.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    data = db.Column(db.Date, nullable=False, default=datetime.utcnow)

    # --- Segmentos corporais (texto livre técnico) ---
    cabeca = db.Column(db.String(255), nullable=True)
    cervical = db.Column(db.String(255), nullable=True)
    ombros = db.Column(db.String(255), nullable=True)
    escapulas = db.Column(db.String(255), nullable=True)
    coluna_toracica = db.Column(db.String(255), nullable=True)
    lombar = db.Column(db.String(255), nullable=True)
    quadril = db.Column(db.String(255), nullable=True)
    joelhos = db.Column(db.String(255), nullable=True)
    pes = db.Column(db.String(255), nullable=True)

    # --- Alinhamentos ---
    alinhamento_frontal = db.Column(db.Text, nullable=True)
    alinhamento_lateral = db.Column(db.Text, nullable=True)

    # --- Indicadores clínicos ---
    grau_desvio = db.Column(db.String(40), nullable=True)   # leve / moderado / acentuado
    dor_relatada = db.Column(db.String(255), nullable=True)
    limitacao_funcional = db.Column(db.String(255), nullable=True)

    # --- Observações ---
    observacoes_tecnicas = db.Column(db.Text, nullable=True)
    observacoes_profissional = db.Column(db.Text, nullable=True)

    # --- Imagens (paths em static/uploads/posture/) ---
    img_frontal = db.Column(db.String(500), nullable=True)
    img_lateral_direita = db.Column(db.String(500), nullable=True)
    img_lateral_esquerda = db.Column(db.String(500), nullable=True)
    img_posterior = db.Column(db.String(500), nullable=True)

    # --- Comparação ---
    avaliacao_anterior_id = db.Column(
        db.Integer, db.ForeignKey("avaliacoes_posturais.id"), nullable=True
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    aluno = db.relationship("Aluno", backref=db.backref("avaliacoes_posturais", lazy="dynamic"))

    def imagens(self) -> list[tuple[str, str]]:
        """Retorna lista de (label, path) das imagens preenchidas."""
        out = []
        for label, attr in (
            ("Frontal", self.img_frontal),
            ("Lateral Direita", self.img_lateral_direita),
            ("Lateral Esquerda", self.img_lateral_esquerda),
            ("Posterior", self.img_posterior),
        ):
            if attr:
                out.append((label, attr))
        return out

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "aluno_id": self.aluno_id,
            "data": self.data.isoformat() if self.data else None,
            "grau_desvio": self.grau_desvio,
            "dor_relatada": self.dor_relatada,
            "limitacao_funcional": self.limitacao_funcional,
            "imagens": [{"label": l, "path": p} for l, p in self.imagens()],
        }
