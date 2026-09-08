# Spec: Trajectory causal e projeções sanitizadas

## Metadata

- Mode: `full`
- Status: `complete`
- Milestone: `A1`
- Planning revision: `2026-09-08`

## Goal

Emitir eventos versionados com sequence, action/span/parent IDs para preflight, model/tool/process, ALLOW/ASK/DENY, validação e resultado, mantendo readers dos records v1.

## Requirements

### REQ-001

Emitir eventos versionados com sequence, action/span/parent IDs para preflight, model/tool/process, ALLOW/ASK/DENY, validação e resultado, mantendo readers dos records v1.

### REQ-002

Persistir intenção crítica fora da sandbox antes do dispatch; redigir conteúdo antes de journal/UI/export e distinguir artefato privado de metadata remota.

### REQ-003

Fixture com modelo fake, retry, ALLOW/ASK/DENY e falha de validação produz cadeia causal sem gaps silenciosos; restart/disk-full são conservadores e canários não vazam.

## Acceptance Criteria

- REQ-001: comportamento definido observável em fixture determinística; contrato legado aplicável preservado.
- REQ-002: tentativa adversarial correspondente é negada/contida antes de ampliar autoridade, com reason code.
- REQ-003: Fixture com modelo fake, retry, ALLOW/ASK/DENY e falha de validação produz cadeia causal sem gaps silenciosos; restart/disk-full são conservadores e canários não vazam.

## Validation

- `REQ-001`: Validar contrato/resultado nas fixtures específicas descritas abaixo.
- `REQ-002`: Cobrir rejeição, drift/revogação, isolamento e ausência de autoridade/segredos conforme requisito.
- `REQ-003`: Reutilizar fixtures de runtime records/control plane; comparar contadores com eventos do fake-server; testar truncation, redaction e reconexão por cursor.
- Antes de ativar, fixar os comandos focados e limites numéricos a partir das fixtures e ferramentas realmente presentes; não instalar dependências autonomamente.
- Comportamento: regressões focadas primeiro. Fronteira crítica: integration/security tests pertinentes. Freeze: `make milestone-gate` uma vez, sem targets sobrepostos; companion usa seus checks próprios.

## Context and Constraints

Proposta sem implementação. Depende dos gates de A1 no [backlog](../docs/EXECUTION-BACKLOG-2026-09.md). [Arquitetura-alvo](../docs/TARGET-ARCHITECTURE.md) e [threat model](../docs/AUTONOMY-THREAT-MODEL.md) orientam o desenho; policy/AGENTS vigentes continuam aplicáveis. Exatamente uma spec pode ser ativa durante uma implementação por repositório; esta permanece draft até aprovação do plano e ativação da fatia.

## Non-Goals

Novo dashboard completo, token streaming, browser e schema de approvals executáveis.

## Implementation Notes

Áreas existentes para inspeção, não promessa de novos módulos: src/local-agent; schemas/runtime; tests/test_runtime_records.py; tests/test_control_plane.py.

Fixtures e testes: Reutilizar fixtures de runtime records/control plane; comparar contadores com eventos do fake-server; testar truncation, redaction e reconexão por cursor.

UX, observabilidade, rollback e stop rules específicos estão no contrato de A1 do backlog. Done requer todos os REQs, evidência registrada e nenhuma alegação de capability ainda não entregue. Se o escopo exceder esta fatia, separar follow-up draft antes de implementar.

## Traceability

- `REQ-001` → contrato/fixtures da área acima e entrega de A1.
- `REQ-002` → testes adversariais da fronteira e threat model aplicável a A1.
- `REQ-003` → caso de aceite determinístico descrito em Requirements e sua evidência de validação.
