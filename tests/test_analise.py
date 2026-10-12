from __future__ import annotations

from conftest import AmbienteFalso, saida

from sentinela.nucleo.analise import Relatorio, executar
from sentinela.nucleo.modelos import Achado, Gravidade


def test_nota_desconta_por_gravidade():
    relatorio = Relatorio(
        (
            Achado("ok", Gravidade.OK, ""),
            Achado("alto", Gravidade.ALTA, ""),
            Achado("medio", Gravidade.MEDIA, ""),
        )
    )
    assert relatorio.nota == 100 - 20 - 10


def test_nota_nao_fica_negativa():
    graves = tuple(Achado(str(i), Gravidade.CRITICA, "") for i in range(5))
    assert Relatorio(graves).nota == 0


def test_problemas_sao_ordenados_e_sem_os_ok():
    relatorio = Relatorio(
        (
            Achado("ok", Gravidade.OK, ""),
            Achado("medio", Gravidade.MEDIA, ""),
            Achado("critico", Gravidade.CRITICA, ""),
        )
    )
    assert [a.titulo for a in relatorio.problemas] == ["critico", "medio"]


def test_executar_roda_todas_as_verificacoes():
    amb = AmbienteFalso(comandos={("ufw", "status"): saida("Status: active")})
    relatorio = executar(amb)
    titulos = {a.titulo for a in relatorio.achados}
    assert "Firewall ativo (ufw)" in titulos
    assert "Servidor SSH não instalado" in titulos
    assert "Pasta .ssh não encontrada" in titulos
