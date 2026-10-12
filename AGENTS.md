# Sentinela — guia para agentes

Auditoria de segurança do PC (Linux). O app **só lê** o sistema: para cada
risco, mostra o que encontrou e o passo a passo para resolver. **Nunca altera
nada** — não executa correção, não escreve em arquivo de config, não roda
comando que muda estado.

Detalhes e decisões ficam em [docs/design.md](docs/design.md) — leia antes de mexer.

## Comandos

```bash
. .venv/bin/activate   # ambiente virtual (crie com: python3 -m venv .venv && pip install -e . ruff pytest)
ruff check .           # lint + complexidade (máx. 6)
ruff format            # formatação
pytest                 # testes
sentinela              # roda a auditoria no terminal
```

Uma tarefa só está pronta quando `ruff check .`, `ruff format --check .` e
`pytest` passam sem erro.

## Regras que valem sempre

1. **Só leitura.** Verificação nunca muda o sistema. Comandos e leituras passam
   pelo `Ambiente`; nada de `subprocess` solto numa verificação.
2. **Toda verificação recebe `Ambiente`** (`sentinela/nucleo/ambiente.py`) e
   devolve `list[Achado]`. Assim o teste injeta um `AmbienteFalso` e roda sem
   tocar na máquina de verdade.
3. **Regra nova = arquivo novo** em `sentinela/verificacoes/`, registrado em
   `sentinela/nucleo/analise.py`, **com teste** em `tests/`.
4. **Todo achado tem passo a passo** (`solucao`) quando pede ação, escrito para
   leigo. Gravidade honesta: não assuste à toa nem minimize risco real.
5. **Degrade com elegância:** se faltar permissão ou o programa não existir,
   devolva um achado `INFO` explicando, nunca um erro.
6. **Limites de qualidade não se negociam** (complexidade ≤ 6): divida a função,
   não aumente o limite nem use `noqa` sem motivo claro e comentado.
7. **Nada de rede nem telemetria.** O Sentinela roda offline; não manda dados
   para lugar nenhum.

## Onde fica cada coisa

```
sentinela/
  nucleo/        modelos (Achado, Gravidade), Ambiente, análise/nota
  verificacoes/  uma verificação por arquivo (firewall, ssh, chaves_ssh...)
  cli.py         saída no terminal
tests/           pytest; AmbienteFalso em conftest.py
docs/            design.md (fonte da verdade)
```

## Idioma

Código, comentários, commits e documentação em **português do Brasil**.
Commits em Conventional Commits (`feat:`, `fix:`, `docs:`...).

## Quando errar

Se cometer um erro que pode se repetir, não conserte só o caso: acrescente a
proteção (um teste, uma regra de lint ou uma linha aqui / em `docs/`).
