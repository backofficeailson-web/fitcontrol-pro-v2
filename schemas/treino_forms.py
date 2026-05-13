"""Treino forms."""
from flask_wtf import FlaskForm
from wtforms import (
    StringField, SelectField, IntegerField, TextAreaField, FloatField,
    SubmitField, HiddenField,
)
from wtforms.validators import DataRequired, Optional, NumberRange, Length


OBJETIVO_CHOICES = [
    ("hipertrofia", "Hipertrofia"),
    ("emagrecimento", "Emagrecimento"),
    ("forca", "Força"),
    ("condicionamento", "Condicionamento"),
    ("resistencia", "Resistência muscular"),
    ("esporte", "Performance esportiva"),
    ("saude", "Saúde geral"),
]
DIVISAO_CHOICES = [
    ("Full Body", "Full Body"),
    ("ABC", "ABC"),
    ("ABCD", "ABCD"),
    ("ABCDE", "ABCDE"),
    ("Upper/Lower", "Upper / Lower"),
]
NIVEL_CHOICES = [
    ("iniciante", "Iniciante"),
    ("intermediario", "Intermediário"),
    ("avancado", "Avançado"),
]
FASE_CHOICES = [
    ("adaptacao", "Adaptação"),
    ("acumulacao", "Acumulação"),
    ("intensificacao", "Intensificação"),
    ("pico", "Pico"),
    ("deload", "Deload"),
]
MODALIDADE_CHOICES = [
    ("musculacao", "Musculação"),
    ("funcional", "Funcional"),
    ("crossfit", "Crossfit"),
    ("corrida", "Corrida"),
    ("hibrido", "Híbrido"),
]


class TreinoForm(FlaskForm):
    aluno_id = HiddenField(validators=[DataRequired()])
    nome = StringField("Nome do treino", validators=[DataRequired(), Length(min=2, max=160)])
    objetivo = SelectField("Objetivo", choices=OBJETIVO_CHOICES, default="hipertrofia")
    modalidade = SelectField("Modalidade", choices=MODALIDADE_CHOICES, default="musculacao")
    fase = SelectField("Fase", choices=FASE_CHOICES, default="adaptacao")
    divisao = SelectField("Divisão", choices=DIVISAO_CHOICES, default="ABC")
    frequencia_semanal = IntegerField(
        "Frequência semanal", validators=[DataRequired(), NumberRange(min=1, max=7)], default=3
    )
    nivel = SelectField("Nível", choices=NIVEL_CHOICES, default="iniciante")
    duracao_semanas = IntegerField(
        "Duração (semanas)", validators=[Optional(), NumberRange(min=2, max=24)], default=8
    )
    observacoes = TextAreaField("Observações")
    status = SelectField(
        "Status",
        choices=[("ativo", "Ativo"), ("arquivado", "Arquivado"), ("rascunho", "Rascunho")],
        default="ativo",
    )
    submit = SubmitField("Salvar treino")


class ExercicioForm(FlaskForm):
    nome = StringField("Nome do exercício", validators=[DataRequired(), Length(min=2, max=160)])
    grupo_muscular = SelectField(
        "Grupo muscular",
        choices=[
            ("peito", "Peito"), ("costas", "Costas"), ("ombros", "Ombros"),
            ("biceps", "Bíceps"), ("triceps", "Tríceps"),
            ("quadriceps", "Quadríceps"), ("posterior", "Posterior"),
            ("gluteos", "Glúteos"), ("panturrilha", "Panturrilha"),
            ("core", "Core"), ("cardio", "Cardio"), ("mobilidade", "Mobilidade"),
            ("geral", "Geral"),
        ],
        default="geral",
    )
    series = IntegerField("Séries", validators=[DataRequired(), NumberRange(min=1, max=12)], default=3)
    repeticoes = StringField("Repetições", validators=[DataRequired(), Length(max=40)], default="10-12")
    carga = StringField("Carga", validators=[Optional(), Length(max=40)])
    descanso = StringField("Descanso", validators=[Optional(), Length(max=40)], default="60s")
    rpe = FloatField("RPE", validators=[Optional(), NumberRange(min=1, max=10)])
    rir = IntegerField("RIR", validators=[Optional(), NumberRange(min=0, max=10)])
    tempo_execucao = StringField("Tempo execução", validators=[Optional(), Length(max=40)])
    dia_semana = SelectField(
        "Dia",
        choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D"), ("E", "E"), ("F", "F")],
        default="A",
    )
    ordem = IntegerField("Ordem", validators=[Optional(), NumberRange(min=1, max=50)], default=1)
    tecnica = SelectField(
        "Técnica",
        choices=[
            ("tradicional", "Tradicional"),
            ("dropset", "Drop Set"),
            ("biset", "Bi-Set"),
            ("triset", "Tri-Set"),
            ("rest_pause", "Rest Pause"),
            ("piramide", "Pirâmide"),
            ("isometria", "Isometria"),
        ],
        default="tradicional",
    )
    observacoes = TextAreaField("Observações")
    submit = SubmitField("Salvar exercício")


class GerarTreinoIAForm(FlaskForm):
    aluno_id = HiddenField(validators=[DataRequired()])
    nome = StringField("Nome do treino", validators=[DataRequired(), Length(max=160)])
    objetivo = SelectField("Objetivo", choices=OBJETIVO_CHOICES, default="hipertrofia")
    divisao = SelectField("Divisão", choices=DIVISAO_CHOICES, default="ABC")
    frequencia_semanal = IntegerField(
        "Frequência semanal", validators=[DataRequired(), NumberRange(min=1, max=7)], default=3
    )
    nivel = SelectField("Nível", choices=NIVEL_CHOICES, default="iniciante")
    duracao_semanas = IntegerField(
        "Duração (semanas)", validators=[Optional(), NumberRange(min=2, max=24)], default=8
    )
    protocolo_chave = SelectField("Protocolo (opcional)", choices=[], default="")
    submit = SubmitField("Gerar treino com IA")
