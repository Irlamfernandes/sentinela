"""Tipos básicos do Sentinela: gravidade e achado de uma verificação."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Gravidade(Enum):
    """Quão sério é o que a verificação encontrou."""

    CRITICA = "critica"
    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"
    OK = "ok"
    INFO = "info"

    @property
    def rotulo(self) -> str:
        return _ROTULOS[self]

    @property
    def peso(self) -> int:
        """Ordem de exibição: mais grave primeiro."""
        return _PESOS[self]

    @property
    def penalidade(self) -> int:
        """Quanto tira da nota final (0 a 100)."""
        return _PENALIDADES[self]


_ROTULOS = {
    Gravidade.CRITICA: "Crítico",
    Gravidade.ALTA: "Alto",
    Gravidade.MEDIA: "Médio",
    Gravidade.BAIXA: "Baixo",
    Gravidade.OK: "Tudo certo",
    Gravidade.INFO: "Informação",
}

_PESOS = {
    Gravidade.CRITICA: 5,
    Gravidade.ALTA: 4,
    Gravidade.MEDIA: 3,
    Gravidade.BAIXA: 2,
    Gravidade.INFO: 1,
    Gravidade.OK: 0,
}

_PENALIDADES = {
    Gravidade.CRITICA: 40,
    Gravidade.ALTA: 20,
    Gravidade.MEDIA: 10,
    Gravidade.BAIXA: 4,
    Gravidade.INFO: 0,
    Gravidade.OK: 0,
}


@dataclass(frozen=True)
class Achado:
    """Uma conclusão de uma verificação, com o passo a passo para resolver."""

    titulo: str
    gravidade: Gravidade
    # O que foi encontrado no sistema.
    descricao: str
    # Por que isso importa (vazio quando está tudo certo).
    risco: str = ""
    # Passo a passo para corrigir, uma instrução por item.
    solucao: tuple[str, ...] = field(default_factory=tuple)
    # Link ou documento para quem quiser se aprofundar.
    referencia: str | None = None
