"""Treino business logic service."""
from datetime import datetime

from models.treino import Treino
from models.exercicio import Exercicio
from repositories.treino_repository import TreinoRepository
from repositories.exercicio_repository import ExercicioRepository
from services.ai_engine import AIEngine
from services.protocolo_service import ProtocoloService
from utils.security import sanitize_text


class TreinoService:
    @staticmethod
    def list_for_user(user_id: int, aluno_id: int | None = None, status: str | None = None) -> list[Treino]:
        return TreinoRepository.list_for_user(user_id, aluno_id, status)

    @staticmethod
    def get(treino_id: int, user_id: int) -> Treino | None:
        return TreinoRepository.get_for_user(treino_id, user_id)

    @staticmethod
    def create_manual(user_id: int, aluno_id: int, data: dict) -> Treino:
        treino = Treino(
            user_id=user_id,
            aluno_id=aluno_id,
            nome=sanitize_text(data.get("nome"), 160) or "Treino sem título",
            objetivo=data.get("objetivo") or "hipertrofia",
            modalidade=data.get("modalidade") or "musculacao",
            fase=data.get("fase") or "adaptacao",
            divisao=data.get("divisao") or "ABC",
            frequencia_semanal=int(data.get("frequencia_semanal") or 3),
            nivel=data.get("nivel") or "iniciante",
            protocolo_origem=data.get("protocolo_origem"),
            duracao_semanas=int(data.get("duracao_semanas") or 8),
            observacoes=sanitize_text(data.get("observacoes"), 5000),
            status=data.get("status") or "ativo",
        )
        return TreinoRepository.add(treino)

    @staticmethod
    def update(treino: Treino, data: dict) -> Treino:
        treino.nome = sanitize_text(data.get("nome"), 160) or treino.nome
        treino.objetivo = data.get("objetivo") or treino.objetivo
        treino.modalidade = data.get("modalidade") or treino.modalidade
        treino.fase = data.get("fase") or treino.fase
        treino.divisao = data.get("divisao") or treino.divisao
        treino.frequencia_semanal = int(data.get("frequencia_semanal") or treino.frequencia_semanal)
        treino.nivel = data.get("nivel") or treino.nivel
        treino.duracao_semanas = int(data.get("duracao_semanas") or treino.duracao_semanas)
        treino.observacoes = sanitize_text(data.get("observacoes"), 5000)
        treino.status = data.get("status") or treino.status
        treino.updated_at = datetime.utcnow()
        TreinoRepository.save()
        return treino

    @staticmethod
    def delete(treino: Treino) -> None:
        TreinoRepository.delete(treino)

    @staticmethod
    def gerar_via_ia(user_id: int, aluno, *, nome: str, objetivo: str, divisao: str,
                    frequencia: int, nivel: str, protocolo_chave: str | None = None,
                    duracao_semanas: int = 8, modalidade: str = "musculacao",
                    fase: str = "adaptacao") -> Treino:
        plano = AIEngine.gerar_treino(
            aluno=aluno, objetivo=objetivo, divisao=divisao,
            frequencia=frequencia, nivel=nivel,
            protocolo_chave=protocolo_chave, duracao_semanas=duracao_semanas,
        )
        protocolo = ProtocoloService.get(protocolo_chave) if protocolo_chave else None

        treino = Treino(
            user_id=user_id,
            aluno_id=aluno.id,
            nome=nome or f"Treino IA - {objetivo}",
            objetivo=objetivo,
            modalidade=modalidade,
            fase=fase,
            divisao=divisao,
            frequencia_semanal=frequencia,
            nivel=nivel,
            protocolo_origem=protocolo_chave,
            duracao_semanas=duracao_semanas,
            observacoes="Treino gerado pelo motor de IA do FitControl Pro.",
            alerta_medico=plano.get("alerta_medico"),
            status="ativo",
        )
        TreinoRepository.add(treino)

        for ex in plano["exercicios"]:
            exercicio = Exercicio(
                treino_id=treino.id,
                nome=ex["nome"],
                grupo_muscular=ex["grupo_muscular"],
                series=ex["series"],
                repeticoes=ex["repeticoes"],
                descanso=ex["descanso"],
                rpe=ex["rpe"],
                rir=ex["rir"],
                tempo_execucao=ex["tempo_execucao"],
                dia_semana=ex["dia_semana"],
                ordem=ex["ordem"],
                tecnica=ex.get("tecnica"),
                observacoes=ex.get("observacoes"),
            )
            ExercicioRepository.add(exercicio)
        return treino

    @staticmethod
    def add_exercicio(treino: Treino, data: dict) -> Exercicio:
        exercicio = Exercicio(
            treino_id=treino.id,
            nome=sanitize_text(data.get("nome"), 160) or "Exercício",
            grupo_muscular=data.get("grupo_muscular") or "geral",
            series=int(data.get("series") or 3),
            repeticoes=data.get("repeticoes") or "10-12",
            carga=sanitize_text(data.get("carga"), 40),
            descanso=data.get("descanso") or "60s",
            rpe=data.get("rpe"),
            rir=data.get("rir"),
            tempo_execucao=data.get("tempo_execucao"),
            observacoes=sanitize_text(data.get("observacoes"), 2000),
            dia_semana=data.get("dia_semana") or "A",
            ordem=int(data.get("ordem") or 1),
            tecnica=data.get("tecnica"),
        )
        return ExercicioRepository.add(exercicio)

    @staticmethod
    def update_exercicio(exercicio: Exercicio, data: dict) -> Exercicio:
        exercicio.nome = sanitize_text(data.get("nome"), 160) or exercicio.nome
        exercicio.grupo_muscular = data.get("grupo_muscular") or exercicio.grupo_muscular
        exercicio.series = int(data.get("series") or exercicio.series)
        exercicio.repeticoes = data.get("repeticoes") or exercicio.repeticoes
        exercicio.carga = sanitize_text(data.get("carga"), 40)
        exercicio.descanso = data.get("descanso") or exercicio.descanso
        exercicio.rpe = data.get("rpe")
        exercicio.rir = data.get("rir")
        exercicio.tempo_execucao = data.get("tempo_execucao")
        exercicio.observacoes = sanitize_text(data.get("observacoes"), 2000)
        exercicio.dia_semana = data.get("dia_semana") or exercicio.dia_semana
        exercicio.ordem = int(data.get("ordem") or exercicio.ordem)
        exercicio.tecnica = data.get("tecnica") or exercicio.tecnica
        ExercicioRepository.save()
        return exercicio

    @staticmethod
    def delete_exercicio(exercicio: Exercicio) -> None:
        ExercicioRepository.delete(exercicio)
