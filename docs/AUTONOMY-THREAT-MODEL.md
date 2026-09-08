# lai harness threat model da autonomia

Estado: desenho para validação, 2026-09-08. Não descreve controles já entregues. Ver [security model atual](SECURITY-MODEL.md), [arquitetura-alvo](TARGET-ARCHITECTURE.md), [riscos](RISK-REGISTER-2026-09.md) e [milestones](EXECUTION-BACKLOG-2026-09.md).

## Ativos, atores e fronteiras

Ativos: código/dados do projeto e host, histórico Git, contas externas, credenciais, sessões, grants/approvals, receipts, journal/artefatos, modelo e disponibilidade de CPU/RAM/disco/rede. Dados de interface e filenames também podem ser privados.

Ator confiável: operador autenticado que concede um escopo. TCB proposto: Harness/supervisor e policy instalados, credential broker, Gateway de autoridade e OS/runtime configurados. Imagem/container e ferramentas selecionados precisam provenance; seleção não torna conteúdo de projeto confiável. Modelo, respostas MCP, web/DOM, arquivos, skills importadas, saída de shell e transcript histórico são dados sem poder de autorização. Um endpoint de modelo remoto altera a fronteira de dados e não é ativado por conveniência do router.

Fronteiras: browser do operador→Gateway; Gateway→Harness; modelo→intenção de ação; supervisor→executor; executor→filesystem/OS; executor→rede/contas; execução→records; pai→filho; fonte→workspace/promoção. Single-user local é o primeiro alvo; isolamento multi-tenant não é alegado.

## Matriz de ameaças e aceites obrigatórios

Todas as fixtures são sintéticas, sem credenciais, contas ou arquivos pessoais reais. Uma fixture passando prova somente o ataque coberto; aumentar autonomia exige o conjunto aplicável e dogfood controlado.

| ID | Ataque / consequência | Controle proposto e responsável | Fixture e resultado exigido | Gate |
| --- | --- | --- | --- | --- |
| TM-01 | Repo/web/skill/transcript instrui obter secret ou elevar autonomia | Harness mantém grants fora do contexto; instruções externas não alteram policy | Conteúdo pede Full, nova tool e secret; grant permanece idêntico e ação é negada | A2, A8 |
| TM-02 | Symlink/TOCTOU, mount, git hook ou dependency script escapam do workspace | Executor em boundary OS, roots verificados, repo independente, sem metadata Git da fonte | Troca symlink durante operação e tenta ler marker fora do mount; acesso não ocorre e fonte permanece intacta | A3 |
| TM-03 | Docker socket/daemon permite mounts ou privilégio do host | Supervisor só cria runtime por perfil fixo; socket nunca montado | Tarefa tenta acessar daemon e registrar mount/root privilegiado; falha antes de executar | A3 |
| TM-04 | Fork bomb, processo detached, output/disco infinito e timeout | Supervisor independente, cgroup/job backend, quotas verificadas | Árvore/fork/output bounded; cancel impede novos processos e cleanup relata estado final | A1, A3 |
| TM-05 | Exfiltração, SSRF, DNS rebinding, redirects/IPv6/proxy bypass | Egress real controla destinos; sem credenciais ambientais; broker | Fake DNS público→privado, metadata, localhost/model/control endpoints e redirect bloqueados; dados privados não chegam ao sink fixture | A6 |
| TM-06 | Credencial aparece em env, argv, log, tool output, screenshot ou export | Broker/adapters mínimos e redaction antes de persistir/mostrar; contas separadas | Canários sintéticos não aparecem em prompt, records, logs, UI/export; uso só no adapter destinatário | A2, A6, A7 |
| TM-07 | Aprovação trocada, repetida, revogada ou aplicada a outro workspace | Intenção imutável, hash/destino/baseline/TTL/principal/policy version e consumo durável | Replay e drift não executam; reinício não reaplica operação aprovada | A2, A4 |
| TM-08 | Resposta perdida após efeito externo provoca duplicação | Receipt/outcome_unknown, idempotency quando suportada, reconciliação | Fake serviço aplica efeito e cai antes de responder; nenhuma repetição automática nem sucesso inventado | A6 |
| TM-09 | Página local, preview ou Markdown tenta controlar UI/approvals | Gateway auth mesmo local, Host/Origin/CSRF, CSP, escaping e origens segregadas | Origem inesperada, token expirado e iframe/script de preview não leem sessão nem aprovam ação | A4 |
| TM-10 | MCP mente sobre read-only ou altera schema/servidor | Harness fixa identidade/schema/tool mapping, isola processo e reavalia alterações | Tool anunciada read-only tenta escrever fora do grant; bloqueada independentemente do hint | A7 |
| TM-11 | Delegate/fork amplia grant, disputa arquivo ou esgota budget pai | Grants subset, ownership, reservas agregadas e cancel recursivo | Filho não usa tool extra; conflito não é integrado; nenhum conjunto excede total pai | A9 |
| TM-12 | Executor adultera audit/apaga evidence ou crash perde intenção | Journal fora do mount sob supervisor; eventos críticos duráveis; readers de gap | Tentativa de overwrite falha; disk-full impede nova ação crítica; restart mostra lacuna e estado conservador | A1 |
| TM-13 | Memória/cache/graph obsoleto vira evidência ou autorização | Hash/root/parser version, provenance e inspeção atual; cache descartável | Rename/delete/drift invalida nó; stale turn não valida patch nem amplia grant | A5, A9 |
| TM-14 | Migration/cliente antigo ganha shell/MCP sem negociação | Contrato novo opt-in por canal; v1 preservado e fallback read-only | Matriz de versões/capabilities incompatíveis mantém flags legados e recusa escrita | A2, A4 |
| TM-15 | Full/GUI usa sessão pessoal e clique executa ato crítico errado | Conta/desktop dedicado, operação tipada ou handoff, stop fora do modelo | Janela/DOM muda após intenção: cancelar ou pedir revisão; nunca clicar às cegas em ação crítica | A10, A11 |
| TM-16 | Imagem, plugin, skill ou dependência instala código host sem consentimento | Provenance/pins, provisionamento explícito, cache por trust domain | Config de repo tenta iniciar/instalar server; apenas declaração é lida, sem processo ou download | A3, A7, A8, A12 |

## Garantias por superfície

Safe preserva seus controles e explicita que o shell local atual é host-level. Autonomous Sandbox exige prova de que **todo processo de projeto** e seus descendentes estão na fronteira; a cópia de arquivos e o Docker somente da validação atual não satisfazem isso. Full/Trusted expõe recursos adicionais com grant e controles do OS, mas não pode apresentar um filtro de strings de shell como proteção de diretórios pessoais.

Conceder shell, dados privados e egress amplo simultaneamente reduz a capacidade de impedir exfiltração e ações autenticadas indiretas. Limitar egress/contas/processos é parte da segurança, não microburocracia. Mesmo destinos permitidos podem aceitar dados privados. A UI informa a mudança material de garantias antes da concessão; nenhuma descrição "Full seguro" substitui enforcement.

Browser profile/context separa estado, não efeitos em servidores. Ações críticas na GUI sem vínculo verificável entre intenção e efeito exigem handoff. Não alegar que screenshot, log ou rollback local desfaz e-mail, release, compra ou cloud. Descrições de ferramentas e anotações MCP também não provam inocuidade.

## Aprovação, recuperação e resposta a incidentes

Aprovação apresenta operação concreta, destino, dados enviados/alterados, scope, duração e irreversibilidade quando aplicável. O usuário pode autorizar classes limitadas por sessão; revogação invalida novas ações. Operações já em voo são reconciliadas por receipt, não presumidas canceladas.

Emergency stop é acionável sem cooperação do modelo: recusar dispatch, revogar filhos/leases, bloquear novas saídas do broker, terminar árvore do executor e fechar proxies/portas. Relatar processos restantes e efeitos desconhecidos. Preservar evidência mínima privada para investigação. Nunca executar replay de tool/approval a partir de checkpoint legado.

Recuperação: verificar hash/drift, reconstruir contexto bounded e requerer grants atuais. Rollback de arquivo usa snapshot compatível; ambientes são descartados; contas externas precisam compensação específica. Falha em cleanup, broker, journal ou readiness essencial deixa a capability indisponível. Escalar a intensidade dos testes conforme a fronteira afetada.

## Evidência externa usada no desenho

Referências primárias consultadas para este planejamento; fixar versões e rever compatibilidade antes da implementação. Não são uma auditoria dos produtos citados.

- Worktrees têm partes de administração Git compartilhadas: [Git worktree](https://git-scm.com/docs/git-worktree.html).
- Daemon Docker é uma superfície privilegiada e rootless depende de condições de execução: [Docker security](https://docs.docker.com/engine/security/), [rootless tips](https://docs.docker.com/engine/security/rootless/tips/).
- Browser sandbox e estado autenticado exigem tratamento explícito: [Playwright Docker](https://playwright.dev/docs/docker), [Playwright auth](https://playwright.dev/docs/auth).
- Auth MCP depende do transporte; HTTP requer tokens destinados ao recurso correto e proteção de endpoints locais: [MCP authorization](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization), [MCP transports](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports).
- Cookies/loopback não eliminam CSRF: [OWASP CSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html).

## Limites de confiança

Não há promessa de resistência universal a prompt injection, kernel/container escape, fornecedor malicioso com privilégio concedido, invasão da conta do operador, exactly-once em serviços externos ou correção por simples passagem de testes. Reavaliar o threat model a cada novo canal, backend, credencial ou classe de consequência; não reabrir toda a arquitetura para mudanças sem nova fronteira.
