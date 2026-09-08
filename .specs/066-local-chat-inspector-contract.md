# Spec: Chat local autenticado e inspector

## Metadata

- Mode: `full`
- Status: `complete`
- Milestone: `A4`
- Planning revision: `2026-09-08`

## Goal

Negociar contrato versionado por canal e oferecer eventos/cursor e conteúdo local sanitizado para chat/inspector, preservando projeção remota metadata e v1 read-only.

## Requirements

### REQ-001

Negociar contrato versionado por canal e oferecer eventos/cursor e conteúdo local sanitizado para chat/inspector, preservando projeção remota metadata e v1 read-only.

### REQ-002

Registrar workspaces server-side, validar identidade/Host/Origin/CSRF, manter bearer Harness no servidor e separar preview; payload do cliente não concede path ou modelo arbitrário.

### REQ-003

Usuário seleciona workspace registrado/sessão/modelo disponível e acompanha run read-only; token expirado, origem adversária e quatro combinações de versões falham de modo explícito.

## Acceptance Criteria

- REQ-001: comportamento definido observável em fixture determinística; contrato legado aplicável preservado.
- REQ-002: tentativa adversarial correspondente é negada/contida antes de ampliar autoridade, com reason code.
- REQ-003: Usuário seleciona workspace registrado/sessão/modelo disponível e acompanha run read-only; token expirado, origem adversária e quatro combinações de versões falham de modo explícito.

## Validation

- `REQ-001`: Validar contrato/resultado nas fixtures específicas descritas abaixo.
- `REQ-002`: Cobrir rejeição, drift/revogação, isolamento e ausência de autoridade/segredos conforme requisito.
- `REQ-003`: Harness control-plane/session fixtures e Gateway server/UI fixtures sintéticas; reconexão/dedup/escaping, isolamento de projetos e auth local.
- Antes de ativar, fixar os comandos focados e limites numéricos a partir das fixtures e ferramentas realmente presentes; não instalar dependências autonomamente.
- Comportamento: regressões focadas primeiro. Fronteira crítica: integration/security tests pertinentes. Freeze: `make milestone-gate` uma vez, sem targets sobrepostos; companion usa seus checks próprios.

## Context and Constraints

Proposta sem implementação. Depende dos gates de A4 no [backlog](../docs/EXECUTION-BACKLOG-2026-09.md). [Arquitetura-alvo](../docs/TARGET-ARCHITECTURE.md) e [threat model](../docs/AUTONOMY-THREAT-MODEL.md) orientam o desenho; policy/AGENTS vigentes continuam aplicáveis. Exatamente uma spec pode ser ativa durante uma implementação por repositório; esta permanece draft até aprovação do plano e ativação da fatia.

## Non-Goals

Escrita autônoma, desktop nativo, rewrite de UI framework ou remote approvals.

## Implementation Notes

Áreas existentes para inspeção, não promessa de novos módulos: src/local-agent; tests/test_control_plane.py; companion lai-gateway/lai_gateway/server.py; companion static UI.

Fixtures e testes: Harness control-plane/session fixtures e Gateway server/UI fixtures sintéticas; reconexão/dedup/escaping, isolamento de projetos e auth local.

UX, observabilidade, rollback e stop rules específicos estão no contrato de A4 do backlog. Done requer todos os REQs, evidência registrada e nenhuma alegação de capability ainda não entregue. Se o escopo exceder esta fatia, separar follow-up draft antes de implementar.

## Traceability

- `REQ-001` → contrato/fixtures da área acima e entrega de A4.
- `REQ-002` → testes adversariais da fronteira e threat model aplicável a A4.
- `REQ-003` → caso de aceite determinístico descrito em Requirements e sua evidência de validação.
