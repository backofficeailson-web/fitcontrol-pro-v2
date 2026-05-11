"""Authentication routes."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from extensions import limiter
from schemas.auth_forms import LoginForm, RegisterForm, ChangePasswordForm
from services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute", methods=["POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = AuthService.authenticate(
                form.email.data, form.password.data,
                ip_address=request.remote_addr,
            )
            login_user(user, remember=form.remember.data)
            flash("Bem-vindo(a) ao FitControl Pro.", "success")
            next_url = request.args.get("next")
            if next_url and next_url.startswith("/"):
                return redirect(next_url)
            return redirect(url_for("dashboard.index"))
        except ValueError as exc:
            flash(str(exc), "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = AuthService.register(
                nome=form.nome.data,
                email=form.email.data,
                password=form.password.data,
                cref=form.cref.data,
            )
            login_user(user)
            flash("Conta criada com sucesso. Bem-vindo(a)!", "success")
            return redirect(url_for("dashboard.index"))
        except ValueError as exc:
            flash(str(exc), "danger")
    return render_template("auth/register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sessão encerrada.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        try:
            AuthService.update_password(
                current_user, form.current_password.data, form.new_password.data
            )
            flash("Senha atualizada com sucesso.", "success")
            return redirect(url_for("auth.profile"))
        except ValueError as exc:
            flash(str(exc), "danger")
    return render_template("auth/profile.html", form=form)
