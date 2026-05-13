"""Avaliacao business logic service - applies anthropometric calculations."""
from datetime import datetime, UTC

from models.avaliacao import Avaliacao
from repositories.avaliacao_repository import AvaliacaoRepository
from utils.calculadoras import (
    calcular_imc,
    classificar_imc,
    calcular_massa_gorda,
    calcular_massa_magra,
    calcular_percentual_gordura_pollock3,
    calcular_percentual_gordura_pollock7,
    calcular_rcq,
    calcular_tmb,
)
from utils.security import sanitize_text


class AvaliacaoService:
    @staticmethod
    def list_for_user(user_id: int, aluno_id: int | None = None) -> list[Avaliacao]:
        return AvaliacaoRepository.list_for_user(user_id, aluno_id)

    @staticmethod
    def get(avaliacao_id: int, user_id: int) -> Avaliacao | None:
        return AvaliacaoRepository.get_for_user(avaliacao_id, user_id)

    @staticmethod
    def history(aluno_id: int, user_id: int) -> list[Avaliacao]:
        return AvaliacaoRepository.history_for_aluno(aluno_id, user_id)

    @staticmethod
    def _enrich_calculations(av: Avaliacao, idade: int | None, sexo: str | None) -> None:
        altura_m = (av.altura or 0) / 100 if av.altura and av.altura > 3 else av.altura
        av.imc = calcular_imc(av.peso, altura_m)
        av.classificacao_imc = classificar_imc(av.imc)
        av.rcq = calcular_rcq(av.cintura, av.quadril)
        altura_cm = av.altura if av.altura and av.altura > 3 else (av.altura or 0) * 100
        av.tmb = calcular_tmb(sexo, av.peso, altura_cm or None, idade)

        if av.protocolo == "pollock_7":
            av.percentual_gordura = calcular_percentual_gordura_pollock7(
                sexo, idade,
                triceps=av.dobra_triceps,
                peitoral=av.dobra_peitoral,
                subaxilar=av.dobra_subaxilar,
                subescapular=av.dobra_subescapular,
                abdominal=av.dobra_abdominal,
                suprailiaca=av.dobra_suprailiaca,
                coxa=av.dobra_coxa,
            )
        else:
            av.percentual_gordura = calcular_percentual_gordura_pollock3(
                sexo, idade,
                triceps=av.dobra_triceps,
                suprailiaca=av.dobra_suprailiaca,
                coxa=av.dobra_coxa,
                peitoral=av.dobra_peitoral,
                abdominal=av.dobra_abdominal,
            )
        av.massa_magra = calcular_massa_magra(av.peso, av.percentual_gordura)
        av.massa_gorda = calcular_massa_gorda(av.peso, av.percentual_gordura)

    @staticmethod
    def create(user_id: int, aluno, data: dict) -> Avaliacao:
        av = Avaliacao(
            user_id=user_id,
            aluno_id=aluno.id,
            data=data.get("data") or datetime.now(UTC).date(),
            protocolo=data.get("protocolo") or "pollock_3",
            peso=data.get("peso"),
            altura=data.get("altura") or aluno.altura,
            cintura=data.get("cintura"),
            quadril=data.get("quadril"),
            peito=data.get("peito"),
            braco=data.get("braco"),
            coxa=data.get("coxa"),
            panturrilha=data.get("panturrilha"),
            abdomen=data.get("abdomen"),
            dobra_triceps=data.get("dobra_triceps"),
            dobra_peitoral=data.get("dobra_peitoral"),
            dobra_subaxilar=data.get("dobra_subaxilar"),
            dobra_subescapular=data.get("dobra_subescapular"),
            dobra_abdominal=data.get("dobra_abdominal"),
            dobra_suprailiaca=data.get("dobra_suprailiaca"),
            dobra_coxa=data.get("dobra_coxa"),
            observacoes=sanitize_text(data.get("observacoes"), 5000),
        )
        AvaliacaoService._enrich_calculations(av, aluno.idade, aluno.sexo)
        return AvaliacaoRepository.add(av)

    @staticmethod
    def update(avaliacao: Avaliacao, aluno, data: dict) -> Avaliacao:
        avaliacao.data = data.get("data") or avaliacao.data
        avaliacao.protocolo = data.get("protocolo") or avaliacao.protocolo
        avaliacao.peso = data.get("peso", avaliacao.peso)
        avaliacao.altura = data.get("altura", avaliacao.altura)
        avaliacao.cintura = data.get("cintura", avaliacao.cintura)
        avaliacao.quadril = data.get("quadril", avaliacao.quadril)
        avaliacao.peito = data.get("peito", avaliacao.peito)
        avaliacao.braco = data.get("braco", avaliacao.braco)
        avaliacao.coxa = data.get("coxa", avaliacao.coxa)
        avaliacao.panturrilha = data.get("panturrilha", avaliacao.panturrilha)
        avaliacao.abdomen = data.get("abdomen", avaliacao.abdomen)
        avaliacao.dobra_triceps = data.get("dobra_triceps", avaliacao.dobra_triceps)
        avaliacao.dobra_peitoral = data.get("dobra_peitoral", avaliacao.dobra_peitoral)
        avaliacao.dobra_subaxilar = data.get("dobra_subaxilar", avaliacao.dobra_subaxilar)
        avaliacao.dobra_subescapular = data.get("dobra_subescapular", avaliacao.dobra_subescapular)
        avaliacao.dobra_abdominal = data.get("dobra_abdominal", avaliacao.dobra_abdominal)
        avaliacao.dobra_suprailiaca = data.get("dobra_suprailiaca", avaliacao.dobra_suprailiaca)
        avaliacao.dobra_coxa = data.get("dobra_coxa", avaliacao.dobra_coxa)
        avaliacao.observacoes = sanitize_text(data.get("observacoes"), 5000)
        AvaliacaoService._enrich_calculations(avaliacao, aluno.idade, aluno.sexo)
        AvaliacaoRepository.save()
        return avaliacao

    @staticmethod
    def delete(avaliacao: Avaliacao) -> None:
        AvaliacaoRepository.delete(avaliacao)

    @staticmethod
    def comparativo(aluno_id: int, user_id: int) -> dict:
        history = AvaliacaoRepository.history_for_aluno(aluno_id, user_id)
        if not history:
            return {"primeira": None, "ultima": None, "delta": {}}
        primeira, ultima = history[0], history[-1]

        def delta(a, b):
            if a is None or b is None:
                return None
            return round(b - a, 2)

        return {
            "primeira": primeira,
            "ultima": ultima,
            "delta": {
                "peso": delta(primeira.peso, ultima.peso),
                "imc": delta(primeira.imc, ultima.imc),
                "percentual_gordura": delta(primeira.percentual_gordura, ultima.percentual_gordura),
                "massa_magra": delta(primeira.massa_magra, ultima.massa_magra),
                "cintura": delta(primeira.cintura, ultima.cintura),
                "quadril": delta(primeira.quadril, ultima.quadril),
            },
            "history": history,
        }
