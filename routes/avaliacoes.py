from datetime import date
from io import BytesIO

from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required

from schemas.avaliacao_forms import AvaliacaoForm
from services.aluno_service import AlunoService
from services.avaliacao_service import AvaliacaoService
from services.pdf_service import PDFService
from services.protocolo_service import ProtocoloService
from utils.security import ensure_owner


avaliacoes_bp = Blueprint("avaliacoes", __name__, url_prefix="/avaliacoes")


def _avaliacao_payload(form: AvaliacaoForm) -> dict:
    return {
        name: field.data
        for name, field in form._fields.items()
        if name not in ("csrf_token", "submit")
    }


def _flash_form_errors(form: AvaliacaoForm) -> None:
    for campo, erros in form.errors.items():
        for erro in erros:
            flash(f"Erro no campo {campo}: {erro}", "danger")


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

    if request.method == "GET":
        if not form.data.data:
            form.data.data = date.today()

        if aluno:
            form.aluno_id.data = aluno.id

    if request.method == "POST":
        if aluno and not form.aluno_id.data:
            form.aluno_id.data = aluno.id

        if form.validate_on_submit():
            target = aluno or AlunoService.get_aluno(int(form.aluno_id.data), current_user.id)

            if not target:
                flash("Aluno inválido.", "danger")
                return redirect(url_for("alunos.index"))

            payload = _avaliacao_payload(form)
            av = AvaliacaoService.create(current_user.id, target, payload)

            flash("Avaliação cadastrada com sucesso.", "success")
            return redirect(url_for("avaliacoes.detail", avaliacao_id=av.id))

        _flash_form_errors(form)

    alunos = AlunoService.list_alunos(current_user.id)

    return render_template(
        "avaliacoes/form.html",
        form=form,
        aluno=aluno,
        alunos=alunos,
        avaliacao=None,
    )


@avaliacoes_bp.route("/<int:avaliacao_id>")
@login_required
def detail(avaliacao_id: int):
    av = AvaliacaoService.get(avaliacao_id, current_user.id)
    ensure_owner(av, current_user.id)

    aluno = AlunoService.get_aluno(av.aluno_id, current_user.id)

    return render_template(
        "avaliacoes/detail.html",
        avaliacao=av,
        aluno=aluno,
    )


@avaliacoes_bp.route("/<int:avaliacao_id>/editar", methods=["GET", "POST"])
@login_required
def edit(avaliacao_id: int):
    av = AvaliacaoService.get(avaliacao_id, current_user.id)
    ensure_owner(av, current_user.id)

    aluno = AlunoService.get_aluno(av.aluno_id, current_user.id)

    form = AvaliacaoForm(obj=av)

    if request.method == "GET":
        form.aluno_id.data = av.aluno_id

    if request.method == "POST":
        if not form.aluno_id.data:
            form.aluno_id.data = av.aluno_id

        if form.validate_on_submit():
            payload = _avaliacao_payload(form)
            AvaliacaoService.update(av, aluno, payload)

            flash("Avaliação atualizada.", "success")
            return redirect(url_for("avaliacoes.detail", avaliacao_id=av.id))

        _flash_form_errors(form)

    alunos = AlunoService.list_alunos(current_user.id)

    return render_template(
        "avaliacoes/form.html",
        form=form,
        aluno=aluno,
        alunos=alunos,
        avaliacao=av,
    )


@avaliacoes_bp.route("/<int:avaliacao_id>/excluir", methods=["POST"])
@login_required
def delete(avaliacao_id: int):
    av = AvaliacaoService.get(avaliacao_id, current_user.id)
    ensure_owner(av, current_user.id)

    AvaliacaoService.delete(av)

    flash("Avaliação excluída.", "success")
    return redirect(url_for("avaliacoes.index"))


@avaliacoes_bp.route("/<int:avaliacao_id>/pdf")
@login_required
def pdf(avaliacao_id: int):
    av = AvaliacaoService.get(avaliacao_id, current_user.id)
    ensure_owner(av, current_user.id)

    aluno = AlunoService.get_aluno(av.aluno_id, current_user.id)

    pdf_bytes = PDFService.avaliacao_pdf(
        av,
        aluno,
        base_url=request.host_url,
    )

    buffer = BytesIO(pdf_bytes)
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"avaliacao_{avaliacao_id}.pdf",
    )