"""Ambiente falso para testar as verificações sem tocar no sistema real."""

from __future__ import annotations

from dataclasses import dataclass, field

from sentinela.nucleo.ambiente import SaidaDeComando

AUSENTE = SaidaDeComando(encontrado=False, codigo=127, texto="")


@dataclass
class AmbienteFalso:
    """Devolve arquivos, permissões e saídas de comando combinados no teste."""

    arquivos: dict[str, str] = field(default_factory=dict)
    modos: dict[str, int] = field(default_factory=dict)
    conteudo_de_pastas: dict[str, list[str]] = field(default_factory=dict)
    comandos: dict[tuple[str, ...], SaidaDeComando] = field(default_factory=dict)
    eh_root: bool = False
    lar: str = "/home/teste"

    def ler(self, caminho: str) -> str | None:
        return self.arquivos.get(caminho)

    def modo(self, caminho: str) -> int | None:
        return self.modos.get(caminho)

    def listar(self, caminho: str) -> list[str]:
        return self.conteudo_de_pastas.get(caminho, [])

    def rodar(self, comando: list[str]) -> SaidaDeComando:
        return self.comandos.get(tuple(comando), AUSENTE)


def saida(texto: str, codigo: int = 0) -> SaidaDeComando:
    return SaidaDeComando(encontrado=True, codigo=codigo, texto=texto)
