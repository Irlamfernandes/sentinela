"""Serviços de rede que costumam ficar ligados sem necessidade."""

from __future__ import annotations

from dataclasses import dataclass

from sentinela.nucleo.ambiente import Ambiente
from sentinela.nucleo.modelos import Achado, Gravidade

ID = "servicos_rede"
NOME = "Serviços de rede"
CATEGORIA = "Rede"


@dataclass(frozen=True)
class Servico:
    unidade: str
    nome: str
    para_que_serve: str
    desligar: str


SERVICOS: tuple[Servico, ...] = (
    Servico(
        "cups",
        "Impressão (CUPS)",
        "serviço de impressão, que abre uma porta de rede",
        "sudo systemctl disable --now cups cups-browsed",
    ),
    Servico(
        "avahi-daemon",
        "Descoberta na rede (Avahi)",
        "anúncio de serviços na rede local",
        "sudo systemctl disable --now avahi-daemon",
    ),
)


def _avaliar(amb: Ambiente, servico: Servico) -> Achado:
    saida = amb.rodar(["systemctl", "is-active", servico.unidade])
    ativo = saida.encontrado and saida.texto.strip() == "active"
    if not ativo:
        return Achado(
            f"{servico.nome} desligado",
            Gravidade.OK,
            f"O serviço {servico.unidade} não está ativo.",
        )
    return Achado(
        f"{servico.nome} ligado",
        Gravidade.BAIXA,
        f"O {servico.para_que_serve} está ativo.",
        "Todo serviço de rede ligado é uma porta a mais que pode ser atacada.",
        (f"Se você não usa, desligue: {servico.desligar}",),
    )


def verificar(amb: Ambiente) -> list[Achado]:
    return [_avaliar(amb, servico) for servico in SERVICOS]
