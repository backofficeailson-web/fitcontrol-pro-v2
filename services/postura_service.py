"""Avaliação Postural - business logic service."""
from __future__ import annotations

from datetime import datetime, UTC, date

from models import db
from models.postura import AvaliacaoPostural
from utils.security import sanitize_text


class PosturaService:

    @staticmethod
    def list_for_aluno(aluno_id: int, user_id: int) -> list[AvaliacaoPostural]:
        return (
            db.session.query(AvaliacaoPostural)
            .filter(AvaliacaoPostural.aluno_id == aluno_id, AvaliacaoPostural.user_id == user_id)
            .order_by(AvaliacaoPostural.data.desc(), AvaliacaoPostural.id.desc())
            .all()
        )

    @staticmethod
    def list_for_user(user_id: int, limit: int | None = None) -> list[AvaliacaoPostural]:
        q = (
            db.session.query(AvaliacaoPostural)
            .filter(AvaliacaoPostural.user_id == user_id)
            .order_by(AvaliacaoPostural.created_at.desc())
        )
        if limit:
            q = q.limit(limit)
        return q.all()

    @staticmethod
    def get(post_id: int, user_id: int) -> AvaliacaoPostural | None:
        return (
            db.session.query(AvaliacaoPostural)
            .filter(AvaliacaoPostural.id == post_id, AvaliacaoPostural.user_id == user_id)
            .first()
        )

    @staticmethod
    def _parse_date(value):
        if not value:
            return datetime.now(UTC).date()
        if isinstance(value, date):
            return value
        try:
            return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return datetime.now(UTC).date()

    @staticmethod
    def create(user_id: int, aluno_id: int, data: dict, images: dict) -> AvaliacaoPostural:
        post = AvaliacaoPostural(
            user_id=user_id,
            aluno_id=aluno_id,
            data=PosturaService._parse_date(data.get("data")),
            cabeca=sanitize_text(data.get("cabeca"), 255),
            cervical=sanitize_text(data.get("cervical"), 255),
            ombros=sanitize_text(data.get("ombros"), 255),
            escapulas=sanitize_text(data.get("escapulas"), 255),
            coluna_toracica=sanitize_text(data.get("coluna_toracica"), 255),
            lombar=sanitize_text(data.get("lombar"), 255),
            quadril=sanitize_text(data.get("quadril"), 255),
            joelhos=sanitize_text(data.get("joelhos"), 255),
            pes=sanitize_text(data.get("pes"), 255),
            alinhamento_frontal=sanitize_text(data.get("alinhamento_frontal"), 5000),
            alinhamento_lateral=sanitize_text(data.get("alinhamento_lateral"), 5000),
            grau_desvio=sanitize_text(data.get("grau_desvio"), 40),
            dor_relatada=sanitize_text(data.get("dor_relatada"), 255),
            limitacao_funcional=sanitize_text(data.get("limitacao_funcional"), 255),
            observacoes_tecnicas=sanitize_text(data.get("observacoes_tecnicas"), 5000),
            observacoes_profissional=sanitize_text(data.get("observacoes_profissional"), 5000),
            img_frontal=images.get("frontal"),
            img_lateral_direita=images.get("lateral_direita"),
            img_lateral_esquerda=images.get("lateral_esquerda"),
            img_posterior=images.get("posterior"),
            avaliacao_anterior_id=data.get("avaliacao_anterior_id"),
        )
        db.session.add(post)
        db.session.commit()
        return post

    @staticmethod
    def update(post: AvaliacaoPostural, data: dict, images: dict) -> AvaliacaoPostural:
        for field in (
            "cabeca", "cervical", "ombros", "escapulas", "coluna_toracica",
            "lombar", "quadril", "joelhos", "pes", "grau_desvio",
            "dor_relatada", "limitacao_funcional",
        ):
            setattr(post, field, sanitize_text(data.get(field), 255))
        post.alinhamento_frontal = sanitize_text(data.get("alinhamento_frontal"), 5000)
        post.alinhamento_lateral = sanitize_text(data.get("alinhamento_lateral"), 5000)
        post.observacoes_tecnicas = sanitize_text(data.get("observacoes_tecnicas"), 5000)
        post.observacoes_profissional = sanitize_text(data.get("observacoes_profissional"), 5000)
        if data.get("data"):
            post.data = PosturaService._parse_date(data["data"])
        for key, attr in (
            ("frontal", "img_frontal"),
            ("lateral_direita", "img_lateral_direita"),
            ("lateral_esquerda", "img_lateral_esquerda"),
            ("posterior", "img_posterior"),
        ):
            if images.get(key):
                setattr(post, attr, images[key])
        post.updated_at = datetime.now(UTC)
        db.session.commit()
        return post

    @staticmethod
    def delete(post: AvaliacaoPostural) -> None:
        db.session.delete(post)
        db.session.commit()

    @staticmethod
    def comparar(post_atual: AvaliacaoPostural, post_anterior: AvaliacaoPostural) -> dict:
        """Compara duas avaliações posturais e retorna diferenças."""
        campos = [
            ("Cabeça", "cabeca"), ("Cervical", "cervical"), ("Ombros", "ombros"),
            ("Escápulas", "escapulas"), ("Coluna Torácica", "coluna_toracica"),
            ("Lombar", "lombar"), ("Quadril", "quadril"),
            ("Joelhos", "joelhos"), ("Pés", "pes"),
        ]
        diffs = []
        for label, attr in campos:
            ant = getattr(post_anterior, attr) or "—"
            atu = getattr(post_atual, attr) or "—"
            mudou = (ant or "").strip().lower() != (atu or "").strip().lower()
            diffs.append({"campo": label, "anterior": ant, "atual": atu, "mudou": mudou})
        return {
            "anterior": post_anterior,
            "atual": post_atual,
            "diferencas": diffs,
            "evolucao_desvio": (post_anterior.grau_desvio or "?") + " → " + (post_atual.grau_desvio or "?"),
        }
