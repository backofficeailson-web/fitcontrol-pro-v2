"""Protocolos catalog routes."""
from flask import Blueprint, render_template, abort, request, redirect, url_for, flash
from flask_login import login_required, current_user

from models import db
from models.protocolo import Protocolo
from services.protocolo_service import ProtocoloService

protocolos_bp = Blueprint("protocolos", __name__, url_prefix="/protocolos")


@protocolos_bp.route("/")
@login_required
def index():
    return render_template(
        "protocolos/list.html",
        protocolos_avaliacao=ProtocoloService.list_avaliacao(),
        protocolos_treino=ProtocoloService.list_treino(),
    )


@protocolos_bp.route("/<int:protocolo_id>/editar", methods=["GET", "POST"])
@login_required
def edit(protocolo_id: int):
    protocolo = Protocolo.query.filter_by(
        id=protocolo_id,
        user_id=current_user.id,
    ).first_or_404()

    if request.method == "POST":
        protocolo.nome = request.form.get("nome", "").strip()
        protocolo.descricao = request.form.get("descricao", "").strip()
        protocolo.payload = request.form.get("payload", "").strip()

        db.session.commit()

        flash("Protocolo atualizado com sucesso.", "success")
        return redirect(url_for("protocolos.detail", chave=protocolo.chave))

    return render_template(
        "protocolos/edit.html",
        protocolo=protocolo,
    )


@protocolos_bp.route("/<chave>")
@login_required
def detail(chave: str):
    protocolo = ProtocoloService.get(chave)
    if not protocolo:
        abort(404)

    return render_template(
        "protocolos/detail.html",
        protocolo=protocolo,
    )