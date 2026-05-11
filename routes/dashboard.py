"""Dashboard routes."""
from flask import Blueprint, render_template
from flask_login import login_required, current_user

from services.dashboard_service import DashboardService
from services.protocolo_service import ProtocoloService

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    metrics = DashboardService.metrics(current_user.id)
    feed = DashboardService.feed(current_user.id)
    chart_evolucao = DashboardService.evolucao_chart(current_user.id)
    chart_atividade = DashboardService.atividade_semana(current_user.id)
    return render_template(
        "dashboard/index.html",
        metrics=metrics,
        feed=feed,
        chart_evolucao=chart_evolucao,
        chart_atividade=chart_atividade,
        protocolos_treino=ProtocoloService.list_treino(),
        protocolos_avaliacao=ProtocoloService.list_avaliacao(),
    )
