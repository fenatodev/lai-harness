# lai harness plano de transformação, setembro de 2026

Estado pós-A12: plano histórico aprovado e executado para todos os marcos não-experimentais. A0–A9 e A12 estão completos; A10/A11 permanecem drafts experimentais. Este arquivo preserva o racional original; use [docs/README.md](README.md), [Architecture](ARCHITECTURE.md) e [Roadmap](../ROADMAP.md) para claims públicos atuais.
Cada capability continua dependendo de código, testes e contrato verificável; planejamento sozinho não ativa comportamento.

## Objetivo e escopo

Evoluir o LAI para um agente local com máxima autonomia útil dentro de fronteiras autorizadas, preservando modelos locais pequenos, contexto eficiente, policy determinística, evidência e simplicidade operacional. O produto continua **lai harness**, com comando `lai` e código neste checkout `lai-local-agent`; `lai-gateway` continua um repositório separado. Não há rename de executável, pacote ou diretório nesta revisão.

A transformação é incremental. Reutiliza o loop, control plane, sessões, records, avaliação, promoção e Gateway. Não inicia uma reescrita, implementação, instalação, benchmark com modelo, mudança de modelo padrão ou publicação.

## Documentos canônicos

| Documento | Responsabilidade |
| --- | --- |
| [Roadmap](../ROADMAP.md) | Estado de produto: implementado, próximo, planejado, experimental, deferred e fora de escopo |
| [Arquitetura atual](ARCHITECTURE.md) | O que o código executa hoje |
| [Arquitetura-alvo](TARGET-ARCHITECTURE.md) | Componentes, contratos, níveis de autonomia e migração |
| [Threat model da autonomia](AUTONOMY-THREAT-MODEL.md) | Ativos, fronteiras, ataques, controles, testes e limites propostos |
| [Security model](SECURITY-MODEL.md) | Controles e limitações efetivamente implementados |
| [Backlog](EXECUTION-BACKLOG-2026-09.md) | Milestones, dependências, critérios, fixtures e stop rules |
| [Decisões](DECISION-LOG-2026-09.md) | Substituições deliberadas e alternativas rejeitadas |
| [Riscos](RISK-REGISTER-2026-09.md) | Risco residual e condição para avançar |
| [Conferência dos 23 itens](REPLAN-COVERAGE-2026-09.md) | Evidência item a item e consistência entre documentos |
| [Manifest](PLANNING-MANIFEST-2026-09.json) | Índice estruturado do mesmo plano; não é configuração de runtime |
| [Plano do Gateway](../../lai-gateway/docs/PROJECT-PLAN-2026-09.md) | Entregas e contratos da interface companheira |

Os links entre repositórios presumem os checkouts irmãos `lai-local-agent` e `lai-gateway`. Em uma instalação/repositório isolado, consultar o documento de mesmo nome no repositório companheiro. Não duplicar o motor de execução para eliminar essa separação.

## Diagnóstico do baseline

Inspeção local: Harness `src/local-agent` declara `0.4.9`, HEAD `4b9b973`; Gateway declara `0.1.34`. A spec [058](../.specs/058-v049-release-freeze.md) registra freeze e validação local completos. Isso não comprova publicação, tag remoto, CI atual ou prontidão da máquina instalada. O baseline integrado anteriormente documentado era `0.4.8` + `0.1.34`; a compatibilidade continua por contrato/capabilities e versão mínima, não por igualdade de patches. Não é necessário bloquear o planejamento na publicação do freeze anterior.

M1–M4 estão completos segundo specs/evidências locais. M5 está completo como freeze local, com publicação não verificada nesta revisão. O manifest anterior ainda dizia M4 draft/M5 não iniciado: essa divergência foi reconciliada. As evidências históricas e specs 001–058 são preservadas, sem transformar uma medição antiga em prova atual.

| Área | Evidência atual | Lacuna para a nova visão |
| --- | --- | --- |
| Loop e ferramentas | `src/local-agent`: policy central, schemas por modo, ferramentas de arquivo, Bash local, validação e rounds limitados | Shell local não é isolado; não há supervisor completo de execução autônoma |
| Isolated work | Cópia disposable de arquivos tracked; validação estruturada em Docker; promoção por hash para worktree | Cópia/worktree não é sandbox; processo do agente e todo shell ainda não vivem em uma fronteira isolada |
| Control plane | `lai serve`, bearer separado, runs assíncronos serializados, cancelamento, sessões persistentes em `src/lai_sessions.py` | Contrato v1 não autoriza shell/MCP; ASK termina run, sem aprovação durável e continuação interativa |
| Gateway | UI estática local/mobile, pareamento, Telegram, sessões e runs read-only; `lai_gateway/` no repositório companheiro | Chat de trabalho completo, diff, approvals, progresso fino e seleção segura de workspace/modelo |
| Observabilidade | JSONL de métricas/audit, checkpoints, snapshots, rollback limitado, export sanitizado | Eventos de controle sintetizados não são trajectory completa; nenhum ledger global de budgets |
| Contexto | Ranking, mapas, symbols, diff/checks/runs metadata; preflights determinísticos | Relações de código, invalidação incremental e qualidade mensurada de graph |
| Rede/MCP | `src/lai_web.py`: busca/fetch HTTPS restritos; `src/lai_mcp.py`: configuração/classificação não executável | Execução MCP, browser e canais de egress governados |
| Segredos | Arquivos de chave privados, bearer server-side, sanitização | Sem credential broker; ambiente de subprocesso herdado não equivale a isolamento |
| Modelos/skills | Eval repetida com seis cenários requeridos; skills portáveis e fallback legado | Perfis por capacidade, roteamento justificado, manifests de skills sem autoridade implícita |
| Distribuição/CI | Instalador stdlib, doctor, wrapper CLI/VS Code; CI Python 3.11/3.12 | Jornada chat-first e eliminação medida de redundância, preservando contratos de release |

O preflight determinístico atual ainda contém uma mensagem de próximo passo específica de M1 em `plan_active_spec_fast_path_response`/saída de contexto no `src/local-agent`. Ela não consulta o manifest de planejamento e não é a prioridade canônica; reconciliar essa mensagem somente em futura spec de runtime, sem alterar comportamento nesta revisão.

## Mudanças de decisão

1. **Autonomia dentro da fronteira passa a ser objetivo de produto.** Safe permanece padrão de migração; Autonomous Sandbox é a experiência principal de trabalho após autorização inicial.
2. **Shell amplo depende de isolamento de todo o executor.** Não basta flexibilizar a lista de comandos nem chamar uma worktree de sandbox.
3. **Credential broker e grants vêm antes das integrações autenticadas.** A ordem preliminar colocava credentials tarde demais.
4. **Web chat começa cedo no Gateway.** O inspector read-only pode ser construído após o contrato de eventos; edição e approvals esperam grants e sandbox. Não há terceiro backend nem nova UI desktop nativa.
5. **MCP deve executar trabalho útil.** O antigo `repo_public_text_read` vira fixture histórica, não teto permanente de produto; apenas replicar `inspect` não justifica a integração.
6. **Instalação começa no primeiro chat beta.** Não se deixa a jornada básica para depois de computer use; a graduação multiplataforma vem mais tarde.
7. **Full/Trusted é opt-in e experimental, não ausência de fronteira.** É possível que o OS não consiga aplicar uma combinação de escopos; nesse caso a combinação fica indisponível.
8. **Validação proporcional preserva sinais.** Python 3.11 tem motivo técnico (`tomllib`); reduzir matriz ou checks obrigatórios exige spec sincronizada com CI, release governance e testes.

As substituições e seus limites estão no Decision Log. Nenhum documento de planejamento afrouxa os guards atuais do repositório, autoriza mutação Git deste trabalho ou instala dependências agora.

## Ordem de dependência e entrega

`A0 diagnóstico/plano → A1 trajectory + budgets → A2 grants + broker → A3 sandbox + primitivas → A4 chat de trabalho` é o caminho crítico. A4 pode iniciar UI de inspeção após A1 e auth após A2, mas só entrega escrita após A3. O usuário confirmou **Linux/WSL2 primeiro; Windows nativo depois**.

A5 graph pode evoluir após A1 em paralelo. A6 rede/browser e A7 MCP dependem da fronteira A3 e dos controles A2; ambos precisam produzir evidência visível em A4 para dogfood. A8 perfis/skills depende de métricas e grants. A9 fork/delegates depende de supervisor, grants, sandbox e chat (A1–A4); graph/perfis/skills são melhorias possíveis, não gates de segurança obrigatórios. A10 Trusted host depende da fronteira e do controle de efeitos comprovados em A1–A4/A6, sem exigir delegates ou MCP; A11 GUI depende de A10. A12 gradua distribuição e economia de validação após A4, sem depender de Full/GUI, com bootstrap entregue já em A4. Não há datas prometidas nem necessidade de chegar a A11 para tornar o LAI útil.

A primeira fatia de implementação, **somente após aprovação do plano**, é a spec 060 (trajectory estruturada). Budget 061 admite desenho/preparação paralelos, mas implementação sequencial no mesmo repositório; ambos fecham A1. Executar uma spec ativa por repositório; paralelismo de desenho não autoriza múltiplas specs ativas no mesmo checkout.

## Critérios de sucesso do produto

- Uma tarefa sintética de corrigir código consegue inspecionar, editar, instalar dependência local autorizada, testar, falhar, corrigir e retestar sem ASK em cada microação da sandbox.
- Todo efeito fora do grant é bloqueado ou vai a aprovação explícita vinculada à operação; a interface explica o motivo e o escopo.
- Cancelamento contém processos descendentes e chamadas novas; operações externas já enviadas podem permanecer com resultado desconhecido, nunca sucesso presumido.
- O operador entende atividade, diff, testes, consumo e resultado pela interface de chat sem reconstruir stderr.
- Comparações usam a mesma fixture, baseline, modelo/configuração e recursos; medem correctness, chamadas, latência, truncation e overhead. Sem limiar inventado com evidência ausente: registrar baseline e limite aceito antes da spec ficar ativa.
- O core permanece utilizável sem browser/MCP/Docker quando esses recursos não são necessários; indisponibilidade de isolamento desabilita Autonomous Sandbox sem fallback silencioso para host.

## Stop rules e non-goals globais

Parar a fatia ao cumprir seus critérios; abrir follow-up para novas ideias. Parar a expansão de autoridade se houver escape, segredo em fixture, aprovação reutilizada, budget contornado, efeito externo não registrado ou regressão no contrato legado. Não corrigir uma falha reduzindo o teste ou escondendo o evento.

Ficam deferred: Windows nativo/macOS como backends certificados, scheduler/notificações proativas, marketplace, ACP genérico e provedores remotos por default. Ficam fora do escopo desta transformação: SaaS multi-tenant, automação comercial incorporada ao Harness, redistribuição/download automático de modelos, aprendizagem que altera policy silenciosamente, garantias universais de rollback ou de imunidade a prompt injection. Computer use é um experimento posterior, não requisito do chat beta.

## Conclusão desta revisão documental

A0 documental está completo; a aprovação do plano continua pendente. A spec [059](../.specs/059-autonomy-architecture-replan.md) registra esta entrega e sua validação. Specs candidatas 060–081 permanecem draft; não habilitam comportamento. O plano, manifesto, backlog e documentos operacionais devem manter a distinção entre baseline e destino. Os comandos de validação desta revisão são estáticos/documentais; não repetem o milestone gate já registrado no freeze 058 nem comprovam uma release nova.
