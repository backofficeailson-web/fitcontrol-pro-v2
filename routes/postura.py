"""Avaliação Postural - routes."""
from __future__ import annotations

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from services.aluno_service import AlunoService
from services.postura_service import PosturaService
from services.upload_service import UploadService, UploadError
from utils.security import ensure_owner

postura_bp = Blueprint("postura", __name__, url_prefix="/postura")


def _save_images(files_dict) -> dict:
    """Salva imagens postais opcionais e retorna {label: path}."""
    out = {}
    for label in ("frontal", "lateral_direita", "lateral_esquerda", "posterior"):
        f = files_dict.get(f"img_{label}")
        if f and f.filename:
            meta = UploadService.save(f, "posture", current_user.id)
            out[label] = meta["path"]
    return out


@postura_bp.route("/")
@login_required
def index():
    posts = PosturaService.list_for_user(current_user.id, limit=100)
    return render_template("postura/list.html", posts=posts)


@postura_bp.route("/aluno/<int:aluno_id>")
@login_required
def por_aluno(aluno_id: int):
    aluno = AlunoService.get_aluno(aluno_id, current_user.id)
    if not aluno:
        abort(404)
    ensure_owner(aluno, current_user.id)
    posts = PosturaService.list_for_aluno(aluno_id, current_user.id)
    return render_template("postura/por_aluno.html", aluno=aluno, posts=posts)


@postura_bp.route("/novo/<int:aluno_id>", methods=["GET", "POST"])
@login_required
def create(aluno_id: int):
    aluno = AlunoService.get_aluno(aluno_id, current_user.id)
    if not aluno:
        abort(404)
    ensure_owner(aluno, current_user.id)

    if request.method == "POST":
        try:
            images = _save_images(request.files)
        except UploadError as exc:
            flash(f"Erro no upload: {exc}", "danger")
            return render_template("postura/form.html", aluno=aluno, post=None,
                                   form_data=request.form)

        post = PosturaService.create(
            user_id=current_user.id,
            aluno_id=aluno.id,
            data=request.form.to_dict(),
            images=images,
        )
        flash("Avaliação postural registrada.", "success")
        return redirect(url_for("postura.detail", post_id=post.id))

    return render_template("postura/form.html", aluno=aluno, post=None)


@postura_bp.route("/<int:post_id>")
@login_required
def detail(post_id: int):
    post = PosturaService.get(post_id, current_user.id)
    if not post:
        abort(404)
    aluno = post.aluno
    anterior = None
    if post.avaliacao_anterior_id:
        anterior = PosturaService.get(post.avaliacao_anterior_id, current_user.id)
    return render_template(
        "postura/detail.html", post=post, aluno=aluno, anterior=anterior
    )


@postura_bp.route("/<int:post_id>/editar", methods=["GET", "POST"])
@login_required
def edit(post_id: int):
    post = PosturaService.get(post_id, current_user.id)
    if not post:
        abort(404)
    if request.method == "POST":
        try:
            images = _save_images(request.files)
        except UploadError as exc:
            flash(f"Erro no upload: {exc}", "danger")
            return render_template("postura/form.html", aluno=post.aluno, post=post,
                                   form_data=request.form)
        PosturaService.update(post, request.form.to_dict(), images)
        flash("Avaliação postural atualizada.", "success")
        return redirect(url_for("postura.detail", post_id=post.id))
    return render_template("postura/form.html", aluno=post.aluno, post=post)


@postura_bp.route("/<int:post_id>/excluir", methods=["POST"])
@login_required
def delete(post_id: int):
    post = PosturaService.get(post_id, current_user.id)
    if not post:
        abort(404)
    aluno_id = post.aluno_id
    PosturaService.delete(post)
    flash("Avaliação postural removida.", "info")
    return redirect(url_for("postura.por_aluno", aluno_id=aluno_id))


@postura_bp.route("/<int:post_id>/comparar/<int:anterior_id>")
@login_required
def comparar(post_id: int, anterior_id: int):
    atual = PosturaService.get(post_id, current_user.id)
    anterior = PosturaService.get(anterior_id, current_user.id)
    if not atual or not anterior:
        abort(404)
    comp = PosturaService.comparar(atual, anterior)
    return render_template("postura/comparar.html", comp=comp, aluno=atual.aluno)
