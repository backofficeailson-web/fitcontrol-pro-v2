"""Alunos CRUD routes."""
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from schemas.aluno_forms import AlunoForm
from services.aluno_service import AlunoService
from services.protocolo_service import ProtocoloService
from utils.security import ensure_owner

alunos_bp = Blueprint("alunos", __name__, url_prefix="/alunos")


@alunos_bp.route("/")
@login_required
def index():
    search = request.args.get("q", "").strip() or None
    status = request.args.get("status") or None
    alunos = AlunoService.list_alunos(current_user.id, search=search, status=status)
    return render_template(
        "alunos/list.html",
        alunos=alunos,
        search=search or "",
        status=status or "todos",
        protocolos_treino=ProtocoloService.list_treino(),
        protocolos_avaliacao=ProtocoloService.list_avaliacao(),
    )


@alunos_bp.route("/novo", methods=["GET", "POST"])
@login_required
def create():
    form = AlunoForm()
    if form.validate_on_submit():
        AlunoService.create_aluno(current_user.id, form.data)
        flash("Aluno cadastrado com sucesso.", "success")
        return redirect(url_for("alunos.index"))
    return render_template("alunos/form.html", form=form, aluno=None)


@alunos_bp.route("/<int:aluno_id>")
@login_required
def detail(aluno_id: int):
    aluno = AlunoService.get_aluno(aluno_id, current_user.id)
    ensure_owner(aluno, current_user.id)
    return render_template(
        "alunos/detail.html",
        aluno=aluno,
        protocolos_treino=ProtocoloService.list_treino(),
        protocolos_avaliacao=ProtocoloService.list_avaliacao(),
    )


@alunos_bp.route("/<int:aluno_id>/editar", methods=["GET", "POST"])
@login_required
def edit(aluno_id: int):
    aluno = AlunoService.get_aluno(aluno_id, current_user.id)
    ensure_owner(aluno, current_user.id)
    form = AlunoForm(obj=aluno)
    if form.validate_on_submit():
        AlunoService.update_aluno(aluno, form.data)
        flash("Dados do aluno atualizados.", "success")
        return redirect(url_for("alunos.detail", aluno_id=aluno.id))
    return render_template("alunos/form.html", form=form, aluno=aluno)


@alunos_bp.route("/<int:aluno_id>/excluir", methods=["POST"])
@login_required
def delete(aluno_id: int):
    aluno = AlunoService.get_aluno(aluno_id, current_user.id)
    ensure_owner(aluno, current_user.id)
    AlunoService.delete_aluno(aluno)
    flash("Aluno removido.", "info")
    return redirect(url_for("alunos.index"))
