"""initial schema

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("nome", sa.String(120), nullable=False),
        sa.Column("email", sa.String(180), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("cref", sa.String(40), nullable=True),
        sa.Column("bio", sa.Text, nullable=True),
        sa.Column("avatar", sa.String(255), nullable=True),
        sa.Column("is_active_flag", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("failed_login_attempts", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_login_at", sa.DateTime, nullable=True),
        sa.Column("locked_until", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "alunos",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nome", sa.String(160), nullable=False),
        sa.Column("email", sa.String(180), nullable=True),
        sa.Column("telefone", sa.String(40), nullable=True),
        sa.Column("nascimento", sa.Date, nullable=True),
        sa.Column("sexo", sa.String(20), nullable=True),
        sa.Column("altura", sa.Float, nullable=True),
        sa.Column("peso_inicial", sa.Float, nullable=True),
        sa.Column("objetivo", sa.String(120), nullable=True),
        sa.Column("observacoes", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="ativo"),
        sa.Column("condicoes_especiais", sa.String(255), nullable=True),
        sa.Column("nivel_condicionamento", sa.String(40), nullable=False, server_default="iniciante"),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_alunos_user_id", "alunos", ["user_id"])
    op.create_index("ix_alunos_nome", "alunos", ["nome"])

    op.create_table(
        "avaliacoes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("aluno_id", sa.Integer, sa.ForeignKey("alunos.id", ondelete="CASCADE"), nullable=False),
        sa.Column("data", sa.Date, nullable=False),
        sa.Column("protocolo", sa.String(60), nullable=False, server_default="pollock_3"),
        sa.Column("peso", sa.Float, nullable=True),
        sa.Column("altura", sa.Float, nullable=True),
        sa.Column("cintura", sa.Float, nullable=True),
        sa.Column("quadril", sa.Float, nullable=True),
        sa.Column("peito", sa.Float, nullable=True),
        sa.Column("braco", sa.Float, nullable=True),
        sa.Column("coxa", sa.Float, nullable=True),
        sa.Column("panturrilha", sa.Float, nullable=True),
        sa.Column("abdomen", sa.Float, nullable=True),
        sa.Column("dobra_triceps", sa.Float, nullable=True),
        sa.Column("dobra_peitoral", sa.Float, nullable=True),
        sa.Column("dobra_subaxilar", sa.Float, nullable=True),
        sa.Column("dobra_subescapular", sa.Float, nullable=True),
        sa.Column("dobra_abdominal", sa.Float, nullable=True),
        sa.Column("dobra_suprailiaca", sa.Float, nullable=True),
        sa.Column("dobra_coxa", sa.Float, nullable=True),
        sa.Column("percentual_gordura", sa.Float, nullable=True),
        sa.Column("massa_magra", sa.Float, nullable=True),
        sa.Column("massa_gorda", sa.Float, nullable=True),
        sa.Column("imc", sa.Float, nullable=True),
        sa.Column("rcq", sa.Float, nullable=True),
        sa.Column("tmb", sa.Float, nullable=True),
        sa.Column("classificacao_imc", sa.String(40), nullable=True),
        sa.Column("observacoes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_avaliacoes_user_id", "avaliacoes", ["user_id"])
    op.create_index("ix_avaliacoes_aluno_id", "avaliacoes", ["aluno_id"])
    op.create_index("ix_avaliacoes_data", "avaliacoes", ["data"])

    op.create_table(
        "treinos",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("aluno_id", sa.Integer, sa.ForeignKey("alunos.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nome", sa.String(160), nullable=False),
        sa.Column("objetivo", sa.String(80), nullable=False, server_default="hipertrofia"),
        sa.Column("modalidade", sa.String(60), nullable=False, server_default="musculacao"),
        sa.Column("fase", sa.String(60), nullable=False, server_default="adaptacao"),
        sa.Column("divisao", sa.String(40), nullable=False, server_default="ABC"),
        sa.Column("frequencia_semanal", sa.Integer, nullable=False, server_default="3"),
        sa.Column("nivel", sa.String(40), nullable=False, server_default="iniciante"),
        sa.Column("protocolo_origem", sa.String(80), nullable=True),
        sa.Column("duracao_semanas", sa.Integer, nullable=False, server_default="8"),
        sa.Column("observacoes", sa.Text, nullable=True),
        sa.Column("alerta_medico", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="ativo"),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_treinos_user_id", "treinos", ["user_id"])
    op.create_index("ix_treinos_aluno_id", "treinos", ["aluno_id"])

    op.create_table(
        "exercicios",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("treino_id", sa.Integer, sa.ForeignKey("treinos.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nome", sa.String(160), nullable=False),
        sa.Column("grupo_muscular", sa.String(60), nullable=False, server_default="geral"),
        sa.Column("series", sa.Integer, nullable=False, server_default="3"),
        sa.Column("repeticoes", sa.String(40), nullable=False, server_default="10-12"),
        sa.Column("carga", sa.String(40), nullable=True),
        sa.Column("descanso", sa.String(40), nullable=True, server_default="60s"),
        sa.Column("rpe", sa.Float, nullable=True),
        sa.Column("rir", sa.Integer, nullable=True),
        sa.Column("tempo_execucao", sa.String(40), nullable=True),
        sa.Column("observacoes", sa.Text, nullable=True),
        sa.Column("dia_semana", sa.String(20), nullable=False, server_default="A"),
        sa.Column("ordem", sa.Integer, nullable=False, server_default="1"),
        sa.Column("tecnica", sa.String(60), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_exercicios_treino_id", "exercicios", ["treino_id"])

    op.create_table(
        "protocolos",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("aluno_id", sa.Integer, sa.ForeignKey("alunos.id", ondelete="CASCADE"), nullable=True),
        sa.Column("chave", sa.String(80), nullable=False),
        sa.Column("nome", sa.String(160), nullable=False),
        sa.Column("categoria", sa.String(60), nullable=False, server_default="avaliacao"),
        sa.Column("descricao", sa.Text, nullable=True),
        sa.Column("payload", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="ativo"),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_protocolos_user_id", "protocolos", ["user_id"])
    op.create_index("ix_protocolos_aluno_id", "protocolos", ["aluno_id"])

    op.create_table(
        "log_entries",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("category", sa.String(40), nullable=False, server_default="general"),
        sa.Column("level", sa.String(20), nullable=False, server_default="INFO"),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("ip_address", sa.String(60), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_log_entries_created_at", "log_entries", ["created_at"])


def downgrade():
    op.drop_index("ix_log_entries_created_at", table_name="log_entries")
    op.drop_table("log_entries")
    op.drop_index("ix_protocolos_aluno_id", table_name="protocolos")
    op.drop_index("ix_protocolos_user_id", table_name="protocolos")
    op.drop_table("protocolos")
    op.drop_index("ix_exercicios_treino_id", table_name="exercicios")
    op.drop_table("exercicios")
    op.drop_index("ix_treinos_aluno_id", table_name="treinos")
    op.drop_index("ix_treinos_user_id", table_name="treinos")
    op.drop_table("treinos")
    op.drop_index("ix_avaliacoes_data", table_name="avaliacoes")
    op.drop_index("ix_avaliacoes_aluno_id", table_name="avaliacoes")
    op.drop_index("ix_avaliacoes_user_id", table_name="avaliacoes")
    op.drop_table("avaliacoes")
    op.drop_index("ix_alunos_nome", table_name="alunos")
    op.drop_index("ix_alunos_user_id", table_name="alunos")
    op.drop_table("alunos")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
