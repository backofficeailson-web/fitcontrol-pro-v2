"""Protocol catalog service - structured definitions for evaluation and training protocols."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProtocoloDef:
    chave: str
    nome: str
    categoria: str
    descricao: str
    tipo: str
    parametros: dict = field(default_factory=dict)
    alerta_medico: Optional[str] = None
    requer_individualizacao: bool = False
    nivel_recomendado: str = "todos"

    def to_dict(self) -> dict:
        return {
            "chave": self.chave,
            "nome": self.nome,
            "categoria": self.categoria,
            "descricao": self.descricao,
            "tipo": self.tipo,
            "parametros": self.parametros,
            "alerta_medico": self.alerta_medico,
            "requer_individualizacao": self.requer_individualizacao,
            "nivel_recomendado": self.nivel_recomendado,
        }


PROTOCOLOS_AVALIACAO: list[ProtocoloDef] = [
    ProtocoloDef("imc", "IMC - Índice de Massa Corporal", "avaliacao",
                 "Cálculo simples de relação peso/altura para classificação OMS.", "antropometrico"),
    ProtocoloDef("rcq", "RCQ - Relação Cintura/Quadril", "avaliacao",
                 "Avalia distribuição de gordura abdominal e risco cardiovascular.", "antropometrico"),
    ProtocoloDef("circunferencias", "Perimetria Completa", "avaliacao",
                 "Medição de cintura, quadril, peito, braço, coxa e panturrilha.", "antropometrico"),
    ProtocoloDef("pollock_3", "Pollock 3 dobras (Jackson/Pollock)", "avaliacao",
                 "Estima percentual de gordura via 3 dobras cutâneas.", "dobras",
                 parametros={"dobras_homem": ["peitoral", "abdominal", "coxa"],
                             "dobras_mulher": ["triceps", "suprailiaca", "coxa"]}),
    ProtocoloDef("pollock_7", "Pollock 7 dobras (Jackson/Pollock)", "avaliacao",
                 "Estima percentual de gordura via 7 dobras com maior precisão.", "dobras",
                 parametros={"dobras": ["triceps", "peitoral", "subaxilar", "subescapular",
                                        "abdominal", "suprailiaca", "coxa"]}),
    ProtocoloDef("postural", "Avaliação Postural", "avaliacao",
                 "Análise visual de desvios posturais nos planos sagital e frontal.", "qualitativo"),
    ProtocoloDef("anamnese", "Anamnese Clínica", "avaliacao",
                 "Coleta histórico de saúde, lesões, medicamentos e estilo de vida.", "qualitativo"),
]


PROTOCOLOS_TREINO: list[ProtocoloDef] = [
    ProtocoloDef("hipertrofia_iniciante", "Hipertrofia Iniciante", "treino",
                 "Estímulo muscular progressivo com volume moderado e foco técnico.",
                 "hipertrofia", parametros={"divisao": "ABC", "frequencia": 3, "rir": 3,
                                            "series": (3, 4), "reps": (10, 12)},
                 nivel_recomendado="iniciante"),
    ProtocoloDef("hipertrofia_avancada", "Hipertrofia Avançada", "treino",
                 "Periodização com volume alto, técnicas avançadas e splits especializados.",
                 "hipertrofia", parametros={"divisao": "ABCDE", "frequencia": 5, "rir": 1,
                                            "series": (4, 6), "reps": (8, 12)},
                 nivel_recomendado="avancado"),
    ProtocoloDef("emagrecimento", "Emagrecimento", "treino",
                 "Combinação de força e metabólico para maximização do gasto calórico.",
                 "emagrecimento", parametros={"divisao": "Full Body", "frequencia": 4,
                                              "series": (3, 4), "reps": (12, 20),
                                              "descanso": "30-45s"}),
    ProtocoloDef("condicionamento", "Condicionamento Geral", "treino",
                 "Foco em capacidade cardiorrespiratória e funcional.",
                 "condicionamento", parametros={"divisao": "Full Body", "frequencia": 3,
                                                "series": (3, 3), "reps": (12, 15)}),
    ProtocoloDef("forca", "Força Máxima", "treino",
                 "Cargas elevadas, baixo volume, foco em recrutamento neural.",
                 "forca", parametros={"divisao": "Upper/Lower", "frequencia": 4,
                                      "series": (4, 6), "reps": (3, 6), "descanso": "120-180s"},
                 nivel_recomendado="intermediario"),
    ProtocoloDef("periodizacao", "Periodização Linear", "treino",
                 "Progressão de volume → intensidade ao longo de mesociclos.",
                 "periodizacao", parametros={"mesociclos": 3, "duracao_semanas": 12}),
    ProtocoloDef("full_body", "Full Body", "treino",
                 "Treina o corpo inteiro em cada sessão, ideal para baixa frequência.",
                 "estrutura", parametros={"divisao": "Full Body", "frequencia": 3}),
    ProtocoloDef("abc", "Divisão ABC", "treino",
                 "3 sessões: peito/tríceps, costas/bíceps, pernas/ombros.",
                 "estrutura", parametros={"divisao": "ABC", "frequencia": 3}),
    ProtocoloDef("abcde", "Divisão ABCDE", "treino",
                 "5 sessões com grupamentos isolados para alto volume.",
                 "estrutura", parametros={"divisao": "ABCDE", "frequencia": 5}),
    ProtocoloDef("upper_lower", "Upper / Lower", "treino",
                 "Alternância entre membros superiores e inferiores.",
                 "estrutura", parametros={"divisao": "Upper/Lower", "frequencia": 4}),
    ProtocoloDef("adaptacao_neural", "Adaptação Neural", "treino",
                 "Fase inicial focada em técnica, mobilidade e padrões motores.",
                 "fase", parametros={"duracao_semanas": 4, "rir": 4, "reps": (12, 15)},
                 nivel_recomendado="iniciante"),
    ProtocoloDef("resistencia_muscular", "Resistência Muscular Localizada", "treino",
                 "Reps altas, descansos curtos, ênfase em capacidade local.",
                 "resistencia", parametros={"reps": (15, 25), "descanso": "30s"}),
    ProtocoloDef("powerlifting", "Powerlifting", "treino",
                 "Foco em agachamento, supino e levantamento terra.",
                 "esporte", parametros={"divisao": "Upper/Lower", "frequencia": 4,
                                        "reps": (1, 5), "descanso": "180-300s"},
                 nivel_recomendado="intermediario"),
    ProtocoloDef("bodybuilder", "Bodybuilder Clássico", "treino",
                 "Volume elevado, isoladores, foco estético.",
                 "esporte", parametros={"divisao": "ABCDE", "frequencia": 5,
                                        "series": (4, 5), "reps": (8, 15)},
                 nivel_recomendado="intermediario"),
    ProtocoloDef("gestantes", "Treino para Gestantes", "treino",
                 "Foco em mobilidade, estabilidade pélvica e respiração. Sem decúbito dorsal após 1º trimestre.",
                 "especial",
                 parametros={"intensidade_max_rpe": 6, "frequencia": 3,
                             "evitar": ["abdominal_decubito", "saltos", "valsalva"]},
                 alerta_medico=("Treino exige liberação obstétrica e acompanhamento clínico. "
                                "Evite Valsalva, decúbito dorsal prolongado e impacto."),
                 requer_individualizacao=True),
    ProtocoloDef("beach_tenis", "Beach Tênis", "treino",
                 "Potência, deslocamento lateral, ombro saudável.",
                 "esporte", parametros={"frequencia": 3,
                                        "ênfase": ["pliometria", "ombro", "core"]}),
    ProtocoloDef("futebol", "Futebol", "treino",
                 "Resistência intermitente, força de membros inferiores e core.",
                 "esporte", parametros={"frequencia": 4,
                                        "ênfase": ["sprint", "agilidade", "posterior"]}),
    ProtocoloDef("lipedema", "Treino para Lipedema", "treino",
                 "Baixo impacto, foco em circulação e mobilidade. Evitar HIIT intenso.",
                 "especial",
                 parametros={"intensidade_max_rpe": 6,
                             "evitar": ["alto_impacto", "isometria_prolongada"]},
                 alerta_medico=("Lipedema requer acompanhamento médico/angiológico. "
                                "Priorize movimentos de baixo impacto e drenagem."),
                 requer_individualizacao=True),
    ProtocoloDef("diabetes", "Treino para Diabéticos", "treino",
                 "Combinação aeróbio + força. Monitorar glicemia antes/depois.",
                 "especial",
                 parametros={"intensidade_max_rpe": 7, "frequencia": 4,
                             "evitar": ["jejum_prolongado_sessao_longa"]},
                 alerta_medico=("Verifique glicemia pré e pós treino. Tenha carboidrato rápido disponível. "
                                "Sem treino se glicemia <70 ou >250 com cetose."),
                 requer_individualizacao=True),
    ProtocoloDef("cardiacos", "Treino para Cardiopatas", "treino",
                 "Aeróbio leve a moderado controlado. Evitar Valsalva.",
                 "especial",
                 parametros={"intensidade_max_rpe": 5,
                             "evitar": ["valsalva", "isometria_pesada", "alto_impacto"]},
                 alerta_medico=("Treino só com liberação cardiológica e teste ergométrico recente. "
                                "Mantenha FC dentro da zona prescrita pelo médico."),
                 requer_individualizacao=True),
]


_INDEX = {p.chave: p for p in (PROTOCOLOS_AVALIACAO + PROTOCOLOS_TREINO)}


class ProtocoloService:
    @staticmethod
    def list_avaliacao() -> list[ProtocoloDef]:
        return list(PROTOCOLOS_AVALIACAO)

    @staticmethod
    def list_treino() -> list[ProtocoloDef]:
        return list(PROTOCOLOS_TREINO)

    @staticmethod
    def list_all() -> list[ProtocoloDef]:
        return list(PROTOCOLOS_AVALIACAO) + list(PROTOCOLOS_TREINO)

    @staticmethod
    def get(chave: str) -> Optional[ProtocoloDef]:
        return _INDEX.get(chave)

    @staticmethod
    def is_especial(chave: str) -> bool:
        proto = _INDEX.get(chave)
        return bool(proto and proto.requer_individualizacao)
