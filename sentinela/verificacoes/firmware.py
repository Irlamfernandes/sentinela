"""Atualizações de firmware (fwupd)."""

from __future__ import annotations

from sentinela.nucleo.ambiente import Ambiente
from sentinela.nucleo.modelos import Achado, Gravidade

ID = "firmware"
NOME = "Firmware"
CATEGORIA = "Hardware"


def verificar(amb: Ambiente) -> list[Achado]:
    saida = amb.rodar(["fwupdmgr", "get-updates"])
    if not saida.encontrado:
        return [
            Achado(
                "fwupd não instalado",
                Gravidade.INFO,
                "Não dá para checar atualizações de firmware sem o fwupd.",
                "",
                ("Para checar firmware: sudo apt install fwupd",),
            )
        ]
    texto = saida.texto.lower()
    if "no updates" in texto or "nenhuma atualiz" in texto or "devices with no available" in texto:
        return [
            Achado("Firmware em dia", Gravidade.OK, "Nenhuma atualização de firmware pendente.")
        ]
    return [
        Achado(
            "Atualizações de firmware disponíveis",
            Gravidade.MEDIA,
            "O fwupd encontrou atualizações de firmware.",
            "Firmware desatualizado pode ter falhas de segurança já conhecidas.",
            (
                "Veja os detalhes: fwupdmgr get-updates",
                "Atualize: sudo fwupdmgr update",
            ),
        )
    ]
