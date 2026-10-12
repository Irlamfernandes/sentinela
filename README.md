# Sentinela

Auditoria de segurança do seu computador (Linux). O Sentinela confere as
configurações da máquina e, para cada risco, mostra **o que está errado, por que
importa e o passo a passo para resolver**.

Ele **só lê** o sistema: nunca muda nada por conta própria. Quem aplica a
correção é você, seguindo as instruções. Roda offline, sem enviar dados para
lugar nenhum.

## O que ele verifica

- **Atualizações:** pacotes de segurança pendentes, atualização automática e se
  a versão do Ubuntu ainda tem suporte.
- **Firewall** ligado (ufw ou firewalld).
- **Portas abertas** para a rede e **serviços** (CUPS, Avahi) ligados à toa.
- **Proteções:** AppArmor, Fail2ban, auditd.
- **Kernel:** ASLR, restrição de ptrace e outros ajustes de segurança.
- **Contas e senhas:** poder de root duplicado, `sudo` sem senha, tamanho mínimo.
- **Servidor SSH:** login de root e acesso por senha.
- **Chaves SSH** e **credenciais no home** (AWS, Git, Docker, etc.) expostas.
- **Arquivos sensíveis:** permissões de `/etc/shadow`, `passwd`, `sudoers` e
  arquivos graváveis por todos no home.
- **Sessão:** bloqueio de tela e login automático.
- **Disco:** criptografia, Secure Boot e dumps de memória.
- **Inicialização**, **histórico de tentativas de login** e **firmware**.

Detalhes e o que ficou para depois estão no [design](docs/design.md). Algumas
verificações mostram mais informação quando você roda com `sudo`.

## Como usar

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
sentinela
```

Saída de exemplo:

```
Sentinela — auditoria de segurança do PC
Nota de segurança: 80/100
1 ponto(s) para revisar:

[Alto] Firewall instalado, mas desligado (ufw)
  O ufw está instalado, porém inativo.
  Risco: Sem firewall, qualquer serviço que esteja escutando fica exposto na rede.
  Como resolver:
    - Abra o terminal.
    - Ligue o firewall: sudo ufw enable
    - Confira o estado: sudo ufw status
```

Uma interface gráfica (GTK4) virá depois.

## Desenvolvimento

```bash
pip install ruff pytest
ruff check .
ruff format --check .
pytest
```

As regras do projeto estão em [AGENTS.md](AGENTS.md) e os detalhes de design em
[docs/design.md](docs/design.md).

## Licença

MIT.
