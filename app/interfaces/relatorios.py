"""Rotas de relatórios/métricas da gestão administrativa."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.application.casos_uso import CalcularTempoMedioExecucao
from app.domain.repositorios import OrdemServicoRepositorio
from app.interfaces.auth import requer_admin
from app.interfaces.dependencias import obter_repositorio
from app.interfaces.schemas import TempoMedioOut

router = APIRouter(
    prefix="/relatorios", tags=["relatórios"], dependencies=[Depends(requer_admin)]
)


def _formatar(segundos: float) -> str:
    total = int(segundos)
    horas, resto = divmod(total, 3600)
    minutos, segs = divmod(resto, 60)
    return f"{horas:02d}:{minutos:02d}:{segs:02d}"


@router.get(
    "/tempo-medio-execucao", response_model=TempoMedioOut,
    summary="Tempo médio de execução dos serviços",
)
def tempo_medio_execucao(repo: OrdemServicoRepositorio = Depends(obter_repositorio)):
    resultado = CalcularTempoMedioExecucao(repo).executar()
    return TempoMedioOut(
        amostras=int(resultado["amostras"]),
        tempo_medio_segundos=float(resultado["tempo_medio_segundos"]),
        tempo_medio_formatado=_formatar(float(resultado["tempo_medio_segundos"])),
    )
