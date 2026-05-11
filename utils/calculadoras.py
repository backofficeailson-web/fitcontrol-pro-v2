"""Anthropometric and metabolic calculators.

Implements: IMC, classification, RCQ, TMB (Mifflin-St Jeor),
Pollock 3 dobras, Pollock 7 dobras (Jackson/Pollock equation),
massa magra and massa gorda derivations.
"""
from __future__ import annotations

import math
from typing import Optional


def calcular_imc(peso_kg: Optional[float], altura_m: Optional[float]) -> Optional[float]:
    if not peso_kg or not altura_m or altura_m <= 0:
        return None
    return round(peso_kg / (altura_m * altura_m), 2)


def classificar_imc(imc: Optional[float]) -> Optional[str]:
    if imc is None:
        return None
    if imc < 18.5:
        return "Abaixo do peso"
    if imc < 25:
        return "Peso normal"
    if imc < 30:
        return "Sobrepeso"
    if imc < 35:
        return "Obesidade Grau I"
    if imc < 40:
        return "Obesidade Grau II"
    return "Obesidade Grau III"


def calcular_rcq(cintura_cm: Optional[float], quadril_cm: Optional[float]) -> Optional[float]:
    if not cintura_cm or not quadril_cm or quadril_cm <= 0:
        return None
    return round(cintura_cm / quadril_cm, 2)


def calcular_tmb(
    sexo: Optional[str],
    peso_kg: Optional[float],
    altura_cm: Optional[float],
    idade: Optional[int],
) -> Optional[float]:
    """Mifflin-St Jeor equation."""
    if not (sexo and peso_kg and altura_cm and idade):
        return None
    base = (10 * peso_kg) + (6.25 * altura_cm) - (5 * idade)
    if sexo.lower().startswith("m"):
        return round(base + 5, 2)
    return round(base - 161, 2)


def _densidade_corporal_pollock3(
    sexo: str, idade: int, soma_dobras: float
) -> float:
    if sexo.lower().startswith("m"):
        return (
            1.10938
            - 0.0008267 * soma_dobras
            + 0.0000016 * (soma_dobras ** 2)
            - 0.0002574 * idade
        )
    return (
        1.0994921
        - 0.0009929 * soma_dobras
        + 0.0000023 * (soma_dobras ** 2)
        - 0.0001392 * idade
    )


def _densidade_corporal_pollock7(
    sexo: str, idade: int, soma_dobras: float
) -> float:
    if sexo.lower().startswith("m"):
        return (
            1.112
            - 0.00043499 * soma_dobras
            + 0.00000055 * (soma_dobras ** 2)
            - 0.00028826 * idade
        )
    return (
        1.097
        - 0.00046971 * soma_dobras
        + 0.00000056 * (soma_dobras ** 2)
        - 0.00012828 * idade
    )


def _siri(densidade: float) -> float:
    if densidade <= 0:
        return 0.0
    return ((4.95 / densidade) - 4.5) * 100


def calcular_percentual_gordura_pollock3(
    sexo: Optional[str],
    idade: Optional[int],
    *,
    triceps: Optional[float] = None,
    suprailiaca: Optional[float] = None,
    coxa: Optional[float] = None,
    peitoral: Optional[float] = None,
    abdominal: Optional[float] = None,
) -> Optional[float]:
    """Pollock 3 dobras.

    Homens (peitoral, abdominal, coxa).
    Mulheres (tríceps, suprailíaca, coxa).
    """
    if not sexo or not idade:
        return None
    if sexo.lower().startswith("m"):
        valores = [peitoral, abdominal, coxa]
    else:
        valores = [triceps, suprailiaca, coxa]
    if any(v is None or v <= 0 for v in valores):
        return None
    soma = float(sum(valores))
    densidade = _densidade_corporal_pollock3(sexo, idade, soma)
    return round(_siri(densidade), 2)


def calcular_percentual_gordura_pollock7(
    sexo: Optional[str],
    idade: Optional[int],
    *,
    triceps: Optional[float] = None,
    peitoral: Optional[float] = None,
    subaxilar: Optional[float] = None,
    subescapular: Optional[float] = None,
    abdominal: Optional[float] = None,
    suprailiaca: Optional[float] = None,
    coxa: Optional[float] = None,
) -> Optional[float]:
    if not sexo or not idade:
        return None
    valores = [triceps, peitoral, subaxilar, subescapular, abdominal, suprailiaca, coxa]
    if any(v is None or v <= 0 for v in valores):
        return None
    soma = float(sum(valores))
    densidade = _densidade_corporal_pollock7(sexo, idade, soma)
    return round(_siri(densidade), 2)


def calcular_massa_magra(peso_kg: Optional[float], percentual_gordura: Optional[float]) -> Optional[float]:
    if peso_kg is None or percentual_gordura is None:
        return None
    return round(peso_kg * (1 - percentual_gordura / 100), 2)


def calcular_massa_gorda(peso_kg: Optional[float], percentual_gordura: Optional[float]) -> Optional[float]:
    if peso_kg is None or percentual_gordura is None:
        return None
    return round(peso_kg * (percentual_gordura / 100), 2)


def somatotipo_basico(
    peso_kg: Optional[float],
    altura_cm: Optional[float],
    cintura_cm: Optional[float],
) -> Optional[str]:
    if not (peso_kg and altura_cm and cintura_cm):
        return None
    indice = (peso_kg / ((altura_cm / 100) ** 2)) + (cintura_cm / altura_cm) * 10
    if indice < 22:
        return "Ectomorfo"
    if indice < 27:
        return "Mesomorfo"
    return "Endomorfo"


def evolucao_percentual(antigo: Optional[float], novo: Optional[float]) -> Optional[float]:
    if antigo is None or novo is None or antigo == 0:
        return None
    return round(((novo - antigo) / antigo) * 100, 2)
