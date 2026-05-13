"""postura e ai_analysis

Revision ID: 002_postura_ai
Revises: 001_initial
Create Date: 2026-05-12 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "002_postura_ai"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "avaliacoes_posturais",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("aluno_id", sa.Integer, sa.ForeignKey("alunos.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("data", sa.Date, nullable=False),
        sa.Column("cabeca", sa.String(255), nullable=True),
        sa.Column("cervical", sa.String(255), nullable=True),
        sa.Column("ombros", sa.String(255), nullable=True),
        sa.Column("escapulas", sa.String(255), nullable=True),
        sa.Column("coluna_toracica", sa.String(255), nullable=True),
        sa.Column("lombar", sa.String(255), nullable=True),
        sa.Column("quadril", sa.String(255), nullable=True),
        sa.Column("joelhos", sa.String(255), nullable=True),
        sa.Column("pes", sa.String(255), nullable=True),
        sa.Column("alinhamento_frontal", sa.Text, nullable=True),
        sa.Column("alinhamento_lateral", sa.Text, nullable=True),
        sa.Column("grau_desvio", sa.String(40), nullable=True),
        sa.Column("dor_relatada", sa.String(255), nullable=True),
        sa.Column("limitacao_funcional", sa.String(255), nullable=True),
        sa.Column("observacoes_tecnicas", sa.Text, nullable=True),
        sa.Column("observacoes_profissional", sa.Text, nullable=True),
        sa.Column("img_frontal", sa.String(500), nullable=True),
        sa.Column("img_lateral_direita", sa.String(500), nullable=True),
        sa.Column("img_lateral_esquerda", sa.String(500), nullable=True),
        sa.Column("img_posterior", sa.String(500), nullable=True),
        sa.Column("avaliacao_anterior_id", sa.Integer, sa.ForeignKey("avaliacoes_posturais.id"), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "ai_analyses",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("nome_arquivo", sa.String(255), nullable=False),
        sa.Column("tipo_arquivo", sa.String(60), nullable=False),
        sa.Column("tamanho_bytes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("mime_type", sa.String(120), nullable=True),
        sa.Column("caminho", sa.String(500), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending", index=True),
        sa.Column("progresso", sa.Integer, nullable=False, server_default="0"),
        sa.Column("resumo", sa.Text, nullable=True),
        sa.Column("erros_detectados", sa.Text, nullable=True),
        sa.Column("sugestoes", sa.Text, nullable=True),
        sa.Column("relatorio_tecnico", sa.Text, nullable=True),
        sa.Column("codigo_corrigido", sa.Text, nullable=True),
        sa.Column("metricas", sa.Text, nullable=True),
        sa.Column("score_seguranca", sa.Integer, nullable=True),
        sa.Column("score_performance", sa.Integer, nullable=True),
        sa.Column("score_arquitetura", sa.Integer, nullable=True),
        sa.Column("score_responsividade", sa.Integer, nullable=True),
        sa.Column("score_banco", sa.Integer, nullable=True),
        sa.Column("erro_msg", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, index=True),
        sa.Column("started_at", sa.DateTime, nullable=True),
        sa.Column("finished_at", sa.DateTime, nullable=True),
    )


def downgrade():
    op.drop_table("ai_analyses")
    op.drop_table("avaliacoes_posturais")
