"""Ajustes de segurança do kernel, lidos de /proc/sys (sysctl)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from sentinela.nucleo.ambiente import Ambiente
from sentinela.nucleo.modelos import Achado, Gravidade

ID = "kernel"
NOME = "Ajustes do kernel"
CATEGORIA = "Sistema"


@dataclass(frozen=True)
class Ajuste:
    caminho: str  # arquivo em /proc/sys correspondente ao sysctl
    sysctl: str  # nome do parâmetro (ex.: kernel.kptr_restrict)
    nome: str
    seguro: Callable[[str], bool]
    valor_seguro: str  # o que pôr no sysctl para corrigir
    risco: str
    gravidade_ruim: Gravidade
    extras: tuple[str, ...] = field(default_factory=tuple)


def _ao_menos(minimo: int) -> Callable[[str], bool]:
    def regra(valor: str) -> bool:
        return valor.isdigit() and int(valor) >= minimo

    return regra


def _igual(esperado: str) -> Callable[[str], bool]:
    return lambda valor: valor == esperado


AJUSTES: tuple[Ajuste, ...] = (
    Ajuste(
        "/proc/sys/kernel/randomize_va_space",
        "kernel.randomize_va_space",
        "Aleatorização da memória (ASLR)",
        _igual("2"),
        "2",
        "Sem ASLR, falhas de programas viram invasão com muito mais facilidade.",
        Gravidade.ALTA,
    ),
    Ajuste(
        "/proc/sys/kernel/yama/ptrace_scope",
        "kernel.yama.ptrace_scope",
        "Restrição de ptrace",
        _ao_menos(1),
        "1",
        "Sem isso, um programa pode ler a memória de outro e roubar senhas.",
        Gravidade.MEDIA,
    ),
    Ajuste(
        "/proc/sys/kernel/dmesg_restrict",
        "kernel.dmesg_restrict",
        "Mensagens do kernel restritas",
        _igual("1"),
        "1",
        "O log do kernel expõe informações úteis para quem quer atacar a máquina.",
        Gravidade.BAIXA,
    ),
    Ajuste(
        "/proc/sys/kernel/kptr_restrict",
        "kernel.kptr_restrict",
        "Endereços do kernel escondidos",
        _ao_menos(1),
        "1",
        "Endereços internos à mostra ajudam a explorar falhas do kernel.",
        Gravidade.BAIXA,
    ),
    Ajuste(
        "/proc/sys/net/ipv4/tcp_syncookies",
        "net.ipv4.tcp_syncookies",
        "Proteção contra SYN flood",
        _igual("1"),
        "1",
        "Sem SYN cookies, um ataque simples pode derrubar a rede da máquina.",
        Gravidade.BAIXA,
    ),
    Ajuste(
        "/proc/sys/net/ipv4/conf/all/accept_redirects",
        "net.ipv4.conf.all.accept_redirects",
        "Rejeita redirecionamentos de rede",
        _igual("0"),
        "0",
        "Aceitar redirecionamentos permite desviar seu tráfego para um atacante.",
        Gravidade.BAIXA,
    ),
)


def _avaliar(amb: Ambiente, ajuste: Ajuste) -> Achado:
    valor = amb.ler(ajuste.caminho)
    if valor is None:
        return Achado(
            f"{ajuste.nome}: não foi possível verificar",
            Gravidade.INFO,
            f"{ajuste.caminho} não existe nesta máquina.",
        )
    atual = valor.strip()
    if ajuste.seguro(atual):
        return Achado(f"{ajuste.nome} ativo", Gravidade.OK, f"{ajuste.sysctl} = {atual}.")
    return Achado(
        f"{ajuste.nome} desativado",
        ajuste.gravidade_ruim,
        f"{ajuste.sysctl} = {atual}.",
        ajuste.risco,
        (
            f"Edite /etc/sysctl.d/99-sentinela.conf (como root) e adicione: "
            f"{ajuste.sysctl} = {ajuste.valor_seguro}",
            "Aplique agora: sudo sysctl --system",
        ),
    )


def verificar(amb: Ambiente) -> list[Achado]:
    return [_avaliar(amb, ajuste) for ajuste in AJUSTES]
