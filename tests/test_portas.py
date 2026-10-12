from __future__ import annotations

from conftest import AmbienteFalso, saida

from sentinela.nucleo.modelos import Gravidade
from sentinela.verificacoes import portas

# Formato do `ss -tulpnH`: Netid State Recv-Q Send-Q Local:Porta Peer users:(("prog",pid=1,fd=2))
SO_LOCAL = (
    'tcp LISTEN 0 128 127.0.0.1:631 0.0.0.0:* users:(("cupsd",pid=1,fd=7))\n'
    'tcp LISTEN 0 128 [::1]:25 [::]:* users:(("master",pid=2,fd=13))\n'
)
EXPOSTO = 'tcp LISTEN 0 128 0.0.0.0:22 0.0.0.0:* users:(("sshd",pid=3,fd=3))\n'


def test_so_local_fica_ok():
    amb = AmbienteFalso(comandos={("ss", "-tulpnH"): saida(SO_LOCAL)})
    (achado,) = portas.verificar(amb)
    assert achado.gravidade is Gravidade.OK


def test_porta_exposta_e_media_com_programa():
    amb = AmbienteFalso(comandos={("ss", "-tulpnH"): saida(SO_LOCAL + EXPOSTO)})
    (achado,) = portas.verificar(amb)
    assert achado.gravidade is Gravidade.MEDIA
    assert "22" in achado.titulo
    assert "sshd" in achado.titulo


def test_sem_ss_vira_info():
    (achado,) = portas.verificar(AmbienteFalso())
    assert achado.gravidade is Gravidade.INFO
