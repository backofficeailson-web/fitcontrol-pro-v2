"""Treinos CRUD + AI generation routes."""
from io import BytesIO

from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user

from schemas.treino_forms import TreinoForm, ExercicioForm, GerarTreinoIAForm
from services.aluno_service import AlunoService
from services.treino_service import TreinoService
from services.pdf_service import PDFService
from services.protocolo_service import ProtocoloService
from utils.security import ensure_owner

treinos_bp = Blueprint("treinos", __name__, url_prefix="/treinos")


def _populate_protocolos(form: GerarTreinoIAForm) -> None:
    choices = [("", "— Sem protocolo —")]
    for p in ProtocoloService.list_treino():
        choices.append((p.chave, p.nome))
    form.protocolo_chave.choices = choices


@treinos_bp.route("/")
@login_required
def index():
    aluno_id = request.args.get("aluno_id", type=int)
    status = request.args.get("status") or None
    treinos = TreinoService.list_for_user(current_user.id, aluno_id=aluno_id, status=status)
    alunos = AlunoService.list_alunos(current_user.id)
    return render_template(
        "treinos/list.html",
        treinos=treinos, alunos=alunos,
        aluno_filtro=aluno_id, status=status or "todos",
        protocolos_treino=ProtocoloService.list_treino(),
        protocolos_avaliacao=ProtocoloService.list_avaliacao(),
    )


@treinos_bp.route("/novo", methods=["GET", "POST"])
@login_required
def create():
    aluno_id = request.args.get("aluno_id", type=int)
    aluno = AlunoService.get_aluno(aluno_id, current_user.id) if aluno_id else None
    form = TreinoForm()
    if aluno:
        form.aluno_id.data = aluno.id
    if form.validate_on_submit():
        target = aluno or AlunoService.get_aluno(int(form.aluno_id.data), current_user.id)
        if not target:
            flash("Aluno inválido.", "danger")
            return redirect(url_for("treinos.index"))
        treino = TreinoService.create_manual(current_user.id, target.id, form.data)
        flash("Treino criado.", "success")
        return redirect(url_for("treinos.detail", treino_id=treino.id))
    alunos = AlunoService.list_alunos(current_user.id)
    return render_template("treinos/form.html", form=form, aluno=aluno, alunos=alunos, treino=None)


@treinos_bp.route("/<int:treino_id>")
@login_required
def detail(treino_id: int):
    treino = TreinoService.get(treino_id, current_user.id)
    ensure_owner(treino, current_user.id)
    aluno = AlunoService.get_aluno(treino.aluno_id, current_user.id)
    return render_template(
        "treinos/detail.html",
        treino=treino, aluno=aluno,
        exercicios_por_dia=treino.exercicios_por_dia(),
    )


@treinos_bp.route("/<int:treino_id>/editar", methods=["GET", "POST"])
@login_required
def edit(treino_id: int):
    treino = TreinoService.get(treino_id, current_user.id)
    ensure_owner(treino, current_user.id)
    form = TreinoForm(obj=treino)
    form.aluno_id.data = treino.aluno_id
    if form.validate_on_submit():
        TreinoService.update(treino, form.data)
        flash("Treino atualizado.", "success")
        return redirect(url_for("treinos.detail", treino_id=treino.id))
    alunos = AlunoService.list_alunos(current_user.id)
    return render_template(
        "treinos/form.html", form=form, aluno=treino.aluno, alunos=alunos, treino=treino,
    )


@treinos_bp.route("/<int:treino_id>/excluir", methods=["POST"])
@login_required
def delete(treino_id: int):
    treino = TreinoService.get(treino_id, current_user.id)
    ensure_owner(treino, current_user.id)
    TreinoService.delete(treino)
    flash("Treino removido.", "info")
    return redirect(url_for("treinos.index"))


@treinos_bp.route("/gerar-ia", methods=["GET", "POST"])
@login_required
def gerar_ia():
    aluno_id = request.args.get("aluno_id", type=int) or request.form.get("aluno_id", type=int)
    aluno = AlunoService.get_aluno(aluno_id, current_user.id) if aluno_id else None
    form = GerarTreinoIAForm()
    _populate_protocolos(form)
    if aluno:
        form.aluno_id.data = aluno.id
    if form.validate_on_submit():
        target = aluno or AlunoService.get_aluno(int(form.aluno_id.data), current_user.id)
        if not target:
            flash("Aluno inválido.", "danger")
            return redirect(url_for("treinos.index"))
        treino = TreinoService.gerar_via_ia(
            current_user.id, target,
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
    alunos = AlunoService.list_alunos(current_user.id)
    return render_template(
        "treinos/gerar_ia.html",
        form=form, aluno=aluno, alunos=alunos,
        protocolos=ProtocoloService.list_treino(),
    )


@treinos_bp.route("/<int:treino_id>/exercicios/novo", methods=["GET", "POST"])
@login_required
def add_exercicio(treino_id: int):
    treino = TreinoService.get(treino_id, current_user.id)
    ensure_owner(treino, current_user.id)
    form = ExercicioForm()
    if form.validate_on_submit():
        TreinoService.add_exercicio(treino, form.data)
        flash("Exercício adicionado.", "success")
        return redirect(url_for("treinos.detail", treino_id=treino.id))
    return render_template(
        "treinos/exercicio_form.html", form=form, treino=treino, exercicio=None,
    )


@treinos_bp.route("/exercicios/<int:exercicio_id>/editar", methods=["GET", "POST"])
@login_required
def edit_exercicio(exercicio_id: int):
    from repositories.exercicio_repository import ExercicioRepository
    exercicio = ExercicioRepository.get_for_user(exercicio_id, current_user.id)
    if not exercicio:
        flash("Exercício não encontrado.", "danger")
        return redirect(url_for("treinos.index"))
    treino = TreinoService.get(exercicio.treino_id, current_user.id)
    form = ExercicioForm(obj=exercicio)
    if form.validate_on_submit():
        TreinoService.update_exercicio(exercicio, form.data)
        flash("Exercício atualizado.", "success")
        return redirect(url_for("treinos.detail", treino_id=treino.id))
    return render_template(
        "treinos/exercicio_form.html", form=form, treino=treino, exercicio=exercicio,
    )


@treinos_bp.route("/exercicios/<int:exercicio_id>/excluir", methods=["POST"])
@login_required
def delete_exercicio(exercicio_id: int):
    from repositories.exercicio_repository import ExercicioRepository
    exercicio = ExercicioRepository.get_for_user(exercicio_id, current_user.id)
    if not exercicio:
        flash("Exercício não encontrado.", "danger")
        return redirect(url_for("treinos.index"))
    treino_id = exercicio.treino_id
    TreinoService.delete_exercicio(exercicio)
    flash("Exercício removido.", "info")
    return redirect(url_for("treinos.detail", treino_id=treino_id))


@treinos_bp.route("/<int:treino_id>/pdf")
@login_required
def pdf(treino_id: int):
    treino = TreinoService.get(treino_id, current_user.id)
    ensure_owner(treino, current_user.id)
    aluno = AlunoService.get_aluno(treino.aluno_id, current_user.id)
    pdf_bytes = PDFService.treino_pdf(treino, aluno, base_url=request.host_url)
    buffer = BytesIO(pdf_bytes)
    buffer.seek(0)
    return send_file(
        buffer, mimetype="application/pdf", as_attachment=True,
        download_name=f"treino_{aluno.nome.replace(' ', '_')}_{treino.id}.pdf",
    )
