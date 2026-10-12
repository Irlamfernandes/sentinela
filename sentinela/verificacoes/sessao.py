"""Proteções da sessão gráfica (GNOME): bloqueio de tela e login automático."""

from __future__ import annotations

from sentinela.nucleo.ambiente import Ambiente
from sentinela.nucleo.modelos import Achado, Gravidade

ID = "sessao"
NOME = "Sessão e tela"
CATEGORIA = "Acesso físico"


def verificar(amb: Ambiente) -> list[Achado]:
    return [_bloqueio_de_tela(amb), _login_automatico(amb)]


def _gsettings(amb: Ambiente, esquema: str, chave: str) -> str | None:
    saida = amb.rodar(["gsettings", "get", esquema, chave])
    return saida.texto.strip() if saida.encontrado and saida.codigo == 0 else None


def _bloqueio_de_tela(amb: Ambiente) -> Achado:
    valor = _gsettings(amb, "org.gnome.desktop.screensaver", "lock-enabled")
    if valor is None:
        return Achado(
            "Bloqueio de tela não verificado",
            Gravidade.INFO,
            "Não foi possível ler a configuração do GNOME (gsettings).",
        )
    if valor == "true":
        return Achado(
            "Bloqueio automático de tela ligado",
            Gravidade.OK,
            "A tela é bloqueada ao ativar a proteção de tela.",
        )
    return Achado(
        "Bloqueio automático de tela desligado",
        Gravidade.MEDIA,
        "A tela não bloqueia sozinha quando você se ausenta.",
        "Qualquer um perto do computador acessa tudo enquanto você não está.",
        (
            "Abra Configurações > Privacidade > Tela de bloqueio.",
            "Ligue o bloqueio automático e defina um tempo curto.",
        ),
    )


def _login_automatico(amb: Ambiente) -> Achado:
    texto = (amb.ler("/etc/gdm3/custom.conf") or "") + (amb.ler("/etc/gdm/custom.conf") or "")
    ligado = any(
        linha.replace(" ", "").lower() == "automaticloginenable=true"
        for linha in texto.splitlines()
        if not linha.strip().startswith("#")
    )
    if not ligado:
        return Achado(
            "Login automático desligado",
            Gravidade.OK,
            "O sistema pede login ao ligar.",
        )
    return Achado(
        "Login automático ligado",
        Gravidade.ALTA,
        "O sistema entra na sua conta sem pedir senha ao ligar.",
        "Quem ligar o computador entra direto na sua sessão.",
        (
            "Abra Configurações > Usuários.",
            "Desligue o 'Início de sessão automático'.",
        ),
    )
