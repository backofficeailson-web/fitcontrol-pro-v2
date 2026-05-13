"""
AIAnalysis — modelo para análises de arquivos via IA.
Suporta upload de ZIP, PDF, imagens, documentos e código,
com fila de processamento, progresso e histórico.
"""
from __future__ import annotations

from datetime import datetime, UTC

from models import db


class AIAnalysis(db.Model):
    __tablename__ = "ai_analyses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    # --- Metadata do upload ---
    nome_arquivo = db.Column(db.String(255), nullable=False)
    tipo_arquivo = db.Column(db.String(60), nullable=False)   # zip / pdf / image / code / doc
    tamanho_bytes = db.Column(db.Integer, nullable=False, default=0)
    mime_type = db.Column(db.String(120), nullable=True)
    caminho = db.Column(db.String(500), nullable=False)        # static/uploads/ai_analysis/...

    # --- Fila de processamento ---
    status = db.Column(
        db.String(20), nullable=False, default="pending", index=True
    )  # pending / processing / done / failed
    progresso = db.Column(db.Integer, nullable=False, default=0)  # 0-100

    # --- Resultados ---
    resumo = db.Column(db.Text, nullable=True)
    erros_detectados = db.Column(db.Text, nullable=True)
    sugestoes = db.Column(db.Text, nullable=True)
    relatorio_tecnico = db.Column(db.Text, nullable=True)
    codigo_corrigido = db.Column(db.Text, nullable=True)
    metricas = db.Column(db.Text, nullable=True)   # JSON serialized

    # --- Categorias avaliadas ---
    score_seguranca = db.Column(db.Integer, nullable=True)        # 0-100
    score_performance = db.Column(db.Integer, nullable=True)
    score_arquitetura = db.Column(db.Integer, nullable=True)
    score_responsividade = db.Column(db.Integer, nullable=True)
    score_banco = db.Column(db.Integer, nullable=True)

    # --- Erro de processamento ---
    erro_msg = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    started_at = db.Column(db.DateTime, nullable=True)
    finished_at = db.Column(db.DateTime, nullable=True)

    def is_finished(self) -> bool:
        return self.status in {"done", "failed"}

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome_arquivo": self.nome_arquivo,
            "tipo_arquivo": self.tipo_arquivo,
            "tamanho_bytes": self.tamanho_bytes,
            "status": self.status,
            "progresso": self.progresso,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "scores": {
                "seguranca": self.score_seguranca,
                "performance": self.score_performance,
                "arquitetura": self.score_arquitetura,
                "responsividade": self.score_responsividade,
                "banco": self.score_banco,
            },
        }
