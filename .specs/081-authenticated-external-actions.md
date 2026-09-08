# Spec: Primeiro adapter de efeito Git autenticado

## Metadata

- Mode: `full`
- Status: `complete`
- Milestone: `A6`
- Planning revision: `2026-09-08`

## Goal

Implementar primeiro adapter Git remoto sobre broker 063 para branch/destino explicitamente autorizado, com intenção/patch/refs/baseline/TTL e receipt durável; fake remote antes de conta real.

## Requirements

### REQ-001

Implementar primeiro adapter Git remoto sobre broker 063 para branch/destino explicitamente autorizado, com intenção/patch/refs/baseline/TTL e receipt durável; fake remote antes de conta real.

### REQ-002

Remote push/merge/publicação não são shell interno: revalidar precondições e grants, bloquear branch protegida/classe não concedida e nunca repetir operação incerta automaticamente.

### REQ-003

Fake remote aceita ação aprovada uma vez; resposta perdida gera outcome_unknown, drift/replay/target alterado não executam e credential canary não entra no executor/UI.

## Acceptance Criteria

- REQ-001: comportamento definido observável em fixture determinística; contrato legado aplicável preservado.
- REQ-002: tentativa adversarial correspondente é negada/contida antes de ampliar autoridade, com reason code.
- REQ-003: Fake remote aceita ação aprovada uma vez; resposta perdida gera outcome_unknown, drift/replay/target alterado não executam e credential canary não entra no executor/UI.

## Validation

- `REQ-001`: Validar contrato/resultado nas fixtures específicas descritas abaixo.
- `REQ-002`: Cobrir rejeição, drift/revogação, isolamento e ausência de autoridade/segredos conforme requisito.
- `REQ-003`: Fixtures locais de remote/broker/approval/idempotency sem rede pública; novos adapters browser/MCP/cloud exigem specs derivadas com efeitos e testes próprios.
- Antes de ativar, fixar os comandos focados e limites numéricos a partir das fixtures e ferramentas realmente presentes; não instalar dependências autonomamente.
- Comportamento: regressões focadas primeiro. Fronteira crítica: integration/security tests pertinentes. Freeze: `make milestone-gate` uma vez, sem targets sobrepostos; companion usa seus checks próprios.

## Context and Constraints

Proposta sem implementação. Depende dos gates de A6 no [backlog](../docs/EXECUTION-BACKLOG-2026-09.md). [Arquitetura-alvo](../docs/TARGET-ARCHITECTURE.md) e [threat model](../docs/AUTONOMY-THREAT-MODEL.md) orientam o desenho; policy/AGENTS vigentes continuam aplicáveis. Exatamente uma spec pode ser ativa durante uma implementação por repositório; esta permanece draft até aprovação do plano e ativação da fatia.

## Non-Goals

Publicar release real, merge protegido, e-mail/compra/cloud genéricos ou token do usuário no prompt.

## Implementation Notes

Áreas existentes para inspeção, não promessa de novos módulos: src/local-agent; tests/test_control_plane.py; tests/test_runtime_records.py; docs/GATEWAY-CONTRACT.md.

Fixtures e testes: Fixtures locais de remote/broker/approval/idempotency sem rede pública; novos adapters browser/MCP/cloud exigem specs derivadas com efeitos e testes próprios.

UX, observabilidade, rollback e stop rules específicos estão no contrato de A6 do backlog. Done requer todos os REQs, evidência registrada e nenhuma alegação de capability ainda não entregue. Se o escopo exceder esta fatia, separar follow-up draft antes de implementar.

## Traceability

- `REQ-001` → contrato/fixtures da área acima e entrega de A6.
- `REQ-002` → testes adversariais da fronteira e threat model aplicável a A6.
- `REQ-003` → caso de aceite determinístico descrito em Requirements e sua evidência de validação.
