"""Internal JSON API routes."""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from services.aluno_service import AlunoService
from services.avaliacao_service import AvaliacaoService
from services.protocolo_service import ProtocoloService
from utils.security import ensure_owner

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/protocolos")
@login_required
def list_protocolos():
    return jsonify({
        "avaliacao": [p.to_dict() for p in ProtocoloService.list_avaliacao()],
        "treino": [p.to_dict() for p in ProtocoloService.list_treino()],
    })


@api_bp.route("/protocolos/<chave>")
@login_required
def get_protocolo(chave: str):
    protocolo = ProtocoloService.get(chave)
    if not protocolo:
        return jsonify({"error": "Protocolo não encontrado."}), 404
    return jsonify(protocolo.to_dict())


@api_bp.route("/alunos")
@login_required
def list_alunos():
    search = request.args.get("q") or None
    alunos = AlunoService.list_alunos(current_user.id, search=search)
    return jsonify([a.to_dict() for a in alunos])


@api_bp.route("/alunos/<int:aluno_id>/evolucao")
@login_required
def aluno_evolucao(aluno_id: int):
    aluno = AlunoService.get_aluno(aluno_id, current_user.id)
    ensure_owner(aluno, current_user.id)
    history = AvaliacaoService.history(aluno_id, current_user.id)
    return jsonify({
        "labels": [a.data.strftime("%d/%m/%Y") if a.data else "" for a in history],
        "peso": [a.peso for a in history],
        "imc": [a.imc for a in history],
        "gordura": [a.percentual_gordura for a in history],
        "massa_magra": [a.massa_magra for a in history],
    })
