# lai harness execution backlog, setembro de 2026

Estado pós-A12: backlog histórico reconciliado. A0–A9 e A12 estão completos; A10/A11 permanecem experimentais. [Plano](PROJECT-PLAN-2026-09.md) · [Arquitetura atual](ARCHITECTURE.md) · [Threat model](AUTONOMY-THREAT-MODEL.md) · [Manifest](PLANNING-MANIFEST-2026-09.json).

## Baseline e histórico preservado

Harness 0.4.9 no código; Gateway 0.1.34. M1/054 structured context, M2/055 mobile read-only, M3/056 MCP design e M4/057 eval estão completos conforme suas evidências. M5/058 é freeze local completo, publicação não verificada nesta revisão. Ver specs [054](../.specs/054-structured-context-dogfood.md), [055](../.specs/055-mobile-readonly-dogfood-loop.md), [056](../.specs/056-mcp-allowlist-design.md), [057](../.specs/057-model-eval-evidence-expansion.md) e [058](../.specs/058-v049-release-freeze.md). Seus limites se referem às entregas históricas, não proíbem os novos milestones.

## Como executar

A0 é entrega documental; A1–A12 são intenções. Os IDs A evitam reutilizar M1–M5. Prioridade não é dependência técnica: graph, perfis e delegates não bloqueiam sandbox/chat/host sem motivo. Os números de specs são identidades, não ordem absoluta; 081 pertence a A6.

Sequência preferida: A0→A1→A2→A3→A4; depois A5, A6, A7, A8 e A9 conforme o gargalo observado; A10/A11 são experimentais posteriores. A12 pode graduar a distribuição do chat sem esperar GUI. Preparação de A4 pode ocorrer após A1/A2, mas escrita depende de A3. A5 pode ser desenhado após A1. A9 depende de supervisor/grants/boundary/chat, não de graph/router. A10 não depende de delegates.

Uma spec ativa por repositório durante implementação; drafts não ativam behavior. No mesmo repo, desenho/fixtures propostas podem ser preparados em paralelo, implementação ocorre em fatias sequenciais com ownership. Gateway pode ter sua spec própria ligada ao mesmo contrato; ver [candidatos GW-C01–08](../../lai-gateway/docs/PROJECT-PLAN-2026-09.md).

Cada contrato abaixo explicita problema, objetivo/motivação, arquitetura, requisitos, segurança, UX, aceite, fixtures/testes, observabilidade, rollback, done, non-goals e stop. Antes de ativar uma spec, definir limites quantitativos (tempo/bytes/calls/recursos) e comando focado a partir do baseline local; ausência de medição não vira aprovação por impressão. Testes futuros descritos aqui não foram executados neste planejamento.

## Índice de milestones

| ID | Entrega | Dependências obrigatórias para fechar | Specs | Estado |
| --- | --- | --- | --- | --- |
| A0 | baseline-and-replan | nenhuma | 59 | complete |
| A1 | trajectory-and-budgets | A0 | 60, 61 | complete |
| A2 | authority-and-credentials | A1 | 62, 63 | complete |
| A3 | sandbox-and-primitives | A2 | 64, 65 | complete |
| A4 | local-web-chat | A1, A2, A3 | 66, 67, 68 | complete |
| A5 | deterministic-code-graph | A1 | 69 | complete |
| A6 | network-browser-external-effects | A2, A3, A4 | 70, 81, 71 | complete |
| A7 | mcp-execution | A2, A3, A4 | 72 | complete |
| A8 | model-profiles-and-skills | A1, A2 | 73, 74 | complete |
| A9 | fork-and-delegates | A1, A2, A3, A4 | 75, 76 | complete |
| A10 | trusted-host | A1, A2, A3, A4, A6 | 77 | experimental |
| A11 | computer-use | A10 | 78 | experimental |
| A12 | distribution-and-validation | A4 | 79, 80 | complete |

## A0 — baseline-and-replan

| Campo | Contrato |
| --- | --- |
| Estado/dono | complete; Harness + Gateway |
| Problema | Ambiguidade de baseline e visão antiga bloqueia decisões coerentes. |
| Objetivo/motivação | Reconciliar implementação, histórico M1–M5 e 23 entregáveis sem executar novas capacidades. |
| Arquitetura | Plano/target/threat model com mapa de fontes; freeze 058 preservado como evidência local. |
| Requisitos | [059](../.specs/059-autonomy-architecture-replan.md); REQ-001 contrato, REQ-002 fronteira, REQ-003 aceite específico de cada spec |
| Dependências | Nenhuma; usa freeze local 058 sem alegar publicação |
| Segurança | Threat model aplicável, grants não derivados do modelo e capability indisponível se fronteira essencial falhar |
| UX | Leitor diferencia produto atual, proposta e próximo passo; não precisa publicar para aprovar plano. |
| Aceite/done | Todos os REQs das specs ligadas comprovados, contratos legados preservados e evidência registrada, respeitando stop abaixo |
| Fixtures/testes | Parser de specs, manifest/links/requisitos e cross-review dos dois repos; sem modelo/contas reais. |
| Observabilidade | Conferência dos 23 itens e relatório estático. |
| Rollback | Reverter somente documentos novos sem alterar records/runtime. |
| Non-goals | Nenhuma implementação, publicação ou recaptura de benchmark. |
| Stop rules | A0 termina quando documentos e checklist passam; implementação aguarda aprovação. |

## A1 — trajectory-and-budgets

| Campo | Contrato |
| --- | --- |
| Estado/dono | next; Harness |
| Problema | Timeline resumida e limites dispersos não sustentam autonomia longa. |
| Objetivo/motivação | Explicar cada ação e conter custo/tempo antes de ampliar authority. |
| Arquitetura | Journal do supervisor + ledger agregado; compatibilidade com records v1. |
| Requisitos | [060](../.specs/060-structured-run-trajectory.md), [061](../.specs/061-aggregate-run-budgets.md); REQ-001 contrato, REQ-002 fronteira, REQ-003 aceite específico de cada spec |
| Dependências | A0 |
| Segurança | Threat model aplicável, grants não derivados do modelo e capability indisponível se fronteira essencial falhar |
| UX | Inspector mínimo pode mostrar progresso/stop e consumo; UI completa não é pré-requisito. |
| Aceite/done | Todos os REQs das specs ligadas comprovados, contratos legados preservados e evidência registrada, respeitando stop abaixo |
| Fixtures/testes | Fake model, retries/validadores, clock, disk-full/restart, canários, corrida de reservas. |
| Observabilidade | Causal IDs, ALLOW/ASK/DENY completos, consumed/reserved e outcome_unknown. |
| Rollback | Desativar writer/capability nova, preservar leitores/ledger e registros antigos. |
| Non-goals | Sem shell ampliado, browser, router ou delegates reais. |
| Stop rules | Parar se evento crítico/consumo puder desaparecer; concluir quando 060–061 passarem. |

## A2 — authority-and-credentials

| Campo | Contrato |
| --- | --- |
| Estado/dono | planned; Harness |
| Problema | Preset ou aprovação sem identidade/escopo pode virar autorização invisível. |
| Objetivo/motivação | Formalizar grants, ASK durável e isolamento mínimo de credentials. |
| Arquitetura | Supervisor como única autoridade; broker fake e contrato novo opt-in, v1 preservado. |
| Requisitos | [062](../.specs/062-scoped-authority-and-approvals.md), [063](../.specs/063-credential-broker-foundation.md); REQ-001 contrato, REQ-002 fronteira, REQ-003 aceite específico de cada spec |
| Dependências | A1 |
| Segurança | Threat model aplicável, grants não derivados do modelo e capability indisponível se fronteira essencial falhar |
| UX | Usuário revê intenção concreta e duração; canal/workspace visíveis, sem secret. |
| Aceite/done | Todos os REQs das specs ligadas comprovados, contratos legados preservados e evidência registrada, respeitando stop abaixo |
| Fixtures/testes | Replay, expiry, revoke, drift, troca de workspace/policy e canários com fake adapter. |
| Observabilidade | Grant/action/approval/receipt IDs, reason codes e revogação, sem payload secreto. |
| Rollback | Revogar grants novos e voltar Safe; nunca replay de approvals legadas. |
| Non-goals | Sem concessão por skill/modelo, OAuth universal ou escrever pelo Gateway agora. |
| Stop rules | Não avançar se approval puder ampliar boundary ou ser reutilizada; concluir 062–063. |

## A3 — sandbox-and-primitives

| Campo | Contrato |
| --- | --- |
| Estado/dono | planned; Harness |
| Problema | Shell atual é host-level; Docker só de validate não contém agente inteiro. |
| Objetivo/motivação | Entregar primeiro ciclo útil autônomo em Linux/WSL2 com baixo impacto fora do ambiente. |
| Arquitetura | Backend verificado, clone/cópia independente e shell/fs/process/git/deps sob grant. |
| Requisitos | [064](../.specs/064-verified-sandbox-executor.md), [065](../.specs/065-autonomous-sandbox-primitives.md); REQ-001 contrato, REQ-002 fronteira, REQ-003 aceite específico de cada spec |
| Dependências | A2 |
| Segurança | Threat model aplicável, grants não derivados do modelo e capability indisponível se fronteira essencial falhar |
| UX | Concessão por ambiente evita ASK por microação; status mostra boundary verificada. |
| Aceite/done | Todos os REQs das specs ligadas comprovados, contratos legados preservados e evidência registrada, respeitando stop abaixo |
| Fixtures/testes | Marker host, socket Docker, hooks/symlink race, install fixture offline, test-fail-fix-retest e cancel de árvore. |
| Observabilidade | Process handles, recursos, imagem/digest, arquivos/diff, testes e cleanup status. |
| Rollback | Descartar ambiente; promover apenas por hash/drift; fonte permanece preservada. |
| Non-goals | Sem socket host, push/release, perfil pessoal, Docker-in-Docker ou múltiplos backends. |
| Stop rules | Qualquer escape ou limite falso bloqueia A3; concluir 064–065 com teste real do backend provisionado. |

## A4 — local-web-chat

| Campo | Contrato |
| --- | --- |
| Estado/dono | partial; Harness + Gateway |
| Problema | Gateway é operacional read-only, não conversa de trabalho completa. |
| Objetivo/motivação | Entregar chat-first com inspector, revisão, approvals e primeiro uso simples. |
| Arquitetura | Gateway UX/auth + Harness sessão/run/authority; contrato novo versionado, v1 safe. |
| Requisitos | [066](../.specs/066-local-chat-inspector-contract.md), [067](../.specs/067-local-chat-work-review.md), [068](../.specs/068-chat-bootstrap-linux-wsl.md); REQ-001 contrato, REQ-002 fronteira, REQ-003 aceite específico de cada spec |
| Dependências | A1, A2, A3 |
| Segurança | Threat model aplicável, grants não derivados do modelo e capability indisponível se fronteira essencial falhar |
| UX | Choose project→chat→tools→diff/testes→review/approve/cancel; pause e checkpoints com limites claros. |
| Aceite/done | Todos os REQs das specs ligadas comprovados, contratos legados preservados e evidência registrada, respeitando stop abaixo |
| Fixtures/testes | Quatro combinações de versões, cross-workspace, CSRF/Origin/Host, preview, reconnect, stale approve e install smoke. |
| Observabilidade | Cursors/event gaps, estado da sessão, budgets e receipts em projeções por canal. |
| Rollback | Desativar writes novas, manter v1 e sessões legíveis; não apagar dados do usuário. |
| Non-goals | Sem mobile writes, terceiro backend, desktop nativo ou rewrite de UI obrigatório. |
| Stop rules | UI 066 pode começar após A1/A2; entrega de trabalho exige A3 e 067–068. |

## A5 — deterministic-code-graph

| Campo | Contrato |
| --- | --- |
| Estado/dono | planned; Harness |
| Problema | Ranking/symbols não conectam dependências nem testes à implementação. |
| Objetivo/motivação | Melhorar seleção por token/tempo com relações locais verificáveis. |
| Arquitetura | Python AST, arestas com provenance/confiança e cache incremental descartável. |
| Requisitos | [069](../.specs/069-deterministic-code-graph.md); REQ-001 contrato, REQ-002 fronteira, REQ-003 aceite específico de cada spec |
| Dependências | A1 |
| Segurança | Threat model aplicável, grants não derivados do modelo e capability indisponível se fronteira essencial falhar |
| UX | Subgraph compacto sob demanda; unknown explícito, sem sobrecarregar chat. |
| Aceite/done | Todos os REQs das specs ligadas comprovados, contratos legados preservados e evidência registrada, respeitando stop abaixo |
| Fixtures/testes | Aliases/ciclos/dynamic imports/rename/delete/stale cache e tarefa de descoberta com baseline fixo. |
| Observabilidade | Index version/cache hit/invalidations, calls/latency/correctness antes/depois. |
| Rollback | Descartar índice e voltar ranking existente sem perder dados de projeto. |
| Non-goals | Sem graph completo, embeddings, background scanner pessoal ou modelo novo. |
| Stop rules | Se aumentar custo sem ganho ou piorar correctness, reduzir escopo; concluir 069. |

## A6 — network-browser-external-effects

A6 progress: 070, 081 and 071 complete. Current browser delivery is fixture-only; real/personal/authenticated browser automation remains outside A6.

| Campo | Contrato |
| --- | --- |
| Estado/dono | planned; Harness + Gateway |
| Problema | Internet/browser/contas atravessam a fronteira mesmo dentro do container. |
| Objetivo/motivação | Permitir pesquisa/workflows e primeira operação externa com efeito verificável. |
| Arquitetura | Egress real + broker/receipts; browser descartável depois; adapter Git remoto limitado. |
| Requisitos | [070](../.specs/070-governed-egress-and-services.md), [081](../.specs/081-authenticated-external-actions.md), [071](../.specs/071-isolated-browser-workflows.md); REQ-001 contrato, REQ-002 fronteira, REQ-003 aceite específico de cada spec |
| Dependências | A2, A3, A4 |
| Segurança | Threat model aplicável, grants não derivados do modelo e capability indisponível se fronteira essencial falhar |
| UX | Atividade/destino/dados enviados claros; ação crítica é revisável, resultado incerto visível. |
| Aceite/done | Todos os REQs das specs ligadas comprovados, contratos legados preservados e evidência registrada, respeitando stop abaixo |
| Fixtures/testes | DNS rebinding/IPv6/proxy, registry fake, remote apply-then-drop, DOM drift, downloads e secrets canary. |
| Observabilidade | Network grants/quotas, auth refs, browser action e receipt/unknown, redaction. |
| Rollback | Revogar egress/leases, fechar browser/ports; efeito já enviado exige reconciliação específica. |
| Non-goals | Sem contas pessoais, cloud/finance universal, secret no prompt ou GUI host. |
| Stop rules | 070 precede browser; 081 depende 063/062/070; browser anônimo dispensa 081, autenticado não. |

## A7 — mcp-execution

A7 complete: the implemented surface is a sandboxed `fixture_stdio` MCP execution adapter, while generic MCP `call-tool` remains denied.

| Campo | Contrato |
| --- | --- |
| Estado/dono | planned; Harness + Gateway |
| Problema | MCP declarativo sem execução não atende a capacidade pedida. |
| Objetivo/motivação | Executar uma integração stdio útil dentro do grant sem autoridade implícita. |
| Arquitetura | Servidor explicitamente escolhido, runtime isolado e tool mapping/schema fixado. |
| Requisitos | [072](../.specs/072-sandboxed-mcp-execution.md); REQ-001 contrato, REQ-002 fronteira, REQ-003 aceite específico de cada spec |
| Dependências | A2, A3, A4 |
| Segurança | Threat model aplicável, grants não derivados do modelo e capability indisponível se fronteira essencial falhar |
| UX | Chat mostra server/tool, decisão, bounded artifact e efeitos, sem raw stdout. |
| Aceite/done | Todos os REQs das specs ligadas comprovados, contratos legados preservados e evidência registrada, respeitando stop abaixo |
| Fixtures/testes | Fake server escreve artefato permitido, mente sobre read-only, muda schema, trava e tenta escape. |
| Observabilidade | Startup/call/cancel, policy/budget, truncation/redaction e status attempted/unknown. |
| Rollback | Revogar server/tool, matar processo e preservar broker declarativo v1. |
| Non-goals | HTTP remoto nesta fatia, wildcard trust, callbacks/sampling, auto-install ou marketplace. |
| Stop rules | Concluir 072 com valor útil e abuso contido; HTTP autenticado requer A6 e nova spec. |

## A8 — model-profiles-and-skills

| Campo | Contrato |
| --- | --- |
| Estado/dono | planned; Harness |
| Problema | Eval e skills existem sem perfis de capacidade nem contrato de extensibilidade. |
| Objetivo/motivação | Selecionar capacidades por evidência e disponibilizar skills sem ampliar grants. |
| Arquitetura | Perfis versionados; seleção manual; manifest declarativo com loader legado. |
| Requisitos | [073](../.specs/073-model-capability-profiles.md) complete; [074](../.specs/074-capability-declared-skills.md) complete; REQ-001 contrato, REQ-002 fronteira, REQ-003 aceite específico de cada spec |
| Dependências | A1, A2 |
| Segurança | Threat model aplicável, grants não derivados do modelo e capability indisponível se fronteira essencial falhar |
| UX | Modelo e skill exibem requisitos/limitações e evidência; contexto progressivo. |
| Aceite/done | Todos os REQs das specs ligadas comprovados, contratos legados preservados e evidência registrada, respeitando stop abaixo |
| Fixtures/testes | Suite incompleta/antiga, repeats, hardware mismatch e skill maliciosa/versão desconhecida. |
| Observabilidade | Model/suite/version, latência/refusal/truncation/correctness e loaded capability subset. |
| Rollback | Manter modelo escolhido e skills legadas; invalidar perfil incompatível. |
| Non-goals | Router automático ainda, default switch, downloads, hooks privilegiados ou marketplace. |
| Stop rules | Concluir 073–074; roteamento só ganha spec após evidência local repetida. |

## A9 — fork-and-delegates

| Campo | Contrato |
| --- | --- |
| Estado/dono | planned; Harness + Gateway |
| Problema | Experimentos misturados e execução paralela sem ownership geram conflito/custo. |
| Objetivo/motivação | Comparar alternativas e delegar em waves com scope e orçamento herdado. |
| Arquitetura | Fork de snapshot/contexto; DAG/ownership; grants subset e ledger pai. |
| Requisitos | [075](../.specs/075-session-fork-comparison.md) complete; [076](../.specs/076-bounded-delegate-waves.md) complete; REQ-001 contrato, REQ-002 fronteira, REQ-003 aceite específico de cada spec |
| Dependências | A1, A2, A3, A4 |
| Segurança | Threat model aplicável, grants não derivados do modelo e capability indisponível se fronteira essencial falhar |
| UX | Comparação por correctness/diff/testes/custo, árvore de tarefas e cancel visível. |
| Aceite/done | Todos os REQs das specs ligadas comprovados, contratos legados preservados e evidência registrada, respeitando stop abaixo |
| Fixtures/testes | Base igual, fork drift, colisão, ciclo DAG, filho falho, budget pai e cancel recursivo. |
| Observabilidade | Parent/child IDs, ownership/conflicts, aggregation e budget total. |
| Rollback | Cancelar filhos, descartar cópias e integrar somente promoção revisada. |
| Non-goals | Swarm, auto-merge, paralelismo ilimitado ou copiar token/approval. |
| Stop rules | 075 antes de 076; graph/perfis ajudam, mas não são dependências obrigatórias de segurança. |

## A10 — trusted-host

| Campo | Contrato |
| --- | --- |
| Estado/dono | complete; Harness fixture contract; Gateway follow-through via existing contract |
| Problema | Alguns workflows úteis precisam recursos do host além da sandbox. |
| Objetivo/motivação | Avaliar Full/Trusted amplo, explícito e aplicável pelo OS. |
| Arquitetura | Conta/processos/paths autorizados e broker/egress com emergency stop. |
| Requisitos | [077](../.specs/077-trusted-host-profile.md); REQ-001 contrato, REQ-002 fronteira, REQ-003 aceite específico de cada spec |
| Dependências | A1, A2, A3, A4, A6 |
| Segurança | Threat model aplicável, grants não derivados do modelo e capability indisponível se fronteira essencial falhar |
| UX | Opt-in mostra recursos e garantias reais; perfil inaplicável é indisponível. |
| Aceite/done | Todos os REQs das specs ligadas comprovados, contratos legados preservados e evidência registrada, respeitando stop abaixo |
| Fixtures/testes | Ambiente host descartável, roots/processes canary, revogação/stop e isolamento de credenciais. |
| Observabilidade | Backend/grant/host operation, residual capability e incident receipts. |
| Rollback | Revogar perfil/leases e voltar Safe; compensação de efeitos é específica. |
| Non-goals | Root irrestrito, desktop pessoal, Windows nativo ou rollback universal. |
| Stop rules | Exigir evidência A3/A4/A6; delegates/MCP não são pré-requisitos artificiais de host. |

A10 complete: entregue como contrato experimental `fixture_linux`, com status, grants TTL, revogação, emergency stop, operações/roots/processos allowlisted, protected-path deny e receipts sem segredo. Host pessoal, shell real, root e Windows nativo continuam indisponíveis até existir boundary OS comprovado.

## A11 — computer-use

| Campo | Contrato |
| --- | --- |
| Estado/dono | experimental; Harness + Gateway |
| Problema | GUI cobre aplicações sem API, com efeitos difíceis de verificar. |
| Objetivo/motivação | Pilotar automação visual em desktop dedicado antes do desktop pessoal. |
| Arquitetura | Adapter de janela/input/captura dentro de VM/desktop de automação e grant. |
| Requisitos | [078](../.specs/078-isolated-computer-use.md); REQ-001 contrato, REQ-002 fronteira, REQ-003 aceite específico de cada spec |
| Dependências | A10 |
| Segurança | Threat model aplicável, grants não derivados do modelo e capability indisponível se fronteira essencial falhar |
| UX | Preview bounded, alvo da ação e stop acessível; handoff para ato crítico ambíguo. |
| Aceite/done | Todos os REQs das specs ligadas comprovados, contratos legados preservados e evidência registrada, respeitando stop abaixo |
| Fixtures/testes | App fixture, mudança de janela, screenshot sensível, injection e cancel sem modelo. |
| Observabilidade | Action/window IDs, captura limitada, estado parcial e unknown externo. |
| Rollback | Fechar sessão/VM; não prometer desfazer aplicação/conta externa. |
| Non-goals | Automação universal, apps pessoais ou novo cliente desktop LAI. |
| Stop rules | Se intenção e alvo crítico não puderem ser vinculados, handoff; concluir piloto 078 sem ampliar escopo. |

## A12 — distribution-and-validation

| Campo | Contrato |
| --- | --- |
| Estado/dono | planned; Harness + Gateway |
| Problema | Instalação frágil e validação repetida aumentam custo sem valor proporcional. |
| Objetivo/motivação | Graduar primeira experiência e reduzir redundância com evidência preservada. |
| Arquitetura | Reusar bootstrap 068 e gates existentes; matriz/contratos/proteção alinhados. |
| Requisitos | [079](../.specs/079-distribution-graduation.md) complete; [080](../.specs/080-risk-proportional-validation.md) complete; REQ-001 contrato, REQ-002 fronteira, REQ-003 aceite específico de cada spec |
| Dependências | A4 |
| Segurança | Threat model aplicável, grants não derivados do modelo e capability indisponível se fronteira essencial falhar |
| UX | Install/configure/open/choose/chat, upgrade/doctor claros; recurso opcional ausente não bloqueia Safe. |
| Aceite/done | Todos os REQs das specs ligadas comprovados, contratos legados preservados e evidência registrada, respeitando stop abaixo |
| Fixtures/testes | Clean Linux/WSL2, upgrade/downgrade/state version e falha semeada por classe de gate. |
| Observabilidade | Install/doctor/capability outcome, tempos e mapa de cobertura/checks. |
| Rollback | Voltar artefato/config compatível, preservar dados e restaurar gates se equivalência falhar. |
| Non-goals | Marketplace, Windows/macOS certificados, publicações automáticas ou retirar segurança para acelerar. |
| Stop rules | Pode graduar chat antes de A10/A11; freeze completo uma vez, sem gates repetidos por spec. |

## Stop rules globais e passagem para implementação

Aprovar plano não equivale a liberar todas as capabilities. Ativar somente a próxima spec com problema/aceite/fixture/risco claros. Atualizar status, evidência e manifest quando uma entrega terminar; não acrescentar notas contraditórias ao final do plano. Parar quando o milestone fecha, quando o backend não aplica o grant, quando há vazamento/escape/replay ou quando a próxima atividade é scope creep.

Aplicar feedback proporcional: documentos→static/links/parser/diff; comportamento→regressões focadas; segurança→fixtures de boundary; freeze/release→gate completo uma vez. Sem dependências instaladas por esta revisão, sem release por cada spec e sem repetir gates já cobertos sem nova falha.
