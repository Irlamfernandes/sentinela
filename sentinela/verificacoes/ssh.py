"""Verifica a configuração do servidor SSH (se instalado).

Lê só o `sshd_config` principal; diretivas trazidas por `Include` ficam de
fora nesta versão (ver docs/design.md).
"""

from __future__ import annotations

from sentinela.nucleo.ambiente import Ambiente
from sentinela.nucleo.modelos import Achado, Gravidade

ID = "ssh"
NOME = "Servidor SSH"
CATEGORIA = "Acesso remoto"

CAMINHO = "/etc/ssh/sshd_config"


def verificar(amb: Ambiente) -> list[Achado]:
    texto = amb.ler(CAMINHO)
    if texto is None:
        return [
            Achado(
                "Servidor SSH não instalado",
                Gravidade.INFO,
                "Não há sshd_config; o acesso remoto por SSH não está configurado.",
            )
        ]
    config = _ler_config(texto)
    return [_login_de_root(config), _senha(config)]


def _ler_config(texto: str) -> dict[str, str]:
    """Diretivas do sshd_config. Vale a primeira ocorrência, como o próprio sshd."""
    config: dict[str, str] = {}
    for linha in texto.splitlines():
        limpa = linha.split("#", 1)[0].strip()
        partes = limpa.split(None, 1)
        if len(partes) == 2:
            config.setdefault(partes[0].lower(), partes[1].strip())
    return config


def _login_de_root(config: dict[str, str]) -> Achado:
    valor = config.get("permitrootlogin", "prohibit-password").lower()
    if valor == "yes":
        return Achado(
            "Login de root pelo SSH liberado",
            Gravidade.ALTA,
            "PermitRootLogin está como 'yes'.",
            "Deixa o root exposto a tentativas automáticas de adivinhar a senha.",
            (
                f"Edite {CAMINHO} (ex.: sudo nano {CAMINHO}).",
                "Troque a linha por: PermitRootLogin prohibit-password",
                "Reinicie o SSH: sudo systemctl restart ssh",
            ),
        )
    return Achado(
        "Login de root pelo SSH restrito",
        Gravidade.OK,
        f"PermitRootLogin está como '{valor}'.",
    )


def _senha(config: dict[str, str]) -> Achado:
    valor = config.get("passwordauthentication", "yes").lower()
    if valor == "no":
        return Achado(
            "SSH aceita apenas chave",
            Gravidade.OK,
            "PasswordAuthentication está como 'no'.",
        )
    return Achado(
        "SSH aceita login por senha",
        Gravidade.MEDIA,
        "PasswordAuthentication está como 'yes'.",
        "Senhas são mais fáceis de adivinhar que chaves em ataques automáticos.",
        (
            "Crie uma chave no seu computador: ssh-keygen -t ed25519",
            "Copie para o servidor: ssh-copy-id usuario@servidor",
            "Teste entrar pela chave antes de desligar a senha.",
            f"Em {CAMINHO}, ponha: PasswordAuthentication no",
            "Reinicie o SSH: sudo systemctl restart ssh",
        ),
    )
