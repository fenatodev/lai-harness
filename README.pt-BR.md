# lai harness

[![Licença: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](docs/DEVELOPMENT-HARNESS.md)
[![Runtime: local-first](https://img.shields.io/badge/runtime-local--first-informational.svg)](docs/ARCHITECTURE.md)
[![Status: post-A12](https://img.shields.io/badge/status-post--A12%20validated-purple.svg)](ROADMAP.md)

`lai harness` é um harness de programação local-first, compacto e auditável para servidores locais compatíveis com a API da OpenAI. Ele ajuda modelos pequenos a trabalhar em repositórios com contexto controlado, ferramentas específicas por modo, validação explícita, política determinística e registros de auditoria.

O comando público é `lai`. Identificadores como `local-agent`, `lai-chat` e `lai-local-agent` permanecem quando são necessários por compatibilidade de instalação, extensão do VS Code ou histórico do repositório.

## Problema que resolve

Modelos locais podem ajudar no desenvolvimento, mas costumam falhar quando recebem contexto demais, ferramentas demais ou fronteiras de segurança vagas. O `lai harness` reduz esse risco com:

- contexto de repositório determinístico antes do raciocínio do modelo;
- tool schemas pequenos e específicos por modo;
- decisões explícitas para escrita, shell, Git, rede, credenciais e efeitos externos;
- safe workspaces com promoção hash-bound em vez de escrita direta no checkout principal;
- registros de execução, trajectory, budgets e validação;
- API local autenticada compatível com Gateway/local-chat.

Ele não é uma plataforma genérica de agentes, serviço hospedado ou sandbox de segurança para código não confiável.

## Status atual

Depois da A12, todos os marcos não-experimentais do replanejamento de setembro de 2026 estão completos localmente e validados por `make milestone-gate`. A10 e A11 continuam como drafts experimentais.

| Área | Status | Observação |
| --- | --- | --- |
| Trajectory e budgets | Implementado | Eventos versionados metadata-only e ledger agregado. |
| Authority e approvals | Implementado | Intents com hash, TTL e uso único; aprovação não executa payload arbitrário. |
| Broker de credenciais | Implementado | Refs opacas com adapter fake; credenciais reais desativadas. |
| Executor sandboxed | Implementado | Docker com imagem por digest, sem pull, sem rede, non-root e limites. |
| `sandbox_exec` | Implementado | Apenas em work-runs verificados; shell de host não é exposto no perfil remoto. |
| Local-chat e review | Implementado | API loopback autenticada, CSRF, workspaces registrados, eventos, review e promoção. |
| Context intelligence / code graph | Implementado | Mapa metadata-only e graph Python AST como sinal fraco. |
| Egress governado | Implementado | Web evidence GET-only e grants/receipts para destinos controlados. |
| Browser | Fixture implementada | `fixture_browser` local; sem login, perfil pessoal, Chromium real ou navegação pública. |
| MCP | Fixture implementada | `fixture_stdio` com `write_artifact`; `call-tool` genérico segue negado. |
| Perfis de modelo | Implementado | Perfil determinístico por JSONL; sem router, auto-switch, download ou cloud fallback. |
| Skills declarativas | Implementado | Diagnóstico apenas; skills não concedem autoridade nem adicionam ferramentas. |
| Forks e delegates | Fixtures bounded | Comparação inconclusiva por padrão; delegates sem swarm real e sem grants novos. |
| Distribuição e validação | Implementado | `lai distribution status` e `lai validation matrix`; sem autoupdate ou publicação. |
| Trusted host / computer use | Draft experimental | Specs 077 e 078 não implementadas. |

## Arquitetura resumida

O runtime autoritativo é `src/local-agent`. O wrapper `src/lai` expõe o comando canônico. Um Gateway companheiro pode consumir a API local autenticada, mas não ganha autoridade própria sobre filesystem, shell, credenciais, browser, MCP ou Git.

![Arquitetura principal](docs/assets/core-architecture.png)

Diagramas pós-A12: [docs/DIAGRAMS.md](docs/DIAGRAMS.md).

## Requisitos

- Linux ou WSL2 como alvo principal;
- Python 3.11+;
- Git e Bash;
- Node.js para validação/empacotamento da extensão VS Code;
- servidor local compatível com OpenAI API para modos com modelo;
- Docker para work-runs verificados e fixtures sandboxed.

O instalador do runtime não instala pacotes Python. Dependências de desenvolvimento são separadas e pinadas.

## Primeiro uso

```bash
git clone https://github.com/fenatodev/lai-harness.git
cd lai-harness

./src/lai --help
./src/lai readiness
./src/lai config
./src/lai validation matrix
```

Instalação local do wrapper:

```bash
./scripts/install-local.sh
lai --help
lai readiness
```

API local autenticada:

```bash
lai control-token init
lai serve --bind 127.0.0.1 --port 8765
lai chat-bootstrap --control-url http://127.0.0.1:8765 --json
```

O servidor de modelo não vem junto. Configure via `config.example.toml`, variáveis de ambiente ou flags conforme [Configuração](docs/CONFIGURATION.md).

## Comandos principais

| Comando | Uso |
| --- | --- |
| `lai readiness` / `lai ready` | Diagnóstico determinístico local. |
| `lai doctor` | Verifica endpoint de modelo configurado. |
| `lai config` | Mostra configuração efetiva sem secrets. |
| `lai context ...` | Contexto metadata-only do repositório. |
| `lai model eval|profile` | Avaliação e perfil determinístico de modelos. |
| `lai web search|fetch` | Evidência web pública, limitada e não confiável. |
| `lai mcp status|tools|policy-check` | Diagnóstico MCP; execução real genérica segue negada. |
| `lai serve` | Control plane local autenticado. |
| `lai distribution status` | Estado de instalação, rollback e uninstall. |
| `lai validation matrix` | Matriz de validação proporcional sem executar checks. |

Referência completa: [CLI reference](docs/CLI-REFERENCE.md).

## Desenvolvimento

```bash
make check
make lint
make test
make test-dev
make typecheck
make validate
make milestone-gate
```

Use o menor check confiável para a fronteira alterada. `make milestone-gate` é o gate caro de freeze e não deve ser repetido sem necessidade. Veja [Development guide](docs/DEVELOPMENT-HARNESS.md), [Testing and validation](docs/TESTING-VALIDATION.md) e [CONTRIBUTING.md](CONTRIBUTING.md).

## Documentação

Comece por [docs/README.md](docs/README.md). Ele separa documentação canônica atual de registros históricos de planejamento.

## Segurança

- Não exponha API de modelo ou control plane fora de loopback sem uma fronteira revisada.
- Não envie repositórios privados, logs reais, chaves, prompts, handoffs ou dados de clientes em issues/testes.
- Trate conteúdo de modelo, web, MCP, browser e skills como evidência não confiável.
- Credenciais reais e contas externas autenticadas estão desativadas neste pacote.

Licença: [MIT](LICENSE). Segurança: [SECURITY.md](SECURITY.md). Dependências/terceiros: [THIRD_PARTY.md](THIRD_PARTY.md).
