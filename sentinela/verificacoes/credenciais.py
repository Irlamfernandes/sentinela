"""Credenciais no home que não devem ser legíveis por outros usuários."""

from __future__ import annotations

from dataclasses import dataclass

from sentinela.nucleo.ambiente import Ambiente
from sentinela.nucleo.modelos import Achado, Gravidade

ID = "credenciais"
NOME = "Credenciais no home"
CATEGORIA = "Arquivos sensíveis"

# Bits de "grupo" e "outros": credenciais não devem tê-los.
OUTROS = 0o077


@dataclass(frozen=True)
class Credencial:
    caminho: str  # relativo ao home
    descricao: str


CREDENCIAIS: tuple[Credencial, ...] = (
    Credencial(".aws/credentials", "chaves da AWS"),
    Credencial(".git-credentials", "senhas de repositórios Git"),
    Credencial(".netrc", "logins de serviços de rede"),
    Credencial(".config/gh/hosts.yml", "token do GitHub (gh)"),
    Credencial(".docker/config.json", "login de registries Docker"),
    Credencial(".pgpass", "senhas do PostgreSQL"),
)


def _avaliar(amb: Ambiente, credencial: Credencial) -> Achado | None:
    caminho = f"{amb.lar}/{credencial.caminho}"
    modo = amb.modo(caminho)
    if modo is None:
        return None  # o arquivo não existe: nada a relatar
    if modo & OUTROS:
        return Achado(
            f"{credencial.caminho} legível por outros",
            Gravidade.ALTA,
            f"{caminho} ({credencial.descricao}) está com {modo:03o}.",
            "Outro usuário da máquina pode copiar essas credenciais e usar no seu lugar.",
            (f"Restrinja: chmod 600 {caminho}",),
        )
    return Achado(
        f"{credencial.caminho} protegido",
        Gravidade.OK,
        f"{caminho} está com {modo:03o}.",
    )


def verificar(amb: Ambiente) -> list[Achado]:
    achados = [_avaliar(amb, c) for c in CREDENCIAIS]
    presentes = [a for a in achados if a is not None]
    if not presentes:
        return [
            Achado(
                "Nenhum arquivo de credenciais conhecido encontrado",
                Gravidade.OK,
                "Nenhum dos arquivos de credenciais verificados existe no seu home.",
            )
        ]
    return presentes
