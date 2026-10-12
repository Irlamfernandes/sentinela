from __future__ import annotations

from conftest import AmbienteFalso, saida

from sentinela.nucleo.modelos import Gravidade
from sentinela.verificacoes import firmware, inicializacao, login


def test_autostart_vazio_fica_ok():
    assert inicializacao._autostart(AmbienteFalso()).gravidade is Gravidade.OK


def test_autostart_com_itens_vira_info():
    amb = AmbienteFalso(conteudo_de_pastas={"/home/teste/.config/autostart": ["x.desktop"]})
    assert inicializacao._autostart(amb).gravidade is Gravidade.INFO


def test_lastb_sem_root_vira_info():
    (achado,) = login.verificar(AmbienteFalso())
    assert achado.gravidade is Gravidade.INFO


def test_muitas_falhas_de_login_e_media():
    linhas = "\n".join(f"root ssh:notty 1.2.3.{i} Mon" for i in range(30)) + "\nbtmp begins ...\n"
    amb = AmbienteFalso(comandos={("lastb", "-w"): saida(linhas)})
    (achado,) = login.verificar(amb)
    assert achado.gravidade is Gravidade.MEDIA


def test_firmware_sem_fwupd_vira_info():
    (achado,) = firmware.verificar(AmbienteFalso())
    assert achado.gravidade is Gravidade.INFO


def test_firmware_em_dia_fica_ok():
    amb = AmbienteFalso(comandos={("fwupdmgr", "get-updates"): saida("No updates available")})
    (achado,) = firmware.verificar(amb)
    assert achado.gravidade is Gravidade.OK
