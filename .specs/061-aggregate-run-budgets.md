# Spec: Budget Controller agregado

## Metadata

- Mode: `full`
- Status: `complete`
- Milestone: `A1`
- Planning revision: `2026-09-08`

## Goal

Reservar antes do dispatch e reconciliar model/tool/shell/retry/validation/token/tempo, inclusive chamadas auxiliares; persistir ledger e reserva de finalização.

## Requirements

### REQ-001

Reservar antes do dispatch e reconciliar model/tool/shell/retry/validation/token/tempo, inclusive chamadas auxiliares; persistir ledger e reserva de finalização.

### REQ-002

Somar reservas de filhos ao teto pai; counters desconhecidos não viram zero; cancel/restart não reiniciam consumo; distinguir limites OS de chamadas exatas.

### REQ-003

Clock/provider fake, retries, verificadores e concorrência não ultrapassam teto; ao esgotar, não ocorre nova ação e saída registra budget_exhausted e evidência pendente.

## Acceptance Criteria

- REQ-001: comportamento definido observável em fixture determinística; contrato legado aplicável preservado.
- REQ-002: tentativa adversarial correspondente é negada/contida antes de ampliar autoridade, com reason code.
- REQ-003: Clock/provider fake, retries, verificadores e concorrência não ultrapassam teto; ao esgotar, não ocorre nova ação e saída registra budget_exhausted e evidência pendente.

## Validation

- `REQ-001`: Validar contrato/resultado nas fixtures específicas descritas abaixo.
- `REQ-002`: Cobrir rejeição, drift/revogação, isolamento e ausência de autoridade/segredos conforme requisito.
- `REQ-003`: Ampliar fixtures de guards/control plane com relógio fake, corrida de reservas, restart e contagem de chamadas auxiliares.
- Antes de ativar, fixar os comandos focados e limites numéricos a partir das fixtures e ferramentas realmente presentes; não instalar dependências autonomamente.
- Comportamento: regressões focadas primeiro. Fronteira crítica: integration/security tests pertinentes. Freeze: `make milestone-gate` uma vez, sem targets sobrepostos; companion usa seus checks próprios.

## Context and Constraints

Proposta sem implementação. Depende dos gates de A1 no [backlog](../docs/EXECUTION-BACKLOG-2026-09.md). [Arquitetura-alvo](../docs/TARGET-ARCHITECTURE.md) e [threat model](../docs/AUTONOMY-THREAT-MODEL.md) orientam o desenho; policy/AGENTS vigentes continuam aplicáveis. Exatamente uma spec pode ser ativa durante uma implementação por repositório; esta permanece draft até aprovação do plano e ativação da fatia.

## Non-Goals

Router, delegates reais e contagem universal de requests internos de shell sem enforcement.

## Implementation Notes

Áreas existentes para inspeção, não promessa de novos módulos: src/local-agent; tests/test_guards_integration.py; tests/test_control_plane.py.

Fixtures e testes: Ampliar fixtures de guards/control plane com relógio fake, corrida de reservas, restart e contagem de chamadas auxiliares.

UX, observabilidade, rollback e stop rules específicos estão no contrato de A1 do backlog. Done requer todos os REQs, evidência registrada e nenhuma alegação de capability ainda não entregue. Se o escopo exceder esta fatia, separar follow-up draft antes de implementar.

## Traceability

- `REQ-001` → contrato/fixtures da área acima e entrega de A1.
- `REQ-002` → testes adversariais da fronteira e threat model aplicável a A1.
- `REQ-003` → caso de aceite determinístico descrito em Requirements e sua evidência de validação.
