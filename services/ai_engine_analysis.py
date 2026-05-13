"""
AI Analysis Engine — análise de arquivos enviados pelos usuários.

Realiza análise heurística inteligente de:
- ZIP de código (estrutura, segurança, performance, arquitetura)
- PDF (estrutura, tamanho, validação)
- Imagens (dimensões, peso, integridade)
- Documentos de texto/código (lint heurístico)

A "IA" aqui é um analisador local determinístico — não chama serviços externos.
Pode ser substituído por OpenAI/Anthropic/Gemini facilmente trocando _analyze_*.
"""
from __future__ import annotations

import json
import logging
import re
import zipfile
from datetime import datetime, UTC
from pathlib import Path

from models import db
from models.ai_analysis import AIAnalysis

logger = logging.getLogger("fitcontrol.ai")


class AIAnalysisEngine:

    # ---- Detecção de tipo ----
    @staticmethod
    def detect_type(filename: str, mime: str) -> str:
        ext = Path(filename).suffix.lower()
        if ext == ".zip":
            return "zip"
        if ext == ".pdf":
            return "pdf"
        if ext in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
            return "image"
        if ext in {".py", ".js", ".html", ".css", ".json", ".sql", ".yml", ".yaml", ".toml", ".ini", ".cfg"}:
            return "code"
        return "doc"

    # ---- Análise principal ----
    @classmethod
    def analyze(cls, analysis_id: int) -> None:
        """Processa uma análise pendente. Sincrono, simples e robusto."""
        analysis = db.session.get(AIAnalysis, analysis_id)
        if not analysis:
            return
        analysis.status = "processing"
        analysis.started_at = datetime.now(UTC)
        analysis.progresso = 5
        db.session.commit()

        try:
            tipo = analysis.tipo_arquivo
            file_path = Path(analysis.caminho)

            if not file_path.exists():
                raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

            analysis.progresso = 20
            db.session.commit()

            if tipo == "zip":
                result = cls._analyze_zip(file_path)
            elif tipo == "pdf":
                result = cls._analyze_pdf(file_path)
            elif tipo == "image":
                result = cls._analyze_image(file_path)
            elif tipo == "code":
                result = cls._analyze_code(file_path)
            else:
                result = cls._analyze_doc(file_path)

            analysis.progresso = 80
            db.session.commit()

            # Aplicar resultados
            analysis.resumo = result["resumo"]
            analysis.erros_detectados = "\n".join(result["erros"]) if result["erros"] else None
            analysis.sugestoes = "\n".join(result["sugestoes"]) if result["sugestoes"] else None
            analysis.relatorio_tecnico = result["relatorio"]
            analysis.codigo_corrigido = result.get("codigo_corrigido")
            analysis.metricas = json.dumps(result.get("metricas", {}), ensure_ascii=False)

            scores = result.get("scores", {})
            analysis.score_seguranca = scores.get("seguranca")
            analysis.score_performance = scores.get("performance")
            analysis.score_arquitetura = scores.get("arquitetura")
            analysis.score_responsividade = scores.get("responsividade")
            analysis.score_banco = scores.get("banco")

            analysis.progresso = 100
            analysis.status = "done"
            analysis.finished_at = datetime.now(UTC)
            db.session.commit()
            logger.info("AIAnalysis #%s concluída", analysis_id)

        except Exception as exc:  # noqa: BLE001
            logger.exception("AIAnalysis #%s falhou: %s", analysis_id, exc)
            analysis.status = "failed"
            analysis.erro_msg = str(exc)[:1000]
            analysis.finished_at = datetime.now(UTC)
            db.session.commit()

    # ============================================================
    # Analisadores específicos
    # ============================================================

    @staticmethod
    def _analyze_zip(path: Path) -> dict:
        erros: list[str] = []
        sugestoes: list[str] = []
        scores = {"seguranca": 80, "performance": 80, "arquitetura": 80,
                  "responsividade": 70, "banco": 80}
        metricas: dict = {"arquivos": 0, "linhas_python": 0, "linhas_html": 0,
                          "tem_dockerfile": False, "tem_requirements": False,
                          "tem_tests": False, "tem_migrations": False}
        sample_code = []

        try:
            with zipfile.ZipFile(path) as zf:
                names = zf.namelist()
                metricas["arquivos"] = len(names)
                for name in names:
                    low = name.lower()
                    if low.endswith("dockerfile") or low == "dockerfile":
                        metricas["tem_dockerfile"] = True
                    if low.endswith("requirements.txt"):
                        metricas["tem_requirements"] = True
                    if "/tests/" in low or "/test_" in low:
                        metricas["tem_tests"] = True
                    if "/migrations/" in low:
                        metricas["tem_migrations"] = True

                    if low.endswith(".py"):
                        try:
                            content = zf.read(name).decode("utf-8", errors="ignore")
                        except Exception:
                            continue
                        metricas["linhas_python"] += content.count("\n")
                        # Padrões de risco
                        if "eval(" in content or "exec(" in content:
                            erros.append(f"{name}: uso de eval/exec (risco de segurança)")
                            scores["seguranca"] -= 8
                        if "DEBUG = True" in content or "debug=True" in content:
                            erros.append(f"{name}: DEBUG habilitado")
                            scores["seguranca"] -= 5
                        if re.search(r"SECRET_KEY\s*=\s*['\"][^'\"]{0,15}['\"]", content):
                            erros.append(f"{name}: SECRET_KEY hardcoded curto")
                            scores["seguranca"] -= 10
                        if ".all()" in content and "limit(" not in content:
                            sugestoes.append(f"{name}: query .all() sem .limit() — risco de N+1 / OOM")
                            scores["performance"] -= 3
                        if "sqlite" in content.lower() and "production" in content.lower():
                            sugestoes.append(f"{name}: SQLite em produção — migre para PostgreSQL")
                            scores["banco"] -= 5
                        if len(sample_code) < 3 and content.strip():
                            sample_code.append((name, content[:400]))
                    elif low.endswith((".html", ".jinja")):
                        try:
                            content = zf.read(name).decode("utf-8", errors="ignore")
                        except Exception:
                            continue
                        metricas["linhas_html"] += content.count("\n")
                        if "viewport" not in content and "<head" in content.lower():
                            sugestoes.append(f"{name}: meta viewport ausente — quebra mobile")
                            scores["responsividade"] -= 4

            # Sugestões estruturais
            if not metricas["tem_dockerfile"]:
                sugestoes.append("Sem Dockerfile — adicione para deploy reprodutível")
                scores["arquitetura"] -= 8
            if not metricas["tem_requirements"]:
                erros.append("Sem requirements.txt — dependências não declaradas")
                scores["arquitetura"] -= 10
            if not metricas["tem_tests"]:
                sugestoes.append("Sem pasta de testes — adicione pytest")
                scores["arquitetura"] -= 5
            if not metricas["tem_migrations"]:
                sugestoes.append("Sem migrations — use Alembic/Flask-Migrate")
                scores["banco"] -= 5

        except zipfile.BadZipFile:
            erros.append("ZIP corrompido ou inválido")
            scores = {k: 0 for k in scores}

        # Normaliza scores
        scores = {k: max(0, min(100, v)) for k, v in scores.items()}

        resumo = (
            f"ZIP analisado: {metricas['arquivos']} arquivos, "
            f"{metricas['linhas_python']} linhas Python, "
            f"{metricas['linhas_html']} linhas HTML. "
            f"Erros: {len(erros)}, Sugestões: {len(sugestoes)}."
        )
        relatorio = AIAnalysisEngine._build_report(
            tipo="ZIP",
            metricas=metricas,
            erros=erros,
            sugestoes=sugestoes,
            scores=scores,
            extra=sample_code,
        )
        return {
            "resumo": resumo, "erros": erros, "sugestoes": sugestoes,
            "relatorio": relatorio, "metricas": metricas, "scores": scores,
        }

    @staticmethod
    def _analyze_pdf(path: Path) -> dict:
        size = path.stat().st_size
        with open(path, "rb") as f:
            header = f.read(8)
        valid = header.startswith(b"%PDF-")
        erros = [] if valid else ["PDF inválido (assinatura ausente)"]
        sugestoes = []
        if size > 5 * 1024 * 1024:
            sugestoes.append(f"PDF grande ({size//1024} KB) — considere otimizar")
        metricas = {"tamanho_bytes": size, "valido": valid,
                    "versao_pdf": header.decode("latin-1", errors="ignore")[:8]}
        scores = {"seguranca": 90, "performance": 90, "arquitetura": 100,
                  "responsividade": 100, "banco": 100}
        return {
            "resumo": f"PDF {'válido' if valid else 'inválido'} ({size//1024} KB)",
            "erros": erros, "sugestoes": sugestoes,
            "relatorio": AIAnalysisEngine._build_report("PDF", metricas, erros, sugestoes, scores),
            "metricas": metricas, "scores": scores,
        }

    @staticmethod
    def _analyze_image(path: Path) -> dict:
        size = path.stat().st_size
        metricas = {"tamanho_bytes": size}
        erros, sugestoes = [], []
        try:
            from PIL import Image
            with Image.open(path) as img:
                metricas["dimensoes"] = f"{img.width}x{img.height}"
                metricas["formato"] = img.format
                metricas["modo"] = img.mode
                if img.width * img.height > 16_000_000:
                    sugestoes.append("Imagem muito grande — considere redimensionar")
                if size > 4 * 1024 * 1024:
                    sugestoes.append("Arquivo de imagem >4MB — otimize para web")
        except Exception as exc:  # noqa: BLE001
            erros.append(f"Falha ao abrir imagem: {exc}")

        scores = {"seguranca": 95, "performance": 90 if size < 2*1024*1024 else 70,
                  "arquitetura": 100, "responsividade": 95, "banco": 100}
        return {
            "resumo": f"Imagem {metricas.get('formato','?')} {metricas.get('dimensoes','?')} ({size//1024} KB)",
            "erros": erros, "sugestoes": sugestoes,
            "relatorio": AIAnalysisEngine._build_report("Imagem", metricas, erros, sugestoes, scores),
            "metricas": metricas, "scores": scores,
        }

    @staticmethod
    def _analyze_code(path: Path) -> dict:
        text = path.read_text(encoding="utf-8", errors="ignore")
        erros, sugestoes = [], []
        scores = {"seguranca": 90, "performance": 90, "arquitetura": 85,
                  "responsividade": 90, "banco": 90}

        if "eval(" in text or "exec(" in text:
            erros.append("Uso de eval()/exec() — risco crítico de segurança")
            scores["seguranca"] -= 25
        if re.search(r"password\s*=\s*['\"][^'\"]+['\"]", text, re.I):
            erros.append("Senha hardcoded detectada")
            scores["seguranca"] -= 25
        if "TODO" in text or "FIXME" in text:
            sugestoes.append("Marcadores TODO/FIXME presentes")
        if "print(" in text and path.suffix == ".py":
            sugestoes.append("Vários `print()` — substitua por logging")
        if ".all()" in text:
            sugestoes.append("Query .all() — adicione paginação/limit em produção")

        metricas = {"linhas": text.count("\n"), "bytes": len(text)}
        codigo_corrigido = None
        if erros:
            codigo_corrigido = (
                "# Sugestão de correção automática:\n"
                "# 1. Remover eval()/exec() e usar parsing estruturado\n"
                "# 2. Mover senhas para variáveis de ambiente (os.getenv)\n"
                "# 3. Substituir print() por logging.getLogger(__name__)\n"
            )

        return {
            "resumo": f"Código analisado ({metricas['linhas']} linhas). "
                      f"{len(erros)} erros, {len(sugestoes)} sugestões.",
            "erros": erros, "sugestoes": sugestoes,
            "relatorio": AIAnalysisEngine._build_report("Código", metricas, erros, sugestoes, scores),
            "metricas": metricas, "scores": scores,
            "codigo_corrigido": codigo_corrigido,
        }

    @staticmethod
    def _analyze_doc(path: Path) -> dict:
        size = path.stat().st_size
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
            palavras = len(text.split())
        except Exception:
            text, palavras = "", 0
        metricas = {"tamanho_bytes": size, "palavras": palavras}
        scores = {"seguranca": 100, "performance": 100, "arquitetura": 100,
                  "responsividade": 100, "banco": 100}
        return {
            "resumo": f"Documento ({palavras} palavras, {size//1024} KB)",
            "erros": [], "sugestoes": [],
            "relatorio": AIAnalysisEngine._build_report("Documento", metricas, [], [], scores),
            "metricas": metricas, "scores": scores,
        }

    # ---- Relatório ----
    @staticmethod
    def _build_report(tipo, metricas, erros, sugestoes, scores, extra=None) -> str:
        lines = [
            f"# Relatório Técnico — {tipo}",
            f"_Gerado em {datetime.now(UTC).isoformat()}Z_",
            "",
            "## Scores",
        ]
        for k, v in scores.items():
            lines.append(f"- **{k.capitalize()}**: {v}/100")
        lines.append("")
        lines.append("## Métricas")
        for k, v in metricas.items():
            lines.append(f"- **{k}**: {v}")
        lines.append("")
        lines.append("## Erros detectados")
        if erros:
            for e in erros:
                lines.append(f"- ❌ {e}")
        else:
            lines.append("- ✅ Nenhum erro crítico encontrado")
        lines.append("")
        lines.append("## Sugestões")
        if sugestoes:
            for s in sugestoes:
                lines.append(f"- 💡 {s}")
        else:
            lines.append("- 👌 Sem sugestões adicionais")
        if extra:
            lines.append("")
            lines.append("## Amostras de código")
            for name, sample in extra:
                lines.append(f"### {name}")
                lines.append("```")
                lines.append(sample)
                lines.append("```")
        return "\n".join(lines)
