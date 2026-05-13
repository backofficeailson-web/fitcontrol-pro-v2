"""PDF rendering service with graceful Windows fallback."""
import logging
from flask import render_template

logger = logging.getLogger("fitcontrol.error")


class PDFService:
    @staticmethod
    def _render_pdf(html: str, base_url: str) -> bytes:
        try:
            from weasyprint import HTML
            return HTML(string=html, base_url=base_url).write_pdf()
        except Exception as exc:
            logger.error("WeasyPrint indisponível: %s", exc)

            fallback_html = f"""
            <!doctype html>
            <html lang="pt-br">
            <head>
                <meta charset="utf-8">
                <title>Relatório FitControl</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        padding: 32px;
                        color: #111;
                    }}
                    .warning {{
                        border: 1px solid #d97706;
                        background: #fff7ed;
                        padding: 16px;
                        margin-bottom: 24px;
                        border-radius: 8px;
                    }}
                </style>
            </head>
            <body>
                <div class="warning">
                    <strong>PDF indisponível neste Windows.</strong><br>
                    O relatório foi gerado em HTML temporariamente porque o WeasyPrint
                    não conseguiu carregar as bibliotecas nativas do sistema.
                </div>
                {html}
            </body>
            </html>
            """
            return fallback_html.encode("utf-8")

    @staticmethod
    def avaliacao_pdf(avaliacao, aluno, base_url: str) -> bytes:
        html = render_template(
            "pdf/avaliacao_pdf.html",
            avaliacao=avaliacao,
            aluno=aluno,
        )
        return PDFService._render_pdf(html, base_url)

    @staticmethod
    def treino_pdf(treino, aluno, base_url: str) -> bytes:
        html = render_template(
            "pdf/treino_pdf.html",
            treino=treino,
            aluno=aluno,
            exercicios_por_dia=treino.exercicios_por_dia(),
        )
        return PDFService._render_pdf(html, base_url)

    @staticmethod
    def aluno_completo_pdf(aluno, avaliacoes, treinos, base_url: str) -> bytes:
        html = render_template(
            "pdf/aluno_completo_pdf.html",
            aluno=aluno,
            avaliacoes=avaliacoes,
            treinos=treinos,
        )
        return PDFService._render_pdf(html, base_url)