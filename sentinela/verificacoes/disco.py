"""Proteção dos dados: criptografia de disco, Secure Boot e dumps de memória."""

from __future__ import annotations

from sentinela.nucleo.ambiente import Ambiente
from sentinela.nucleo.modelos import Achado, Gravidade

ID = "disco"
NOME = "Disco e inicialização"
CATEGORIA = "Dados"


def verificar(amb: Ambiente) -> list[Achado]:
    return [_criptografia(amb), _secure_boot(amb), _core_dumps(amb)]


def _criptografia(amb: Ambiente) -> Achado:
    saida = amb.rodar(["lsblk", "-o", "TYPE,FSTYPE", "-n"])
    if not saida.encontrado:
        return Achado(
            "Criptografia de disco não verificada",
            Gravidade.INFO,
            "O comando 'lsblk' não está disponível.",
        )
    if "crypt" in saida.texto or "LUKS" in saida.texto:
        return Achado(
            "Disco com criptografia",
            Gravidade.OK,
            "Há volume criptografado (LUKS).",
        )
    return Achado(
        "Disco sem criptografia",
        Gravidade.MEDIA,
        "Nenhum volume criptografado encontrado.",
        "Se o computador for perdido ou roubado, os dados podem ser lidos por outra pessoa.",
        (
            "A criptografia de disco (LUKS) é escolhida ao instalar o Ubuntu.",
            "Para ligar depois, é preciso backup e reinstalação.",
        ),
    )


def _secure_boot(amb: Ambiente) -> Achado:
    saida = amb.rodar(["mokutil", "--sb-state"])
    if not saida.encontrado:
        return Achado(
            "Secure Boot não verificado",
            Gravidade.INFO,
            "O comando 'mokutil' não está disponível.",
        )
    if "enabled" in saida.texto.lower():
        return Achado(
            "Secure Boot ligado",
            Gravidade.OK,
            "O sistema só carrega código de inicialização assinado.",
        )
    return Achado(
        "Secure Boot desligado",
        Gravidade.BAIXA,
        "O Secure Boot está desativado.",
        "Ele dificulta que um código malicioso se instale antes do sistema iniciar.",
        ("Ligue o Secure Boot na BIOS/UEFI do computador.",),
    )


def _core_dumps(amb: Ambiente) -> Achado:
    valor = (amb.ler("/proc/sys/kernel/core_pattern") or "").strip()
    if valor.startswith("|") or valor in ("", "core"):
        return Achado(
            "Dumps de memória controlados",
            Gravidade.OK,
            f"core_pattern = {valor or 'vazio'}.",
        )
    return Achado(
        "Dumps de memória gravados em disco",
        Gravidade.BAIXA,
        f"core_pattern = {valor}.",
        "Um dump pode conter senhas que estavam na memória do programa.",
        (
            "Edite /etc/sysctl.d/99-sentinela.conf (como root).",
            "Adicione: kernel.core_pattern = core",
            "Aplique: sudo sysctl --system",
        ),
    )
