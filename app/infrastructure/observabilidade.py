"""Observabilidade: log estruturado e registro de auditoria.

O log sai em JSON (uma linha por evento), fácil de coletar e consultar. A
função `auditar` grava o evento na trilha de auditoria e emite o log, sem nunca
derrubar o fluxo principal se a gravação da auditoria falhar.
"""
from __future__ import annotations

import json
import logging
import sys
from typing import Any

_CONFIGURADO = False


class _FormatadorJson(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        dados: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "nivel": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        contexto = getattr(record, "contexto", None)
        if isinstance(contexto, dict):
            dados.update(contexto)
        return json.dumps(dados, ensure_ascii=False)


def configurar_logs(nivel: int = logging.INFO) -> None:
    """Configura o log estruturado (idempotente)."""
    global _CONFIGURADO
    if _CONFIGURADO:
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_FormatadorJson())
    raiz = logging.getLogger()
    raiz.handlers = [handler]
    raiz.setLevel(nivel)
    _CONFIGURADO = True


def obter_logger(nome: str) -> logging.Logger:
    return logging.getLogger(nome)


def auditar(
    repo_auditoria,
    *,
    ator: str,
    evento: str,
    entidade_id: Any = None,
    detalhe: str | None = None,
) -> None:
    """Grava o evento na trilha de auditoria e emite o log estruturado.

    A auditoria é best-effort: se a gravação falhar, o log registra o problema,
    mas a operação de negócio não é interrompida.
    """
    logger = obter_logger("auditoria")
    id_str = str(entidade_id) if entidade_id is not None else None
    try:
        repo_auditoria.registrar(
            ator=ator, evento=evento, entidade_id=entidade_id, detalhe=detalhe
        )
    except Exception:  # nosec B110 - auditoria nunca derruba o fluxo principal
        logger.warning(
            "falha ao registrar auditoria",
            extra={"contexto": {"evento": evento, "ator": ator}},
        )
    logger.info(
        evento,
        extra={"contexto": {"evento": evento, "ator": ator, "entidade_id": id_str}},
    )
