"""Fronteira com o sistema operacional.

Toda verificação recebe um `Ambiente` e só o usa para **ler**: arquivos,
permissões e a saída de comandos. Nada aqui altera o sistema. Nos testes,
um ambiente falso devolve conteúdos de mentira, então as verificações rodam
sem tocar na máquina de verdade.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class SaidaDeComando:
    """Resultado de rodar um comando."""

    # Falso quando o programa nem está instalado.
    encontrado: bool
    codigo: int
    texto: str


class Ambiente(Protocol):
    """O que uma verificação pode consultar do sistema (só leitura)."""

    @property
    def eh_root(self) -> bool: ...

    @property
    def lar(self) -> str: ...

    def ler(self, caminho: str) -> str | None: ...

    def modo(self, caminho: str) -> int | None: ...

    def listar(self, caminho: str) -> list[str]: ...

    def rodar(self, comando: list[str]) -> SaidaDeComando: ...


class Sistema:
    """`Ambiente` real, lendo o sistema de verdade a partir de `raiz`."""

    def __init__(self, raiz: str | Path = "/", *, lar: str | None = None) -> None:
        self._raiz = Path(raiz)
        self._lar = lar or str(Path.home())

    @property
    def eh_root(self) -> bool:
        return hasattr(os, "geteuid") and os.geteuid() == 0

    @property
    def lar(self) -> str:
        return self._lar

    def _alvo(self, caminho: str) -> Path:
        return self._raiz / caminho.lstrip("/")

    def ler(self, caminho: str) -> str | None:
        try:
            return self._alvo(caminho).read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None

    def modo(self, caminho: str) -> int | None:
        try:
            return self._alvo(caminho).stat().st_mode & 0o777
        except OSError:
            return None

    def listar(self, caminho: str) -> list[str]:
        try:
            return sorted(p.name for p in self._alvo(caminho).iterdir())
        except OSError:
            return []

    def rodar(self, comando: list[str]) -> SaidaDeComando:
        if shutil.which(comando[0]) is None:
            return SaidaDeComando(encontrado=False, codigo=127, texto="")
        try:
            r = subprocess.run(  # noqa: S603 - comandos fixos, sem entrada do usuário
                comando, capture_output=True, text=True, timeout=15, check=False
            )
        except (OSError, subprocess.SubprocessError):
            return SaidaDeComando(encontrado=True, codigo=1, texto="")
        return SaidaDeComando(encontrado=True, codigo=r.returncode, texto=r.stdout + r.stderr)
