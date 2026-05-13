"""Calculator unit tests."""
from utils.calculadoras import (
    calcular_imc, classificar_imc, calcular_rcq, calcular_tmb,
    calcular_percentual_gordura_pollock3, calcular_percentual_gordura_pollock7,
    calcular_massa_magra, calcular_massa_gorda,
)


def test_imc_basic():
    assert calcular_imc(70, 1.75) == round(70 / (1.75 ** 2), 2)


def test_imc_invalid():
    assert calcular_imc(None, 1.75) is None
    assert calcular_imc(70, 0) is None


def test_classificar_imc():
    assert classificar_imc(17) == "Abaixo do peso"
    assert classificar_imc(22) == "Peso normal"
    assert classificar_imc(27) == "Sobrepeso"
    assert classificar_imc(32) == "Obesidade Grau I"
    assert classificar_imc(37) == "Obesidade Grau II"
    assert classificar_imc(45) == "Obesidade Grau III"


def test_rcq():
    assert calcular_rcq(80, 100) == 0.8
    assert calcular_rcq(None, 100) is None


def test_tmb_male():
    val = calcular_tmb("masculino", 80, 180, 30)
    assert val is not None and val > 0


def test_tmb_female():
    val = calcular_tmb("feminino", 60, 165, 28)
    assert val is not None and val > 0


def test_pollock3_male():
    val = calcular_percentual_gordura_pollock3(
        "masculino", 30, peitoral=10, abdominal=15, coxa=12,
    )
    assert val is not None and 0 < val < 60


def test_pollock7_returns_none_when_missing():
    assert calcular_percentual_gordura_pollock7("masculino", 30) is None


def test_massa_magra_e_gorda():
    assert calcular_massa_magra(80, 20) == 64.0
    assert calcular_massa_gorda(80, 20) == 16.0
