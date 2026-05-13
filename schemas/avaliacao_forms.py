"""Avaliacao forms."""
from flask_wtf import FlaskForm
from wtforms import (
    SelectField, FloatField, DateField, TextAreaField, SubmitField, HiddenField,
)
from wtforms.validators import DataRequired, Optional, NumberRange


class AvaliacaoForm(FlaskForm):
    aluno_id = HiddenField(validators=[DataRequired()])
    data = DateField("Data da avaliação", validators=[DataRequired()], format="%Y-%m-%d")
    protocolo = SelectField(
        "Protocolo de avaliação",
        choices=[
            ("pollock_3", "Pollock 3 dobras"),
            ("pollock_7", "Pollock 7 dobras"),
            ("imc", "Apenas IMC"),
            ("circunferencias", "Apenas perimetria"),
        ],
        default="pollock_3",
    )

    peso = FloatField("Peso (kg)", validators=[Optional(), NumberRange(min=20, max=350)])
    altura = FloatField("Altura (cm)", validators=[Optional(), NumberRange(min=50, max=250)])
    cintura = FloatField("Cintura (cm)", validators=[Optional(), NumberRange(min=30, max=250)])
    quadril = FloatField("Quadril (cm)", validators=[Optional(), NumberRange(min=30, max=250)])
    peito = FloatField("Peito (cm)", validators=[Optional(), NumberRange(min=30, max=250)])
    braco = FloatField("Braço (cm)", validators=[Optional(), NumberRange(min=15, max=80)])
    coxa = FloatField("Coxa (cm)", validators=[Optional(), NumberRange(min=20, max=120)])
    panturrilha = FloatField("Panturrilha (cm)", validators=[Optional(), NumberRange(min=15, max=80)])
    abdomen = FloatField("Abdômen (cm)", validators=[Optional(), NumberRange(min=30, max=250)])

    dobra_triceps = FloatField("Dobra Tríceps (mm)", validators=[Optional(), NumberRange(min=1, max=80)])
    dobra_peitoral = FloatField("Dobra Peitoral (mm)", validators=[Optional(), NumberRange(min=1, max=80)])
    dobra_subaxilar = FloatField("Dobra Subaxilar (mm)", validators=[Optional(), NumberRange(min=1, max=80)])
    dobra_subescapular = FloatField("Dobra Subescapular (mm)", validators=[Optional(), NumberRange(min=1, max=80)])
    dobra_abdominal = FloatField("Dobra Abdominal (mm)", validators=[Optional(), NumberRange(min=1, max=80)])
    dobra_suprailiaca = FloatField("Dobra Suprailíaca (mm)", validators=[Optional(), NumberRange(min=1, max=80)])
    dobra_coxa = FloatField("Dobra Coxa (mm)", validators=[Optional(), NumberRange(min=1, max=80)])

    observacoes = TextAreaField("Observações")
    submit = SubmitField("Salvar avaliação")
