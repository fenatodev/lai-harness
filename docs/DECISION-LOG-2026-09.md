# lai harness decisões de planejamento, setembro de 2026

Estado pós-A12: decisões preservadas como rationale histórico da transformação. As decisões que correspondem a A0–A9/A12 foram implementadas conforme specs completas; A10/A11 continuam experimentais. Para o estado público atual, consulte [Architecture](ARCHITECTURE.md), [Known limitations](KNOWN-LIMITATIONS.md) e [Roadmap](../ROADMAP.md).

## Reconciliação das decisões anteriores

IDs antigos permanecem rastreáveis; escopo temporal evita contradizer o produto futuro com limites do baseline.

| ID anterior | Decisão anterior | Tratamento nesta revisão |
| --- | --- | --- |
| DEC-001 | Context intelligence antes de Gateway polish | Substituída por DEC-008/011: chat é capacidade principal; inspector cedo, escrita após fronteira |
| DEC-002 | MCP não executa até design/testes | Preservada no runtime atual; destino ampliado por DEC-012 |
| DEC-003 | Ministral até evidência repetida | Preservada e ampliada por DEC-015; não há troca de modelo nesta revisão |
| DEC-004 | Contexto selecionado/medido, não prompts maiores | Preservada em graph incremental A5 |
| DEC-005 | Não iniciar release na antiga branch de planejamento | Restrição daquele ciclo; spec 058 já fechou freeze local. Nova revisão só documental, sem publicação |
| DEC-006 | M2 fecha com sanitização/dogfood mobile | Histórico concluído; não proíbe chat produtivo em A4 |
| DEC-007 | M3 design-only, única classe futura repo_public_text_read | M3 continua concluído e design-only; exclusividade futura substituída por DEC-012 |

## DEC-008 — Autonomia útil como objetivo, Safe como migração

Escolha: máxima liberdade dentro de grant verificável; Safe padrão inicial, Autonomous Sandbox principal após autorização, Full/Trusted experimental. Substitui tratar contenção máxima de ferramentas como objetivo final. Não remover limites porque uma capability parece útil. Presets, modos de tarefa, canal e backend são dimensões separadas; autoridade efetiva é sua interseção.

## DEC-009 — Fronteira OS antes de shell amplo

Escolha: executor inteiro em boundary, não só validate. Linux/WSL2 primeiro; container rootless quando controles funcionarem, VM para necessidades mais fortes. Worktree é instrumento de Git/promoção e não sandbox. Preferir clone/cópia independente ao `.git` compartilhado com a fonte. Não ampliar regex de comandos como substituto de containment; não montar Docker socket do host.

## DEC-010 — Autoridade/credentials antes de integração autenticada

Escolha: grants, journal, budgets e broker mínimo antecedem rede/browser/MCP autenticados. Corrige a ordem preliminar do pedido. Um fake adapter permite testar o contrato sem construir OAuth universal; adapters reais entram incrementalmente. ASK durável não reusa replay de recovery. Aprovação vincula operação, destino, estado e expiração; timeout pode significar resultado desconhecido.

## DEC-011 — Gateway como web chat principal

Escolha: reutilizar Gateway Python/static para chat local, mantendo Harness como única autoridade de sessão/run/modelo. CLI/VS Code continuam. Rejeita terceiro servidor de agente e desktop nativo inicial. UI de inspector começa cedo; escrita só com auth local, contrato novo e A3. Mobile/Telegram mantêm grants próprios, sem herdar Full. Bootstrap entra já no beta de chat.

## DEC-012 — MCP executável com valor demonstrável

Escolha: a futura integração pode alterar artefatos e operar processos dentro da sandbox; não se limita para sempre a `repo_public_text_read`. O design M3 é histórico e fornece fixtures, não política universal. Config/schema/server são não confiáveis; executar exige identidade autorizada e runtime. CLI/control v1 atuais continuam não executáveis. HTTP autenticado, callbacks e novas classes precisam fatias separadas.

## DEC-013 — Observabilidade causal, sem coleta indiscriminada

Escolha: trajectory estruturada antes da expansão, com ALLOW/ASK/DENY e model/tool/process spans, budget e receipts. Rejeita stderr bruto como API e "logs completos" como captura de segredos/raciocínio privado. Conteúdo local sob demanda e projeção remota metadata são distintos. Budget/receipts críticos não desaparecem por retenção de audit.

## DEC-014 — Full tem limites reais

Escolha: conta/desktop dedicado e grants aplicáveis pelo OS antes de host amplo. Não prometer confirmação universal enquanto shell tem credenciais, rede e arquivos pessoais acessíveis. Se não houver enforcement, o perfil protegido correspondente é indisponível. Computer use começa em desktop isolado; ações críticas ambíguas vão para operação tipada ou humano. Rollback é específico por recurso.

## DEC-015 — Evidência local para graph, router e delegates

Escolha: graph determinístico parcial com provenance, invalidação e fixtures; sem embeddings por default. Model profiles versionados precedem roteamento, com repeated eval e custo de carga/memória. Skills não concedem authority. Fork e budgets precedem delegates; waves e ownership evitam edição concorrente caótica. Paralelismo só compensa se melhorar qualidade/tempo no hardware disponível.

## DEC-016 — Validação proporcional sem perder contratos

Escolha: documentação recebe checks documentais/static; comportamento recebe regressões focadas; fronteiras críticas e freeze recebem gates completos pertinentes. Não rodar todo milestone gate por documento. Python >=3.11 é requisito real (`tomllib`); revisão de redundância/matriz/checks de proteção é spec 080, não remoção textual ou alteração remota agora. Core runtime segue stdlib; browser/MCP/backends opcionais podem ter dependências explícitas isoladas em specs dedicadas, sem novas dependências nesta entrega.

## DEC-017 — Planejamento reconciliado sem reescrever história

Escolha: manter nomes oficiais `*-2026-09.md`, usados por referências existentes; reescrever seu conteúdo prospectivo e preservar evidências M1–M5 com estado correto. Não há benefício em renomear todos os documentos para um novo conjunto de aliases. Adicionar apenas arquitetura-alvo/threat model e specs necessários. Manifest passa a schema 2 de planejamento (não runtime), com histórico separado de A0–A12. Nenhum consumidor de runtime usa esse manifest hoje; registrar incompatibilidade documental em vez de chamá-la mudança de capabilities.

## Decisões abertas antes de ativar a spec correspondente

| Questão | Proposta atual / critério para fechar | Spec |
| --- | --- | --- |
| Backend/container e imagem/toolchain | Um backend Linux/WSL2; comprovar limites, digest/provenance, provisioning e cleanup | 064 |
| Sessão web/cursor/transport | Auth local revogável; polling incremental primeiro; SSE se necessário, sem token Harness no browser | 066 |
| Budgets numéricos e limites de performance | Medir fixture baseline/hardware e fixar thresholds antes de implementar | 060–061 |
| Parser JS/TS e dependência opcional | Python AST primeiro; custo, licença, precision e invalidação justificam parser | 069 |
| Revisão/SDK MCP | Fixar protocolo suportado com evidência primária atual e fixtures | 072 |
| Matriz Python/duplicações | Piso 3.11; preservar sinais/required-check IDs até migração coordenada | 080 |

Essas escolhas técnicas não impedem revisar o plano; não são autorizações implícitas para instalar, publicar ou executar contas externas.
