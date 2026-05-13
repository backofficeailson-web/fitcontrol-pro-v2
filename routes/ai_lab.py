"""AI Lab — área de IA para upload e análise de arquivos."""
from __future__ import annotations

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user

from extensions import limiter
from models import db
from models.ai_analysis import AIAnalysis
from services.upload_service import UploadService, UploadError
from services.ai_engine_analysis import AIAnalysisEngine

ai_lab_bp = Blueprint("ai_lab", __name__, url_prefix="/ai")


@ai_lab_bp.route("/")
@login_required
def index():
    analises = (
        db.session.query(AIAnalysis)
        .filter(AIAnalysis.user_id == current_user.id)
        .order_by(AIAnalysis.created_at.desc())
        .limit(50)
        .all()
    )
    return render_template("ai_lab/index.html", analises=analises)


@ai_lab_bp.route("/upload", methods=["POST"])
@login_required
@limiter.limit("20 per minute")
def upload():
    f = request.files.get("arquivo")
    if not f or not f.filename:
        flash("Selecione um arquivo para análise.", "warning")
        return redirect(url_for("ai_lab.index"))

    try:
        meta = UploadService.save(f, "ai_analysis", current_user.id)
    except UploadError as exc:
        flash(f"Upload inválido: {exc}", "danger")
        return redirect(url_for("ai_lab.index"))

    tipo = AIAnalysisEngine.detect_type(meta["original_name"], meta["mime"])
    analysis = AIAnalysis(
        user_id=current_user.id,
        nome_arquivo=meta["original_name"],
        tipo_arquivo=tipo,
        tamanho_bytes=meta["size_bytes"],
        mime_type=meta["mime"],
        caminho=meta["absolute_path"],
        status="pending",
        progresso=0,
    )
    db.session.add(analysis)
    db.session.commit()

    # Processamento sincrono (rápido para uploads pequenos)
    AIAnalysisEngine.analyze(analysis.id)

    flash("Arquivo analisado com sucesso.", "success")
    return redirect(url_for("ai_lab.detail", analysis_id=analysis.id))


@ai_lab_bp.route("/<int:analysis_id>")
@login_required
def detail(analysis_id: int):
    a = db.session.get(AIAnalysis, analysis_id)
    if not a or a.user_id != current_user.id:
        abort(404)
    return render_template("ai_lab/detail.html", a=a)


@ai_lab_bp.route("/<int:analysis_id>/status")
@login_required
def status(analysis_id: int):
    a = db.session.get(AIAnalysis, analysis_id)
    if not a or a.user_id != current_user.id:
        abort(404)
    return jsonify(a.to_dict())


@ai_lab_bp.route("/<int:analysis_id>/excluir", methods=["POST"])
@login_required
def delete(analysis_id: int):
    a = db.session.get(AIAnalysis, analysis_id)
    if not a or a.user_id != current_user.id:
        abort(404)
    UploadService.delete(a.caminho.replace(str(db.engine.url), ""))
    db.session.delete(a)
    db.session.commit()
    flash("Análise removida.", "info")
    return redirect(url_for("ai_lab.index"))


@ai_lab_bp.route("/<int:analysis_id>/reprocessar", methods=["POST"])
@login_required
@limiter.limit("10 per minute")
def reprocessar(analysis_id: int):
    a = db.session.get(AIAnalysis, analysis_id)
    if not a or a.user_id != current_user.id:
        abort(404)
    a.status = "pending"
    a.progresso = 0
    a.erro_msg = None
    db.session.commit()
    AIAnalysisEngine.analyze(a.id)
    flash("Análise reprocessada.", "success")
    return redirect(url_for("ai_lab.detail", analysis_id=a.id))
