"""Permissões de arquivos sensíveis do sistema."""

from __future__ import annotations

from dataclasses import dataclass

from sentinela.nucleo.ambiente import Ambiente
from sentinela.nucleo.modelos import Achado, Gravidade

ID = "arquivos"
NOME = "Arquivos sensíveis"
CATEGORIA = "Arquivos sensíveis"


@dataclass(frozen=True)
class Alvo:
    caminho: str
    maximo: int  # permissão máxima aceitável (octal)
    risco: str


ALVOS: tuple[Alvo, ...] = (
    Alvo(
        "/etc/shadow",
        0o640,
        "As senhas do sistema (em forma embaralhada) ficam aqui; não podem ser lidas por todos.",
    ),
    Alvo(
        "/etc/passwd",
        0o644,
        "Se qualquer um puder escrever aqui, pode criar um usuário com poder de root.",
    ),
    Alvo(
        "/etc/sudoers",
        0o440,
        "Quem escreve aqui controla quem vira root.",
    ),
)


def _avaliar(amb: Ambiente, alvo: Alvo) -> Achado:
    modo = amb.modo(alvo.caminho)
    if modo is None:
        return Achado(
            f"{alvo.caminho}: não verificado",
            Gravidade.INFO,
            "Arquivo ausente ou sem permissão de leitura para checar.",
        )
    if modo & ~alvo.maximo & 0o777:
        return Achado(
            f"Permissão frouxa em {alvo.caminho}",
            Gravidade.ALTA,
            f"{alvo.caminho} está com {modo:03o} (o máximo seguro é {alvo.maximo:03o}).",
            alvo.risco,
            (f"Ajuste: sudo chmod {alvo.maximo:03o} {alvo.caminho}",),
        )
    return Achado(
        f"Permissão correta em {alvo.caminho}",
        Gravidade.OK,
        f"{alvo.caminho} está com {modo:03o}.",
    )


def _mundo_gravavel(amb: Ambiente) -> Achado:
    saida = amb.rodar(
        ["find", amb.lar, "-xdev", "-type", "f", "-perm", "-0002", "-not", "-path", "*/.*"]
    )
    if not saida.encontrado:
        return Achado(
            "Arquivos graváveis por todos: não verificado",
            Gravidade.INFO,
            "O comando 'find' não está disponível.",
        )
    arquivos = [linha for linha in saida.texto.splitlines() if linha.strip()]
    if not arquivos:
        return Achado(
            "Nenhum arquivo gravável por todos no home",
            Gravidade.OK,
            "Nenhum arquivo do seu home pode ser alterado por outros usuários.",
        )
    exemplos = ", ".join(arquivos[:3])
    return Achado(
        f"{len(arquivos)} arquivo(s) graváveis por qualquer usuário",
        Gravidade.MEDIA,
        f"No seu home, por exemplo: {exemplos}.",
        "Outro usuário da máquina pode alterar esses arquivos, inclusive para inserir código.",
        (
            "Veja todos: find ~ -xdev -type f -perm -0002 -not -path '*/.*'",
            "Tire a escrita de outros: chmod o-w <arquivo>",
        ),
    )


def verificar(amb: Ambiente) -> list[Achado]:
    achados = [_avaliar(amb, alvo) for alvo in ALVOS]
    achados.append(_mundo_gravavel(amb))
    return achados
