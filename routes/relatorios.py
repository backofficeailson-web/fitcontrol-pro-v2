"""Relatorios routes."""
from io import BytesIO

from flask import Blueprint, render_template, request, send_file, flash, redirect, url_for
from flask_login import login_required, current_user

from services.aluno_service import AlunoService
from services.avaliacao_service import AvaliacaoService
from services.treino_service import TreinoService
from services.pdf_service import PDFService
from services.protocolo_service import ProtocoloService
from utils.security import ensure_owner

relatorios_bp = Blueprint("relatorios", __name__, url_prefix="/relatorios")


@relatorios_bp.route("/")
@login_required
def index():
    alunos = AlunoService.list_alunos(current_user.id)
    return render_template(
        "relatorios/index.html",
        alunos=alunos,
        protocolos_treino=ProtocoloService.list_treino(),
        protocolos_avaliacao=ProtocoloService.list_avaliacao(),
    )


@relatorios_bp.route("/aluno/<int:aluno_id>/pdf")
@login_required
def aluno_pdf(aluno_id: int):
    aluno = AlunoService.get_aluno(aluno_id, current_user.id)
    ensure_owner(aluno, current_user.id)
    avaliacoes = AvaliacaoService.history(aluno_id, current_user.id)
    treinos = TreinoService.list_for_user(current_user.id, aluno_id=aluno_id)
    pdf_bytes = PDFService.aluno_completo_pdf(
        aluno, avaliacoes, treinos, base_url=request.host_url,
    )
    buffer = BytesIO(pdf_bytes)
    buffer.seek(0)
    return send_file(
        buffer, mimetype="application/pdf", as_attachment=True,
        download_name=f"relatorio_{aluno.nome.replace(' ', '_')}.pdf",
    )
