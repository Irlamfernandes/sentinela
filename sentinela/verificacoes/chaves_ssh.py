"""Verifica as permissões da pasta ~/.ssh e das chaves privadas."""

from __future__ import annotations

from sentinela.nucleo.ambiente import Ambiente
from sentinela.nucleo.modelos import Achado, Gravidade

ID = "chaves_ssh"
NOME = "Chaves SSH"
CATEGORIA = "Arquivos sensíveis"

# Bits de permissão para "grupo" e "outros": chaves não devem tê-los.
OUTROS = 0o077


def verificar(amb: Ambiente) -> list[Achado]:
    pasta = f"{amb.lar}/.ssh"
    modo = amb.modo(pasta)
    if modo is None:
        return [
            Achado(
                "Pasta .ssh não encontrada",
                Gravidade.INFO,
                "Não há ~/.ssh; nenhuma chave SSH para verificar.",
            )
        ]
    achados = [_pasta(pasta, modo)]
    for nome in amb.listar(pasta):
        if _parece_chave_privada(nome):
            achados.append(_chave(amb, f"{pasta}/{nome}", nome))
    return achados


def _parece_chave_privada(nome: str) -> bool:
    return nome.startswith("id_") and not nome.endswith(".pub")


def _pasta(caminho: str, modo: int) -> Achado:
    if modo & OUTROS:
        return Achado(
            "Pasta .ssh acessível por outros usuários",
            Gravidade.MEDIA,
            f"{caminho} está com permissão {modo:03o} (o esperado é 700).",
            "Outros usuários da máquina podem ver o conteúdo das suas chaves.",
            (f"Ajuste a permissão: chmod 700 {caminho}",),
        )
    return Achado(
        "Pasta .ssh protegida",
        Gravidade.OK,
        f"{caminho} está com permissão {modo:03o}.",
    )


def _chave(amb: Ambiente, caminho: str, nome: str) -> Achado:
    modo = amb.modo(caminho) or 0
    if modo & OUTROS:
        return Achado(
            f"Chave privada {nome} exposta",
            Gravidade.ALTA,
            f"{caminho} está com permissão {modo:03o} (o esperado é 600).",
            "Uma chave privada legível por outros pode ser copiada e usada no seu lugar.",
            (f"Ajuste a permissão: chmod 600 {caminho}",),
        )
    return Achado(
        f"Chave privada {nome} protegida",
        Gravidade.OK,
        f"{caminho} está com permissão {modo:03o}.",
    )
