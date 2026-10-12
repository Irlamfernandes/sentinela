"""Sentinela no terminal: roda a auditoria e mostra o resultado."""

from __future__ import annotations

from sentinela.nucleo.ambiente import Sistema
from sentinela.nucleo.analise import Relatorio, executar
from sentinela.nucleo.modelos import Achado


def _mostrar_achado(achado: Achado) -> None:
    print(f"\n[{achado.gravidade.rotulo}] {achado.titulo}")
    print(f"  {achado.descricao}")
    if achado.risco:
        print(f"  Risco: {achado.risco}")
    if achado.solucao:
        print("  Como resolver:")
        for passo in achado.solucao:
            print(f"    - {passo}")


def _mostrar(relatorio: Relatorio) -> None:
    print("Sentinela — auditoria de segurança do PC")
    print(f"Nota de segurança: {relatorio.nota}/100")
    problemas = relatorio.problemas
    if not problemas:
        print("Nenhum problema encontrado.")
        return
    print(f"{len(problemas)} ponto(s) para revisar:")
    for achado in problemas:
        _mostrar_achado(achado)


def main() -> int:
    _mostrar(executar(Sistema()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
