"""Protocolos catalog routes."""
from flask import Blueprint, render_template, abort
from flask_login import login_required

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


@protocolos_bp.route("/<chave>")
@login_required
def detail(chave: str):
    protocolo = ProtocoloService.get(chave)
    if not protocolo:
        abort(404)
    return render_template("protocolos/detail.html", protocolo=protocolo)
