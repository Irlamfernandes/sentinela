# Sentinela — documento de design

Auditoria de segurança do computador (Linux). O Sentinela **lê** as
configurações do sistema e, para cada risco, mostra o que encontrou, por que
importa e o **passo a passo** para resolver. Ele **nunca altera o sistema**: só
diagnostica. A correção é sempre feita pela pessoa, seguindo as instruções.

Feito primeiro para Ubuntu/GNOME (o que o dono usa), com o código pronto para
receber outras distribuições depois.

## Princípios

- **Só leitura.** Nenhuma verificação muda o sistema. Isso é seguro e
  educativo: a pessoa entende e aplica a correção.
- **Tudo de graça e local.** Sem serviço pago, sem nuvem, sem telemetria. Roda
  offline.
- **Linguagem para leigo.** Cada achado tem título claro, o risco em uma frase
  e os passos de correção prontos para colar no terminal.
- **Honestidade na gravidade.** Não inventar alarme nem esconder risco real.
- **Degrada com elegância.** Faltou permissão ou o programa não existe? Vira um
  achado informativo, não um erro.

## Arquitetura

Quatro peças, com dependência num só sentido:

```
cli / interface ──► nucleo.analise ──► verificacoes ──► nucleo.ambiente + nucleo.modelos
```

| Peça                 | Responsabilidade                                                        |
| -------------------- | ----------------------------------------------------------------------- |
| `nucleo.modelos`     | `Gravidade` e `Achado` (o resultado de uma verificação)                 |
| `nucleo.ambiente`    | Fronteira com o SO: ler arquivo, permissão, pasta e saída de comando    |
| `verificacoes/`      | Uma verificação por arquivo; recebe `Ambiente`, devolve `list[Achado]`  |
| `nucleo.analise`     | Roda todas, calcula a nota e ordena os problemas                        |
| `cli` / interface    | Mostra o relatório                                                      |

**Por que `Ambiente`:** toda leitura do sistema passa por ele. No app é o
`Sistema` real; no teste é o `AmbienteFalso`, que devolve conteúdos de mentira.
Assim cada verificação é testada com pytest, sem tocar na máquina de verdade —
a mesma ideia do `Banco` do projeto Despensa.

## Gravidade e nota

| Gravidade | Penalidade na nota |
| --------- | ------------------ |
| Crítico   | 40                 |
| Alto      | 20                 |
| Médio     | 10                 |
| Baixo     | 4                  |
| Info / OK | 0                  |

A nota começa em 100 e cada achado desconta a penalidade da sua gravidade
(mínimo 0). É um resumo para orientar, não uma medida exata.

## Verificações

### Prontas (v1)

- **Firewall** — ufw ou firewalld ativo.
- **Servidor SSH** — `PermitRootLogin` e `PasswordAuthentication` no
  `sshd_config` (só o arquivo principal; `Include` fica para depois).
- **Chaves SSH** — permissões de `~/.ssh` (700) e das chaves privadas (600).

### Planejadas (todas de leitura, sem custo)

- **Portas abertas** — serviços escutando (`ss -tulpn`); destacar os abertos
  para fora.
- **Atualizações de segurança** pendentes (`apt`) e se `unattended-upgrades`
  está ativo.
- **Programas que iniciam com o sistema** — serviços do systemd habilitados e
  autostart do usuário (`~/.config/autostart`).
- **Contas e acesso** — UID 0 além de root; membros do grupo sudo; (com
  permissão) contas sem senha.
- **Bloqueio de tela** automático (`gsettings` do GNOME).
- **Criptografia de disco** (LUKS via `lsblk`) e Secure Boot (`mokutil`).
- **Logins recentes e falhas** (`last` / `lastb`; `lastb` pede root).
- **Arquivos sensíveis** com permissão frouxa no home (world-writable, chaves
  legíveis por outros).
- **Firmware** desatualizado (`fwupdmgr get-updates`).

Cada uma só entra com teste e indicando quando precisa de root (degradando para
`INFO` se não tiver).

## Permissões (root)

O app roda como usuário comum. A maioria das verificações não precisa de root.
As que precisam (ex.: regras de firewall, `lastb`) devem, sem root, devolver um
achado `INFO` dizendo o que não deu para checar e como rodar com permissão —
nunca falhar. A interface vai poder pedir a senha pelo diálogo padrão do sistema
só nessas horas (fase futura).

## Interface

- **v1:** terminal (`sentinela`), com nota e lista de problemas.
- **Depois:** GTK4 + libadwaita (cara de app nativo do GNOME, modo escuro
  automático), distribuível pelo Flathub para compartilhar. Exportar relatório
  em HTML.

A interface só chama `nucleo.analise.executar` e desenha o resultado; nenhuma
regra de segurança mora nela.

## Tecnologia

- **Python puro**, sem dependências de execução.
- **Harness:** ruff (lint + formatação + complexidade ≤ 6), pytest, CI no
  GitHub Actions. Documentação em `docs/` como fonte da verdade.

## Pontos em aberto

1. Ordem de implementação das verificações planejadas.
2. Quando começar a interface GTK (sugestão: depois de ~8 verificações).
