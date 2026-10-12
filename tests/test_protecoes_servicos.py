from __future__ import annotations

from conftest import AmbienteFalso, saida

from sentinela.nucleo.modelos import Gravidade
from sentinela.verificacoes import protecoes, servicos_rede


def _ativos(*servicos: str) -> dict[tuple[str, ...], object]:
    return {("systemctl", "is-active", s): saida("active") for s in servicos}


def test_apparmor_ativo_fica_ok():
    amb = AmbienteFalso(
        arquivos={"/sys/module/apparmor/parameters/enabled": "Y"},
        comandos=_ativos("apparmor", "fail2ban", "auditd"),
    )
    apparmor, fail2ban, auditd = protecoes.verificar(amb)
    assert apparmor.gravidade is Gravidade.OK
    assert fail2ban.gravidade is Gravidade.OK
    assert auditd.gravidade is Gravidade.OK


def test_apparmor_inativo_e_alto():
    apparmor, fail2ban, _ = protecoes.verificar(AmbienteFalso())
    assert apparmor.gravidade is Gravidade.ALTA
    assert fail2ban.gravidade is Gravidade.BAIXA


def test_servico_de_rede_ligado_e_baixo():
    amb = AmbienteFalso(comandos=_ativos("cups"))
    cups, avahi = servicos_rede.verificar(amb)
    assert cups.gravidade is Gravidade.BAIXA
    assert avahi.gravidade is Gravidade.OK
