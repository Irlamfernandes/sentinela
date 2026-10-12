"""Verifica se há um firewall ativo (ufw ou firewalld)."""

from __future__ import annotations

from sentinela.nucleo.ambiente import Ambiente
from sentinela.nucleo.modelos import Achado, Gravidade

ID = "firewall"
NOME = "Firewall"
CATEGORIA = "Rede"


def verificar(amb: Ambiente) -> list[Achado]:
    ufw = amb.rodar(["ufw", "status"])
    if ufw.encontrado:
        return [_do_ufw(ufw.texto)]
    firewalld = amb.rodar(["firewall-cmd", "--state"])
    if firewalld.encontrado:
        return [_do_firewalld(firewalld.texto)]
    return [_sem_firewall()]


def _do_ufw(texto: str) -> Achado:
    if "Status: active" in texto:
        return Achado(
            "Firewall ativo (ufw)",
            Gravidade.OK,
            "O ufw está ativo e filtrando conexões.",
        )
    return Achado(
        "Firewall instalado, mas desligado (ufw)",
        Gravidade.ALTA,
        "O ufw está instalado, porém inativo.",
        "Sem firewall, qualquer serviço que esteja escutando fica exposto na rede.",
        (
            "Abra o terminal.",
            "Ligue o firewall: sudo ufw enable",
            "Confira o estado: sudo ufw status",
        ),
    )


def _do_firewalld(texto: str) -> Achado:
    if "running" in texto:
        return Achado(
            "Firewall ativo (firewalld)",
            Gravidade.OK,
            "O firewalld está em execução.",
        )
    return Achado(
        "Firewall instalado, mas parado (firewalld)",
        Gravidade.ALTA,
        "O firewalld está instalado, porém parado.",
        "Sem firewall, qualquer serviço que esteja escutando fica exposto na rede.",
        (
            "Abra o terminal.",
            "Inicie o serviço: sudo systemctl enable --now firewalld",
            "Confira o estado: sudo firewall-cmd --state",
        ),
    )


def _sem_firewall() -> Achado:
    return Achado(
        "Nenhum firewall encontrado",
        Gravidade.MEDIA,
        "Não há ufw nem firewalld instalados.",
        "Um firewall reduz o risco de um serviço aberto ser acessado de fora.",
        (
            "Instale o ufw: sudo apt install ufw",
            "Ligue o firewall: sudo ufw enable",
        ),
    )
