"""Proteções ativas: AppArmor, Fail2ban e auditd."""

from __future__ import annotations

from sentinela.nucleo.ambiente import Ambiente
from sentinela.nucleo.modelos import Achado, Gravidade

ID = "protecoes"
NOME = "Proteções do sistema"
CATEGORIA = "Sistema"


def verificar(amb: Ambiente) -> list[Achado]:
    return [_apparmor(amb), _fail2ban(amb), _auditd(amb)]


def _ativo(amb: Ambiente, servico: str) -> bool:
    saida = amb.rodar(["systemctl", "is-active", servico])
    return saida.encontrado and saida.texto.strip() == "active"


def _apparmor(amb: Ambiente) -> Achado:
    habilitado = amb.ler("/sys/module/apparmor/parameters/enabled")
    if habilitado is not None and habilitado.strip() == "Y" and _ativo(amb, "apparmor"):
        return Achado(
            "AppArmor ativo",
            Gravidade.OK,
            "O AppArmor está carregado e em execução.",
        )
    return Achado(
        "AppArmor inativo",
        Gravidade.ALTA,
        "O AppArmor não está carregado ou o serviço está parado.",
        "O AppArmor limita o estrago que um programa invadido pode fazer.",
        (
            "Ligue o serviço: sudo systemctl enable --now apparmor",
            "Confira os perfis: sudo aa-status",
        ),
    )


def _fail2ban(amb: Ambiente) -> Achado:
    if _ativo(amb, "fail2ban"):
        return Achado(
            "Fail2ban ativo",
            Gravidade.OK,
            "O fail2ban está bloqueando tentativas repetidas de login.",
        )
    return Achado(
        "Fail2ban ausente ou parado",
        Gravidade.BAIXA,
        "Não há fail2ban ativo.",
        "Ele bloqueia quem fica tentando adivinhar senhas (sobretudo no SSH).",
        (
            "Instale: sudo apt install fail2ban",
            "Ligue: sudo systemctl enable --now fail2ban",
        ),
    )


def _auditd(amb: Ambiente) -> Achado:
    if _ativo(amb, "auditd"):
        return Achado(
            "Auditoria do sistema ativa (auditd)",
            Gravidade.OK,
            "O auditd está registrando eventos de segurança.",
        )
    return Achado(
        "Auditoria do sistema ausente (auditd)",
        Gravidade.INFO,
        "O auditd não está ativo.",
        "Ele guarda um histórico detalhado, útil para investigar um incidente.",
        (
            "Instale: sudo apt install auditd",
            "Ligue: sudo systemctl enable --now auditd",
        ),
    )
