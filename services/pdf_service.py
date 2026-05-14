"""PDF rendering service with WeasyPrint and pure-Python fallback."""
import logging
import re
from io import BytesIO
from html import unescape

from flask import render_template

logger = logging.getLogger("fitcontrol.error")


def _html_to_text(html: str) -> str:
    text = re.sub(r"<style.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<script.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</p>|</div>|</tr>|</h1>|</h2>|</h3>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


def _escape_pdf_text(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
    )


def _simple_pdf_from_text(text: str) -> bytes:
    lines = []
    for raw_line in text.splitlines():
        raw_line = raw_line.strip()
        if not raw_line:
            lines.append("")
            continue

        while len(raw_line) > 90:
            lines.append(raw_line[:90])
            raw_line = raw_line[90:]

        lines.append(raw_line)

    if not lines:
        lines = ["Relatório FitControl"]

    pages = []
    current = []

    for line in lines:
        current.append(line)
        if len(current) >= 42:
            pages.append(current)
            current = []

    if current:
        pages.append(current)

    objects = []
    pages_refs = []

    def add_object(content: str) -> int:
        objects.append(content)
        return len(objects)

    font_id = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    for page_lines in pages:
        stream_lines = ["BT", "/F1 10 Tf", "50 790 Td", "14 TL"]

        for line in page_lines:
            safe = _escape_pdf_text(line)
            stream_lines.append(f"({safe}) Tj")
            stream_lines.append("T*")

        stream_lines.append("ET")
        stream = "\n".join(stream_lines)

        content_id = add_object(
            f"<< /Length {len(stream.encode('latin-1', errors='replace'))} >>\n"
            f"stream\n{stream}\nendstream"
        )

        page_id = add_object(
            "<< /Type /Page /Parent 0 0 R "
            "/MediaBox [0 0 595 842] "
            f"/Resources << /Font << /F1 {font_id} 0 R >> >> "
            f"/Contents {content_id} 0 R >>"
        )

        pages_refs.append(page_id)

    kids = " ".join(f"{page_id} 0 R" for page_id in pages_refs)
    pages_id = add_object(
        f"<< /Type /Pages /Kids [{kids}] /Count {len(pages_refs)} >>"
    )

    catalog_id = add_object(f"<< /Type /Catalog /Pages {pages_id} 0 R >>")

    fixed_objects = []
    for obj in objects:
        fixed_objects.append(obj.replace("/Parent 0 0 R", f"/Parent {pages_id} 0 R"))

    pdf = BytesIO()
    pdf.write(b"%PDF-1.4\n")

    offsets = [0]

    for index, obj in enumerate(fixed_objects, start=1):
        offsets.append(pdf.tell())
        pdf.write(f"{index} 0 obj\n".encode("latin-1"))
        pdf.write(obj.encode("latin-1", errors="replace"))
        pdf.write(b"\nendobj\n")

    xref_start = pdf.tell()
    pdf.write(f"xref\n0 {len(fixed_objects) + 1}\n".encode("latin-1"))
    pdf.write(b"0000000000 65535 f \n")

    for offset in offsets[1:]:
        pdf.write(f"{offset:010d} 00000 n \n".encode("latin-1"))

    pdf.write(
        (
            "trailer\n"
            f"<< /Size {len(fixed_objects) + 1} /Root {catalog_id} 0 R >>\n"
            "startxref\n"
            f"{xref_start}\n"
            "%%EOF"
        ).encode("latin-1")
    )

    return pdf.getvalue()


class PDFService:
    @staticmethod
    def _render_pdf(html: str, base_url: str) -> bytes:
        try:
            from weasyprint import HTML
            return HTML(string=html, base_url=base_url).write_pdf()
        except Exception as exc:
            logger.error("WeasyPrint indisponível. Usando fallback PDF simples: %s", exc)
            text = _html_to_text(html)
            return _simple_pdf_from_text(text)

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