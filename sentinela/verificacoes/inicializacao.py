"""Programas que iniciam junto com o sistema ou com a sessão."""

from __future__ import annotations

from sentinela.nucleo.ambiente import Ambiente
from sentinela.nucleo.modelos import Achado, Gravidade

ID = "inicializacao"
NOME = "Programas de inicialização"
CATEGORIA = "Sistema"


def verificar(amb: Ambiente) -> list[Achado]:
    return [_servicos(amb), _autostart(amb)]


def _servicos(amb: Ambiente) -> Achado:
    saida = amb.rodar(["systemctl", "list-unit-files", "--state=enabled", "--no-legend"])
    if not saida.encontrado:
        return Achado(
            "Não foi possível listar os serviços",
            Gravidade.INFO,
            "O comando 'systemctl' não está disponível.",
        )
    nomes = [linha.split()[0] for linha in saida.texto.splitlines() if linha.split()]
    return Achado(
        f"{len(nomes)} serviço(s) iniciam com o sistema",
        Gravidade.INFO,
        "Lista do que sobe no boot. Revise se há algo que você não reconhece.",
        "",
        (
            "Veja a lista: systemctl list-unit-files --state=enabled",
            "Para desligar algo que não usa: sudo systemctl disable <nome>",
        ),
    )


def _autostart(amb: Ambiente) -> Achado:
    pasta = f"{amb.lar}/.config/autostart"
    itens = [nome for nome in amb.listar(pasta) if nome.endswith(".desktop")]
    if not itens:
        return Achado(
            "Nenhum programa extra inicia com a sessão",
            Gravidade.OK,
            "A pasta de autostart do usuário está vazia.",
        )
    return Achado(
        f"{len(itens)} programa(s) iniciam com a sua sessão",
        Gravidade.INFO,
        f"Encontrados em {pasta}: {', '.join(itens)}.",
        "Malware às vezes se registra aqui para abrir sempre que você entra.",
        (
            f"Revise os arquivos em {pasta}.",
            "Apague o .desktop de algo que você não reconhece.",
        ),
    )
