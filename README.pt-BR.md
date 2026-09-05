# lai harness

<p align="center">
  <strong>Harness de programação local-first para LLMs pequenos.</strong><br>
  Ferramentas compactas, policy determinística, gates de evidência, auditoria e governança de release ao redor da inferência local.
</p>

<p align="center">
  <a href="https://github.com/fenatodev/lai-harness/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/fenatodev/lai-harness/actions/workflows/ci.yml/badge.svg?branch=main"></a>
  <a href="https://github.com/fenatodev/lai-harness/releases"><img alt="Release" src="https://img.shields.io/github/v/release/fenatodev/lai-harness?include_prereleases&label=release"></a>
  <img alt="Harness Score" src="https://img.shields.io/badge/Harness%20Score-L4%20%C2%B7%20100%2F108-2563eb">
  <a href="LICENSE"><img alt="Licença" src="https://img.shields.io/badge/license-MIT-0f766e"></a>
</p>

> **Release atual:** `v0.4.0-beta.18` · beta experimental · fluxo Linux/WSL-first · inferência local por endpoint OpenAI-compatible, desenvolvido com llama.cpp.

O lai harness foi criado para um problema específico: modelos locais pequenos perdem muita capacidade quando precisam carregar prompts gigantes, schemas genéricos e muitas rodadas de ferramentas. O projeto reduz esse overhead e coloca ao redor do modelo regras que não dependem da própria resposta do modelo: policy, specs, validação, auditoria, checkpoints e release protegido.

Ele complementa agentes cloud de alto contexto. O trabalho local fica rápido e delimitado; quando necessário, `project-handoff` entrega contexto compacto e verificável para outra sessão ou outro agente.

## Estado do projeto

| Área | Estado atual |
| --- | --- |
| Versão | `0.4.0-beta.18` |
| Maturidade do harness | L4 · Self-correcting · 100/108 (93%) |
| Runtime | Python stdlib; sem dependências Python no harness |
| Interfaces | CLI (`lai`) + extensão VS Code |
| Modelo local | HTTP OpenAI-compatible; desenvolvido com llama.cpp + GGUF do usuário |
| Controle remoto | Control plane autenticado em loopback; work isolado + promotion hashada para feature worktree dedicada, sem shell remoto nem escrita no checkout ativo |
| Release | `main` protegida, CI obrigatório, tag anotada, tag CI e verificação de digest |

Harness Score é usado como ratchet externo de maturidade do repositório, não como certificação de segurança.

## Arquitetura

![Arquitetura central do lai harness](docs/assets/core-architecture.png)

Princípios centrais:

- **menos overhead para o modelo:** ferramentas específicas por modo, contexto limitado, inspeção em lote e mapa semântico;
- **segurança determinística quando possível:** `ALLOW` / `ASK` / `DENY`, hooks, guards de branch e perfis remotos explícitos;
- **falhas viram evidência:** validação, acceptance/sanity gates, readiness, métricas, histórico de runs e auditoria;
- **release faz parte do harness:** feature branch, PR, CI, `ready_to_tag`, tag CI, artefato congelado, digest e handoff remoto.

Leia [Architecture](docs/ARCHITECTURE.md), [Development harness](docs/DEVELOPMENT-HARNESS.md) e [Security model](docs/SECURITY-MODEL.md).

## Principais capacidades

- ferramentas compactas e específicas por modo;
- `inspect` multi-arquivo e `patch` transacional;
- confinement de paths e checks explícitos de symlink para mutações;
- policy centralizada e `lai policy-check` determinístico;
- `.specs/` com requisitos `REQ-NNN` e inspeção por `lai spec`;
- contexto semântico, handoff persistente, checkpoints e resume com detecção de drift;
- métricas JSONL e auditoria forense versionadas, com retenção local configurável, histórico/export de runs e `lai readiness`;
- avaliação determinística de modelos locais com `lai model`;
- control plane `lai serve` autenticado e limitado a loopback;
- runs assíncronos remotos de leitura e work isolado (`implement` / `fix` / `refactor` / `ci-fix`) sob perfis sem shell;
- promotion explícita vinculada ao SHA-256 do patch, com revalidação e criação de `lai/promotion-*` em worktree Git dedicada;
- `release-check`, `release-pack`, `release-governance` e `project-handoff` determinísticos;
- hooks de desenvolvimento, ratchet mypy estrito nos módulos de guardrail, lock gerado dos sensores de desenvolvimento e gate L4 do Harness Score separado do runtime do produto.

## Início rápido

Requisitos: Python 3.11+, Git, ripgrep, VS Code compatível e um endpoint local OpenAI-compatible autenticado.

```bash
git clone https://github.com/fenatodev/lai-harness.git
cd lai-harness
./scripts/install-local.sh

mkdir -p ~/.config/lai
umask 077
python3 -c 'import secrets; print(secrets.token_urlsafe(32), end="")' \
  > ~/.config/lai/llama-api-key

lai doctor
lai readiness
lai config
```

No VS Code, alguns exemplos:

```text
@lai /plan planeje um teste de regressão focado
@lai /diagnose explique por que o CI está falhando
@lai /implement implemente a mudança mínima e valide
@lai /review revise minhas alterações Git atuais
```

Leia [Installation](docs/INSTALLATION.md) e [Quick start](docs/QUICKSTART.md) antes de usar modos que escrevem arquivos.

## Controle local e acesso móvel privado

O `lai serve` cria uma fronteira HTTP autenticada somente em loopback para runs assíncronos. Modos de leitura continuam sem shell; `implement`, `fix`, `refactor` e `ci-fix` trabalham em safe workspaces descartáveis e validam dentro de uma sandbox Docker. A beta.15 acrescenta uma fronteira separada de promotion: somente um run `succeeded`, com source baseline limpo e inalterado, gera uma proposta vinculada ao SHA-256 exato do patch. Após aprovação, o LAI revalida e aplica o patch em uma feature worktree `lai/promotion-*`; o checkout ativo continua intocado. Não há shell remoto genérico, commit, push, merge ou publicação de release por essa API.

```bash
lai control-token init
lai serve --bind 127.0.0.1 --port 8765
```

![Arquitetura de acesso móvel privado](docs/assets/private-mobile-access.png)

O `lai-gateway` mostrado acima é um **projeto companion separado**. Ele não faz parte da distribuição deste repositório. A função dele é oferecer PWA/Telegram privados mantendo o bearer token no PC e o control plane do harness em loopback.

## Release protegido e verificável

![Fluxo protegido de release do LAI](docs/assets/release-flow.png)

O fluxo exige:

1. feature branch + validação local;
2. PR com checks obrigatórios;
3. `main` limpa/sincronizada e `release-check=ready_to_tag`;
4. tag anotada apontando exatamente para a `main` validada;
5. tag CI + publication gates;
6. publicação do VSIX/release pack congelado;
7. verificação remota de branch protection, Release e digest;
8. handoff convergente sem ações manuais pendentes.

```bash
lai release-check --target 0.4.0-beta.18 --json
lai release-pack --target 0.4.0-beta.18 --with-vsix --json
lai release-governance --target 0.4.0-beta.18 --remote --json
lai project-handoff --target 0.4.0-beta.18 --remote --json
```

## Segurança

O lai harness **não é uma sandbox**. As ferramentas de arquivo ficam confinadas à raiz do repositório e a inspeção Git dedicada é somente leitura, mas `bash` local permitido ainda executa com as permissões do usuário. A policy governa ações; ela não substitui isolamento do sistema operacional.

O controle remoto é mais estreito por design. Runs de leitura recebem apenas ferramentas de inspeção. Runs de work recebem ferramentas de arquivo confinadas ao workspace + `validate`, trabalham numa cópia isolada e retornam evidência limitada. Promotion é uma ação determinística separada: aprovação vinculada ao hash do patch, nova validação `full` na sandbox, verificação de SHA/branch/estado limpo da origem, criação de feature worktree dedicada e verificação do hash após `git apply`. O checkout ativo não é editado. A sandbox continua sem rede, HOME do host ou socket Docker.

Use modos de escrita somente em workspaces confiáveis, com backup ou descartáveis, sob conta de menor privilégio. Nunca publique chaves, tokens de controle, estados, métricas, auditoria, modelos ou handoffs reais.

## Limitações atuais

- fluxo Linux/WSL-first;
- comportamento depende fortemente do modelo/prompt;
- modelos locais podem produzir afirmações incorretas e precisam de grounding/validação;
- policy de `bash` não é containment;
- ainda não há instalador automático de modelo nem extensão no Marketplace;
- promotion cria uma feature worktree local dedicada; commit, push, PR e merge continuam fora dessa capability e exigirão cortes próprios;
- a validação de work remoto exige Docker e a imagem de sandbox já presente localmente; o harness nunca faz pull automático.

## Documentação visual

Os diagramas são apoio de documentação; código, testes, policy e security model são a fonte autoritativa. `docs/assets/visual-assets.json` registra a versão do LAI em que os visuais foram revisados, e o CI exige que esse marker acompanhe a versão do produto. Assim, toda nova versão força revisão explícita das arquiteturas.

## Documentação e histórico

- [Roadmap](ROADMAP.md)
- [Changelog](CHANGELOG.md)
- [Beta readiness](docs/BETA-READINESS.md)
- [Release governance](docs/RELEASE-GOVERNANCE.md)
- [Development journey](docs/DEVELOPMENT-JOURNEY.md)
- [Safe workspaces](docs/SAFE-WORKSPACES.md)
- [Project handoff](docs/PROJECT-HANDOFF.md)
- [Runtime records](docs/RUNTIME-RECORDS.md)

O código original do LAI usa [MIT](LICENSE). VS Code, llama.cpp, modelos, GGUF e templates permanecem sob termos próprios e não são redistribuídos. Veja [Third-party software](THIRD_PARTY.md).

---

<p align="center"><strong>IA local. Governada. Reprodutível. Auditável.</strong></p>
