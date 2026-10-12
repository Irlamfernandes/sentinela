from __future__ import annotations

from conftest import AmbienteFalso, saida

from sentinela.nucleo.modelos import Gravidade
from sentinela.verificacoes import arquivos, credenciais


def test_shadow_restrito_fica_ok():
    amb = AmbienteFalso(modos={"/etc/shadow": 0o640, "/etc/passwd": 0o644, "/etc/sudoers": 0o440})
    permissoes = [a for a in arquivos.verificar(amb) if "/etc/" in a.titulo]
    assert all(a.gravidade is Gravidade.OK for a in permissoes)


def test_arquivo_gravavel_por_todos_e_media():
    amb = AmbienteFalso(
        comandos={
            (
                "find",
                "/home/teste",
                "-xdev",
                "-type",
                "f",
                "-perm",
                "-0002",
                "-not",
                "-path",
                "*/.*",
            ): saida("/home/teste/aberto.sh\n")
        }
    )
    assert arquivos._mundo_gravavel(amb).gravidade is Gravidade.MEDIA


def test_shadow_legivel_por_todos_e_alto():
    amb = AmbienteFalso(modos={"/etc/shadow": 0o644})
    shadow = next(a for a in arquivos.verificar(amb) if "/etc/shadow" in a.titulo)
    assert shadow.gravidade is Gravidade.ALTA


def test_credencial_exposta_e_alta():
    amb = AmbienteFalso(modos={"/home/teste/.aws/credentials": 0o644})
    (achado,) = credenciais.verificar(amb)
    assert achado.gravidade is Gravidade.ALTA
    assert "chmod 600" in achado.solucao[0]


def test_credencial_protegida_fica_ok():
    amb = AmbienteFalso(modos={"/home/teste/.pgpass": 0o600})
    (achado,) = credenciais.verificar(amb)
    assert achado.gravidade is Gravidade.OK


def test_sem_credenciais_retorna_um_ok():
    (achado,) = credenciais.verificar(AmbienteFalso())
    assert achado.gravidade is Gravidade.OK
