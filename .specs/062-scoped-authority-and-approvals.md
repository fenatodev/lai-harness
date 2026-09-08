# Spec: Grants e aprovação durável

## Metadata

- Mode: `full`
- Status: `complete`
- Milestone: `A2`
- Planning revision: `2026-09-08`

## Goal

Definir presets independentes de modo/canal/backend e grants versionados por principal/run/workspace; autoridade é interseção com policy e controles verificáveis.

## Requirements

### REQ-001

Definir presets independentes de modo/canal/backend e grants versionados por principal/run/workspace; autoridade é interseção com policy e controles verificáveis.

### REQ-002

ASK cria intenção imutável com payload/hash/destino/precondições/TTL/revogação; aprovação de uso único revalida antes de executar e nunca deriva de checkpoint ou texto.

### REQ-003

Replay, outro workspace, policy nova, grant revogado e payload modificado não executam; v1 continua shell/MCP false; fake backend inaplicável é DENY.

## Acceptance Criteria

- REQ-001: comportamento definido observável em fixture determinística; contrato legado aplicável preservado.
- REQ-002: tentativa adversarial correspondente é negada/contida antes de ampliar autoridade, com reason code.
- REQ-003: Replay, outro workspace, policy nova, grant revogado e payload modificado não executam; v1 continua shell/MCP false; fake backend inaplicável é DENY.

## Validation

- `REQ-001`: Validar contrato/resultado nas fixtures específicas descritas abaixo.
- `REQ-002`: Cobrir rejeição, drift/revogação, isolamento e ausência de autoridade/segredos conforme requisito.
- `REQ-003`: Expandir fixtures de promoção/hash/drift e sessões; testar lifecycle/restart/idempotência de pedido e matriz de contrato antigo/novo.
- Antes de ativar, fixar os comandos focados e limites numéricos a partir das fixtures e ferramentas realmente presentes; não instalar dependências autonomamente.
- Comportamento: regressões focadas primeiro. Fronteira crítica: integration/security tests pertinentes. Freeze: `make milestone-gate` uma vez, sem targets sobrepostos; companion usa seus checks próprios.

## Context and Constraints

Proposta sem implementação. Depende dos gates de A2 no [backlog](../docs/EXECUTION-BACKLOG-2026-09.md). [Arquitetura-alvo](../docs/TARGET-ARCHITECTURE.md) e [threat model](../docs/AUTONOMY-THREAT-MODEL.md) orientam o desenho; policy/AGENTS vigentes continuam aplicáveis. Exatamente uma spec pode ser ativa durante uma implementação por repositório; esta permanece draft até aprovação do plano e ativação da fatia.

## Non-Goals

Habilitar shell/MCP, remote approvals mobile, alterar guards de desenvolvimento ou prometer exactly-once externo.

## Implementation Notes

Áreas existentes para inspeção, não promessa de novos módulos: src/local-agent; tests/test_control_plane.py; tests/test_control_sessions.py; docs/GATEWAY-CONTRACT.md.

Fixtures e testes: Expandir fixtures de promoção/hash/drift e sessões; testar lifecycle/restart/idempotência de pedido e matriz de contrato antigo/novo.

UX, observabilidade, rollback e stop rules específicos estão no contrato de A2 do backlog. Done requer todos os REQs, evidência registrada e nenhuma alegação de capability ainda não entregue. Se o escopo exceder esta fatia, separar follow-up draft antes de implementar.

## Traceability

- `REQ-001` → contrato/fixtures da área acima e entrega de A2.
- `REQ-002` → testes adversariais da fronteira e threat model aplicável a A2.
- `REQ-003` → caso de aceite determinístico descrito em Requirements e sua evidência de validação.
