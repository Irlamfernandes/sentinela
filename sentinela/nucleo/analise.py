"""Junta as verificações, roda todas e resume o resultado."""

from __future__ import annotations

from dataclasses import dataclass

from sentinela.nucleo.ambiente import Ambiente
from sentinela.nucleo.modelos import Achado
from sentinela.verificacoes import chaves_ssh, firewall, ssh

# Ordem em que as verificações rodam e aparecem.
VERIFICACOES = (firewall, ssh, chaves_ssh)


@dataclass(frozen=True)
class Relatorio:
    achados: tuple[Achado, ...]

    @property
    def nota(self) -> int:
        """0 a 100: começa em 100 e cada problema desconta pela gravidade."""
        perdido = sum(a.gravidade.penalidade for a in self.achados)
        return max(0, 100 - perdido)

    @property
    def problemas(self) -> tuple[Achado, ...]:
        """Só os achados que pedem ação, do mais grave ao menos grave."""
        pendentes = [a for a in self.achados if a.gravidade.penalidade > 0]
        return tuple(sorted(pendentes, key=lambda a: a.gravidade.peso, reverse=True))


def executar(amb: Ambiente) -> Relatorio:
    achados: list[Achado] = []
    for verificacao in VERIFICACOES:
        achados.extend(verificacao.verificar(amb))
    return Relatorio(tuple(achados))
