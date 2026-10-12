"""Contas de usuário, poder de administrador e política de senha."""

from __future__ import annotations

from sentinela.nucleo.ambiente import Ambiente
from sentinela.nucleo.modelos import Achado, Gravidade

ID = "contas"
NOME = "Contas e senhas"
CATEGORIA = "Acesso"


def verificar(amb: Ambiente) -> list[Achado]:
    passwd = amb.ler("/etc/passwd") or ""
    return [_outros_root(passwd), _sudo_sem_senha(amb), _tamanho_minimo_de_senha(amb)]


def _outros_root(passwd: str) -> Achado:
    donos = [linha.split(":")[0] for linha in passwd.splitlines() if _uid_zero(linha)]
    extras = [nome for nome in donos if nome != "root"]
    if not extras:
        return Achado(
            "Só o root tem poder total",
            Gravidade.OK,
            "Nenhuma outra conta usa UID 0.",
        )
    return Achado(
        "Outra conta com poder total (UID 0)",
        Gravidade.CRITICA,
        f"Além do root, têm UID 0: {', '.join(extras)}.",
        "Uma segunda conta com UID 0 é poder de root escondido, muito usado por invasores.",
        (
            "Confirme se você criou essa(s) conta(s).",
            "Se não reconhece, isso é sinal de invasão: investigue antes de qualquer coisa.",
        ),
    )


def _uid_zero(linha: str) -> bool:
    campos = linha.split(":")
    return len(campos) >= 3 and campos[2] == "0"


def _sudo_sem_senha(amb: Ambiente) -> Achado:
    texto = amb.ler("/etc/sudoers") or ""
    linhas = [
        linha.strip()
        for linha in texto.splitlines()
        if "NOPASSWD" in linha and not linha.strip().startswith("#")
    ]
    if not linhas:
        return Achado(
            "Sudo sempre pede senha",
            Gravidade.OK,
            "Nenhuma regra NOPASSWD em /etc/sudoers.",
        )
    return Achado(
        "Sudo sem senha configurado",
        Gravidade.MEDIA,
        f"{len(linhas)} regra(s) NOPASSWD em /etc/sudoers.",
        "Quem chegar à sua sessão vira root sem precisar digitar nada.",
        (
            "Edite com: sudo visudo",
            "Remova as linhas com NOPASSWD que você não precisa.",
        ),
    )


def _tamanho_minimo_de_senha(amb: Ambiente) -> Achado:
    texto = amb.ler("/etc/security/pwquality.conf") or ""
    minimo = _ler_minlen(texto)
    if minimo is not None and minimo >= 12:
        return Achado(
            "Tamanho mínimo de senha adequado",
            Gravidade.OK,
            f"pwquality exige ao menos {minimo} caracteres.",
        )
    return Achado(
        "Senha sem tamanho mínimo forte",
        Gravidade.BAIXA,
        "O pwquality não exige pelo menos 12 caracteres.",
        "Senhas curtas são adivinhadas rápido.",
        (
            "Edite /etc/security/pwquality.conf (como root).",
            "Defina: minlen = 12",
        ),
    )


def _ler_minlen(texto: str) -> int | None:
    for linha in texto.splitlines():
        limpa = linha.split("#", 1)[0]
        if "minlen" in limpa and "=" in limpa:
            valor = limpa.split("=", 1)[1].strip()
            return int(valor) if valor.isdigit() else None
    return None
