"""Aluno forms."""
from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, DateField, SelectField,
    FloatField, SubmitField,
)
from wtforms.validators import DataRequired, Optional, Email, Length, NumberRange


class AlunoForm(FlaskForm):
    nome = StringField("Nome completo", validators=[DataRequired(), Length(min=2, max=160)])
    email = StringField("E-mail", validators=[Optional(), Email(), Length(max=180)])
    telefone = StringField("Telefone", validators=[Optional(), Length(max=40)])
    nascimento = DateField("Data de nascimento", validators=[Optional()], format="%Y-%m-%d")
    sexo = SelectField(
        "Sexo",
        choices=[("", "Selecione"), ("masculino", "Masculino"), ("feminino", "Feminino"), ("outro", "Outro")],
        validators=[Optional()],
    )
    altura = FloatField("Altura (m)", validators=[Optional(), NumberRange(min=0.5, max=2.5)])
    peso_inicial = FloatField("Peso inicial (kg)", validators=[Optional(), NumberRange(min=20, max=350)])
    objetivo = SelectField(
        "Objetivo principal",
        choices=[
            ("", "Selecione"),
            ("hipertrofia", "Hipertrofia"),
            ("emagrecimento", "Emagrecimento"),
            ("forca", "Força"),
            ("condicionamento", "Condicionamento"),
            ("resistencia", "Resistência"),
            ("esporte", "Performance Esportiva"),
            ("saude", "Saúde geral"),
            ("estetica", "Estética"),
        ],
        validators=[Optional()],
    )
    nivel_condicionamento = SelectField(
        "Nível",
        choices=[("iniciante", "Iniciante"), ("intermediario", "Intermediário"), ("avancado", "Avançado")],
        default="iniciante",
    )
    condicoes_especiais = StringField(
        "Condições especiais (separe por vírgula)", validators=[Optional(), Length(max=255)]
    )
    observacoes = TextAreaField("Observações", validators=[Optional(), Length(max=5000)])
    status = SelectField(
        "Status",
        choices=[("ativo", "Ativo"), ("inativo", "Inativo"), ("pausado", "Pausado")],
        default="ativo",
    )
    submit = SubmitField("Salvar")
