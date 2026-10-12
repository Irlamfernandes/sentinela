from __future__ import annotations

from datetime import date

from conftest import AmbienteFalso, saida

from sentinela.nucleo.modelos import Gravidade
from sentinela.verificacoes import atualizacoes

OS_2404 = 'VERSION_ID="24.04"\n'
OS_2004 = 'VERSION_ID="20.04"\n'


def test_sem_pacotes_de_seguranca_fica_ok():
    amb = AmbienteFalso(comandos={("apt-get", "--just-print", "upgrade"): saida("Inst bash\n")})
    assert atualizacoes._seguranca(amb).gravidade is Gravidade.OK


def test_com_pacotes_de_seguranca_e_alto():
    texto = "Inst libc6 (ubuntu-security)\nInst openssl (24.04.1 Ubuntu:24.04/noble-security)\n"
    amb = AmbienteFalso(comandos={("apt-get", "--just-print", "upgrade"): saida(texto)})
    achado = atualizacoes._seguranca(amb)
    assert achado.gravidade is Gravidade.ALTA
    assert "2" in achado.titulo


def test_versao_com_suporte_fica_ok():
    amb = AmbienteFalso(arquivos={"/etc/os-release": OS_2404}, data_de_hoje=date(2026, 10, 12))
    assert atualizacoes._suporte(amb).gravidade is Gravidade.OK


def test_versao_sem_suporte_e_critico():
    amb = AmbienteFalso(arquivos={"/etc/os-release": OS_2004}, data_de_hoje=date(2026, 10, 12))
    assert atualizacoes._suporte(amb).gravidade is Gravidade.CRITICA


def test_atualizacao_automatica_ligada_fica_ok():
    conf = 'APT::Periodic::Unattended-Upgrade "1";\n'
    amb = AmbienteFalso(arquivos={"/etc/apt/apt.conf.d/20auto-upgrades": conf})
    assert atualizacoes._automaticas(amb).gravidade is Gravidade.OK


def test_atualizacao_automatica_desligada_e_media():
    assert atualizacoes._automaticas(AmbienteFalso()).gravidade is Gravidade.MEDIA
