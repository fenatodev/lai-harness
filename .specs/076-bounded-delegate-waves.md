# Spec: Delegates em waves com ownership

## Metadata

- Mode: `full`
- Status: `complete`
- Milestone: `A9`
- Planning revision: `2026-09-08`

## Goal

Orquestrar DAG de tarefas em waves com scopes/contextos próprios, ownership de arquivos, budgets reservados no pai e agregação de resultados evidenciada.

## Requirements

### REQ-001

Orquestrar DAG de tarefas em waves com scopes/contextos próprios, ownership de arquivos, budgets reservados no pai e agregação de resultados evidenciada.

### REQ-002

Filho não amplia grants ou edita área alheia; cancelar/revogar pai alcança toda árvore; reconciliação detecta conflito de arquivo/contrato antes de promoção.

### REQ-003

Fixtures disjuntas completam e agregam; dependência falha, colisão, budget esgotado e cancel impedem sucesso falso; execução serial permanece disponível para hardware limitado.

## Acceptance Criteria

- REQ-001: comportamento definido observável em fixture determinística; contrato legado aplicável preservado.
- REQ-002: tentativa adversarial correspondente é negada/contida antes de ampliar autoridade, com reason code.
- REQ-003: Fixtures disjuntas completam e agregam; dependência falha, colisão, budget esgotado e cancel impedem sucesso falso; execução serial permanece disponível para hardware limitado.

## Validation

- `REQ-001`: Validar contrato/resultado nas fixtures específicas descritas abaixo.
- `REQ-002`: Cobrir rejeição, drift/revogação, isolamento e ausência de autoridade/segredos conforme requisito.
- `REQ-003`: Fake workers/model e relógio, max parallelism pequeno, ownership/dag cycle/conflict/cancel tests; medir ganho antes de elevar concorrência.
- Antes de ativar, fixar os comandos focados e limites numéricos a partir das fixtures e ferramentas realmente presentes; não instalar dependências autonomamente.
- Comportamento: regressões focadas primeiro. Fronteira crítica: integration/security tests pertinentes. Freeze: `make milestone-gate` uma vez, sem targets sobrepostos; companion usa seus checks próprios.

## Context and Constraints

Proposta sem implementação. Depende dos gates de A9 no [backlog](../docs/EXECUTION-BACKLOG-2026-09.md). [Arquitetura-alvo](../docs/TARGET-ARCHITECTURE.md) e [threat model](../docs/AUTONOMY-THREAT-MODEL.md) orientam o desenho; policy/AGENTS vigentes continuam aplicáveis. Exatamente uma spec pode ser ativa durante uma implementação por repositório; esta permanece draft até aprovação do plano e ativação da fatia.

## Non-Goals

Autocriação ilimitada de agentes, swarm, aprendizagem de policy ou dependência obrigatória de graph/router.

## Implementation Notes

Áreas existentes para inspeção, não promessa de novos módulos: src/local-agent; src/lai_sessions.py; tests/test_control_plane.py; tests/test_control_sessions.py.

Fixtures e testes: Fake workers/model e relógio, max parallelism pequeno, ownership/dag cycle/conflict/cancel tests; medir ganho antes de elevar concorrência.

UX, observabilidade, rollback e stop rules específicos estão no contrato de A9 do backlog. Done requer todos os REQs, evidência registrada e nenhuma alegação de capability ainda não entregue. Se o escopo exceder esta fatia, separar follow-up draft antes de implementar.

## Traceability

- `REQ-001` → contrato/fixtures da área acima e entrega de A9.
- `REQ-002` → testes adversariais da fronteira e threat model aplicável a A9.
- `REQ-003` → caso de aceite determinístico descrito em Requirements e sua evidência de validação.
