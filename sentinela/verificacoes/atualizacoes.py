"""Atualizações pendentes, atualização automática e fim de suporte do sistema."""

from __future__ import annotations

from datetime import date

from sentinela.nucleo.ambiente import Ambiente
from sentinela.nucleo.modelos import Achado, Gravidade

ID = "atualizacoes"
NOME = "Atualizações"
CATEGORIA = "Sistema"

# Fim do suporte padrão das versões LTS do Ubuntu (5 anos).
FIM_DE_SUPORTE: dict[str, date] = {
    "20.04": date(2025, 4, 30),
    "22.04": date(2027, 4, 30),
    "24.04": date(2029, 4, 30),
    "26.04": date(2031, 4, 30),
}


def verificar(amb: Ambiente) -> list[Achado]:
    return [_seguranca(amb), _automaticas(amb), _suporte(amb)]


def _seguranca(amb: Ambiente) -> Achado:
    saida = amb.rodar(["apt-get", "--just-print", "upgrade"])
    if not saida.encontrado:
        return Achado(
            "Não foi possível checar atualizações",
            Gravidade.INFO,
            "O comando 'apt-get' não está disponível.",
        )
    quantas = sum(1 for linha in saida.texto.splitlines() if "-security" in linha.lower())
    if quantas == 0:
        return Achado(
            "Sem atualizações de segurança pendentes",
            Gravidade.OK,
            "Nenhum pacote de segurança aguardando instalação.",
        )
    return Achado(
        f"{quantas} atualização(ões) de segurança pendente(s)",
        Gravidade.ALTA,
        f"Há {quantas} pacote(s) de segurança para instalar.",
        "Falha conhecida e sem correção é o caminho mais comum de invasão.",
        (
            "Atualize a lista: sudo apt update",
            "Instale as atualizações: sudo apt upgrade",
        ),
    )


def _automaticas(amb: Ambiente) -> Achado:
    texto = amb.ler("/etc/apt/apt.conf.d/20auto-upgrades") or ""
    ligado = 'Unattended-Upgrade "1"' in texto
    if ligado:
        return Achado(
            "Atualização automática de segurança ligada",
            Gravidade.OK,
            "O unattended-upgrades está configurado para instalar correções sozinho.",
        )
    return Achado(
        "Atualização automática de segurança desligada",
        Gravidade.MEDIA,
        "O unattended-upgrades não está ligado.",
        "Sem ele, correções de segurança dependem de você lembrar de atualizar.",
        (
            "Instale: sudo apt install unattended-upgrades",
            "Ligue: sudo dpkg-reconfigure -plow unattended-upgrades",
        ),
    )


def _suporte(amb: Ambiente) -> Achado:
    versao = _versao_ubuntu(amb.ler("/etc/os-release"))
    fim = FIM_DE_SUPORTE.get(versao or "")
    if versao is None or fim is None:
        return Achado(
            "Versão do sistema não reconhecida",
            Gravidade.INFO,
            "Não foi possível determinar se a versão ainda tem suporte.",
        )
    if amb.hoje() <= fim:
        return Achado(
            f"Ubuntu {versao} com suporte",
            Gravidade.OK,
            f"Recebe atualizações de segurança até {fim.strftime('%d/%m/%Y')}.",
        )
    return Achado(
        f"Ubuntu {versao} sem suporte",
        Gravidade.CRITICA,
        f"O suporte terminou em {fim.strftime('%d/%m/%Y')}.",
        "Sem suporte, novas falhas de segurança não são mais corrigidas.",
        (
            "Faça backup dos seus dados.",
            "Atualize para uma versão LTS com suporte: sudo do-release-upgrade",
        ),
    )


def _versao_ubuntu(os_release: str | None) -> str | None:
    if not os_release:
        return None
    for linha in os_release.splitlines():
        if linha.startswith("VERSION_ID="):
            return linha.split("=", 1)[1].strip().strip('"')
    return None
