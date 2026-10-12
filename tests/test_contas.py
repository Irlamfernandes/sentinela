from __future__ import annotations

from conftest import AmbienteFalso

from sentinela.nucleo.modelos import Gravidade
from sentinela.verificacoes import contas

PASSWD_OK = "root:x:0:0:root:/root:/bin/bash\nirlam:x:1000:1000:Irlam:/home/irlam:/bin/bash\n"
PASSWD_RUIM = PASSWD_OK + "oculto:x:0:0::/root:/bin/bash\n"


def test_so_root_com_uid_zero_fica_ok():
    assert contas._outros_root(PASSWD_OK).gravidade is Gravidade.OK


def test_segundo_uid_zero_e_critico():
    achado = contas._outros_root(PASSWD_RUIM)
    assert achado.gravidade is Gravidade.CRITICA
    assert "oculto" in achado.descricao


def test_sudo_nopasswd_e_media():
    amb = AmbienteFalso(arquivos={"/etc/sudoers": "irlam ALL=(ALL) NOPASSWD: ALL\n"})
    assert contas._sudo_sem_senha(amb).gravidade is Gravidade.MEDIA


def test_sudo_nopasswd_comentado_fica_ok():
    amb = AmbienteFalso(arquivos={"/etc/sudoers": "# irlam ALL=(ALL) NOPASSWD: ALL\n"})
    assert contas._sudo_sem_senha(amb).gravidade is Gravidade.OK


def test_minlen_forte_fica_ok():
    amb = AmbienteFalso(arquivos={"/etc/security/pwquality.conf": "minlen = 12\n"})
    assert contas._tamanho_minimo_de_senha(amb).gravidade is Gravidade.OK


def test_minlen_fraco_e_baixo():
    amb = AmbienteFalso(arquivos={"/etc/security/pwquality.conf": "minlen = 6\n"})
    assert contas._tamanho_minimo_de_senha(amb).gravidade is Gravidade.BAIXA
