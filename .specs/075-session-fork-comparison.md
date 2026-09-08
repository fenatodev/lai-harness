# Spec: Fork e comparação de experimentos

## Metadata

- Mode: `full`
- Status: `complete`
- Milestone: `A9`
- Planning revision: `2026-09-08`

## Goal

Criar sessões/runs derivados com snapshot/base comum e workspaces independentes; comparar correctness/testes/patch antes de latency/calls/tokens/recursos.

## Requirements

### REQ-001

Criar sessões/runs derivados com snapshot/base comum e workspaces independentes; comparar correctness/testes/patch antes de latency/calls/tokens/recursos.

### REQ-002

Fork não copia token/approval/processo nem concede novo budget; grant filho é subset autorizado e reservas contam no experimento pai; histórico permanece untrusted.

### REQ-003

Duas abordagens fixture usam mesma base, outputs separados e custo agregado; resultados não equivalentes são inconclusivos; integração só por promoção hash/drift.

## Acceptance Criteria

- REQ-001: comportamento definido observável em fixture determinística; contrato legado aplicável preservado.
- REQ-002: tentativa adversarial correspondente é negada/contida antes de ampliar autoridade, com reason code.
- REQ-003: Duas abordagens fixture usam mesma base, outputs separados e custo agregado; resultados não equivalentes são inconclusivos; integração só por promoção hash/drift.

## Validation

- `REQ-001`: Validar contrato/resultado nas fixtures específicas descritas abaixo.
- `REQ-002`: Cobrir rejeição, drift/revogação, isolamento e ausência de autoridade/segredos conforme requisito.
- `REQ-003`: Reusar session/snapshot/promotion fixtures e fake model determinístico; testar drift entre forks, expiry e export sanitizado.
- Antes de ativar, fixar os comandos focados e limites numéricos a partir das fixtures e ferramentas realmente presentes; não instalar dependências autonomamente.
- Comportamento: regressões focadas primeiro. Fronteira crítica: integration/security tests pertinentes. Freeze: `make milestone-gate` uma vez, sem targets sobrepostos; companion usa seus checks próprios.

## Context and Constraints

Proposta sem implementação. Depende dos gates de A9 no [backlog](../docs/EXECUTION-BACKLOG-2026-09.md). [Arquitetura-alvo](../docs/TARGET-ARCHITECTURE.md) e [threat model](../docs/AUTONOMY-THREAT-MODEL.md) orientam o desenho; policy/AGENTS vigentes continuam aplicáveis. Exatamente uma spec pode ser ativa durante uma implementação por repositório; esta permanece draft até aprovação do plano e ativação da fatia.

## Non-Goals

Delegates simultâneos nesta fatia, seleção automática de vencedor ou merge na fonte.

## Implementation Notes

Áreas existentes para inspeção, não promessa de novos módulos: src/lai_sessions.py; src/local-agent; tests/test_control_sessions.py; tests/test_runtime_records.py.

Fixtures e testes: Reusar session/snapshot/promotion fixtures e fake model determinístico; testar drift entre forks, expiry e export sanitizado.

UX, observabilidade, rollback e stop rules específicos estão no contrato de A9 do backlog. Done requer todos os REQs, evidência registrada e nenhuma alegação de capability ainda não entregue. Se o escopo exceder esta fatia, separar follow-up draft antes de implementar.

## Traceability

- `REQ-001` → contrato/fixtures da área acima e entrega de A9.
- `REQ-002` → testes adversariais da fronteira e threat model aplicável a A9.
- `REQ-003` → caso de aceite determinístico descrito em Requirements e sua evidência de validação.
