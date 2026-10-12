"""Portas em escuta, com destaque para as abertas para fora da máquina."""

from __future__ import annotations

from dataclasses import dataclass

from sentinela.nucleo.ambiente import Ambiente
from sentinela.nucleo.modelos import Achado, Gravidade

ID = "portas"
NOME = "Portas abertas"
CATEGORIA = "Rede"

# Endereços locais: quem escuta aí não está exposto na rede.
_LOCAIS = ("127.", "::1", "[::1]")


@dataclass(frozen=True)
class Porta:
    endereco: str
    porta: str
    programa: str


def verificar(amb: Ambiente) -> list[Achado]:
    saida = amb.rodar(["ss", "-tulpnH"])
    if not saida.encontrado:
        return [
            Achado(
                "Não foi possível listar as portas",
                Gravidade.INFO,
                "O comando 'ss' não está disponível.",
            )
        ]
    expostas = [p for p in _ler_portas(saida.texto) if _exposta(p.endereco)]
    if not expostas:
        return [
            Achado(
                "Nenhuma porta aberta para a rede",
                Gravidade.OK,
                "Os serviços em escuta estão limitados à própria máquina.",
            )
        ]
    return [_porta_exposta(p) for p in expostas]


def _ler_portas(texto: str) -> list[Porta]:
    portas: list[Porta] = []
    for linha in texto.splitlines():
        campos = linha.split()
        if len(campos) < 5:
            continue
        endereco, porta = _separar(campos[4])
        portas.append(Porta(endereco, porta, _programa(linha)))
    return portas


def _separar(local: str) -> tuple[str, str]:
    endereco, _, porta = local.rpartition(":")
    return endereco, porta


def _programa(linha: str) -> str:
    inicio = linha.find('users:(("')
    if inicio == -1:
        return "desconhecido"
    resto = linha[inicio + len('users:(("') :]
    return resto.split('"', 1)[0]


def _exposta(endereco: str) -> bool:
    return not any(endereco.startswith(local) for local in _LOCAIS)


def _porta_exposta(porta: Porta) -> Achado:
    return Achado(
        f"Porta {porta.porta} aberta para a rede ({porta.programa})",
        Gravidade.MEDIA,
        f"O programa '{porta.programa}' escuta em {porta.endereco}:{porta.porta}.",
        "Serviços abertos para fora podem ser acessados por outros aparelhos da rede.",
        (
            "Confirme se você precisa desse serviço acessível na rede.",
            "Se for só local, configure-o para escutar em 127.0.0.1.",
            "Se não usa, desligue o serviço.",
        ),
    )
