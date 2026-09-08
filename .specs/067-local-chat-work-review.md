# Spec: Chat de trabalho, revisão e lifecycle

## Metadata

- Mode: `full`
- Status: `complete`
- Milestone: `A4`
- Planning revision: `2026-09-08`

## Goal

Expor execução autorizada A3, plano, tool/process, diff/testes/budget e ASK na UI local; pause/cancel/continue usam estados do supervisor e revisão da intenção exata.

## Requirements

### REQ-001

Expor execução autorizada A3, plano, tool/process, diff/testes/budget e ASK na UI local; pause/cancel/continue usam estados do supervisor e revisão da intenção exata.

### REQ-002

Aprovar não troca workspace/payload/grant; revogação impede novas ações; rollback usa capacidades e snapshots compatíveis, com limites visíveis e sem replay legado.

### REQ-003

Fluxo escolher projeto→chat→editar/testar→revisar diff→aprovar promoção funciona em fixtures; stale approval não executa; reconnect/cancel não duplica ação.

## Acceptance Criteria

- REQ-001: comportamento definido observável em fixture determinística; contrato legado aplicável preservado.
- REQ-002: tentativa adversarial correspondente é negada/contida antes de ampliar autoridade, com reason code.
- REQ-003: Fluxo escolher projeto→chat→editar/testar→revisar diff→aprovar promoção funciona em fixtures; stale approval não executa; reconnect/cancel não duplica ação.

## Validation

- `REQ-001`: Validar contrato/resultado nas fixtures específicas descritas abaixo.
- `REQ-002`: Cobrir rejeição, drift/revogação, isolamento e ausência de autoridade/segredos conforme requisito.
- `REQ-003`: Fixtures integradas de UI/control plane, promoção/drift e cancel durante aprovação/validação; receipts exibem resultado desconhecido quando aplicável.
- Antes de ativar, fixar os comandos focados e limites numéricos a partir das fixtures e ferramentas realmente presentes; não instalar dependências autonomamente.
- Comportamento: regressões focadas primeiro. Fronteira crítica: integration/security tests pertinentes. Freeze: `make milestone-gate` uma vez, sem targets sobrepostos; companion usa seus checks próprios.

## Context and Constraints

Proposta sem implementação. Depende dos gates de A4 no [backlog](../docs/EXECUTION-BACKLOG-2026-09.md). [Arquitetura-alvo](../docs/TARGET-ARCHITECTURE.md) e [threat model](../docs/AUTONOMY-THREAT-MODEL.md) orientam o desenho; policy/AGENTS vigentes continuam aplicáveis. Exatamente uma spec pode ser ativa durante uma implementação por repositório; esta permanece draft até aprovação do plano e ativação da fatia.

## Non-Goals

Mobile escreve por herança, merge automático, rollback de efeitos externos ou token streaming obrigatório.

## Implementation Notes

Áreas existentes para inspeção, não promessa de novos módulos: src/local-agent; tests/test_control_plane.py; companion lai-gateway/lai_gateway/server.py; companion static UI.

Fixtures e testes: Fixtures integradas de UI/control plane, promoção/drift e cancel durante aprovação/validação; receipts exibem resultado desconhecido quando aplicável.

UX, observabilidade, rollback e stop rules específicos estão no contrato de A4 do backlog. Done requer todos os REQs, evidência registrada e nenhuma alegação de capability ainda não entregue. Se o escopo exceder esta fatia, separar follow-up draft antes de implementar.

## Traceability

- `REQ-001` → contrato/fixtures da área acima e entrega de A4.
- `REQ-002` → testes adversariais da fronteira e threat model aplicável a A4.
- `REQ-003` → caso de aceite determinístico descrito em Requirements e sua evidência de validação.
