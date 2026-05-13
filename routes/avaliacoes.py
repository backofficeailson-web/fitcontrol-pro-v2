"""Avaliacoes CRUD routes."""
from datetime import date

from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user

from io import BytesIO

from schemas.avaliacao_forms import AvaliacaoForm
from services.aluno_service import AlunoService
from services.avaliacao_service import AvaliacaoService
from services.pdf_service import PDFService
from services.protocolo_service import ProtocoloService
from utils.security import ensure_owner

avaliacoes_bp = Blueprint("avaliacoes", __name__, url_prefix="/avaliacoes")


@avaliacoes_bp.route("/")
@login_required
def index():
    aluno_id = request.args.get("aluno_id", type=int)
    avals = AvaliacaoService.list_for_user(current_user.id, aluno_id=aluno_id)
    alunos = AlunoService.list_alunos(current_user.id)
    return render_template(
        "avaliacoes/list.html",
        avaliacoes=avals,
        alunos=alunos,
        aluno_filtro=aluno_id,
        protocolos_avaliacao=ProtocoloService.list_avaliacao(),
        protocolos_treino=ProtocoloService.list_treino(),
    )


@avaliacoes_bp.route("/novo", methods=["GET", "POST"])
@login_required
def create():
    aluno_id = request.args.get("aluno_id", type=int) or request.form.get("aluno_id", type=int)
    aluno = AlunoService.get_aluno(aluno_id, current_user.id) if aluno_id else None
    if aluno_id and not aluno:
        flash("Aluno não encontrado.", "danger")
        return redirect(url_for("alunos.index"))

    form = AvaliacaoForm()
    if not form.data.data:
        form.data.data = date.today()
    if aluno:
        form.aluno_id.data = aluno.id

    if form.validate_on_submit():
        target = aluno or AlunoService.get_aluno(int(form.aluno_id.data), current_user.id)
        if not target:
            flash("Aluno inválido.", "danger")
            return redirect(url_for("alunos.index"))
        payload = {name: field.data for name, field in form._fields.items()}
        av = AvaliacaoService.create(current_user.id, target, payload)
        flash("Avaliação cadastrada com sucesso.", "success")
        return redirect(url_for("avaliacoes.detail", avaliacao_id=av.id))

    alunos = AlunoService.list_alunos(current_user.id)
    return render_template(
        "avaliacoes/form.html",
        form=form, aluno=aluno, alunos=alunos, avaliacao=None,
    )


@avaliacoes_bp.route("/<int:avaliacao_id>")
@login_required
def detail(avaliacao_id: int):
    av = AvaliacaoService.get(avaliacao_id, current_user.id)
    ensure_owner(av, current_user.id)
    aluno = AlunoService.get_aluno(av.aluno_id, current_user.id)
    return render_template("avaliacoes/detail.html", avaliacao=av, aluno=aluno)


@avaliacoes_bp.route("/<int:avaliacao_id>/editar", methods=["GET", "POST"])
@login_required
def edit(avaliacao_id: int):
    av = AvaliacaoService.get(avaliacao_id, current_user.id)
    ensure_owner(av, current_user.id)
    aluno = AlunoService.get_aluno(av.aluno_id, current_user.id)
    form = AvaliacaoForm(obj=av)
    form.aluno_id.data = av.aluno_id
    if form.validate_on_submit():
        AvaliacaoService.update(av, aluno, form.data)
        flash("Avaliação atualizada.", "success")
        return redirect(url_for("avaliacoes.detail", avaliacao_id=av.id))
    alunos = AlunoService.list_alunos(current_user.id)
    return render_template(
        "avaliacoes/form.html",
        form=form, aluno=aluno, alunos=alunos, avaliacao=av,
    )


@avaliacoes_bp.route("/<int:avaliacao_id>/excluir", methods=["POST"])
@login_required
def delete(avaliacao_id: int):
    av = AvaliacaoService.get(avaliacao_id, current_user.id)
    ensure_owner(av, current_user.id)
    AvaliacaoService.delete(av)
    flash("Avaliação removida.", "info")
    return redirect(url_for("avaliacoes.index"))


@avaliacoes_bp.route("/<int:avaliacao_id>/pdf")
@login_required
def pdf(avaliacao_id: int):
    av = AvaliacaoService.get(avaliacao_id, current_user.id)
    ensure_owner(av, current_user.id)
    aluno = AlunoService.get_aluno(av.aluno_id, current_user.id)
    pdf_bytes = PDFService.avaliacao_pdf(av, aluno, base_url=request.host_url)
    buffer = BytesIO(pdf_bytes)
    buffer.seek(0)
    return send_file(
        buffer, mimetype="application/pdf", as_attachment=True,
        download_name=f"avaliacao_{aluno.nome.replace(' ', '_')}_{av.data}.pdf",
    )


@avaliacoes_bp.route("/comparativo/<int:aluno_id>")
@login_required
def comparativo(aluno_id: int):
    aluno = AlunoService.get_aluno(aluno_id, current_user.id)
    ensure_owner(aluno, current_user.id)
    dados = AvaliacaoService.comparativo(aluno_id, current_user.id)
    return render_template("avaliacoes/comparativo.html", aluno=aluno, dados=dados)
