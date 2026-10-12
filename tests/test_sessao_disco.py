from __future__ import annotations

from conftest import AmbienteFalso, saida

from sentinela.nucleo.modelos import Gravidade
from sentinela.verificacoes import disco, sessao

SCREENSAVER = ("gsettings", "get", "org.gnome.desktop.screensaver", "lock-enabled")


def test_bloqueio_ligado_fica_ok():
    amb = AmbienteFalso(comandos={SCREENSAVER: saida("true")})
    assert sessao._bloqueio_de_tela(amb).gravidade is Gravidade.OK


def test_bloqueio_desligado_e_media():
    amb = AmbienteFalso(comandos={SCREENSAVER: saida("false")})
    assert sessao._bloqueio_de_tela(amb).gravidade is Gravidade.MEDIA


def test_login_automatico_ligado_e_alto():
    conf = "[daemon]\nAutomaticLoginEnable=true\nAutomaticLogin=irlam\n"
    amb = AmbienteFalso(arquivos={"/etc/gdm3/custom.conf": conf})
    assert sessao._login_automatico(amb).gravidade is Gravidade.ALTA


def test_login_automatico_desligado_fica_ok():
    assert sessao._login_automatico(AmbienteFalso()).gravidade is Gravidade.OK


def test_disco_criptografado_fica_ok():
    amb = AmbienteFalso(comandos={("lsblk", "-o", "TYPE,FSTYPE", "-n"): saida("crypt crypto_LUKS")})
    assert disco._criptografia(amb).gravidade is Gravidade.OK


def test_disco_sem_criptografia_e_media():
    amb = AmbienteFalso(comandos={("lsblk", "-o", "TYPE,FSTYPE", "-n"): saida("part ext4")})
    assert disco._criptografia(amb).gravidade is Gravidade.MEDIA


def test_core_dumps_em_disco_e_baixo():
    amb = AmbienteFalso(arquivos={"/proc/sys/kernel/core_pattern": "/tmp/core.%p"})
    assert disco._core_dumps(amb).gravidade is Gravidade.BAIXA
