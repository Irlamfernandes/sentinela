from __future__ import annotations

from conftest import AmbienteFalso

from sentinela.nucleo.modelos import Gravidade
from sentinela.verificacoes import kernel

SEGUROS = {
    "/proc/sys/kernel/randomize_va_space": "2",
    "/proc/sys/kernel/yama/ptrace_scope": "1",
    "/proc/sys/kernel/dmesg_restrict": "1",
    "/proc/sys/kernel/kptr_restrict": "1",
    "/proc/sys/net/ipv4/tcp_syncookies": "1",
    "/proc/sys/net/ipv4/conf/all/accept_redirects": "0",
}


def test_todos_seguros_ficam_ok():
    achados = kernel.verificar(AmbienteFalso(arquivos=SEGUROS))
    assert all(a.gravidade is Gravidade.OK for a in achados)


def test_aslr_desligado_e_alto():
    arquivos = {**SEGUROS, "/proc/sys/kernel/randomize_va_space": "0"}
    (aslr,) = [a for a in kernel.verificar(AmbienteFalso(arquivos=arquivos)) if "ASLR" in a.titulo]
    assert aslr.gravidade is Gravidade.ALTA
    assert any("randomize_va_space" in passo for passo in aslr.solucao)


def test_arquivo_ausente_vira_info():
    achados = kernel.verificar(AmbienteFalso())
    assert all(a.gravidade is Gravidade.INFO for a in achados)
