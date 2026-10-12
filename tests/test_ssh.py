from __future__ import annotations

from conftest import AmbienteFalso

from sentinela.nucleo.modelos import Gravidade
from sentinela.verificacoes import ssh


def _com_config(texto: str) -> AmbienteFalso:
    return AmbienteFalso(arquivos={ssh.CAMINHO: texto})


def test_sem_sshd_config_e_apenas_info():
    (achado,) = ssh.verificar(AmbienteFalso())
    assert achado.gravidade is Gravidade.INFO


def test_root_liberado_e_senha_e_alto_e_medio():
    root, senha = ssh.verificar(_com_config("PermitRootLogin yes\nPasswordAuthentication yes\n"))
    assert root.gravidade is Gravidade.ALTA
    assert senha.gravidade is Gravidade.MEDIA


def test_config_segura_fica_ok():
    root, senha = ssh.verificar(
        _com_config("PermitRootLogin prohibit-password\nPasswordAuthentication no\n")
    )
    assert root.gravidade is Gravidade.OK
    assert senha.gravidade is Gravidade.OK


def test_comentarios_e_padroes_sao_respeitados():
    # Sem diretivas: vale o padrão (root restrito, senha habilitada).
    root, senha = ssh.verificar(_com_config("# arquivo vazio\n#PermitRootLogin yes\n"))
    assert root.gravidade is Gravidade.OK
    assert senha.gravidade is Gravidade.MEDIA


def test_vale_a_primeira_ocorrencia():
    root, _ = ssh.verificar(_com_config("PermitRootLogin yes\nPermitRootLogin no\n"))
    assert root.gravidade is Gravidade.ALTA
