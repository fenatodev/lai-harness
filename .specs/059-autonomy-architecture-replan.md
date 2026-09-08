# Spec: Replanejamento arquitetural da autonomia LAI

## Metadata

- Mode: `full`
- Status: `complete`

## Goal

Concluir a entrega documental dos 23 itens do pedido de replanejamento nos dois projetos, fundamentada no código e sem implementar funcionalidades.

## Requirements

### REQ-001

Entregar diagnóstico do estado atual: Inventário por código nos dois repositórios; source 0.4.9/0.1.34, publicação não verificada.

### REQ-002

Entregar decisões antigas que precisam mudar: DEC-001–007 preservadas/reconciliadas; novas DEC-008–017 e alternativas explícitas.

### REQ-003

Entregar arquitetura-alvo: Harness único runtime/autoridade; Gateway chat; reuso incremental e contratos separados.

### REQ-004

Entregar três níveis formais de autonomia: Safe, Autonomous Sandbox e Full/Trusted como presets de grants; modo/canal/backend independentes.

### REQ-005

Entregar threat model atualizado: TM-01–16 com fronteiras, responsáveis, fixtures e gates.

### REQ-006

Entregar estratégia de sandbox: Executor inteiro Linux/WSL2, workspace independente, limits/mounts/egress; worktree não é sandbox.

### REQ-007

Entregar browser/computer use: Browser descartável antes de desktop/VM dedicado; efeitos críticos tipados ou handoff.

### REQ-008

Entregar estratégia mcp: Execução stdio útil em 072; HTTP autenticado depois; v1 atual continua não executável.

### REQ-009

Entregar credentials/secrets: Broker mínimo em 063, adapter limitado em 081, grants/audience/TTL/receipts e canários.

### REQ-010

Entregar estratégia de interface: Web chat no Gateway com auth local, workspace, diff/testes/ASK/cancel; bootstrap cedo.

### REQ-011

Entregar trajectory/observability: Journal causal, redaction antes de persistência, projections e readers compatíveis.

### REQ-012

Entregar budget architecture: Reservas antes de dispatch, auxiliares/filhos, ledger e limites OS reais.

### REQ-013

Entregar code graph/context evolution: AST primeiro, edges parciais/provenance, invalidação e comparação local; sem vector DB default.

### REQ-014

Entregar skills architecture: Capabilities/validação/contexto/saída declarados, loader legado e nenhuma autoridade por instalação.

### REQ-015

Entregar model routing: Perfis versionados e seleção manual primeiro; router condicionado a evidência repetida, sem default/cloud implícitos.

### REQ-016

Entregar subagent architecture: DAG/waves, scopes, ownership, budgets pai/filho, aggregation/conflict/cancel; serial possível.

### REQ-017

Entregar instalação/distribuição: Bootstrap A4 e graduação A12; install/configure/open/choose/chat; Linux/WSL2 confirmado.

### REQ-018

Entregar milestones em dependência: A0–A12 com dependências reais, ordem preferida, paralelo de preparação e gates de escrita.

### REQ-019

Entregar specs candidatas: 22 arquivos draft 060–081 com REQ/aceite/validação/non-goals; Gateway GW-C01–08 vinculados.

### REQ-020

Entregar critérios de aceite: Cada milestone/spec tem resultado observável, fixtures, testes, observabilidade, rollback, done e stop.

### REQ-021

Entregar riscos: Riscos herdados e RISK-008–022 com probabilidade/impacto, dono e condição de avanço.

### REQ-022

Entregar itens que não construir agora: Roadmap diferencia experimental/deferred/fora de escopo; sem Big Bang, marketplace, cloud/default-model ou GUI precoce.

### REQ-023

Entregar documentos oficiais atualizados: Plano/backlog/manifest/roadmaps/arquitetura/security/dev docs dos dois repos e história reconciliados.

## Acceptance Criteria

- Todos os 23 itens têm artefato canônico e conferência explícita.
- Planejamento/roadmap/manifest/backlog convergem em baseline, estados, dependências e próximo passo.
- Docs atuais e target não se contradizem; histórico de M1–M5 permanece distinguível.
- Somente Markdown e manifest de planejamento mudam; specs candidatas ficam draft e nenhum runtime é habilitado.

## Validation

- `REQ-001`: revisão de [Diagnóstico do estado atual](../docs/PROJECT-PLAN-2026-09.md#diagnóstico-do-baseline) e linha 01 da matriz de cobertura.
- `REQ-002`: revisão de [Decisões antigas que precisam mudar](../docs/DECISION-LOG-2026-09.md#reconciliação-das-decisões-anteriores) e linha 02 da matriz de cobertura.
- `REQ-003`: revisão de [Arquitetura-alvo](../docs/TARGET-ARCHITECTURE.md#composição-e-responsabilidades) e linha 03 da matriz de cobertura.
- `REQ-004`: revisão de [Três níveis formais de autonomia](../docs/TARGET-ARCHITECTURE.md#modelo-formal-de-autoridade) e linha 04 da matriz de cobertura.
- `REQ-005`: revisão de [Threat model atualizado](../docs/AUTONOMY-THREAT-MODEL.md#matriz-de-ameaças-e-aceites-obrigatórios) e linha 05 da matriz de cobertura.
- `REQ-006`: revisão de [Estratégia de sandbox](../docs/TARGET-ARCHITECTURE.md#sandbox-e-primitivas-úteis) e linha 06 da matriz de cobertura.
- `REQ-007`: revisão de [Browser/computer use](../docs/TARGET-ARCHITECTURE.md#browser-e-computer-use) e linha 07 da matriz de cobertura.
- `REQ-008`: revisão de [Estratégia MCP](../docs/TARGET-ARCHITECTURE.md#mcp-executável) e linha 08 da matriz de cobertura.
- `REQ-009`: revisão de [Credentials/secrets](../docs/TARGET-ARCHITECTURE.md#rede-credenciais-e-efeitos-externos) e linha 09 da matriz de cobertura.
- `REQ-010`: revisão de [Estratégia de interface](../docs/TARGET-ARCHITECTURE.md#interface-e-contrato-entre-projetos) e linha 10 da matriz de cobertura.
- `REQ-011`: revisão de [Trajectory/observability](../docs/TARGET-ARCHITECTURE.md#trajectory-artefatos-e-inspector) e linha 11 da matriz de cobertura.
- `REQ-012`: revisão de [Budget architecture](../docs/TARGET-ARCHITECTURE.md#budget-controller) e linha 12 da matriz de cobertura.
- `REQ-013`: revisão de [Code graph/context evolution](../docs/TARGET-ARCHITECTURE.md#contexto-memória-modelos-e-skills) e linha 13 da matriz de cobertura.
- `REQ-014`: revisão de [Skills architecture](../docs/TARGET-ARCHITECTURE.md#contexto-memória-modelos-e-skills) e linha 14 da matriz de cobertura.
- `REQ-015`: revisão de [Model routing](../docs/TARGET-ARCHITECTURE.md#contexto-memória-modelos-e-skills) e linha 15 da matriz de cobertura.
- `REQ-016`: revisão de [Subagent architecture](../docs/TARGET-ARCHITECTURE.md#fork-comparação-e-delegates) e linha 16 da matriz de cobertura.
- `REQ-017`: revisão de [Instalação/distribuição](../docs/TARGET-ARCHITECTURE.md#instalação-validação-e-evolução) e linha 17 da matriz de cobertura.
- `REQ-018`: revisão de [Milestones em dependência](../docs/EXECUTION-BACKLOG-2026-09.md#índice-de-milestones) e linha 18 da matriz de cobertura.
- `REQ-019`: revisão de [Specs candidatas](../docs/EXECUTION-BACKLOG-2026-09.md#como-executar) e linha 19 da matriz de cobertura.
- `REQ-020`: revisão de [Critérios de aceite](../docs/EXECUTION-BACKLOG-2026-09.md#índice-de-milestones) e linha 20 da matriz de cobertura.
- `REQ-021`: revisão de [Riscos](../docs/RISK-REGISTER-2026-09.md#riscos-da-transformação) e linha 21 da matriz de cobertura.
- `REQ-022`: revisão de [Itens que não construir agora](../docs/PROJECT-PLAN-2026-09.md#stop-rules-e-non-goals-globais) e linha 22 da matriz de cobertura.
- `REQ-023`: revisão de [Documentos oficiais atualizados](../docs/PROJECT-PLAN-2026-09.md#documentos-canônicos) e linha 23 da matriz de cobertura.
- Executar `make check`, parser real das specs novas e inventário separado da compatibilidade histórica, JSON/consistência do manifest, links locais/âncoras nos dois repos, publication scan documental aplicável e `git diff --check`.
- Inspecionar diff/arquivos não rastreados para confirmar ausência de implementação e preservar o workspace file preexistente.

## Context and Constraints

O usuário autorizou explicitamente edição/reconciliação documental e proibiu implementação. Nenhuma autorização de Git mutation/install/publication é inferida. As regras vigentes continuam em efeito.

## Non-Goals

Implementar runtime/UI, ativar qualquer spec 060–081, instalar dependências, mudar modelo, executar contas externas, commitar, publicar ou certificar isolamento sem testes próprios.

## Implementation Notes

Os nomes oficiais de setembro são mantidos para preservar referências; documentos target/threat/coverage complementam responsabilidades específicas. Revisar como um único pacote documental, com checkouts irmãos Harness/Gateway; os outros milestones ficam para implementação incremental depois da aprovação.

## Traceability

- `REQ-001` → [artefato](../docs/PROJECT-PLAN-2026-09.md#diagnóstico-do-baseline); [conferência](../docs/REPLAN-COVERAGE-2026-09.md).
- `REQ-002` → [artefato](../docs/DECISION-LOG-2026-09.md#reconciliação-das-decisões-anteriores); [conferência](../docs/REPLAN-COVERAGE-2026-09.md).
- `REQ-003` → [artefato](../docs/TARGET-ARCHITECTURE.md#composição-e-responsabilidades); [conferência](../docs/REPLAN-COVERAGE-2026-09.md).
- `REQ-004` → [artefato](../docs/TARGET-ARCHITECTURE.md#modelo-formal-de-autoridade); [conferência](../docs/REPLAN-COVERAGE-2026-09.md).
- `REQ-005` → [artefato](../docs/AUTONOMY-THREAT-MODEL.md#matriz-de-ameaças-e-aceites-obrigatórios); [conferência](../docs/REPLAN-COVERAGE-2026-09.md).
- `REQ-006` → [artefato](../docs/TARGET-ARCHITECTURE.md#sandbox-e-primitivas-úteis); [conferência](../docs/REPLAN-COVERAGE-2026-09.md).
- `REQ-007` → [artefato](../docs/TARGET-ARCHITECTURE.md#browser-e-computer-use); [conferência](../docs/REPLAN-COVERAGE-2026-09.md).
- `REQ-008` → [artefato](../docs/TARGET-ARCHITECTURE.md#mcp-executável); [conferência](../docs/REPLAN-COVERAGE-2026-09.md).
- `REQ-009` → [artefato](../docs/TARGET-ARCHITECTURE.md#rede-credenciais-e-efeitos-externos); [conferência](../docs/REPLAN-COVERAGE-2026-09.md).
- `REQ-010` → [artefato](../docs/TARGET-ARCHITECTURE.md#interface-e-contrato-entre-projetos); [conferência](../docs/REPLAN-COVERAGE-2026-09.md).
- `REQ-011` → [artefato](../docs/TARGET-ARCHITECTURE.md#trajectory-artefatos-e-inspector); [conferência](../docs/REPLAN-COVERAGE-2026-09.md).
- `REQ-012` → [artefato](../docs/TARGET-ARCHITECTURE.md#budget-controller); [conferência](../docs/REPLAN-COVERAGE-2026-09.md).
- `REQ-013` → [artefato](../docs/TARGET-ARCHITECTURE.md#contexto-memória-modelos-e-skills); [conferência](../docs/REPLAN-COVERAGE-2026-09.md).
- `REQ-014` → [artefato](../docs/TARGET-ARCHITECTURE.md#contexto-memória-modelos-e-skills); [conferência](../docs/REPLAN-COVERAGE-2026-09.md).
- `REQ-015` → [artefato](../docs/TARGET-ARCHITECTURE.md#contexto-memória-modelos-e-skills); [conferência](../docs/REPLAN-COVERAGE-2026-09.md).
- `REQ-016` → [artefato](../docs/TARGET-ARCHITECTURE.md#fork-comparação-e-delegates); [conferência](../docs/REPLAN-COVERAGE-2026-09.md).
- `REQ-017` → [artefato](../docs/TARGET-ARCHITECTURE.md#instalação-validação-e-evolução); [conferência](../docs/REPLAN-COVERAGE-2026-09.md).
- `REQ-018` → [artefato](../docs/EXECUTION-BACKLOG-2026-09.md#índice-de-milestones); [conferência](../docs/REPLAN-COVERAGE-2026-09.md).
- `REQ-019` → [artefato](../docs/EXECUTION-BACKLOG-2026-09.md#como-executar); [conferência](../docs/REPLAN-COVERAGE-2026-09.md).
- `REQ-020` → [artefato](../docs/EXECUTION-BACKLOG-2026-09.md#índice-de-milestones); [conferência](../docs/REPLAN-COVERAGE-2026-09.md).
- `REQ-021` → [artefato](../docs/RISK-REGISTER-2026-09.md#riscos-da-transformação); [conferência](../docs/REPLAN-COVERAGE-2026-09.md).
- `REQ-022` → [artefato](../docs/PROJECT-PLAN-2026-09.md#stop-rules-e-non-goals-globais); [conferência](../docs/REPLAN-COVERAGE-2026-09.md).
- `REQ-023` → [artefato](../docs/PROJECT-PLAN-2026-09.md#documentos-canônicos); [conferência](../docs/REPLAN-COVERAGE-2026-09.md).


## Validation Evidence

Revisão documental concluída em 2026-09-08; aprovação da arquitetura e implementação permanecem etapas posteriores.

- `make check` passou no Harness: sintaxe Python/JS/shell, JSON da extensão e `git diff --check`.
- `bash scripts/check-publication.sh` passou no Harness, incluindo documentos/specs novos e o manifest.
- `bash scripts/publication-scan.sh README.md SECURITY.md ROADMAP.md docs` passou no Gateway; `git diff --check` passou nos dois repositórios.
- Conferência local verificou 61 arquivos Markdown alterados/novos e 375 links locais, inclusive âncoras e referências entre os checkouts irmãos.
- Parser real `src/lai_specs.py`: 23 specs novas 059–081 válidas; 060–081 permanecem draft e não há spec ativa. 059 completa somente a entrega documental.
- Inspeção adicional das 81 specs constatou 19 incompatibilidades históricas com o parser atual, todas anteriores a 059 e com bytes inalterados em relação ao HEAD. Dívida registrada em RISK-006; não se alega aprovação global das specs históricas.
- Manifest JSON válido: 13 milestones A0–A12, dependências sem ciclos, estados/specs iguais ao backlog, 22 candidatas de implementação e 8 grupos Gateway; 23 itens conferidos na matriz de cobertura.
- Revisão cruzada corrigiu baseline 0.4.8/0.4.9, MCP declarativo versus executável, worktree versus sandbox, ASK terminal versus futuro approval, promoção já existente, dependências artificiais e duplicação de gates nos documentos.
- Inventário de alterações limitado a Markdown e manifest de planejamento. O arquivo de workspace preexistente foi preservado. Nenhum código, teste, configuração de runtime, modelo, dependência, commit, instalação ou publicação foi alterado/executado como implementação.
- Não foi executado milestone-gate: esta fatia é documental e não refaz a evidência histórica do freeze 058 nem comprova uma release nova.
