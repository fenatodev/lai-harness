# Conferência dos 23 itens — replanejamento LAI

Revisão documental de 2026-09-08. Esta matriz confere a entrega inicial solicitada, não declara funcionalidades implementadas nem aprovação do plano. A spec [059](../.specs/059-autonomy-architecture-replan.md) rastreia os mesmos 23 requisitos. Todas as specs de implementação permanecem draft.

## Cobertura do pedido original

| Item / requisito | Entrega solicitada | Evidência canônica | Conferência |
| --- | --- | --- | --- |
| 01 / REQ-001 | Diagnóstico do estado atual | [Inventário por código nos dois repositórios; source 0.4.9/0.1.34, publicação não verificada.](PROJECT-PLAN-2026-09.md#diagnóstico-do-baseline) | Coberto no planejamento |
| 02 / REQ-002 | Decisões antigas que precisam mudar | [DEC-001–007 preservadas/reconciliadas; novas DEC-008–017 e alternativas explícitas.](DECISION-LOG-2026-09.md#reconciliação-das-decisões-anteriores) | Coberto no planejamento |
| 03 / REQ-003 | Arquitetura-alvo | [Harness único runtime/autoridade; Gateway chat; reuso incremental e contratos separados.](TARGET-ARCHITECTURE.md#composição-e-responsabilidades) | Coberto no planejamento |
| 04 / REQ-004 | Três níveis formais de autonomia | [Safe, Autonomous Sandbox e Full/Trusted como presets de grants; modo/canal/backend independentes.](TARGET-ARCHITECTURE.md#modelo-formal-de-autoridade) | Coberto no planejamento |
| 05 / REQ-005 | Threat model atualizado | [TM-01–16 com fronteiras, responsáveis, fixtures e gates.](AUTONOMY-THREAT-MODEL.md#matriz-de-ameaças-e-aceites-obrigatórios) | Coberto no planejamento |
| 06 / REQ-006 | Estratégia de sandbox | [Executor inteiro Linux/WSL2, workspace independente, limits/mounts/egress; worktree não é sandbox.](TARGET-ARCHITECTURE.md#sandbox-e-primitivas-úteis) | Coberto no planejamento |
| 07 / REQ-007 | Browser/computer use | [Browser descartável antes de desktop/VM dedicado; efeitos críticos tipados ou handoff.](TARGET-ARCHITECTURE.md#browser-e-computer-use) | Coberto no planejamento |
| 08 / REQ-008 | Estratégia MCP | [Execução stdio útil em 072; HTTP autenticado depois; `fixture_stdio` existe e MCP genérico continua negado.](TARGET-ARCHITECTURE.md#mcp-executável) | Coberto no planejamento |
| 09 / REQ-009 | Credentials/secrets | [Broker mínimo em 063, adapter limitado em 081, grants/audience/TTL/receipts e canários.](TARGET-ARCHITECTURE.md#rede-credenciais-e-efeitos-externos) | Coberto no planejamento |
| 10 / REQ-010 | Estratégia de interface | [Web chat no Gateway com auth local, workspace, diff/testes/ASK/cancel; bootstrap cedo.](TARGET-ARCHITECTURE.md#interface-e-contrato-entre-projetos) | Coberto no planejamento |
| 11 / REQ-011 | Trajectory/observability | [Journal causal, redaction antes de persistência, projections e readers compatíveis.](TARGET-ARCHITECTURE.md#trajectory-artefatos-e-inspector) | Coberto no planejamento |
| 12 / REQ-012 | Budget architecture | [Reservas antes de dispatch, auxiliares/filhos, ledger e limites OS reais.](TARGET-ARCHITECTURE.md#budget-controller) | Coberto no planejamento |
| 13 / REQ-013 | Code graph/context evolution | [AST primeiro, edges parciais/provenance, invalidação e comparação local; sem vector DB default.](TARGET-ARCHITECTURE.md#contexto-memória-modelos-e-skills) | Coberto no planejamento |
| 14 / REQ-014 | Skills architecture | [Capabilities/validação/contexto/saída declarados, loader legado e nenhuma autoridade por instalação.](TARGET-ARCHITECTURE.md#contexto-memória-modelos-e-skills) | Coberto no planejamento |
| 15 / REQ-015 | Model routing | [Perfis versionados e seleção manual primeiro; router condicionado a evidência repetida, sem default/cloud implícitos.](TARGET-ARCHITECTURE.md#contexto-memória-modelos-e-skills) | Coberto no planejamento |
| 16 / REQ-016 | Subagent architecture | [DAG/waves, scopes, ownership, budgets pai/filho, aggregation/conflict/cancel; serial possível.](TARGET-ARCHITECTURE.md#fork-comparação-e-delegates) | Coberto no planejamento |
| 17 / REQ-017 | Instalação/distribuição | [Bootstrap A4 e graduação A12; install/configure/open/choose/chat; Linux/WSL2 confirmado.](TARGET-ARCHITECTURE.md#instalação-validação-e-evolução) | Coberto no planejamento |
| 18 / REQ-018 | Milestones em dependência | [A0–A12 com dependências reais, ordem preferida, paralelo de preparação e gates de escrita.](EXECUTION-BACKLOG-2026-09.md#índice-de-milestones) | Coberto no planejamento |
| 19 / REQ-019 | Specs candidatas | [22 arquivos draft 060–081 com REQ/aceite/validação/non-goals; Gateway GW-C01–08 vinculados.](EXECUTION-BACKLOG-2026-09.md#como-executar) | Coberto no planejamento |
| 20 / REQ-020 | Critérios de aceite | [Cada milestone/spec tem resultado observável, fixtures, testes, observabilidade, rollback, done e stop.](EXECUTION-BACKLOG-2026-09.md#índice-de-milestones) | Coberto no planejamento |
| 21 / REQ-021 | Riscos | [Riscos herdados e RISK-008–022 com probabilidade/impacto, dono e condição de avanço.](RISK-REGISTER-2026-09.md#riscos-da-transformação) | Coberto no planejamento |
| 22 / REQ-022 | Itens que não construir agora | [Roadmap diferencia experimental/deferred/fora de escopo; sem Big Bang, marketplace, cloud/default-model ou GUI precoce.](PROJECT-PLAN-2026-09.md#stop-rules-e-non-goals-globais) | Coberto no planejamento |
| 23 / REQ-023 | Documentos oficiais atualizados | [Plano/backlog/manifest/roadmaps/arquitetura/security/dev docs dos dois repos e história reconciliados.](PROJECT-PLAN-2026-09.md#documentos-canônicos) | Coberto no planejamento |

## Conferência de consistência entre os documentos

| Tema | Regra reconciliada |
| --- | --- |
| Baseline | Source Harness 0.4.9/Gateway 0.1.34; 0.4.8 é baseline integrado histórico, não versão atual do Harness |
| Release | Spec 058 prova freeze local histórico; esta revisão não verifica publicação/CI remotos e não publica |
| Estado | Arquitetura/security operacionais descrevem código atual; target/threat model/presets são proposta |
| Autoridade | Grants e enforcement no Harness; Gateway, skill, modelo e delegates não ampliam policy |
| Sandbox | Cópia/worktree e validate atual em Docker não são contenção de todo executor |
| Compatibilidade | v1 shell/MCP false permanece; execução nova exige negociação por canal/backend |
| Dependências | A1/A2 antes de A3; escrita A4 depois de A3; broker antes de auth externa; graph/router/delegates não são bloqueios artificiais |
| Sequenciamento | IDs 060–081 são identidade, não ordem; 081 está em A6; A12 pode fechar antes de host/GUI |
| Plataforma | Linux/WSL2 primeiro, Windows nativo depois, conforme resposta do usuário |
| Histórico | M1–M4 completos; M5 completo localmente; M1 workplan/M3 design identificados como históricos |
| Segurança | Full não promete contenção impossível; checkpoint não replay; rollback não desfaz efeitos externos |
| Validação | Esta entrega é documental; checks de syntax/links/specs/manifest/publication scan pertinentes. Matriz/gates runtime só mudam na spec 080 |
| Identidade | Produto lai harness, comando lai, checkout lai-local-agent; nenhum rename técnico ou nova daemon |
| Escopo | Nenhuma feature, dependência, modelo, release ou configuração de autoridade modificada |

A varredura adicional encontrou 19 specs históricas incompatíveis com o parser atual, todas inativas e idênticas ao HEAD. Essa dívida está registrada em RISK-006; não é confundida com validação das 23 specs novas nem reescreve evidências antigas.

## Evidência desta revisão

A conclusão e os resultados efetivamente executados são registrados na seção Validation Evidence da spec 059. Validação documental não substitui os testes futuros dos milestones. Links entre repositórios presumem checkouts irmãos, conforme documentado no plano.
