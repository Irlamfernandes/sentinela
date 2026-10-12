from __future__ import annotations

from conftest import AmbienteFalso

from sentinela.nucleo.modelos import Gravidade
from sentinela.verificacoes import chaves_ssh

PASTA = "/home/teste/.ssh"


def test_sem_pasta_ssh_e_apenas_info():
    (achado,) = chaves_ssh.verificar(AmbienteFalso())
    assert achado.gravidade is Gravidade.INFO


def test_pasta_e_chave_protegidas_ficam_ok():
    amb = AmbienteFalso(
        modos={PASTA: 0o700, f"{PASTA}/id_ed25519": 0o600},
        conteudo_de_pastas={PASTA: ["id_ed25519", "id_ed25519.pub", "known_hosts"]},
    )
    pasta, chave = chaves_ssh.verificar(amb)
    assert pasta.gravidade is Gravidade.OK
    assert chave.gravidade is Gravidade.OK


def test_chave_privada_legivel_por_outros_e_alta():
    amb = AmbienteFalso(
        modos={PASTA: 0o700, f"{PASTA}/id_rsa": 0o644},
        conteudo_de_pastas={PASTA: ["id_rsa"]},
    )
    _, chave = chaves_ssh.verificar(amb)
    assert chave.gravidade is Gravidade.ALTA
    assert any("chmod 600" in passo for passo in chave.solucao)


def test_pasta_aberta_e_media():
    amb = AmbienteFalso(modos={PASTA: 0o755}, conteudo_de_pastas={PASTA: []})
    (pasta,) = chaves_ssh.verificar(amb)
    assert pasta.gravidade is Gravidade.MEDIA
