# Sentinela

Auditoria de segurança do seu computador (Linux). O Sentinela confere as
configurações da máquina e, para cada risco, mostra **o que está errado, por que
importa e o passo a passo para resolver**.

Ele **só lê** o sistema: nunca muda nada por conta própria. Quem aplica a
correção é você, seguindo as instruções. Roda offline, sem enviar dados para
lugar nenhum.

## O que ele verifica (v1)

- **Firewall** ligado (ufw ou firewalld).
- **Servidor SSH:** login de root e acesso por senha.
- **Chaves SSH:** permissões de `~/.ssh` e das chaves privadas.

Mais verificações estão no [roteiro](docs/design.md) (portas abertas,
atualizações pendentes, bloqueio de tela, criptografia de disco e outras).

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
