"""Authentication forms."""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional


class LoginForm(FlaskForm):
    email = StringField(
        "E-mail",
        validators=[DataRequired(message="Informe o e-mail."), Email(message="E-mail inválido."), Length(max=180)],
    )
    password = PasswordField(
        "Senha",
        validators=[DataRequired(message="Informe a senha."), Length(min=6, max=128)],
    )
    remember = BooleanField("Manter conectado")
    submit = SubmitField("Entrar")


class RegisterForm(FlaskForm):
    nome = StringField(
        "Nome completo",
        validators=[DataRequired(message="Informe seu nome."), Length(min=3, max=120)],
    )
    email = StringField(
        "E-mail profissional",
        validators=[DataRequired(), Email(), Length(max=180)],
    )
    cref = StringField("CREF (opcional)", validators=[Optional(), Length(max=40)])
    password = PasswordField(
        "Senha",
        validators=[DataRequired(), Length(min=8, message="Senha deve ter no mínimo 8 caracteres.")],
    )
    confirm_password = PasswordField(
        "Confirmar senha",
        validators=[DataRequired(), EqualTo("password", message="As senhas não conferem.")],
    )
    submit = SubmitField("Criar conta")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Senha atual", validators=[DataRequired()])
    new_password = PasswordField(
        "Nova senha", validators=[DataRequired(), Length(min=8)]
    )
    confirm_new_password = PasswordField(
        "Confirmar nova senha",
        validators=[DataRequired(), EqualTo("new_password", message="As senhas não conferem.")],
    )
    submit = SubmitField("Atualizar senha")
