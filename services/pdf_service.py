"""PDF rendering service using WeasyPrint."""
import logging

from flask import render_template

logger = logging.getLogger("fitcontrol.error")


class PDFService:
    @staticmethod
    def _render_pdf(html: str, base_url: str) -> bytes:
        try:
            from weasyprint import HTML  # imported lazily for environments without weasyprint
        except Exception as exc:
            logger.error("WeasyPrint indisponível: %s", exc)
            raise RuntimeError(
                "WeasyPrint não está disponível neste ambiente. "
                "Instale as dependências do sistema (libpango, libcairo, libgdk-pixbuf)."
            ) from exc
        return HTML(string=html, base_url=base_url).write_pdf()

    @staticmethod
    def avaliacao_pdf(avaliacao, aluno, base_url: str) -> bytes:
        html = render_template(
            "pdf/avaliacao_pdf.html", avaliacao=avaliacao, aluno=aluno
        )
        return PDFService._render_pdf(html, base_url)

    @staticmethod
    def treino_pdf(treino, aluno, base_url: str) -> bytes:
        html = render_template(
            "pdf/treino_pdf.html", treino=treino, aluno=aluno,
            exercicios_por_dia=treino.exercicios_por_dia(),
        )
        return PDFService._render_pdf(html, base_url)

    @staticmethod
    def aluno_completo_pdf(aluno, avaliacoes, treinos, base_url: str) -> bytes:
        html = render_template(
            "pdf/aluno_completo_pdf.html",
            aluno=aluno, avaliacoes=avaliacoes, treinos=treinos,
        )
        return PDFService._render_pdf(html, base_url)
