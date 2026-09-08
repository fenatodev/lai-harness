# lai harness registro de riscos, setembro de 2026

Estado pós-A12: registro histórico de riscos da transformação. Riscos cobertos por A0–A9/A12 têm mitigação implementada somente na extensão comprovada por código/testes; riscos de A10/A11 permanecem experimentais. Consulte [Security model](SECURITY-MODEL.md), [Known limitations](KNOWN-LIMITATIONS.md) e [Threat model](AUTONOMY-THREAT-MODEL.md) para fronteiras atuais.

## Riscos herdados reconciliados

| ID | Risco histórico | Estado e decisão atual |
| --- | --- | --- |
| RISK-001 | Gateway polish consome capacidade do core | Reformulado: A4 precisa entregar chat útil com autoridade no Harness; UI cosmética continua sem prioridade |
| RISK-002 | MCP amplia autoridade cedo | Aberto: A2/A3/A7 substituem adiamento indefinido por fronteira e execução testável |
| RISK-003 | Mais contexto piora latência/correctness | Watch: A5 mede graph antes/depois, mantém inspeção e provenance |
| RISK-004 | Troca de modelo gera churn | Watch: A8 exige repeated evidence na suite atual, sem default automático |
| RISK-005 | Mobile esconde falhas de auth/sessão | Mitigação parcial histórica em M2; novo chat exige auth local e contrato próprio A4 |
| RISK-006 | Plano diverge do código | Aberto: manifest/backlog/specs/arquitetura reconciliados nesta revisão; revisar por capability |
| RISK-007 | Ritual de release começa cedo | Watch: freeze 058 já existe; este plano não publica nem reexecuta gates sem motivo |

## Riscos da transformação

Probabilidade/impacto são avaliações qualitativas para sequenciamento, não estimativas medidas. Todos estão abertos até os aceites indicados.

| ID | Probabilidade / impacto | Risco e consequência | Dono / mitigação planejada | Evidência para avançar / stop |
| --- | --- | --- | --- | --- |
| RISK-008 | Alta / crítico | Chamar workspace de sandbox libera shell com autoridade host | Harness runtime; boundary real, clone independente, mounts mínimos | A3: TM-02/03/04; qualquer escape bloqueia autonomia |
| RISK-009 | Alta / crítico | Shell+rede+secrets contornam policy e exfiltram | Credential/egress brokers; ambiente mínimo e contas separadas | A2/A6: canários e sinks; segredo exposto interrompe expansão |
| RISK-010 | Média / crítico | Replay/drift de aprovação e efeito externo duplicado | Supervisor; intenção vinculada, receipt/unknown/idempotency | A2/A6: restart/timeout/replay; sem prova de precondição, não executar |
| RISK-011 | Alta / alto | Budgets só no loop deixam retries/filhos/processos ilimitados | Supervisor; reservas agregadas e limites OS verificados | A1/A9: nenhuma combinação excede pai; limite inexequível desabilita perfil |
| RISK-012 | Média / crítico | Web local/preview obtém autoridade por auth inadequada | Gateway; auth local, Origin/Host/CSRF e isolamento de origem | A4: TM-09, compatibilidade legada; não liberar writes antes |
| RISK-013 | Alta / alto | Journal vira vazamento ou não registra ações relevantes | Harness records; redaction antes de gravação, causal IDs e quotas | A1: ALLOW/ASK/DENY, canários/disk-full/restart; perda explícita |
| RISK-014 | Alta / alto | MCP/browser mentem sobre efeitos ou usam credenciais ambientais | Adapters; identidade/schema, runtime e broker por destino | A6/A7: tool enganosa e DOM mutável; metadata do fornecedor não autoriza |
| RISK-015 | Média / alto | Kernel/container/daemon comprometidos | Runtime ops; updates explícitos, imagem por digest, rootless/VM | A3/A10: readiness e limites; risco residual continua, sem promessa absoluta |
| RISK-016 | Alta / alto | Dois backends/Gateways/modelos duplicam estado e RAM | Harness dono de execução/modelo; Gateway de UX; capability contract | A4: quatro combinações de versões e único runtime no dogfood |
| RISK-017 | Média / alto | Fork/delegates conflitam e multiplicam custo | Orchestrator; DAG/waves/ownership e budget pai | A9: conflitos recusados, cancellation recursivo, comparação válida |
| RISK-018 | Alta / alto | Full/GUI faz promessa impossível de contenção/rollback | Host adapter + UX; conta/desktop dedicado e handoff crítico | A10/A11: escopos aplicáveis e TM-15; combinação não aplicável indisponível |
| RISK-019 | Alta / médio | Complexidade degrada modelos pequenos e instalação | Context/model/packaging; schemas progressivos e módulos opcionais | A4/A5/A8/A12: baseline custo/latência/correctness e smoke clean |
| RISK-020 | Média / alto | Reduzir CI quebra suporte ou required-check governance | Development harness; spec coordenada com matriz e release checks | A12: cobertura equivalente e checks alinhados; não afrouxar para passar |
| RISK-021 | Alta / médio | Scope creep adia indefinidamente o primeiro agente útil | Planejamento; A1–A4 é primeiro corte; graph/delegates/GUI não bloqueiam beta | Cada milestone termina no done; ideias extras viram draft/deferred |
| RISK-022 | Média / alto | Cache/graph/model evidence obsoletos parecem corretos | Context/eval; hashes/versões/unknown e validação independente | A5/A8: drift invalida; suite antiga não decide troca de modelo |

## Dívida histórica constatada nesta revisão

O parser atual rejeita 19 specs históricas 001–058 por seções/status/traceability de formatos antigos. Seus bytes são iguais ao HEAD e nenhuma está ativa; as 23 specs novas 059–081 seguem o parser atual. Isso é dívida de migração documental associada a RISK-006, não falha introduzida pela nova arquitetura. Não reinterpretar essas specs antigas como ativas nem editar evidência histórica para simular validação retroativa. Uma futura migração de formatos deve preservar status/provenance e ter spec própria.

## Critério de aceitação de risco residual

A spec responsável deve declarar controles que pode provar, o que permanece exposto e o que o usuário autoriza. Um alerta genérico não torna um perfil aplicável pelo OS. Risco crítico de atravessar grant sem controle bloqueia a capability; risco de usabilidade/performance deve ser medido e pode motivar reduzir escopo. Registrar desvios no Decision Log, com fixture e decisão revisável.
