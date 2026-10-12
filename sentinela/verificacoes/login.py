"""Histórico de acessos: tentativas falhas de login."""

from __future__ import annotations

from sentinela.nucleo.ambiente import Ambiente
from sentinela.nucleo.modelos import Achado, Gravidade

ID = "login"
NOME = "Histórico de login"
CATEGORIA = "Acesso"

# A partir de quantas tentativas falhas vale a pena alertar.
LIMITE = 20


def verificar(amb: Ambiente) -> list[Achado]:
    saida = amb.rodar(["lastb", "-w"])
    if not saida.encontrado or saida.codigo != 0:
        return [
            Achado(
                "Tentativas de login não verificadas",
                Gravidade.INFO,
                "Para ler as tentativas falhas é preciso rodar como root (sudo).",
                "",
                ("Rode a auditoria com permissão: sudo sentinela",),
            )
        ]
    falhas = [linha for linha in saida.texto.splitlines() if linha.strip() and not _rodape(linha)]
    if len(falhas) < LIMITE:
        return [
            Achado(
                "Poucas tentativas falhas de login",
                Gravidade.OK,
                f"{len(falhas)} tentativa(s) falha(s) registrada(s).",
            )
        ]
    return [
        Achado(
            "Muitas tentativas falhas de login",
            Gravidade.MEDIA,
            f"{len(falhas)} tentativa(s) falha(s) de login registradas.",
            "Pode indicar alguém tentando adivinhar uma senha.",
            (
                "Veja os detalhes: sudo lastb",
                "Se houver SSH exposto, instale o fail2ban e prefira login por chave.",
            ),
        )
    ]


def _rodape(linha: str) -> bool:
    return linha.startswith("btmp begins")
