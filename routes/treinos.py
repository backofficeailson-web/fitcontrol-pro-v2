from io import BytesIO

from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required

from schemas.treino_forms import ExercicioForm, GerarTreinoIAForm, TreinoForm
from services.aluno_service import AlunoService
from services.pdf_service import PDFService
from services.protocolo_service import ProtocoloService
from services.treino_service import TreinoService
from utils.security import ensure_owner


treinos_bp = Blueprint("treinos", __name__, url_prefix="/treinos")


def _posted_int(name):
    values = request.form.getlist(name)

    for value in reversed(values):
        if value not in (None, "", "None"):
            try:
                return int(value)
            except ValueError:
                return None

    return None


def _flash_form_errors(form):
    for campo, erros in form.errors.items():
        for erro in erros:
            flash(f"Erro no campo {campo}: {erro}", "danger")


def populate_protocolos(form):
    protocolos = ProtocoloService.list_treino()
    choices = [("", "Nenhum protocolo")]

    for protocolo in protocolos:
        choices.append((protocolo.chave, protocolo.nome))

    if hasattr(form, "protocolo_chave"):
        form.protocolo_chave.choices = choices


def populate_alunos(form):
    alunos = AlunoService.list_alunos(current_user.id)
    form.aluno_id.choices = [(a.id, a.nome) for a in alunos]
    return alunos


def _form_payload(form):
    return {
        name: field.data
        for name, field in form._fields.items()
        if name not in ("csrf_token", "submit")
    }


@treinos_bp.route("/")
@login_required
def index():
    aluno_id = request.args.get("aluno_id", type=int)
    status = request.args.get("status")

    treinos = TreinoService.list_for_user(
        current_user.id,
        aluno_id=aluno_id,
        status=status or "todos",
    )

    alunos = AlunoService.list_alunos(current_user.id)

    return render_template(
        "treinos/list.html",
        treinos=treinos,
        alunos=alunos,
        aluno_filtro=aluno_id,
        status=status,
        protocolos_treino=ProtocoloService.list_treino(),
    )


@treinos_bp.route("/novo", methods=["GET", "POST"])
@login_required
def create():
    aluno_id = request.args.get("aluno_id", type=int) or _posted_int("aluno_id")
    aluno = AlunoService.get_aluno(aluno_id, current_user.id) if aluno_id else None

    form = TreinoForm()
    alunos = populate_alunos(form)
    populate_protocolos(form)

    if request.method == "GET" and aluno:
        form.aluno_id.data = aluno.id

    if request.method == "POST":
        if aluno_id:
            form.aluno_id.data = aluno_id

        if form.validate_on_submit():
            target = aluno or AlunoService.get_aluno(int(form.aluno_id.data), current_user.id)

            if not target:
                flash("Aluno inválido.", "danger")
                return redirect(url_for("treinos.index"))

            payload = _form_payload(form)
            payload["aluno_id"] = target.id

            treino = TreinoService.create(current_user.id, target, payload)

            flash("Treino cadastrado com sucesso.", "success")
            return redirect(url_for("treinos.detail", treino_id=treino.id))

        _flash_form_errors(form)

    return render_template(
        "treinos/form.html",
        form=form,
        aluno=aluno,
        alunos=alunos,
        treino=None,
        protocolos=ProtocoloService.list_treino(),
    )


@treinos_bp.route("/gerar-ia", methods=["GET", "POST"])
@login_required
def gerar_ia():
    aluno_id = request.args.get("aluno_id", type=int) or _posted_int("aluno_id")
    aluno = AlunoService.get_aluno(aluno_id, current_user.id) if aluno_id else None

    form = GerarTreinoIAForm()
    alunos = populate_alunos(form)
    populate_protocolos(form)

    if request.method == "GET" and aluno:
        form.aluno_id.data = aluno.id

    if request.method == "POST":
        if aluno_id:
            form.aluno_id.data = aluno_id

        if form.validate_on_submit():
            target = aluno or AlunoService.get_aluno(int(form.aluno_id.data), current_user.id)

            if not target:
                flash("Aluno inválido.", "danger")
                return redirect(url_for("treinos.index"))

            treino = TreinoService.gerar_via_ia(
                current_user.id,
                target,
                nome=form.nome.data,
                objetivo=form.objetivo.data,
                divisao=form.divisao.data,
                frequencia=form.frequencia_semanal.data,
                nivel=form.nivel.data,
                protocolo_chave=form.protocolo_chave.data or None,
                duracao_semanas=form.duracao_semanas.data or 8,
            )

            flash("Treino gerado pelo motor de IA.", "success")
            return redirect(url_for("treinos.detail", treino_id=treino.id))

        _flash_form_errors(form)

    return render_template(
        "treinos/gerar_ia.html",
        form=form,
        aluno=aluno,
        alunos=alunos,
        protocolos=ProtocoloService.list_treino(),
    )


@treinos_bp.route("/<int:treino_id>")
@login_required
def detail(treino_id):
    treino = TreinoService.get(treino_id, current_user.id)
    ensure_owner(treino, current_user.id)

    aluno = AlunoService.get_aluno(treino.aluno_id, current_user.id)

    return render_template(
        "treinos/detail.html",
        treino=treino,
        aluno=aluno,
        exercicios_por_dia=treino.exercicios_por_dia(),
    )


@treinos_bp.route("/<int:treino_id>/editar", methods=["GET", "POST"])
@login_required
def edit(treino_id):
    treino = TreinoService.get(treino_id, current_user.id)
    ensure_owner(treino, current_user.id)

    aluno = AlunoService.get_aluno(treino.aluno_id, current_user.id)

    form = TreinoForm(obj=treino)
    alunos = populate_alunos(form)
    populate_protocolos(form)

    if request.method == "GET":
        form.aluno_id.data = treino.aluno_id

    if request.method == "POST":
        aluno_id = _posted_int("aluno_id") or treino.aluno_id
        form.aluno_id.data = aluno_id

        if form.validate_on_submit():
            payload = _form_payload(form)
            payload["aluno_id"] = aluno.id

            TreinoService.update(treino, aluno, payload)

            flash("Treino atualizado.", "success")
            return redirect(url_for("treinos.detail", treino_id=treino.id))

        _flash_form_errors(form)

    return render_template(
        "treinos/form.html",
        form=form,
        aluno=aluno,
        alunos=alunos,
        treino=treino,
        protocolos=ProtocoloService.list_treino(),
    )


@treinos_bp.route("/<int:treino_id>/exercicios/novo", methods=["GET", "POST"])
@login_required
def add_exercicio(treino_id):
    treino = TreinoService.get(treino_id, current_user.id)
    ensure_owner(treino, current_user.id)

    form = ExercicioForm()

    if form.validate_on_submit():
        TreinoService.add_exercicio(treino, form.data)

        flash("Exercício adicionado.", "success")
        return redirect(url_for("treinos.detail", treino_id=treino.id))

    return render_template(
        "treinos/exercicio_form.html",
        form=form,
        treino=treino,
        exercicio=None,
    )


@treinos_bp.route("/<int:treino_id>/excluir", methods=["POST"])
@login_required
def delete(treino_id):
    treino = TreinoService.get(treino_id, current_user.id)
    ensure_owner(treino, current_user.id)

    TreinoService.delete(treino)

    flash("Treino excluído.", "success")
    return redirect(url_for("treinos.index"))


@treinos_bp.route("/<int:treino_id>/pdf")
@login_required
def pdf(treino_id):
    treino = TreinoService.get(treino_id, current_user.id)
    ensure_owner(treino, current_user.id)

    aluno = AlunoService.get_aluno(treino.aluno_id, current_user.id)

    pdf_bytes = PDFService.treino_pdf(
        treino,
        aluno,
        base_url=request.host_url,
    )

    buffer = BytesIO(pdf_bytes)
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"treino_{treino_id}.pdf",
    )