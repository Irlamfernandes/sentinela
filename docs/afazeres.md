# Sentinela — o que ainda falta

Lista de tarefas, da mais útil para a menos urgente. O que já está pronto fica
em [design.md](design.md).

## 1. Interface e saída

- [ ] **Interface gráfica (GTK4 + libadwaita):** tela com a nota, lista de
      problemas por gravidade e, em cada um, "por que importa" e o passo a passo.
- [ ] **Exportar relatório em HTML** (para guardar ou compartilhar).
- [ ] **Saída em JSON** (`sentinela --json`) para usar em scripts.
- [ ] **Opções de linha de comando** (`argparse`): `--tudo` (mostrar também os
      itens OK), `--categoria <nome>`, `--version`, `--help`.
- [ ] **Pedir root só quando precisa:** rodar as verificações que exigem
      permissão via `pkexec`, com o diálogo padrão do sistema, em vez de pedir
      para rodar tudo com `sudo`.

## 2. Novas verificações

- [ ] **Validade de senha** (`login.defs`: `PASS_MAX_DAYS`).
- [ ] **Contas com senha vazia** (`/etc/shadow`; precisa de root).
- [ ] **`umask` padrão** muito permissivo.
- [ ] **Opções de montagem** de `/tmp` e `/home` (`nosuid`, `nodev`, `noexec`).
- [ ] **Sincronização de horário (NTP)** ativa — log com hora errada atrapalha
      investigação.
- [ ] **Diretivas `Include` do SSH** (hoje só lemos o `sshd_config` principal).
- [ ] **Snap/Flatpak desatualizados.**
- [ ] **Repositórios de terceiros (PPAs)** de origem duvidosa.
- [ ] **Senha no GRUB** (impede burlar a inicialização).
- [ ] **Lista de usuários na tela de login** do GDM visível.
- [ ] **Modo "completo" opcional:** varredura de SUID/SGID e arquivos sem dono
      em todo o disco (lento e exige root — fora do modo padrão de propósito).

## 3. Distribuição

- [ ] **Instalação fácil:** publicar como pacote (pipx) e, depois, no **Flathub**.
- [ ] **Metadados no `pyproject.toml`:** autor, URL do projeto, classifiers.
- [ ] **Página de ajuda / man page.**

## 4. Qualidade e infraestrutura

- [ ] **Cobertura de testes** no CI (pytest-cov) e um teste por tipo de achado.
- [ ] **Checagem de tipos** (mypy) no CI.
- [ ] **gitleaks** no CI (varredura de segredos), como no projeto Despensa.
- [ ] **Hook de pré-commit** rodando ruff e pytest antes de cada commit.
- [ ] **CHANGELOG** e guia de contribuição.

## Ideias para o futuro

- [ ] Guardar o resultado de cada varredura para **mostrar o que mudou** desde a
      última vez.
- [ ] **Perfis** (ex.: "notebook", "servidor") que ajustam o que é esperado.
- [ ] Suporte a **outras distribuições** além do Ubuntu/Debian (Fedora, Arch).
