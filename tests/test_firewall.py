from __future__ import annotations

from conftest import AmbienteFalso, saida

from sentinela.nucleo.modelos import Gravidade
from sentinela.verificacoes import firewall


def test_ufw_ativo_fica_ok():
    amb = AmbienteFalso(comandos={("ufw", "status"): saida("Status: active")})
    (achado,) = firewall.verificar(amb)
    assert achado.gravidade is Gravidade.OK


def test_ufw_inativo_e_alto_e_traz_passos():
    amb = AmbienteFalso(comandos={("ufw", "status"): saida("Status: inactive")})
    (achado,) = firewall.verificar(amb)
    assert achado.gravidade is Gravidade.ALTA
    assert any("ufw enable" in passo for passo in achado.solucao)


def test_firewalld_ativo_quando_nao_ha_ufw():
    amb = AmbienteFalso(comandos={("firewall-cmd", "--state"): saida("running")})
    (achado,) = firewall.verificar(amb)
    assert achado.gravidade is Gravidade.OK


def test_sem_nenhum_firewall_e_medio():
    (achado,) = firewall.verificar(AmbienteFalso())
    assert achado.gravidade is Gravidade.MEDIA
